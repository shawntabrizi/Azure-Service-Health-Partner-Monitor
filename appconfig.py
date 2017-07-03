# This is your Application's Configuration File.
# Make sure not to upload this file!

#Flask App Secret. Used for "session".
flaskSecret = "<generateKey>"

# Register your V1 app at https://portal.azure.com.
# Make sure to add 2 Reply URLs to your application:
# <domain>/partner/login/authorized    i.e. http://localhost:5000/partner/login/authorized
# <domain>/customer/login/authorized   i.e. http://localhost:5000/customer/login/authorized
clientId = "<GUID>"
clientSecret = "<SECRET>"

#The various resource endpoints. You may need to update this for different cloud environments.
aad_endpoint = "https://login.microsoftonline.com/"
resource_arm = "https://management.azure.com/"
resource_graph = "https://graph.windows.net/"
api_version_graph = "1.6"
