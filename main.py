import os
import webapp2
import jinja2
from google.appengine.api import users

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class MainHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            template = JINJA_ENVIRONMENT.get_template("index.html")
            self.response.write(template.render())
        else:
            return webapp2.redirect(users.create_login_url())


app = webapp2.WSGIApplication([
    ('/.*', MainHandler)
], debug=True)
