hook_secret = None
import version
import platform
OAUTH2_PROVIDERS = {
    'quickbooks': {
        'client_id' : 'ABNqSMYyurXwhGpB21K9pcbFvxtlbZ356QKmn2LYjqsXeiIO2v',
        'client_secret' : 'QgXeKbzMgHg4wVLqGgpHdFXqpQUGPvDyJ0Pw3O14',
        'redirect_uri': "https://d10f-2600-1700-5ae0-6400-7d4d-f798-2b01-b70c.ngrok-free.app/callback"
    }
}

ENVIRONMENT = 'production'

WEBHOOK_URL = 'https://8fd5-174-127-245-175.ngrok-free.app'

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
