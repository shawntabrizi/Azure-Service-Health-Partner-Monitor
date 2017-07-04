# External Python Libraries Used:
import requests

# Our Python Functions:
import appconfig as g

# Create headers for REST queries. Used for both ARM and AAD Graph API queries.
def create_headers(access_token):
    return {
        'Authorization': 'Bearer ' + access_token,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
        }

### Start of Authorization Code Grant Flow Authentication
# Note for the Authorization Code Grant Flow, we use the 'common' endpoint by default, rather than specifying a tenant.

# Generate AAD Login URL
def login_url(state, redirect_uri, tenant_id='common'):
    params = {
        'url': g.aad_endpoint + tenant_id + '/oauth2/authorize',
        'response_type': 'code',
        'client_id': g.clientId,
        'redirect_uri': redirect_uri,
        'state': state
        }

    # You can add additional querystrings here if you want to do things like force login or prompt for consent
    login_url = '%(url)s?response_type=%(response_type)s&client_id=%(client_id)s&redirect_uri=%(redirect_uri)s&state=%(state)s' %params

    # Return URL
    return login_url

# Get Access Token using Authorization Code
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

    # Return raw Access Token
    return r.json()['access_token']

### End of Authorization Code Grant Flow Authentication

### Start of Client Credential Flow Authentication
# Note that we need to specify Tenant ID for these App Only Tokens. If you use the 'common' endpoint, it will choose the tenant where the app is registered.
def get_access_token_app(resource, tenant_id):
    payload = {
        'client_id': g.clientId,
        'grant_type': 'client_credentials',
        'resource': resource,
        'client_secret': g.clientSecret
        }

    token_endpoint = g.aad_endpoint + tenant_id + '/oauth2/token'
    r = requests.post(token_endpoint, data=payload)

    # Return raw Access Token
    return r.json()['access_token']