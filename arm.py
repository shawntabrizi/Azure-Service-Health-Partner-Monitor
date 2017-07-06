# External Python Libraries Used:
import uuid
from azure.mgmt.resource.subscriptions import SubscriptionClient
from azure.monitor import MonitorClient
from azure.mgmt.authorization import AuthorizationManagementClient
from azure.mgmt.authorization.models import RoleAssignmentProperties
import datetime

# Our Python Functions:
import appconfig as g

def get_subscriptions_lib(credentials):
    subscriptions_client = SubscriptionClient(credentials)
    subscriptions = subscriptions_client.subscriptions.list()
    subscription_list = []
    for subscription in subscriptions:
        subscription_list.append(subscription)

    return subscription_list

def get_activity_log_lib(credentials, subscription_id):
    monitor_client = MonitorClient(credentials, subscription_id)
    month = datetime.date.today() - datetime.timedelta(30)
    select = ",".join(["eventName", "eventDataId","status","eventTimestamp"])
    filter = " and ".join(["eventTimestamp ge {}".format(month)])
    logs = monitor_client.activity_logs.list(filter=filter, select=select)
    log_list = []
    for log in logs:
        log_list.append(log)

    return log_list

def add_service_principal_to_role_lib(credentials,subscription_id,spoid):
    auth_client = AuthorizationManagementClient(credentials,subscription_id)
    scope = '/subscriptions/' + subscription_id
    role_definition_id = '/subscriptions/' + subscription_id + '/providers/Microsoft.Authorization/roleDefinitions/acdd72a7-3385-48ef-bd42-f606fba81ae7'
    principal_id = spoid
    try:
        result = auth_client.role_assignments.create(scope, uuid.uuid4(), RoleAssignmentProperties(role_definition_id,principal_id))
        success = True
    except Exception as e:
        result = e
        success = False

    return result, success