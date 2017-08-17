# External Python Libraries Used:
from flask import Flask, redirect, url_for, session, request, render_template
import requests
import uuid
from tinydb import TinyDB, Query

# Our Python Functions:
from arm import *
from graph import *
from authentication import *

global_credentials = None

app = Flask(__name__)
app.debug = True
app.secret_key = g.flaskSecret

# Home Page, with different Login Buttons for Customer or Partner
@app.route('/')
def index():
    return render_template('index.html')

# Login Page for both Customer and Partner
@app.route('/<string:user_type>/login', methods = ['POST', 'GET'])
def login(user_type):
    # If user specifies a tenant id, use that instead of common
    subscription_id = request.form['subscriptionId']
    tenant_id = get_tenant_id(subscription_id)
    session['tenant_id'] = tenant_id
    session['subscription_id'] = subscription_id

    # Check if there is already a token in the session
    if (global_credentials is not None) and ('access_token_graph' in session):
        return redirect(url_for(user_type))

    # Use State Parameter to help mitigate XSRF attacks
    guid = uuid.uuid4()
    session['state'] = guid

    # Need to send the full Redirect URI, so we use _external to add root domain
    redirect_uri = login_url(session['state'], url_for('authorized', user_type=user_type, _external=True), tenant_id=tenant_id)

    return redirect(redirect_uri, code=301)

# Logout page which scrubs all the session data.
@app.route('/logout', methods = ['POST', 'GET'])
def logout():
    session.clear()
    return redirect(url_for('index'))

# Recieve the Authorization Code, and exchange it for Access Tokens to both ARM and AAD Graph API
@app.route('/<string:user_type>/login/authorized')
def authorized(user_type):
    #Capture code in the URL
    code = request.args['code']

    # Check that the state variable was not touched
    if str(session['state']) != str(request.args['state']):
        raise Exception('State has been messed with, end authentication')
    
    redirect_uri = url_for('authorized', user_type=user_type, _external=True)

    global global_credentials
    global_credentials = get_user_credentials(code, redirect_uri, g.resource_arm)
    session['access_token_graph'] = get_access_token_code(code, redirect_uri, g.resource_graph)
    session['access_token_arm'] = global_credentials.signed_session().headers['Authorization'].replace("Bearer ","")

    # Return user to their appropriate landing page
    print(session['tenant_id'])
    if (session['tenant_id'] != 'common') and (session['subscription_id']):
        return redirect(url_for('customer_healthLog', subscription_id=session['subscription_id']))
    else:
        return redirect(url_for(user_type))


### Start of Customer Pages
# Customer Landing Page. Shows the user their raw access tokens
@app.route('/customer')
def customer():
    return render_template('customer.html', credential_arm=str(session['access_token_arm']), token_graph=str(session['access_token_graph']))

# Customer Subscription Page. Shows the user their Azure Subscriptions
@app.route('/customer/subscriptions')
def customer_subscriptions():
    subscriptions = get_subscriptions(global_credentials)
    return render_template('subscriptions.html', subscriptions=subscriptions)

# Customer Health Service Log Page. Shows the user the Azure Health Health Service Log for the subscription they picked.
@app.route('/customer/subscriptions/<string:subscription_id>/healthLog')
def customer_healthLog(subscription_id):
    subscription_id = str(subscription_id)
    health_log_grouped = get_health_log(global_credentials,subscription_id)
    return render_template('healthLog.html', health_log_grouped=health_log_grouped, subscription_id=subscription_id, user_type='customer')

# Grant Access Page. Allows the user to grant the application access to read their subscription even when the user is not currently logged in.
@app.route('/customer/subscriptions/<string:subscription_id>/healthLog/grantAccess')
def grantAccess(subscription_id):
    subscription_id = str(subscription_id)
    # Use the AAD Graph API to get: Service Principal Object Id, Tenant Display Name, Tenant Id, and Username of the signed in user.
    spoid = get_service_principal_object_id(session['access_token_graph'])
    tenant_displayname, tenant_id = get_tenant_details(session['access_token_graph'])
    username = get_user_details(session['access_token_graph'])

    # Try to add Service Principal to ARM Reader Role
    result, success = add_service_principal_to_role(global_credentials,subscription_id,spoid)
    
    # Add Subscription and Tenant information to DB if Success or if Role Assigment Already Exists
    if success or ('RoleAssignmentExists' in str(result)):
        db = TinyDB('.\db.json')
        q = Query()
        db_row = {
            'subscriptionId': subscription_id,
            'tenantId': tenant_id,
            'tenantDisplayName': tenant_displayname,
            'username': username,
            }
        # Add information to DB if the information is new. We are assuming Subscription ID is globally unique.
        if(not db.search(q.subscriptionId == subscription_id)):
            db.insert(db_row)
            message = "Subscription Added to Partner Database!"
        else:
            message = "Partner already has access to this Subscription:"
    else:
        message = "Error adding Service Principal to ARM Reader Role. See error message below:"

    return render_template('grantaccess.html', result=result, message=message)

### End of Customer Pages

### Start of Partner Pages
# These pages could be modified to check that only "Partners" have access.
# Add Sign In for Partner User
# Add a AAD Graph API query to check "Tenant ID" or "Username" to see if it matches what you expect.

# List Customer Subscriptions Page. This page shows the partner all the customers that have granted access to their subscription.
@app.route('/partner/customers')
def partner_customers():
    db = TinyDB('.\db.json')
    customers = db.all()
    return render_template('partner_customers.html', customers=customers)

# Health Service Log Page. This page shows the partner the health service logs for the subscription, using an App Only Token.
@app.route('/partner/customers/<string:subscription_id>/healthLog')
def partner_healthLog(subscription_id):
    subscription_id = str(subscription_id)
    db = TinyDB('.\db.json')
    q = Query()
    subscription = db.get(q.subscriptionId == subscription_id)
    # Get an App Only Token for the specific Tenant where the subscription lives.
    credential = get_app_credentials(g.resource_arm, subscription['tenantId'])
    health_log_grouped = get_health_log(credential, subscription_id)
    return render_template('healthLog.html', health_log_grouped=health_log_grouped, subscription_id=subscription_id, user_type='partner')

### End of Partner Pages

#Trying to catch any errors. Most likely a sign in issue...
@app.errorhandler(Exception)
def error_page(e):
    return render_template('error_page.html', error=e)

if __name__ == '__main__':
    app.run()

