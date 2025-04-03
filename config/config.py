import boto3
import os


# Function to initialize the boto3 client
def get_inspector_client(region):
    aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')

    if aws_access_key_id and aws_secret_access_key:
        client = boto3.client(
            'inspector2',
            region_name=region,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )
    else:
        # If no environment variables, rely on the AWS CLI credentials configured via `aws configure`
        client = boto3.client(
            'inspector2',
            region_name=region
        )

    return client
