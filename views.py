from flask import Flask, redirect, url_for, session, request, render_template
import requests
import uuid
from tinydb import TinyDB, Query


from arm import *
from graph import *
from authentication import *

app = Flask(__name__)
app.debug = True
app.secret_key = 'development'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/<string:user_type>/login', methods = ['POST', 'GET'])
def login(user_type):

    if ('access_token_arm' in session) and ('access_token_graph' in session):
        return redirect(url_for(user_type))

    # Generate the guid to only accept initiated logins
    guid = uuid.uuid4()
    session['state'] = guid

    redirect_uri = login_url(session['state'], url_for('authorized', user_type=user_type, _external=True))

    return redirect(redirect_uri, code=301)
    
@app.route('/logout', methods = ['POST', 'GET'])
def logout():
    session.pop('access_token_arm', None)
    session.pop('access_token_graph', None)
    session.pop('state', None)
    return redirect(url_for('index'))

@app.route('/<string:user_type>/login/authorized')
def authorized(user_type):
    code = request.args['code']

    if str(session['state']) != str(request.args['state']):
        raise Exception('State has been messed with, end authentication')
    
    # Okay to store this in a local variable, encrypt if it's going to client
    # machine or database. Treat as a password. 
    redirect_uri = url_for('authorized', user_type=user_type, _external=True)
    session['access_token_arm'] = get_access_token_arm(code, redirect_uri)
    session['access_token_graph'] = get_access_token_graph(code, redirect_uri)

    return redirect(url_for(user_type)) 

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
    result = add_service_principal_to_role(session['access_token_arm'],subscription_id,spoid)
    tenant_displayname, tenant_id = get_tenant_details(session['access_token_graph'])
    username = get_user_details(session['access_token_graph'])
    #success is 201
    if result.status_code is 201: 
        db = TinyDB('.\db.json')
        db_row = {
            'subscriptionId': subscription_id,
            'tenantId': tenant_id,
            'tenantDisplayName': tenant_displayname,
            'username': username,
            }
        db.insert(db_row)

    return render_template('grantaccess.html', result=result.json())


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
    session['access_token_app'] = get_app_access_token_arm(subscription['tenantId'])
    activity_log = get_activity_log(session['access_token_app'], subscription_id)
    return render_template('partner_activityLog.html', activity_log=activity_log['value'], access_token=session['access_token_app'])

if __name__ == '__main__':
    app.run()