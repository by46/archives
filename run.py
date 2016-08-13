"""deimos entry point

"""

from gevent.wsgi import WSGIServer

from archives import app

if __name__ == '__main__':

    app.logger.info('archives listening %s:%s', app.config['HTTP_HOST'], app.config['HTTP_PORT'])
    WSGIServer((app.config['HTTP_HOST'], app.config['HTTP_PORT']), application=app).serve_forever()
