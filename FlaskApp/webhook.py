import requests
import config
import asana
import pprint,json
from asana.rest import ApiException


payload = {}
headers = {
  'Authorization': 'Bearer {0}'.format(config.ASANA_PTOKEN)
}

webhook_data = ''

def getWebhook():    
    url = "https://app.asana.com/api/1.0/webhooks?workspace=1207746425168483"

    response = requests.request("GET", url, headers=headers, data=payload)

    print(response.text)

    global webhook_data 
    webhook_data = json.loads(response.content.decode('utf-8'))

def deleteWebhook():
    url = "https://app.asana.com/api/1.0/webhooks/{0}".format(webhook_data['data'][0]['gid'])
    response = requests.request("DELETE", url, headers=headers, data=payload)
    print(response.text)


def createHook():
    config.hook_secret
    configuration = asana.Configuration()
    #configuration.access_token = asana_auth['oauth2_token']
    configuration.access_token = '{0}'.format(config.ASANA_PTOKEN)
    api_client = asana.ApiClient(configuration)
    webhooks_api_instance = asana.WebhooksApi(api_client)
    body =     { "data": {
                            "resource": "1207746538402654",
                             "target": "{0}/receive-webhook".format(config.WEBHOOK_URL),
                 "filters": [
                            {
                 "action": "changed",
                "resource_type": "task"
                }
                             ]
                            }} # dict | The webhook workspace and target.
    opts = {
    'opt_fields': "active,created_at,filters,filters.action,filters.fields,filters.resource_subtype,last_failure_at,last_failure_content,last_success_at,resource,resource.name,target", # list[str] | This endpoint returns a compact resource, which excludes some properties by default. To include those optional properties, set this query parameter to a comma-separated list of the properties you wish to include.
     }
    try:
    # Establish a webhook
        api_response = webhooks_api_instance.create_webhook(body, opts)
        print("create webhook headers")
      
        print(api_response)
        
    except ApiException as e:
        print("Exception when calling WebhooksApi->create_webhook: %s\n" % e)
    return ""

getWebhook()   
if 'data' in webhook_data and webhook_data['data']:
    deleteWebhook()

createHook()






    
