import requests
import appconfigreal as g

def create_headers(access_token):
    return {
        'Authorization': 'Bearer ' + access_token,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
        }

def login_url(state, redirect_uri, tenant_id='common'):
    params = {
        'url': g.aad_endpoint + tenant_id + '/oauth2/authorize',
        'response_type': 'code',
        'client_id': g.clientId,
        'redirect_uri': redirect_uri,
        'state': state
        }

    login_url = '%(url)s?response_type=%(response_type)s&client_id=%(client_id)s&redirect_uri=%(redirect_uri)s&state=%(state)s&prompt=consent' %params
    return login_url

def get_access_token_code(code, redirect_uri, resource, tenant_id='common'):
    payload = {
        'client_id': g.clientId,
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': redirect_uri,
        'resource': resource,
        'client_secret': g.clientSecret
    }
    
    token_endpoint = g.aad_endpoint + tenant_id + '/oauth2/token'
    r = requests.post(token_endpoint, data=payload)
    return r.json()['access_token']

def get_access_token_app(resource, tenant_id='common'):
    payload = {
        'client_id': g.clientId,
        'grant_type': 'client_credentials',
        'resource': resource,
        'client_secret': g.clientSecret
        }

    token_endpoint = g.aad_endpoint + tenant_id + '/oauth2/token'
    r = requests.post(token_endpoint, data=payload)

    return r.json()['access_token']