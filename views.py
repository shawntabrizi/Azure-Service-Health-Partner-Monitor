# External Python Libraries Used:
from flask import Flask, redirect, url_for, session, request, render_template
import requests
import uuid
from tinydb import TinyDB, Query

# Our Python Functions:
from arm import *
from graph import *
from authentication import *

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
    # Check if there is already a token in the session
    if ('access_token_arm' in session) and ('access_token_graph' in session):
        return redirect(url_for(user_type))

    # Use State Parameter to help mitigate XSRF attacks
    guid = uuid.uuid4()
    session['state'] = guid

    # Need to send the full Redirect URI, so we use _external to add root domain
    redirect_uri = login_url(session['state'], url_for('authorized', user_type=user_type, _external=True))

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
    session['access_token_arm'] = get_access_token_code(code, redirect_uri, g.resource_arm)
    session['access_token_graph'] = get_access_token_code(code, redirect_uri, g.resource_graph)

    # Return user to their appropriate landing page
    return redirect(url_for(user_type)) 

# Customer Landing Page
@app.route('/customer')
def customer():
    token_arm = session['access_token_arm']
    token_graph = session['access_token_graph']
    return render_template('customer.html', token_arm=str(token_arm), token_graph=str(token_graph))

@app.route('/customer/subscriptions')
def customer_subscriptions():
    subscriptions = get_subscriptions(session['access_token_arm'])
    return render_template('subscriptions.html', subscriptions=subscriptions['value'])

@app.route('/customer/subscriptions/<string:subscription_id>/activityLog')
def customer_activityLog(subscription_id):
    activity_log = get_activity_log(session['access_token_arm'],subscription_id)
    return render_template('activityLog.html', activity_log=activity_log['value'], subscription_id=subscription_id)

@app.route('/customer/subscriptions/<string:subscription_id>/activityLog/grantAccess')
def grantAccess(subscription_id):
    spoid = get_service_principal_object_id(session['access_token_graph'])
    tenant_displayname, tenant_id = get_tenant_details(session['access_token_graph'])
    username = get_user_details(session['access_token_graph'])

    result = add_service_principal_to_role(session['access_token_arm'],subscription_id,spoid)
    
    #add to DB if Success (201) or RoleAssigmentExists (409)
    if result.status_code == 201 or result.status_code == 409:
        db = TinyDB('.\db.json')
        q = Query()
        db_row = {
            'subscriptionId': subscription_id,
            'tenantId': tenant_id,
            'tenantDisplayName': tenant_displayname,
            'username': username,
            }
        #add row in DB if subscription does not already exist
        if(not db.search(q.subscriptionId == subscription_id)):
            db.insert(db_row)
            message = "Subscription Added to Partner Database!"
        else:
            message = "Partner already has access to this Subscription:"
    else:
        message = "Error adding Service Principal to ARM Reader Role. See error message below:"

    return render_template('grantaccess.html', result=result.json(), message=message)


@app.route('/partner')
def partner():
    token_arm = session['access_token_arm']
    token_graph = session['access_token_graph']
    return render_template('partner.html', token_arm=str(token_arm), token_graph=str(token_graph))

@app.route('/partner/subscriptions')
def partner_subscriptions():
    db = TinyDB('.\db.json')
    subscriptions = db.all()
    return render_template('partner_subscriptions.html', subscriptions=subscriptions)

@app.route('/partner/<string:subscription_id>/activityLog')
def partner_activityLog(subscription_id):
    db = TinyDB('.\db.json')
    q = Query()
    subscription = db.get(q.subscriptionId == subscription_id)
    session['access_token_app'] = get_access_token_app(g.resource_arm, subscription['tenantId'])
    activity_log = get_activity_log(session['access_token_app'], subscription_id)
    return render_template('partner_activityLog.html', activity_log=activity_log['value'], access_token=session['access_token_app'])

if __name__ == '__main__':
    app.run()