import boto3
import json

client = boto3.client('lambda', region_name='us-east-2')
try:
    response = client.get_function_configuration(FunctionName='Onehr_Clientservice')
    with open('config_singular.json', 'w', encoding='utf-8') as f:
        json.dump(response, f, indent=2, default=str)
except Exception as e:
    print(f"Error: {e}")
