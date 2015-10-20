import json
from google.appengine.api import users
import datetime
from google.appengine.ext import ndb
from google.appengine.api import channel


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
        if request_data.get(key, None) is None:
            error_400(response, "VALIDATION_ERROR_MISSING_DATA", "The request data is missing the input value '%s'" % key)
            return False
    return True


def validate_is_team_owner(response, player, team):
    if not team.owner == player.key:
        error_400(response, "ERROR_NOT_OWNER", "Not the team owner.")
        return False
    else:
        return True


def set_json_response(response, data):
    response.headers['Content-Type'] = 'application/json'
    response.out.write(json.dumps(data))


def current_user_player():
    user = users.get_current_user()
    return ndb.Key('Player', user.user_id()).get()  # I use 'Player' because it allows me not to import Player from models, which again avoids a looped import


def datetime_to_epoch(datetime_obj):
    return int((datetime_obj - datetime.datetime(1970, 1, 1)).total_seconds()),


def websocket_notify_player(event, player_key, object_path, object):
    """
    Notifies an specific player of a new event and possible local/javascript data that should be updated. Yes this means that
    the server has control over the client data. This increases the coupling between server-client which is an acceptable tradeoff for less code.

    :param event: Tag identifier named in the format [EntityInFocus]_[Action]. The best example to illustrate this is what was previously called
    "MatchFound" and "MatchFinished" which are now
        "Player_MatchFound"  - Because it is the players that is in focus and that is targeted by the notification.
        "Match_Finished" - Because its the match related players that are targeted by the notification.

    :param player_key:

    :param object_path: The javascript object path. Has to be on the angularjs $rootScope. Examples:
        Update single value (cash):
            "player" with object {'cash': 100}
        Update object:
            "player" with object {'team': team_data}
        Update/add item to array:
            "player.team.applications.[2131231231231]" with object. Updates if id 2131231231231 is found in array. Adds otherwise.
        Delete item from array:
            "player.team.applications.-[2131231231231]". Also with object because an controller might want to subscribe to the event and use the object data.

    :param object: Has to be a dict

    For full examples search the code for "websocket_notify_player"

    """
    channel.send_message(player_key.id(), json.dumps({'event': event, 'object_path': object_path, 'object': object}))


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
