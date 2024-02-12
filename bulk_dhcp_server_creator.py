#azzalinko11 version 0.1

#import libs
import credentials_file
import requests
import csv
import json
# Import the Prisma SASE SDK API constructor etc
from prisma_sase import API, jd

# Instantiate the Prisma SASEx API constructor
sdk = API()

# Call Prisma SASE API login and creds from "credentials_file.py" file using the Interactive helpers (Handle SAML2.0 login and MSP functions too!).
sdk.interactive.login_secret(client_id=credentials_file.client_id, 
                             client_secret=credentials_file.client_secret, 
                             tsg_id=credentials_file.scope)

# Path to the CSV file containing the DHCP config lists
csv_file = 'dhcp_import.csv'

# Read the DHCP config from the CSV file
dhcp_objects = []
with open(csv_file, 'r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        dhcp_object = {
            "disabled": False,
            "tags": None,
            "description": row['Description'],
            "network_context_id": None,
            "subnet": row['Subnet'],
            "gateway": row['IP_Addr'],
            "broadcast_address": row['BroadcastIP'],
            "domain_name": row['DomainName'],
            "dns_servers": [
                row['DNS1'],
                row['DNS2']
            ],
            "default_lease_time": row['Def_Lease_Time'],
            "max_lease_time": row['Max_Lease_Time'],
            "ip_ranges": [
                {
                    "start_ip": row['DhcpStartIP'],
                    "end_ip": row['DhcpEndIP']
                }
            ],
            "static_mappings": None,
            "custom_options": None,
            "address_family": "ipv4",
            "vrf_context_id": row['VRF_ID']
        }
        dhcp_objects.append(dhcp_object)
        # Extract SITE_ID from the current row
        site_id = row['SITE_ID']

#convert to json and strip brackets
dhcp_data_cov_json = json.dumps(dhcp_objects, indent = 4)[1:-1]
print(dhcp_data_cov_json)

# Send the POST request to add the address objects with error handling
success_count = 0
failure_count = 0

for dhcp_obj in dhcp_objects:
    try:
        response = sdk.post.dhcpservers(
            site_id=site_id,
            data=json.dumps(dhcp_obj),
        )
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx status codes)

        if response.status_code == 200:
            success_count += 1
            print(f'Successfully added DHCP configuration: {dhcp_obj["description"]}')
        else:
            failure_count += 1
            print(f'Failed to add DHCP configuration: {dhcp_obj["description"]}, Status Code: {response.status_code}, Response: {response.text}')

    except requests.exceptions.RequestException as e:
        failure_count += 1
        print(f'Exception occurred while adding DHCP configuration: {dhcp_obj["description"]}, Error: {e}')

print(f'Successfully added {success_count} DHCP configurations. Failed to add {failure_count} configurations.')