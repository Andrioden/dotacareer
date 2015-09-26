import json
from google.appengine.api import users
from models import Player
import datetime


def error_400(response, code, message):
    response.headers['Content-Type'] = 'application/json'
    response.set_status(400)
    response.out.write(json.dumps({'code': code, 'message': message}))


def validate_logged_inn(response):
    user = users.get_current_user()
    if not user:
        unauthorized_401(response, "VALIDATION_ERROR_NOT_LOGGED_INN", "The browsing user is not logged in.")
        return False
    else:
        return True


def unauthorized_401(response, code, message):
    response.headers['Content-Type'] = 'application/json'
    response.set_status(401)
    response.out.write(json.dumps({'code': code, 'message': message}))


def validate_request_data(response, request_data, list_of_dict_keys):
    for key in list_of_dict_keys:
        if not request_data.get(key, False):
            error_400(response, "VALIDATION_ERROR_MISSING_DATA", "The request data is missing the input value '%s'" % key)
            return False
    return True


def set_json_response(response, data):
    response.headers['Content-Type'] = 'application/json'
    response.out.write(json.dumps(data))


def current_user_player():
    user = users.get_current_user()
    return Player.query(Player.userid == user.user_id()).get()


def is_hour_in_start_end_time_range_adjusted_for_timezone_offset_issue(start_hour, end_hour, check_hour):
    """ The browser allow the player to set a local start and end time. These two values are then adjusted by
    the timezone offset. Example follows:
    - Player set local start time 00:00 and end time 04:00
    - Players browser is in Norway which is GMT +2 hours.
    - Time is adjusted to start time -2 and end time 2.

    This scenario basically fucks up a normal range check, since how can the NOW hour every be negative?

    That is why it is done like this
    """
    legal_hours = []

    start_end_hour_dif = end_hour - start_hour

    if start_hour < 0:
        min_hour = 24 + start_hour
        max_hour = max(24, start_hour + start_end_hour_dif)
        legal_hours.extend(range(min_hour, max_hour+1))

    if end_hour > 24:
        min_hour = min(0, end_hour - start_end_hour_dif)
        max_hour = end_hour - 24
        legal_hours.extend(range(min_hour, max_hour))

    legal_hours.extend(range(start_hour, end_hour))

    #print "%s to %s gives legal hours: %s" % (start_hour, end_hour, legal_hours)

    return check_hour in legal_hours
