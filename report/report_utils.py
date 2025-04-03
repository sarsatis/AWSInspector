import requests
import uuid
from config.config import get_inspector_client
import json


# Function to download the scan report
def download_scan_report(region, scan_arn):
    client = get_inspector_client(region)
    # Request the report URL
    response = client.get_cis_scan_report(
        reportFormat='CSV',
        scanArn=scan_arn,
        targetAccounts=['468896299932']
    )

    pretty_json = json.dumps(response, indent=4)
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
