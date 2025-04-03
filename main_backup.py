import uuid

import boto3
import requests
import os
import json
from datetime import datetime

# Define a list of regions
# regions = ['ap-southeast-1', 'us-west-2', 'eu-central-1']
regions = ['us-east-1']

def convert_datetime(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()  # Convert datetime to ISO 8601 string format
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")


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


# Function to get the scan configurations for a region
def get_scan_configurations(region):
    client = get_inspector_client(region)

    # List scan configurations in the given region
    response = client.list_cis_scan_configurations()

    pretty_json = json.dumps(response, indent=4, default=convert_datetime)
    print(f"Scan configurations: {pretty_json}")

    # Extract scan configuration ARNs
    scan_configuration_arns = [config['scanConfigurationArn'] for config in response.get('scanConfigurations', [])]

    print(f"Scan configurations list: {scan_configuration_arns}")
    return scan_configuration_arns


# Function to get the latest successful scan from a given configuration ARN
def get_latest_successful_scan_from_config(region, scan_configuration_arn):
    client = get_inspector_client(region)

    # Define the filter criteria
    filter_criteria = {
        'scanConfigurationArnFilters': [
            {
                'comparison': 'EQUALS',  # Use 'EQUALS' to filter by the exact ARN
                'value': scan_configuration_arn
            }
        ],
        'scanStatusFilters': [
            {
                'comparison': 'EQUALS',
                'value': 'COMPLETED'  # Filter to get only completed scans
            }
        ]
    }

    # List scans for the given scan configuration ARN
    response = client.list_cis_scans(filterCriteria=filter_criteria)

    pretty_json = json.dumps(response, indent=4, default=convert_datetime)
    print(f"Scans for configuration {scan_configuration_arn}: {pretty_json}")

    # Check for successful scans
    successful_scans = response.get('scans', [])

    # Sort by timestamp and return the latest scan ARN
    if successful_scans:
        latest_scan = successful_scans[0]
        return latest_scan['scanArn']
    return None


# Function to download the scan report
def download_scan_report(region, scan_arn):
    client = get_inspector_client(region)
    # Request the report URL
    response = client.get_cis_scan_report(
        reportFormat='CSV',
        scanArn=scan_arn,
        targetAccounts=['468896299932']
    )

    pretty_json = json.dumps(response, indent=4, default=convert_datetime)
    print(f"url {pretty_json}")
    unique_id = uuid.uuid4()
    # Download the report
    if 'url' in response:
        r = response['url']
        res = requests.get(r)
        if res.status_code == 200:
            content = res.content
            with open(f'report_{region}_{unique_id}.csv', 'wb') as file:
                file.write(content)
            print(f"Report downloaded for {region}")
        else:
            print(f"Failed to download report for {region}")
    else:
        print(f"No URL found for scan ARN {scan_arn} in {region}")


# Main logic to loop through regions and process each region
def process_scans():
    for region in regions:
        print(f"Processing region: {region}")

        # Get the scan configurations
        scan_configuration_arns = get_scan_configurations(region)

        for scan_configuration_arn in scan_configuration_arns:
            print(f"Processing scan configuration ARN: {scan_configuration_arn}")

            # Get the latest successful scan ARN from the scan configuration
            scan_arn = get_latest_successful_scan_from_config(region, scan_configuration_arn)

            if scan_arn:
                print(f"Latest successful scan ARN found in {region}: {scan_arn}")
                download_scan_report(region, scan_arn)
            else:
                print(f"No successful scans found for configuration ARN {scan_configuration_arn} in {region}")


# Run the process
process_scans()
