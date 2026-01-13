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
            limit=5
        )
        
        for stream in streams['logStreams']:
            stream_name = stream['logStreamName']
            print(f"\n--- Logs from {stream_name} ---")
            
            events = client.get_log_events(
                logGroupName=log_group,
                logStreamName=stream_name,
                limit=100
            )
            
            for event in events['events']:
                print(f"{time.ctime(event['timestamp']/1000)}: {event['message'].strip()}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_detailed_logs()
