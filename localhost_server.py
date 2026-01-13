from flask import Flask, request, jsonify, render_template_string
import lambda_function
import json

app = Flask(__name__)

# Mock Lambda Context object
class MockContext:
    def __init__(self):
        self.function_name = "local_server_lambda"
        self.memory_limit_in_mb = 128
        self.invoked_function_arn = "arn:aws:lambda:local:000000000000:function:local_server"
        self.aws_request_id = "local-request-id"

# Simple HTML Interface for testing
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OneHR Lambda Local Explorer</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f4f7f6; color: #333; margin: 0; padding: 20px; }
        .container { max-width: 800px; margin: auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; text-align: center; }
        .section { margin-bottom: 25px; }
        label { display: block; margin-bottom: 8px; font-weight: bold; }
        textarea { width: 100%; height: 150px; padding: 12px; border: 1px solid #ddd; border-radius: 8px; font-family: monospace; font-size: 14px; background: #fafafa; }
        button { background: #3498db; color: white; border: none; padding: 12px 24px; border-radius: 8px; cursor: pointer; font-size: 16px; margin-top: 10px; width: 100%; transition: background 0.3s; }
        button:hover { background: #2980b9; }
        .result-container { margin-top: 30px; border-top: 2px solid #eee; padding-top: 20px; }
        pre { background: #2c3e50; color: #ecf0f1; padding: 15px; border-radius: 8px; overflow-x: auto; font-size: 13px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 OneHR Lambda Explorer</h1>
        <div class="section">
            <label for="payload">Request Payload (JSON)</label>
            <textarea id="payload" placeholder='{ "operation": "get_clients" }'>{ "operation": "get_clients" }</textarea>
            <button onclick="sendRequest()">Test Endpoint</button>
        </div>
        
        <div class="result-container" id="result-box" style="display:none;">
            <label>Response Status: <span id="status-code">-</span></label>
            <pre id="response-preview">No request sent yet.</pre>
        </div>
    </div>

    <script>
        async function sendRequest() {
            const payloadText = document.getElementById('payload').value;
            const resultBox = document.getElementById('result-box');
            const responsePreview = document.getElementById('response-preview');
            const statusCode = document.getElementById('status-code');
            
            resultBox.style.display = 'block';
            responsePreview.innerText = '📡 Processing...';

            try {
                const response = await fetch('/lambda', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: payloadText
                });
                
                const data = await response.json();
                statusCode.innerText = response.status;
                responsePreview.innerText = JSON.stringify(data, null, 4);
                
                if (response.status >= 400) {
                    statusCode.style.color = '#e74c3c';
                } else {
                    statusCode.style.color = '#27ae60';
                }
            } catch (error) {
                statusCode.innerText = 'ERROR';
                responsePreview.innerText = '❌ Request failed: ' + error.message;
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/lambda', methods=['POST'])
def run_lambda():
    try:
        event = request.get_json()
        response = lambda_function.lambda_handler(event, MockContext())
        return jsonify(json.loads(response['body'])), response['statusCode']
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("--- Localhost API UI Starting ---")
    print("Open your browser at http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000)
