# App-Integration-QBO
Proof of concept for Project Management tool integration with Quickbooks Online

**The problem**

Small business owners face significant challenges when managing projects and finances manually. Using separate systems - Asana for project management  and QuickBooks for accounting often leads to inefficiencies, data discrepancies, and time-consuming manual entries. This fragmented approach increases the risk of errors, delays in invoicing, and difficulty in tracking payments. The lack of integration between these tools hinders seamless workflow automation, making it hard for small businesses to scale effectively and focus on growth.

**The solution**

Small business owners can automate transactions between project management tools and QuickBooks, creating a seamless and efficient workflow. This proof of concept aims to highlight that this automation can be achieved through Webhooks triggers & API actions. Webhooks can trigger real-time updates, such as creating/closing tasks in Asana for order management, while API calls can automatically log and update items & invoices in QuickBooks. User security is ensured through OAuth authentication.
This integration reduces manual data entry, minimizes errors, and ensures data consistency across platforms. Automating these processes saves time, improves accuracy, and allows small businesses to focus on growth and customer satisfaction.

This **README** page focuses on automating the user data flow between Asana and Quickbooks Online:
* Login into Asana
* Create task for new order tracking in Asana. Assign a service/item to task
* Track/update the ordered item or service details in Quickbooks. 
* Create invoices of the service/item in QuickBooks. 
* Track if payments were made in Asana.

The technical app integration for the above user flow is as follows:
* User Authentication: OAuth tokens are exchanged with middleware app to authenticate users securely for both Asana and QuickBooks.
* Webhook Listener: A webhook listener is set up to receive and process events from Asana.
* Data Processing: Received data is mapped and validated to ensure it meets the requirements of the QuickBooks API.
* QBO API Calls: API calls are made to QuickBooks to perform actions such as creating or updating items and invoices.
* Feedback Loop: QBO API responses mapped and sent back to Asana and posted as task

**Requirements**

* [intuit Developer account](https://developer.intuit.com/)
* [asana account](https://asana.com/)
* Apps on intuit and Asana (to get clientID and client SecretKey)
* Python Flask
* Asana & Quickbooks SDK
* ngrok

**Installation**

* Clone the GitHub repo to your computer
* Fill in your **config.py** file values by copying over from the keys section for your app
* Install ngrok for Flask. Set ngrok auth token
  
**Running the app**

cd to the project directory

` pip install -r requirements.txt`

Run the command ` python3 app.py` for MacOS/Linux

Run `ngrok http 5000`

open a browser and enter http://localhost:5000

Next, setup the webhook by running command ` python3 webhook.py` 



**Authentication**

QuickBooks Authorization:
  Click the button 'Connect to QuickBooks'.
  Authenticate and authorize the application.
  You will be redirected back to the application, and receive the access token .

Asana Authorization:
  Click the button 'Connect to Asana'.
  Authenticate and authorize the application.
  You will be redirected back to the application, and receive the access token 
