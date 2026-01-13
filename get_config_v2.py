import boto3
import json

client = boto3.client('lambda', region_name='us-east-2')
response = client.get_function_configuration(FunctionName='Onehr_Clientservices')
with open('config_final.json', 'w', encoding='utf-8') as f:
    json.dump(response, f, indent=2, default=str)
