import json
from flask import request, _request_ctx_stack
from functools import wraps
from jose import jwt
from urllib.request import urlopen
import os

AUTH0_DOMAIN = os.environ['AUTH0_DOMAIN']
ALGORITHMS = os.environ['ALGORITHMS']
API_AUDIENCE = os.environ['API_AUDIENCE']
CLIENT_ID = os.environ['CLIENT_ID']
REDIRECT_URL = os.environ['REDIRECT_URL']

log_in_url = 'https://' + AUTH0_DOMAIN + '/authorize?audience=' + API_AUDIENCE \
             + '&response_type=token&client_id=' + CLIENT_ID \
             + '&redirect_uri=' + REDIRECT_URL


class AuthError(Exception):
    '''
    AuthError Exception
    A standardized way to communicate auth failure modes
    '''
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


def get_token_auth_header():
    '''
    Attempts to get the header from the request
    Raises an AuthError if no header is present
    Then, attempta to split bearer and the token
    and raises an AuthError if the header is malformed
    If all successful, returns the token part of the header
    Obtains the Access Token from the Authorization Header
    '''
    auth = ''

    try:
        auth = request.headers['Authorization']
    except KeyError:
        raise AuthError({
            'code': 'authorization_header_missing',
            'description': 'No authorization information.'
        }, 401)

    if not auth:
        raise AuthError({
            'code': 'authorization_header_missing',
            'description': 'Authorization header is expected.'
        }, 401)

    parts = auth.split()

    if parts[0].lower() != 'bearer':
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must start with "Bearer".'
        }, 401)

    elif len(parts) == 1:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Token not found.'
        }, 401)

    elif len(parts) > 2:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must be bearer token.'
        }, 401)

    token = parts[1]
    return token


def check_permissions(permission, payload):
    '''
    @INPUTS
        permission: string permission (i.e. 'post:games')
        payload: decoded jwt payload

    Raises an AuthError if permissions are not included in the payload
    Raises an AuthError if the requested permission string is not in
    the payload permissions array
    Otherwise, returns true
    '''
    if 'permissions' not in payload:
        raise AuthError({
            'code': 'invalid_claims',
            'description': 'Permissions not included in JWT.'
        }, 400)

    if permission not in payload['permissions']:
        raise AuthError({
            'code': 'unauthorized',
            'description': 'Permission not found.'
        }, 403)

    return True


def verify_decode_jwt(token):
    '''
    @INPUTS
        token: a json web token (string)

    Takes an Auth0 token with key id (kid)
    and verifies the token using Auth0 /.well-known/jwks.json
    Decodes the payload from the token and validates the claims
    Returns the decoded payload
    '''
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    unverified_header = ''

    try:
        unverified_header = jwt.get_unverified_header(token)
    except jwt.JWTError:
        raise AuthError({
            'code': 'invalid_claims',
            'description': 'Error decoding token headers.'
        }, 400)

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
                'description': 'Incorrect claims. Please, check the audience '
                               'and issuer.'
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
    '''
    @INPUTS
        permission: string permission (i.e. 'post:games')

    Calls get_token_auth_header method to get the token
    Then, calls the verify_decode_jwt method to decode the jwt
    Next, calls check_permissions method validate claims and check the
    requested permission
    Return the decorator which passes the decoded payload to the 
    decorated method
    '''
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
         
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator
