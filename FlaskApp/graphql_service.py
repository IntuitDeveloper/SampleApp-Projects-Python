import json
import uuid
import datetime
from typing import Dict, Any

def prepare_variables(customer_name: str, customer_id: str) -> Dict[str, Any]:
    """
    Prepare variables for GraphQL project creation mutation.
    
    Args:
        customer_name (str): Name of the customer
        customer_id (str): ID of the customer
        
    Returns:
        Dict[str, Any]: Prepared variables for the GraphQL mutation
    """
    # Calculate dates
    now = datetime.datetime.now(datetime.timezone.utc)
    formatted_date = now.strftime('%Y-%m-%dT%H:%M:%S.') + f"{now.microsecond // 1000:03d}Z"
    future_date = now + datetime.timedelta(days=1825)
    format_future_date = future_date.strftime('%Y-%m-%dT%H:%M:%S.') + f"{future_date.microsecond // 1000:03d}Z"
    
    # Read variables template from JSON file
    with open('static/graphql/graphql_variables.json', 'r') as f:
        config = json.load(f)
        
    # Prepare variables
    variables = {
        **config['defaults'],  # Include default values
        "name": config['template']['name'].format(uuid=uuid.uuid4()),
        "description": config['template']['description'].format(customerName=customer_name),
        "startDate": formatted_date,
        "dueDate": format_future_date,
        "customer": {"id": int(customer_id)}
    }
    
    return variables 