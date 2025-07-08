# QuickBooks Project Management API Sample App

This is a sample Python application that demonstrates how to integrate with QuickBooks Project Management API using OAuth 2.0 authentication.

## Features

- OAuth 2.0 authentication with QuickBooks
- Project Management API integration

## Prerequisites

- Python 3.8 or higher
- QuickBooks Developer Account
- QuickBooks Online Account
- ngrok (for local development)

## Setup

1. Clone the repository:
```bash
git clone git@github.com:IntuitDeveloper/SampleApp-Projects-Python.git

```

2. Install dependencies:
```bash
cd FlaskApp
pip install -r requirements.txt
```

3. Configure your QuickBooks app:
   - Go to [Intuit Developer Portal](https://developer.intuit.com)
   - Create a new app or use an existing one
   - Enable Project Management API scope
   - Add your redirect URI (e.g., `https://your-ngrok-url/callback`)

4. Update configuration:
   - Open `FlaskApp/config.py`
   - Update the OAuth2 provider details with your app credentials:
     ```python
     OAUTH2_PROVIDERS = {
         'quickbooks': {
             'client_id': 'YOUR_CLIENT_ID',
             'client_secret': 'YOUR_CLIENT_SECRET',
             'redirect_uri': 'YOUR_REDIRECT_URI'
         }
     }
     ```

5. Start ngrok:
```bash
ngrok http 5001
```

6. Run the application:
```bash
cd FlaskApp
python app.py
```

## Usage

1. Visit `http://localhost:5001` in your browser
2. Click "Connect to QuickBooks" to authenticate
3. After successful authentication, you can:
   - View customer list
   - Create new projects associated with customers

## Project Structure

```
Sample-app-projects-python/
├── FlaskApp/
│   ├── app.py                 # Main application file
│   ├── config.py             # Configuration settings
│   ├── oauth_pythonclient/   # OAuth client implementation
│   ├── static/              # Static files (CSS, images)
│   └── templates/           # HTML templates
└── README.md
```

## API Endpoints

- `/` - Home page
- `/qbo-login` - Initiates OAuth flow
- `/callback` - OAuth callback handler
- `/call-qbo` - Retrieves customer data
- `/create-projects` - Creates new projects

## Error Handling

The application includes error handling for:
- OAuth authentication failures
- API request failures
- Missing parameters
- Invalid scopes



## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.

## Support

For support, please visit the [Intuit Developer Community](https://intuitdevelopercommunity.com/) or create an issue in this repository.
