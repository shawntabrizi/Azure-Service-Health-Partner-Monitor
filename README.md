# Azure-Health-Partner-Monitor
Unless you are registered as a user in the tenant where the Azure Subscription lives, you will not be able to access Health Logs for an Azure Subscription using your user credentials. For partner and customers this may be an unreasonable requirement, so instead, we will use an Application Identity to access the logs in the customer’s subscription on behalf of the partner. To enable this, the follow steps need to take place:

  1.	An Azure AD Application needs to be registered in the Partner tenant.
  2.	The customer needs to login and give consent to the application to have delegated access to Azure Resource Manager.
  3.	The application then needs to add its own Service Principal to the ARM Reader role so that it can access the Health Logs in the future without the Customer logged in.
  4.	The application gets an access token to ARM with its Application Identity, and retrieves the Customer Health information on-behalf of the partner.


# Registering your Application
1.	Go to the Azure Portal (https://portal.azure.com)
2.	Navigate to the “App Registration” blade
3.	Create a New Application Registration
  a.	Name = “Azure Health Monitor”
  b.	Application Type = “Web app / API”
  c.	Sign-on URL = “http://localhost:5000/customer/login/authorized”
4.	Make the application Multi-Tenant
  a.	Properties > Multi-Tenanted > Yes
5.	Update your “Required permissions” to enable access to ARM
  a.	Required Permissions > Add > Select an API > Windows Azure Service Management API
  b.	Select “Access Azure Service Management as organization users (preview)” in Delegated Permissions
6.	Create a New Application Key
  a.	Keys > Description > “app_key”
  b.	Keys > Duration > (choose an expiry time)
  c.	Copy the value for your application key
 
# Set Up the Python Flask Sample
After you have completed your app registration, you should have 2 pieces:
  1.	An Application ID GUID
  2.	An App Secret String
  
After you download and unpackage the sample, you will need to update “appconfig.py” to use these values. Additionally, you should generate a new secret key which will be used for Flask sessions. Make sure to never share your “appconfig.py” file! Once you save your updated configuration file, you are ready to run the sample!
