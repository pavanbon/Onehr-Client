import subprocess
import json

def list_lambdas():
    try:
        result = subprocess.run(
            ["aws", "lambda", "list-functions", "--region", "us-east-2", "--query", "Functions[].FunctionName"],
            capture_output=True, text=True, check=True
        )
        functions = json.loads(result.stdout)
        print("Functions found:")
        for f in functions:
            print(f"- {f}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_lambdas()
