import json
from config.config import get_inspector_client
from datetime import datetime


def convert_datetime(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()  # Convert datetime to ISO 8601 string format
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")


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
