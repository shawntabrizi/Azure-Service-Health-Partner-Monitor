# External Python Libraries Used:
import requests

# Our Python Functions:
from authentication import create_headers
import appconfig as g

# Query the AAD Graph API to get the Object ID of the Service Principal using the Application's App ID
def get_service_principal_object_id(access_token):
    headers = create_headers(access_token)

    params = {
        'url': g.resource_graph,
        'api_version': g.api_version_graph,
        'app_id': g.clientId
        }

    # Note we are using the "myorganization" endpoint, which figures out tenant information from the claims in the access token
    sp_by_appid_url = '%(url)s/myorganization/servicePrincipalsByAppId/%(app_id)s/objectId?api-version=%(api_version)s' %params
    r = requests.get(sp_by_appid_url, headers=headers)

    #Return Object ID GUID
    return r.json()['value']

# Get tenant details for the signed in user. We only return Tenant Display Name and Tenant ID, but more information can be accessed if necessary.
def get_tenant_details(access_token):
    headers = create_headers(access_token)

    params = {
        'url': g.resource_graph,
        'api_version': g.api_version_graph
        }

    # Note we are using the "myorganization" endpoint, which figures out tenant information from the claims in the access token
    tenant_details_url = '%(url)s/myorganization/tenantDetails?api-version=%(api_version)s' %params
    r = requests.get(tenant_details_url, headers=headers)

    #Return Tenant Display Name String and Tenant ID GUID
    return r.json()['value'][0]['displayName'], r.json()['value'][0]['objectId']

# Get user details for the signed in user. We only return the User Principal Name (username) of the user, but more information can be accessed if necessary.
def get_user_details(access_token):
    headers = create_headers(access_token)

    params = {
        'url': g.resource_graph,
        'api_version': g.api_version_graph
        }

    # Note we are using the "me" endpoint, which figures out tenant and user information from the claims in the access token
    user_details_url = '%(url)s/me?api-version=%(api_version)s' %params
    r = requests.get(user_details_url, headers=headers)

    # Return Username String for user.
    return r.json()['userPrincipalName']