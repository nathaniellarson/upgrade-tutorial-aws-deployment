# example commands from the various steps in the tutorial
# the following work for the author -- please modify as necessary for your local/AWS environment
aws cloudformation deploy --template-file C:\Users\nathaniel.larson\Desktop\Repos\upgrade-tutorial-aws-deployment\cloudFormationTemplateEC2.json --stack-name example-cli-ec2-deployment-stack --profile academy
aws ec2 describe-instances --filter "Name=instance-state-name,Values=running"
aws ec2 describe-instances --filters "Name=instance-state-name,Values=running" --query "Reservations[].Instances[].InstanceId"
aws ec2 describe-instances --filter "Name=instance-state-name,Values=running" --query "Reservations[].Instances[].Tags[?Key=='Name'].Value[]"