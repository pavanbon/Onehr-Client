import boto3
import time

def get_latest_logs():
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
            print("No log streams found.")
            return

        stream_name = streams['logStreams'][0]['logStreamName']
        print(f"Reading logs from: {stream_name}")
        
        events = client.get_log_events(
            logGroupName=log_group,
            logStreamName=stream_name,
            limit=50
        )
        
        for event in events['events']:
            print(f"{time.ctime(event['timestamp']/1000)}: {event['message'].strip()}")
            
    except Exception as e:
        print(f"Error fetching logs: {e}")

if __name__ == "__main__":
    get_latest_logs()
