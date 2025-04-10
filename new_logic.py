import uuid
import boto3
import requests
import os
import json
from datetime import datetime

# Use a predefined structure instead of fetching config ARNs
scan_details = [
    {
        "region": "us-west-2",
        "scanConfigArn": ["arn1", "arn2"]
    },
    {
        "region": "ap-southeast-1",
        "scanConfigArn": ["arn3"]
    },
    {
        "region": "eu-central-1",
        "scanConfigArn": ["arn4"]
    }
]

def convert_datetime(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

def get_inspector_client(region):
    aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')

    if aws_access_key_id and aws_secret_access_key:
        return boto3.client(
            'inspector2',
            region_name=region,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )
    else:
        return boto3.client('inspector2', region_name=region)

def get_latest_successful_scan_from_config(region, scan_configuration_arn):
    client = get_inspector_client(region)

    filter_criteria = {
        'scanConfigurationArnFilters': [
            {
                'comparison': 'EQUALS',
                'value': scan_configuration_arn
            }
        ],
        'scanStatusFilters': [
            {
                'comparison': 'EQUALS',
                'value': 'COMPLETED'
            }
        ]
    }

    response = client.list_cis_scans(filterCriteria=filter_criteria)
    print(f"Scans for configuration {scan_configuration_arn}:")
    print(json.dumps(response, indent=4, default=convert_datetime))

    successful_scans = response.get('scans', [])
    if successful_scans:
        latest_scan = successful_scans[0]
        return latest_scan['scanArn']
    return None

def download_scan_report(region, scan_arn):
    client = get_inspector_client(region)
    response = client.get_cis_scan_report(
        reportFormat='CSV',
        scanArn=scan_arn,
        targetAccounts=['468896299932']
    )

    print(f"Report URL response for scan {scan_arn}:")
    print(json.dumps(response, indent=4, default=convert_datetime))

    unique_id = uuid.uuid4()
    if 'url' in response:
        res = requests.get(response['url'])
        if res.status_code == 200:
            with open(f'report_{region}_{unique_id}.csv', 'wb') as file:
                file.write(res.content)
            print(f"Report downloaded for {region}")
        else:
            print(f"Failed to download report for {region}")
    else:
        print(f"No URL found for scan ARN {scan_arn} in {region}")

def process_scans():
    for entry in scan_details:
        region = entry['region']
        scan_arns = entry['scanConfigArn']
        print(f"Processing region: {region}")

        for scan_config_arn in scan_arns:
            print(f"Processing scan configuration ARN: {scan_config_arn}")
            scan_arn = get_latest_successful_scan_from_config(region, scan_config_arn)

            if scan_arn:
                print(f"Latest successful scan ARN found: {scan_arn}")
                download_scan_report(region, scan_arn)
            else:
                print(f"No successful scans found for configuration ARN {scan_config_arn} in {region}")

# Run the process
process_scans()
