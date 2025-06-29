import boto3
import datetime

def lambda_handler(event, context):
    # Log the incoming event
    print("Received event:", event)

    # Extract instance ID(s) from the event
    try:
        instance_ids = [
            detail['instance-id']
            for detail in [event['detail']]
            if detail['state'] == 'running'
        ]
    except KeyError:
        print("No instance ID found in the event")
        return

    # Exit if no instances
    if not instance_ids:
        print("No instances in 'running' state")
        return

    # Initialize EC2 client
    ec2 = boto3.client('ec2')

    # Create tags
    current_date = datetime.datetime.utcnow().strftime('%Y-%m-%d')
    tags = [
        {'Key': 'LaunchDate', 'Value': current_date},
        {'Key': 'Environment', 'Value': 'Development'},
        {'Key': 'LaunchedBy', 'Value': 'Munisekar'},
        {'Key': 'Project', 'Value': 'Muni_Auto_Tag'}  
    ]

    # Apply tags to each instance
    try:
        ec2.create_tags(Resources=instance_ids, Tags=tags)
        print(f"Successfully tagged instances {instance_ids}")
    except Exception as e:
        print(f"Error tagging instances: {e}")
