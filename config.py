hook_secret = None
import version
import platform
OAUTH2_PROVIDERS = {
    'asana': {
        'client_id': '1207748466259067',
        'client_secret': 'e558cdb75fc66b0e7cb7536fb4c347e4',
        'authorize_url': 'https://app.asana.com/-/oauth_authorize',
        'token_url': 'https://app.asana.com/-/oauth_token',
        'redirect_uri':'http://localhost:5001/callback/asana',
        'oauth2_token':'None'
    },
    'quickbooks': {
        'client_id' : 'ABNqSMYyurXwhGpB21K9pcbFvxtlbZ356QKmn2LYjqsXeiIO2v',
        'client_secret' : 'QgXeKbzMgHg4wVLqGgpHdFXqpQUGPvDyJ0Pw3O14',
        'redirect_uri': "https://d10f-2600-1700-5ae0-6400-7d4d-f798-2b01-b70c.ngrok-free.app/callback"
    }
}

ENVIRONMENT = 'production'

# gid of tasks & fields in Asana
ASANA_GID = {
    'invoice' : '1207746538402679',
    'item' : '1207748437685985'
}


WEBHOOK_URL = 'https://8fd5-174-127-245-175.ngrok-free.app'

ASANA_PTOKEN = '2/1207746425168472/1207748354223553:d9f95607af721d5a8cf8832fb4571f95'


MIGRATION_URL = {
    'sandbox': 'https://developer-sandbox.api.intuit.com/v2/oauth2/tokens/migrate',
    'production': 'https://developer.api.intuit.com/v2/oauth2/tokens/migrate',
}

DISCOVERY_URL = {
    'sandbox': 'https://developer.intuit.com/.well-known/openid_sandbox_configuration/',
    'production': 'https://developer.intuit.com/.well-known/openid_configuration/',
}

# info for user-agent

PYTHON_VERSION = platform.python_version()
OS_SYSTEM = platform.uname()[0]
OS_RELEASE_VER = platform.uname()[2]
OS_MACHINE = platform.uname()[4]

ACCEPT_HEADER = {
    'Accept': 'application/json',
    'User-Agent': '{0}-{1}-{2}-{3} {4} {5} {6}'.format('Intuit-OAuthClient', version.__version__,'Python', PYTHON_VERSION, OS_SYSTEM, OS_RELEASE_VER, OS_MACHINE)
}
