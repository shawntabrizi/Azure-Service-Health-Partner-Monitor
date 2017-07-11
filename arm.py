# External Python Libraries Used:
import uuid
from azure.mgmt.resource.subscriptions import SubscriptionClient
from azure.monitor import MonitorClient
from azure.mgmt.authorization import AuthorizationManagementClient
from azure.mgmt.authorization.models import RoleAssignmentProperties
import datetime
from collections import defaultdict
import re

# Our Python Functions:
import appconfig as g
from authentication import get_app_credentials

# Get Tenant ID for given Subscription Id
def get_tenant_id(subscription_id):
    # Get the default ARM App Only Access Token
    tenant_id = 'common'
    credentials = get_app_credentials(g.resource_arm, tenant_id)
    subscriptions_client = SubscriptionClient(credentials)

    # Try to get information about the subscription, expect an error
    try:
        subscriptions_client.subscriptions.get(subscription_id)
    except Exception as e:
        # If Error says the token is from the wrong tenant, parse the correct tenant, and return it
        if 'InvalidAuthenticationTokenTenant' in str(e):
            tenant_id = re.findall("Please use the authority \(URL\) 'https\:\/\/login\.windows\.net\/(.*)'", str(e))[0]

    return tenant_id


# Using a Subscription Client and ARM Credentials, get a list of the Azure Subscriptions available to that user.
def get_subscriptions(credentials):
    subscriptions_client = SubscriptionClient(credentials)
    subscriptions = subscriptions_client.subscriptions.list()
    subscription_list = []
    for subscription in subscriptions:
        subscription_list.append(subscription)

    return subscription_list

# Using a Monitor Client and ARM Credentials, get the Health Service Logs of a particular Azure Subscription.
def get_health_log(credentials, subscription_id):
    monitor_client = MonitorClient(credentials, subscription_id)
    # Note we query the Health Service Log for the past 60 days.
    date = datetime.date.today() - datetime.timedelta(60)
    # Choose the properties you get back by adjusting this.
    # select = ",".join(["eventName", "eventDataId", "status", "eventTimestamp", "properties"])
    # None returns all properties
    select = None
    # Get different results by updating your filter. Here we only get the Health Service Logs
    filter = " and ".join(["eventTimestamp ge {}".format(date), "category eq 'ServiceHealth'"])
    logs = monitor_client.activity_logs.list(filter=filter, select=select)
    # Group log by Incident Id
    log_list_grouped = defaultdict(list)
    for log in logs:
        log_list_grouped[log.properties['IncidentId']].append(log)

    return log_list_grouped

# Using an Authorization Management Client and ARM Credentials, try to assign this Application's service principal to the ARM Reader Role
def add_service_principal_to_role(credentials,subscription_id,spoid):
    auth_client = AuthorizationManagementClient(credentials,subscription_id)
    scope = '/subscriptions/' + subscription_id
    # ARM Reader role is hardcoded here
    role_definition_id = '/subscriptions/' + subscription_id + '/providers/Microsoft.Authorization/roleDefinitions/acdd72a7-3385-48ef-bd42-f606fba81ae7'
    principal_id = spoid
    # Try to assign the Service Principal to the Role... but a lot could go wrong.
    try:
        result = auth_client.role_assignments.create(scope, uuid.uuid4(), RoleAssignmentProperties(role_definition_id,principal_id))
        success = True
    # Tell the user what went wrong.
    except Exception as e:
        result = e
        success = False

    return result, success