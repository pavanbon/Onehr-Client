import boto3
import json

client = boto3.client('lambda', region_name='us-east-2')
response = client.get_function_configuration(FunctionName='Onehr_Clientservices')
print(json.dumps(response, indent=2, default=str))
