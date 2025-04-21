from flask import Flask, render_template, redirect, request, session, abort, make_response 
import hmac ,json , hashlib , requests , secrets , uuid, datetime
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
from gql.transport.aiohttp import AIOHTTPTransport
"""
"""
app = Flask(__name__)
app.secret_key = "dev key" 

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
    auth_code = str(request.args.get('code'))
    realm_id = str(request.args.get('realmId'))
    print(auth_code,realm_id )
    auth_client.get_bearer_token(auth_code,realm_id=realm_id)
    session['new_token'] = auth_client.refresh_token
    session['realm_id'] = auth_client.realm_id
    session['auth_header'] = 'Bearer {0}'.format(auth_client.access_token)
    print(auth_client.access_token)
    return render_template('index.html')

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

    #change_ID = mapData()
    #print(change_ID)
   # if change_ID == config.ASANA_GID['invoice']:
    #str_item = itemDetail
    #json_item = json.loads(str_item)
    #itemID = json_item['Item']['Id']
    #graphql_url = 'https://qb.api.intuit.com/graphql'

    base_url = 'https://quickbooks.api.intuit.com'  
    cust_url = '{0}/v3/company/{1}/query'.format(base_url, auth_client.realm_id)
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

    for customer in custData:
        if 'Id' in customer:
            custDict[customer['Id']] = customer['FullyQualifiedName']
    custName = list(custDict.values())
    print(custName)
    return render_template('index.html', customers=custName)

@app.route("/create-projects",methods=['GET','POST'])
def getProjects():
    selected_custName = request.form.get('customers')
    custID = next((k for k, v in custDict.items() if v == selected_custName), None)
    # Instantiate the client with an endpoint.
    transport = AIOHTTPTransport(url="https://qb.api.intuit.com/graphql", headers={ 'Authorization': session['auth_header'],
                                                                                    'Accept': 'application/json'
                                                            
                                                                                         })
    # Create a GraphQL client using the defined transport
    client = Client(transport=transport, fetch_schema_from_transport=False)
    # Create the query string and variables required for the request.
    query = gql("""
    
                    mutation ProjectManagementCreateProject($name: String!, $description: String, $startDate: DateTime, $dueDate: DateTime!, $status: ProjectManagement_Status, $customer: ProjectManagement_CustomerInput, $priority: Int, $pinned: Boolean, $completionRate: Decimal, $emailAddress: [Qb_EmailAddressInput], $addresses: [Qb_PostalAddressInput]) { projectManagementCreateProject(input:{ name: $name, description: $description, startDate: $startDate, dueDate: $dueDate, status: $status, customer: $customer, priority: $priority, pinned: $pinned, completionRate: $completionRate, emailAddress: $emailAddress, addresses: $addresses }) { ... on ProjectManagement_Project { id, name, description, startDate, dueDate, status, priority, customer{ id }, priority, pinned, completionRate, emailAddress { email, name } addresses { streetAddressLine1, streetAddressLine2, streetAddressLine3, state, postalCode } } } }

        """
             )
    projectName = "App Test-Demo 1" + str(uuid.uuid4())
    now = datetime.datetime.now(datetime.timezone.utc)
    formatted_date = now.strftime('%Y-%m-%dT%H:%M:%S.') + f"{now.microsecond // 1000:03d}Z"
    future_date = now + datetime.timedelta(days=1825)
    format_future_date = future_date.strftime('%Y-%m-%dT%H:%M:%S.') + f"{future_date.microsecond // 1000:03d}Z"
    variables = {"name":projectName ,
        "description": projectName,
        "startDate": formatted_date,
        "dueDate": format_future_date,
        "status": "OPEN",
        "customer": { "id": int(custID) },
        "priority": 1,
        "pinned": False
    }

    # Get name of continent with code "AF"
    result = client.execute(query, variable_values=variables)
    projects = result.get('projectManagementCreateProject', {})

    return render_template('index.html',customers=custName,project=projects)


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

