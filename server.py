import tornado.ioloop
import tornado.web


class HookHandler(tornado.web.RequestHandler):
    def get(self):
        pass

    def post(self):
        print self.request.body


if __name__ == '__main__':
    application = tornado.web.Application([
        (r'/hook', HookHandler)
    ])

    application.listen(8089, address="0.0.0.0")
    tornado.ioloop.IOLoop.current().start()