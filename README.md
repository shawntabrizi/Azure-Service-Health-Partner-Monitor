# Azure-Health-Partner-Monitor
This is a web app which allows partners to view customer health activity through ARM

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
