import json
from google.appengine.api import users
from models import Player

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
#
#
# def forbidden_403(response, code, message):
#     response.headers['Content-Type'] = 'application/json'
#     response.set_status(403)
#     response.out.write(json.dumps({'error_code': code, 'error_message': message}))
#
#


#
#
# def validate_logged_in_admin(response):
#     if not users.is_current_user_admin():
#         forbidden_403(response, "VALIDATION_ERROR_MISSING_ADMIN_PERMISSION", "The browsing user is logged in and authenticated, but does not have admin permissions.")
#         return False
#     else:
#         return True