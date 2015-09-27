#!/usr/bin/env python

import webapp2
import logging
from utils import *
from heroes_metrics import hero_metrics


class HeroesHandler(webapp2.RequestHandler):
    def get(self):
        set_json_response(self.response, hero_metrics)


app = webapp2.WSGIApplication([
    (r'/api/heroes/rest/', HeroesHandler),

], debug=True)
