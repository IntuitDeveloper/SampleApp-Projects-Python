from flask import Flask, render_template, redirect, request, session, abort, make_response, flash
import hmac, json, hashlib, requests, secrets, uuid, datetime
import config
from client import AuthClient
#from intuitlib.enums import Scopes
from enums import Scopes
from quickbooks import QuickBooks
from quickbooks.objects.customer import Customer
#from asana.rest import ApiException
from pprint import pprint
from urllib.parse import urlencode
from quickbooks.objects.item import Item
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = "dev key"  # In production, use a secure secret key

qbo_auth = config.OAUTH2_PROVIDERS['quickbooks']
#setup and call QBO authorization
auth_client = AuthClient (
                            environment=config.ENVIRONMENT,
                            client_id=qbo_auth['client_id'], 
                            client_secret =qbo_auth['client_secret'],
                            redirect_uri = qbo_auth['redirect_uri']

)

scopes =  [Scopes.ACCOUNTING , Scopes.PROJECT , Scopes.CUSTOM_FIELDS ]

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
        
        if not auth_code or not realm_id:
            flash('Authentication failed: Missing required parameters')
            return redirect('/')
            
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

#setup and call asana authorization

# data mapping
def mapData():
    data = session['event_data']
    str_data = data.decode('utf-8')
    json_data = json.loads(str_data)
    task_change = json_data["events"][0]['change']
    if (task_change['action']) == 'changed':
         change_ID = task_change["new_value"]["enum_value"]["gid"]
         return change_ID

custName = []
custDict = {}
# post data to QBO
@app.route("/call-qbo",methods=['GET','POST'])
def callQbo():
    try:
        base_url = 'https://quickbooks.api.intuit.com'  
        cust_url = '{0}/v3/company/{1}/query'.format(base_url, session['realm_id'])
        body = "Select * from Customer where Job = false "
        headers = {
                    'Authorization': session['auth_header'],
                    'Accept': 'application/json',
                    'Content-Type': 'application/text'
             }
        cust_response = requests.request("POST",cust_url, headers=headers, data=body)   
        #print(cust_response.text)
        data = json.loads(cust_response.text)
        print(data)
        custData = data['QueryResponse']['Customer']
        print(custData)

        global custDict
        custDict = {}
        for customer in custData:
            if 'Id' in customer:
                custDict[customer['Id']] = customer['FullyQualifiedName']
        custName = list(custDict.values())
        print(custName)
        return render_template('index.html', customers=custName)
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching customers: {str(e)}")
        flash('Error fetching customers. Please try again.')
        return redirect('/')
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        flash('An unexpected error occurred. Please try again.')
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
        query = gql("""
            mutation ProjectManagementCreateProject($name: String!, $description: String, $startDate: DateTime, $dueDate: DateTime!, $status: ProjectManagement_Status, $customer: ProjectManagement_CustomerInput, $priority: Int, $pinned: Boolean, $completionRate: Decimal, $emailAddress: [Qb_EmailAddressInput], $addresses: [Qb_PostalAddressInput]) {
                projectManagementCreateProject(input:{
                    name: $name,
                    description: $description,
                    startDate: $startDate,
                    dueDate: $dueDate,
                    status: $status,
                    customer: $customer,
                    priority: $priority,
                    pinned: $pinned,
                    completionRate: $completionRate,
                    emailAddress: $emailAddress,
                    addresses: $addresses
                }) {
                    ... on ProjectManagement_Project {
                        id
                        name
                        description
                        startDate
                        dueDate
                        status
                        priority
                        customer { id }
                        pinned
                        completionRate
                        emailAddress { email name }
                        addresses { streetAddressLine1 streetAddressLine2 streetAddressLine3 state postalCode }
                    }
                }
            }
        """)
        
        now = datetime.datetime.now(datetime.timezone.utc)
        formatted_date = now.strftime('%Y-%m-%dT%H:%M:%S.') + f"{now.microsecond // 1000:03d}Z"
        future_date = now + datetime.timedelta(days=1825)
        format_future_date = future_date.strftime('%Y-%m-%dT%H:%M:%S.') + f"{future_date.microsecond // 1000:03d}Z"
        
        variables = {
            "name": f"Project-{uuid.uuid4()}",
            "description": f"Project for {selected_custName}",
            "startDate": formatted_date,
            "dueDate": format_future_date,
            "status": "OPEN",
            "customer": {"id": int(custID)},
            "priority": 1,
            "pinned": False
        }
        
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

        
    """  
    with open('createProjPayload.txt', 'r') as f:
        payload = json.load(f)
    json_payload = json.dumps(payload)
    print(json_payload)
    graph_headers =   headers = {
                    'Authorization': auth_header,
                    'Accept': 'application/json',
                     'Content-Type': 'application/json'
             }
    proj_resp = requests.post(graphql_url , headers=graph_headers, data=json_payload)
    print("**Created Project**")
    print(json.loads(proj_resp.text)) 
    """

