# -*- coding: UTF-8 -*-

def start():
    global ioloop, t
    import controller
    from threading import Thread
    from tornado.ioloop import IOLoop
    from src import messages
    
    messages.starting()
    
    ioloop = IOLoop.instance()
    t = Thread(target=lambda:ioloop.start())
    t.start()
    
    messages.wellcome()

def stop():
    from src import messages
    
    def callback():
        from src import db
        db.client.disconnect()
        ioloop.stop()
        
    ioloop.add_callback(callback)
    t.join()
    
    messages.stopped()

if __name__ == "__main__":
    from src.utils import run_inside
    from tornado.gen import coroutine
    
    start()

    @run_inside(ioloop.add_callback)
    def clients():
        from controller import MSGHandler
        total = MSGHandler.client_count
        current = len(MSGHandler.clients)
        print('Connected clients: %d' % current)
        print('Total connections opened: %d' % total)
        print(
            'Total connections closed: %d' % (total-current)
        )

    @run_inside(ioloop.add_callback)
    def bcast(message):
        from controller import MSGHandler
        MSGHandler.broadcast(message)

    def q():
        from sys import exit
        stop()
        exit()
    
    def h():
        from sys import modules
        help(modules[__name__])
    
    def make(goal):
        from os import system
        system('make %s' % goal)
    
    @run_inside(ioloop.add_callback)
    def clients():
        from controller import MSGHandler
        total = MSGHandler.client_count
        current = len(MSGHandler.clients)
        print('Connected clients: %d' % current)
        print('Total connections opened: %d' % total)
        print(
            'Total connections closed: %d' % (total-current)
        )

    @run_inside(ioloop.add_callback)
    def bcast(message):
        from controller import MSGHandler
        MSGHandler.broadcast(message)

    @run_inside(ioloop.add_callback)
    @coroutine
    def add_room(room_name, svg_path,
                 output_path='./qrmaster'):
        import src.utils.qrmaster as qrm
        from pymongo.errors import DuplicateKeyError, \
                                   OperationFailure
        from conf import app_name, proxy_url, \
                         app_logo_path
        from src.db.room import Room, CodeType
        from src import messages as msg
        
        try:
            _, code_objs = yield Room.create(room_name,
                                         svg_path)
            codes = (
                [
                    c.id,
                    c.room_id if c.code_type ==
                    CodeType.room.value else c.seat_id
                ]
                for c in code_objs
            )
            qrm.generate(codes, url=proxy_url,
                         title=app_name,
                         img_path=app_logo_path,
                         output_path=output_path)
            
        except OperationFailure:
            pass
