import subprocess
import json

def check_lambdas_modified():
    names = ["client", "Onehr_Client_API", "Onehr_ClientOnboarding", "Onehr_Clientservice"]
    for name in names:
        try:
            result = subprocess.run(
                ["aws", "lambda", "get-function", "--function-name", name, "--region", "us-east-2"],
                capture_output=True, text=True, check=True
            )
            data = json.loads(result.stdout)
            print(f"{name}: LastModified: {data['Configuration']['LastModified']}")
        except:
            print(f"{name}: Not found or error.")

if __name__ == "__main__":
    check_lambdas_modified()
