# Azure-Service-Health-Partner-Monitor
Azure Service Health provides guidance and support when issues in Azure services affect you. It provides timely and personalized information about the impact of service issues and helps you prepare for upcoming planned maintenance.  Azure customers review service health events in their personalized service health dashboard in Azure portal. There, they can receive alerts and updates via emails, text messages, and webhook notifications.  However, if you are an Azure partner who helps many customers manage their Azure cloud, it can be challenging to review Service Health data for your customers in a centralized place.  This Python Flask code sample will demonstrate how you can request access to, and query Service Health events from multiple Azure subscriptions, belonging to multiple Azure customers, and review them in a single place.

# Overview
Unless you are registered as a user in the tenant where the Azure Subscription lives, you will not be able to access Health Logs for an Azure Subscription using your user credentials. For partner and customers this may be an unreasonable requirement, so instead, we will use an Application Identity to access the logs in the customer’s subscription on behalf of the partner. To enable this, the follow steps need to take place:

  1.	An Azure AD Application needs to be registered in the Partner tenant.
  2.	The customer needs to login and give consent to the application to have delegated access to Azure Resource Manager.
  3.	The application then needs to add its own Service Principal to the ARM Reader role so that it can access the Health Logs in the future without the Customer logged in.
  4.	The application gets an access token to ARM with its Application Identity, and retrieves the Customer Health information on-behalf of the partner.


# Registering your Application
1.	Go to the Azure Portal (https://portal.azure.com)
2.	Navigate to the “App Registration” blade
3.	Create a New Application Registration
    1.	Name = “Azure Health Monitor”
    2.	Application Type = “Web app / API”
    3.	Sign-on URL = “http://localhost:5000/customer/login/authorized”
4.	Make the application Multi-Tenant
    1.	Properties > Multi-Tenanted > Yes
5.	Update your “Required permissions” to enable access to ARM
    1.	Required Permissions > Add > Select an API > Windows Azure Service Management API
    2.	Select “Access Azure Service Management as organization users (preview)” in Delegated Permissions
6.	Create a New Application Key
    1.	Keys > Description > “app_key”
    2.	Keys > Duration > (choose an expiry time)
    3.	Copy the value for your application key

# Set Up Python Environment
You need to install the following Python Libraries in order to get your application to run:
1.	pip install adal
2.	pip install azure-batch
3.  pip install azure-mgmt-scheduler
4.	pip install msrestazure
5.	pip install tinydb

 
# Set Up the Python Flask Sample
After you have completed your app registration, you should have 2 pieces:
  1.	An Application ID GUID
  2.	An App Secret String
  
After you download and unpackage the sample, you will need to update “appconfig.py” to use these values. Additionally, you should generate a new secret key which will be used for Flask sessions. Make sure to never share your “appconfig.py” file! Once you save your updated configuration file, you are ready to run the sample!
