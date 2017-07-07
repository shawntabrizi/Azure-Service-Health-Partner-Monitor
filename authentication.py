# External Python Libraries Used:
import requests
import adal
from msrestazure.azure_active_directory import AdalAuthentication

# Our Python Functions:
import appconfig as g

# Create headers for REST queries. Used for both ARM and AAD Graph API queries.
def create_headers(access_token):
    return {
        'Authorization': 'Bearer ' + access_token,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
        }

# Note that when a tenant is not specified, we use the 'common' endpoint
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
    login_url = '%(url)s?response_type=%(response_type)s&client_id=%(client_id)s&redirect_uri=%(redirect_uri)s&state=%(state)s&prompt=consent' %params

    # Return URL
    return login_url

# Get Access Token using Authorization Code
def get_access_token_code(code, redirect_uri, resource, tenant_id='common'):
    context = adal.AuthenticationContext(g.aad_endpoint + tenant_id)
    return context.acquire_token_with_authorization_code(code, redirect_uri, resource, g.clientId, g.clientSecret)['accessToken']

# Special Credentials are used for the ARM Python SDK
# User Credential Object
def get_user_credentials(code, redirect_uri, resource, tenant_id='common'):
    context = adal.AuthenticationContext(g.aad_endpoint + tenant_id)
    credentials = AdalAuthentication(context.acquire_token_with_authorization_code, code, redirect_uri, resource, g.clientId, g.clientSecret)
    return credentials

# App Credential Object
def get_app_credentials(resource, tenant_id='common'):
    context = adal.AuthenticationContext(g.aad_endpoint + tenant_id)
    credentials = AdalAuthentication(context.acquire_token_with_client_credentials, resource, g.clientId, g.clientSecret)
    return credentials