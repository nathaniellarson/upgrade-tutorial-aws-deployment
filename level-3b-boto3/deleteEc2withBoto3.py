import boto3 

# Option 1: Session from profile
academy_boto3 = boto3.session.Session(profile_name='academy')
# OR Option 2: Change default profile
# boto3.setup_default_session(profile_name='academy') ## and then use boto3 instead of 'academy_boto3'
# OR Option 3: Session from access keys
# boto3_session = boto3.session.Session(aws_access_key_id = XXXXX, aws_secret_access_key = XXXXX) ## and then use boto3_session instead of 'academy_boto3'

ec2 = academy_boto3.resource('ec2')

## Get the instances that are running with the given name
instances = ec2.instances.filter(
    Filters=[{'Name': 'instance-state-name', 'Values': ['running']},
             {'Name': 'tag:Name', 'Values': ['my-boto3-ec2-instance']}]) # or whichever name

for instance in instances:  
    print("Filtered instances:", instance)

## Terminate the given instances or abort
print("Delete instances? (y/n)")
consent = input()
if consent == "y":
    instances.terminate()
    print("Delete completed!")
else:
    print("Delete aborted!") 