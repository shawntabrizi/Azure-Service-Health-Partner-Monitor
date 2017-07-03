from authentication import create_headers
import requests
import appconfig as g

def get_service_principal_object_id(access_token):
    headers = create_headers(access_token)

    params = {
        'url': g.resource_graph,
        'api_version': g.api_version_graph,
        'app_id': g.clientId
        }

    sp_by_appid_url = '%(url)s/myorganization/servicePrincipalsByAppId/%(app_id)s/objectId?api-version=%(api_version)s' %params

    r = requests.get(sp_by_appid_url, headers=headers)

    return r.json()['value']

def get_tenant_details(access_token):
    headers = create_headers(access_token)

    params = {
        'url': g.resource_graph,
        'api_version': g.api_version_graph
        }

    tenant_details_url = '%(url)s/myorganization/tenantDetails?api-version=%(api_version)s' %params

    r = requests.get(tenant_details_url, headers=headers)

    return r.json()['value'][0]['displayName'], r.json()['value'][0]['objectId']

def get_user_details(access_token):
    headers = create_headers(access_token)

    params = {
        'url': g.resource_graph,
        'api_version': g.api_version_graph
        }

    user_details_url = '%(url)s/me?api-version=%(api_version)s' %params

    r = requests.get(user_details_url, headers=headers)

    return r.json()['userPrincipalName']