import subprocess
import json

def get_config(name):
    try:
        result = subprocess.run(
            ["aws", "lambda", "get-function-configuration", "--function-name", name, "--region", "us-east-2"],
            capture_output=True, text=True, check=True
        )
        data = json.loads(result.stdout)
        print(f"{name} Handler: {data['Handler']}")
    except Exception as e:
        print(f"{name} error: {e}")

get_config("Onehr_Client_API")
get_config("client")
