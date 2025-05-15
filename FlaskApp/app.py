from flask import Flask, render_template, redirect, request, session, abort, make_response, flash
import hmac, json, hashlib, requests, secrets, uuid, datetime
import config
from intuitlib.client import AuthClient
from intuitlib.enums import Scopes
from quickbooks import QuickBooks
from quickbooks.objects.customer import Customer
#from asana.rest import ApiException
from pprint import pprint
from urllib.parse import urlencode
from quickbooks.objects.item import Item
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
import logging
from graphql_service import prepare_variables
from quickbooks_service import QuickBooksService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = "dev key"  # In production, use a secure secret key

qbo_auth = config.OAUTH2_PROVIDERS['quickbooks']
# Setup and call QBO authorization
auth_client = AuthClient(
    client_id=qbo_auth['client_id'],
    client_secret=qbo_auth['client_secret'],
    environment=config.ENVIRONMENT,
    redirect_uri=qbo_auth['redirect_uri']
)

# Define the scopes
scopes = [
    Scopes.ACCOUNTING,
    Scopes.PROJECT_MANAGEMENT
]

auth_url = auth_client.get_authorization_url(scopes)


@app.route('/qbo-login', methods = ['GET'])
def button():
    
    return redirect(auth_url)

def getAuthHeader():
    auth_header = 'Bearer {0}'.format(auth_client.access_token)
    return auth_header

# get qbo access token
@app.route('/callback', methods=['GET','POST'])
def qboCallback():
    try:
        
        auth_code = request.args.get('code')
        realm_id = request.args.get('realmId')
       
        auth_client.get_bearer_token(auth_code, realm_id=realm_id)
       
        
        session['new_token'] = auth_client.refresh_token
        session['realm_id'] = auth_client.realm_id
        session['auth_header'] = f'Bearer {auth_client.access_token}'
    
        flash('Successfully connected to QuickBooks')

        return redirect('/')
    except Exception as e:
        logger.error(f"Error in callback: {str(e)}")
        flash('Authentication failed. Please try again.')
        return redirect('/')


custName = []
custDict = {}
# post data to QBO
@app.route("/call-qbo",methods=['GET','POST'])
def callQbo():
    try:
        qbo_service = QuickBooksService(
            auth_header=session['auth_header'],
            realm_id=session['realm_id']
        )
        
        global custDict
        custDict = qbo_service.get_customers()
        custName = qbo_service.get_customer_names()
        
        return render_template('index.html', customers=custName)
    except Exception as e:
        logger.error(f"Error in callQbo: {str(e)}")
        flash('Error fetching customers. Please try again.')
        return redirect('/')

@app.route("/create-projects",methods=['GET','POST'])
def getProjects():
    try:
        selected_custName = request.form.get('customers')
        if not selected_custName:
            flash('Please select a customer')
            return redirect('/')
            
        custID = next((k for k, v in custDict.items() if v == selected_custName), None)
        if not custID:
            flash('Invalid customer selected')
            return redirect('/')
            
        transport = RequestsHTTPTransport(
            url='https://qb.api.intuit.com/graphql',
            headers={
                'Authorization': session['auth_header'],
                'Accept': 'application/json'
            }
        )
        
        client = Client(transport=transport, fetch_schema_from_transport=False)
        
        # Read the GraphQL mutation from file
        with open('static/graphql/project.graphql', 'r') as f:
            query = gql(f.read())
        
        # Prepare variables using the service
        variables = prepare_variables(selected_custName, custID)
        
        result = client.execute(query, variable_values=variables)
        projects = result.get('projectManagementCreateProject', {})
        
        if not projects:
            flash('Failed to create project')
            return redirect('/')
            
        flash('Project created successfully')
        return render_template('index.html', customers=custName, project=projects)
        
    except Exception as e:
        logger.error(f"Error creating project: {str(e)}")
        flash('Error creating project. Please try again.')
        return redirect('/')


# receive events from asana
#hook_secret = None

#@app.route("/create-webhook", methods=["GET", 'POST'])
@app.route('/', methods =['GET', 'POST'] )
def home():
    return render_template('index.html')

#print(auth_url)
#app.run(port=5001)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)

