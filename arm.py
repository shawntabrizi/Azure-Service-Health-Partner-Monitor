# External Python Libraries Used:
import uuid
from azure.mgmt.resource.subscriptions import SubscriptionClient
from azure.monitor import MonitorClient
from azure.mgmt.authorization import AuthorizationManagementClient
from azure.mgmt.authorization.models import RoleAssignmentProperties
import datetime
from collections import defaultdict

# Our Python Functions:
import appconfig as g

# Using a Subscription Client and ARM Credentials, get a list of the Azure Subscriptions available to that user.
def get_subscriptions(credentials):
    subscriptions_client = SubscriptionClient(credentials)
    subscriptions = subscriptions_client.subscriptions.list()
    subscription_list = []
    for subscription in subscriptions:
        subscription_list.append(subscription)

    return subscription_list

# Using a Monitor Client and ARM Credentials, get the Activity Log of a particular Azure Subscription.
def get_activity_log(credentials, subscription_id):
    monitor_client = MonitorClient(credentials, subscription_id)
    # Note we query the Activity Log for the past 30 days.
    month = datetime.date.today() - datetime.timedelta(30)
    # Get more properties back by adjusting this.
    #select = ",".join(["eventName", "eventDataId", "status", "eventTimestamp", "operationId"])
    select = None
    # Get different results by updating your filter.
    filter = " and ".join(["eventTimestamp ge {}".format(month)])
    logs = monitor_client.activity_logs.list(filter=filter, select=select)
    # Group log by Operation Id
    log_list_grouped = defaultdict(list)
    for log in logs:
        log_list_grouped[log.operation_id].append(log)

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