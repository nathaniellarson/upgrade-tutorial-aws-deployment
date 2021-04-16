import boto3

# Option 1: Session from profile
academy_boto3 = boto3.session.Session(profile_name='academy')
# OR Option 2: Change default profile
# boto3.setup_default_session(profile_name='academy') ## and then use boto3 instead of 'academy_boto3'
# OR Option 3: Session from access keys
# boto3_session = boto3.session.Session(aws_access_key_id = XXXXX, aws_secret_access_key = XXXXX) ## and then use boto3_session instead of 'academy_boto3'

ec2 = academy_boto3.resource('ec2')

# create a new EC2 instance
instances = ec2.create_instances( # run_instances would result in the same creation 
    ImageId='ami-0915bcb5fa77e4892',
    InstanceType='t2.micro',
    MaxCount = 1,
    MinCount = 1,
    TagSpecifications=[
    {
        'ResourceType': 'instance',
        'Tags': [
            {
                'Key': 'Name',
                'Value': 'my-boto3-ec2-instance'
            },
        ]
    }
    ]
 )

print("Create complete!")

for instance in instances:  
    print("New instance:", instance)

