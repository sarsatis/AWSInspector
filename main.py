import json
from scan.scan_utils import get_scan_configurations, get_latest_successful_scan_from_config
from report.report_utils import download_scan_report

# Define a list of regions
regions = ['us-east-1']


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
if __name__ == '__main__':
    process_scans()
