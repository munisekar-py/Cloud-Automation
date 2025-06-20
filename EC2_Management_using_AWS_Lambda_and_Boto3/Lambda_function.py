import boto3

def lambda_handler(event, context):
    ec2 = boto3.client('ec2', region_name='us-west-2')

    # Describe instances with Auto-Stop or Auto-Start tags
    response = ec2.describe_instances(
        Filters=[
            {
                'Name': 'tag:Action',
                'Values': ['Auto-Stop', 'Auto-Start']
            }
        ]
    )

    to_stop = []
    to_start = []

    # Helper to get instance Name from Tags
    def get_instance_name(tags):
        for tag in tags:
            if tag['Key'] == 'Name':
                return tag['Value']
        return "Unnamed"

    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            state = instance['State']['Name']
            tags = instance.get('Tags', [])

            name = get_instance_name(tags)

            for tag in tags:
                if tag['Key'] == 'Action':
                    if tag['Value'] == 'Auto-Stop' and state not in ['stopping', 'stopped']:
                        to_stop.append({"InstanceId": instance_id, "Name": name, "State": state})
                    elif tag['Value'] == 'Auto-Start' and state not in ['pending', 'running']:
                        to_start.append({"InstanceId": instance_id, "Name": name, "State": state})

    # Print affected instances
    if to_stop:
        print("Instances to STOP:")
        for inst in to_stop:
            print(f" - {inst['Name']} ({inst['InstanceId']}) in state {inst['State']}")
        ec2.stop_instances(InstanceIds=[i['InstanceId'] for i in to_stop])

    if to_start:
        print("Instances to START:")
        for inst in to_start:
            print(f" - {inst['Name']} ({inst['InstanceId']}) in state {inst['State']}")
        ec2.start_instances(InstanceIds=[i['InstanceId'] for i in to_start])

    return {
        'statusCode': 200,
        'body': {
            "StoppedInstances": to_stop,
            "StartedInstances": to_start
        }
    }
