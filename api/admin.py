#!/usr/bin/env python

import webapp2
import logging
import inspect
import models
from google.appengine.ext import ndb


class EmptyDatabaseHandler(webapp2.RequestHandler):
    def get(self):
        for name in dir(models):
            potential_class = getattr(models, name)
            if inspect.isclass(potential_class) and potential_class.__module__ == "models":
                logging.info("Deleting all entities of '%s'" % potential_class.__name__)
                ndb.delete_multi(
                    potential_class.query().fetch(keys_only=True)
                )

app = webapp2.WSGIApplication([
    (r'/api/admin/emptyDatabase', EmptyDatabaseHandler),
], debug=True)
