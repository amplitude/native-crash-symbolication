import logging

from tornado.web import RequestHandler


_logger = logging.getLogger(__name__)

class MainHandler(RequestHandler):
  
    def get(self, app):
        self.redirect('https://www.amplitude.com/app/%s/crashes' % app)
        return

class LandingHandler(RequestHandler):

    def get(self):
        self.redirect('https://www.amplitude.com/')

class SettingsHandler(RequestHandler):

    def get(self):
        self.redirect('https://www.amplitude.com/settings')
