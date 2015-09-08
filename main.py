import os
import webapp2
import jinja2
import logging
from google.appengine.api import users
from google.appengine.api import channel

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class MainHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if not user:
            return webapp2.redirect(users.create_login_url())

        channel_token = channel.create_channel(user.user_id())
        template_values = {'channel_token': channel_token}
        logging.info("Creating websocket channel with userid %s which is token %s" % (user.user_id(), channel_token))

        template = JINJA_ENVIRONMENT.get_template("index.html")
        self.response.write(template.render(template_values))


class LogoutHandler(webapp2.RequestHandler):
    def get(self):
        logging.info("LOGGING OUT")
        return webapp2.redirect(users.create_logout_url("/"))


app = webapp2.WSGIApplication([
    ('/logout', LogoutHandler),
    ('/.*', MainHandler),
], debug=True)