import requests
import appconfig as g


def login_url(state, redirect_uri):
    params = {
        'url': g.authorization_endpoint,
        'response_type': 'code',
        'client_id': g.clientId,
        'redirect_uri': redirect_uri,
        'state': state
        }

    login_url = '%(url)s?response_type=%(response_type)s&client_id=%(client_id)s&redirect_uri=%(redirect_uri)s&state=%(state)s&prompt=consent' %params
    return login_url

def get_access_token_arm(code, redirect_uri):
    payload = {
        'client_id': g.clientId,
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': redirect_uri,
        'resource': g.resource_arm,
        'client_secret': g.clientSecret
    }
    r = requests.post(g.token_endpoint, data=payload)
    return r.json()['access_token']

def get_access_token_graph(code, redirect_uri):
    payload = {
        'client_id': g.clientId,
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': redirect_uri,
        'resource': g.resource_graph,
        'client_secret': g.clientSecret
    }
    r = requests.post(g.token_endpoint, data=payload)
    return r.json().get('access_token', '')

def create_headers(access_token):
    return {
        'Authorization': 'Bearer ' + access_token,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
        }

def get_app_access_token_arm(tenant_id):
    payload = {
        'client_id': g.clientId,
        'grant_type': 'client_credentials',
        'resource': g.resource_arm,
        'client_secret': g.clientSecret
        }

    tenant_token_endpoint = g.token_endpoint.replace('common', tenant_id)
    r = requests.post(tenant_token_endpoint, data=payload)

    return r.json()['access_token']