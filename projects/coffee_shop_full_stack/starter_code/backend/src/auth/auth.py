import json
from flask import request, _request_ctx_stack, abort
from functools import wraps
from jose import jwt
from urllib.request import urlopen

AUTH0_DOMAIN = 'dev-ygohk7ap.eu.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'coffee-shop'


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


def get_token_auth_header():
    """
    Checks that the request has the a correctly formatted
    Authorization header, and returns the JSON web token.
    """
    if 'Authorization' not in request.headers:
        raise AuthError

    auth_header = request.headers['Authorization']
    header_parts = auth_header.split(' ')

    if len(header_parts) != 2:
        raise AuthError
    elif header_parts[0].lower() != 'bearer':
        raise AuthError

    token = header_parts[1]
    return token


def check_permissions(permission, payload):
    """
    Checks that the given permission, i.e.
    'patch:drinks' is in the payload.
    """
    if 'permissions' not in payload.keys():
        raise AuthError

    if permission not in payload['permissions']:
        raise AuthError

    return True


def verify_decode_jwt(token):
    """
    Boilerplate code which contacts Auth0 and provides numerous
    checks to assert that the given token is valid.
    """
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )

            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Please, check the audience and issuer.'
            }, 401)
        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)
    raise AuthError({
        'code': 'invalid_header',
        'description': 'Unable to find the appropriate key.'
    }, 400)


def requires_auth(permission=''):
    """
    Decorator for api endpoints which need certain
    permissions to proceed.
    """
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                token = get_token_auth_header()
                payload = verify_decode_jwt(token)
                check_permissions(permission, payload)
            except:
                abort(401)
            return f(payload, *args, **kwargs)

        return wrapper

    return requires_auth_decorator
