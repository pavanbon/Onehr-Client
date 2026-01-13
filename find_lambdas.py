import subprocess
import json

def find_client_lambdas():
    try:
        result = subprocess.run(
            ["aws", "lambda", "list-functions", "--region", "us-east-2", "--query", "Functions[].FunctionName"],
            capture_output=True, text=True, check=True
        )
        functions = json.loads(result.stdout)
        print("Matching functions:")
        for f in functions:
            if "client" in f.lower() or "onehr" in f.lower():
                print(f"- {f}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_client_lambdas()
