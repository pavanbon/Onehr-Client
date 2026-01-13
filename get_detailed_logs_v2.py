import boto3
import time

def get_detailed_logs():
    client = boto3.client('logs', region_name='us-east-2')
    log_group = '/aws/lambda/Onehr_Clientservices'
    
    try:
        streams = client.describe_log_streams(
            logGroupName=log_group,
            orderBy='LastEventTime',
            descending=True,
            limit=1
        )
        
        if not streams['logStreams']:
            return

        stream_name = streams['logStreams'][0]['logStreamName']
        print(f"Stream: {stream_name}")
        
        events = client.get_log_events(
            logGroupName=log_group,
            logStreamName=stream_name,
            limit=200
        )
        
        for event in events['events']:
            msg = event['message'].strip()
            # Filter out some noise to see the error
            if "TRACEBACK" in msg.upper() or "ERROR" in msg.upper() or "EXCEPTION" in msg.upper() or "RUNTIMEERROR" in msg.upper():
                 print(f"!!! {msg}")
            else:
                 print(msg)
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_detailed_logs()
