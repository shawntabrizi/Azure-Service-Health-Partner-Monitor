# External Python Libraries Used:
import requests
import uuid

# Our Python Functions:
from authentication import create_headers
import appconfig as g

# Get a list of the Azure Subscriptions available to the User in the Tenant Context
def get_subscriptions(access_token):
    headers = create_headers(access_token)

    params = {
        'url': g.resource_arm,
        'api_version': "2016-07-01"
        }

    subscriptions_url = '%(url)s/subscriptions?api-version=%(api_version)s' %params
    r = requests.get(subscriptions_url, headers=headers)

    #Return the full JSON response
    return r.json()

# Get the Activity Log for a particular Azure Subscription
def get_activity_log(access_token, subscription_id):
    headers = create_headers(access_token)

    #Adjust these paramters to change your query
    params = {
        'url': g.resource_arm,
        'subscription_id': subscription_id,
        'api_version': "2015-04-01",
        'filter': "eventTimestamp ge '2017-6-1T00:00:37Z'",
        'select': 'eventName,eventDataId,status'
        }

    activity_log_url = '%(url)s/subscriptions/%(subscription_id)s/providers/microsoft.insights/eventtypes/management/values?api-version=%(api_version)s&$filter=%(filter)s&$select=%(select)s' %params
    r = requests.get(activity_log_url, headers=headers)

    # Return the full JSON response
    return r.json()

# Add this application's service principal to the ARM Reader Role
def add_service_principal_to_role(access_token, subscription_id, spoid):
    headers = create_headers(access_token)

    # Note the ARM Reader role is hardcoded here
    params = {
        'url': g.resource_arm,
        'subscription_id': subscription_id,
        'api_version': "2016-07-01",
        'role_assignment_name': uuid.uuid4(),
        'reader_role': 'acdd72a7-3385-48ef-bd42-f606fba81ae7'
        }

    data = {
        'properties': {
            'roleDefinitionId': "/subscriptions/%(subscription_id)s/providers/Microsoft.Authorization/roleDefinitions/%(reader_role)s" %params,
            'principalId': spoid
            }
        }

    create_role_assignments_url = '%(url)s/subscriptions/%(subscription_id)s/providers/Microsoft.Authorization/roleAssignments/%(role_assignment_name)s?api-version=%(api_version)s' %params
    r = requests.put(create_role_assignments_url, headers=headers, json=data)

    #Return full request result so we can get the JSON and the Status Code
    return r