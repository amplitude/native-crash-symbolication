import tornado.ioloop
import tornado.web
import tornado.httpserver
import settings

if __name__ == "__main__":
    settings.load()
    
    import logging
    import routes
    from tornado.options import options

    application = tornado.web.Application(
        routes.ALL,
        debug=options.debug,
        static_path=options.static_path,
        template_path=options.template_path,
        cookie_secret=options.cookie_secret,
        login_url='/login')

    max_buffer_size = 262144000 # 250 MB

    if options.ssl_cert and options.ssl_key:
        ssl_options = {
                       'certfile': options.ssl_cert,
                       'keyfile': options.ssl_key
                       }
        app_server = tornado.httpserver.HTTPServer(application, ssl_options=ssl_options, xheaders=True, max_buffer_size=max_buffer_size)
        app_server.listen(options.port)
    else:
        application.listen(options.port, xheaders=True, max_buffer_size=max_buffer_size)

    try:
        logger = logging.getLogger(__name__)
        logger.info('Listening on port %i...' % options.port)
        tornado.ioloop.IOLoop.instance().set_blocking_log_threshold(10.0)
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        logger.info('Done')
        pass
