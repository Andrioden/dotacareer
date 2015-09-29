# Correct path so ndb can be imported (in models.py)
import sys
sys.path.insert(0, "C:\Program Files (x86)\Google\google_appengine")
import dev_appserver
dev_appserver.fix_sys_path()

import models
import inspect
from google.appengine.ext import ndb

def get_all_classes_from_module():
    for name in dir(models):
        potential_class = getattr(models, name)
        if inspect.isclass(potential_class) and potential_class.__module__ == "models":
            print "Deleting all %s" % potential_class.__name__
            print potential_class.__module__
            # ndb.delete_multi(
            #     models.Bet.query().fetch(keys_only=True)
            # )


get_all_classes_from_module()