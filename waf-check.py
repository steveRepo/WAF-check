# Loop through each zone on an account to check its WAF Update Eligibility Status.
# Prints to screen or writes to file waf_compatibility_check.txt

import http.client
import json

# Get auth details
def get_auth():
  print('\n' + "WAF compatibility checker. Check your zone's WAF Update Eligibility Status account-wide. False indicates the zone is not eligible for WAF update." + '\n')
  # Print results to file or screen?
  write_to_file = input("Would you like to write the results to a file? If no, all zone results will print to screen. (y/n): ")
  if write_to_file.lower() == 'y':
    write_to_file = True
  else:
    write_to_file = False

  # get auth key
  api_key = input("Enter your API key: ")
  # get auth email
  auth_email = input("Enter your auth email: ")
  # get account id
  account_id = input("Enter the account id you wish to check: ")

  return auth_email, api_key, account_id, write_to_file

# Get the zone list 
def get_zone_list(auth_email, api_key, account_id):

  # Set up the request header
  headers = {
    'Content-Type': 'application/json', 
    'X-Auth-Email': auth_email,
    'X-Auth-Key': api_key 
  }

  # setup the request
  conn = http.client.HTTPSConnection("api.cloudflare.com")
  
  # Make the API Call to get the zone name and ID across all zones in account
  try:
    conn.request("GET", "/client/v4/zones?account.id=" + account_id, headers=headers)
    res = conn.getresponse()
    data = res.read()
    response_data = data.decode('utf-8')
    data = json.loads(response_data)

    # iterate over each "item" in the returned JSON and extract the ID and Name into a dictionary
    zone_items_list = [{'id': item['id'], 'name': item['name']} for item in data['result']]

    return zone_items_list, headers
  
  # Flag Errors
  except Exception as e:
    print(f"An error occurred while fetching Zone list: {e}")
    conn.close()

    return [], headers

# Main loop to call endpoint
def check_WAF_compatiblity(zone_items_list, headers, write_to_file):
   
  # Initialize counter
  total_items_count = 0 

  # Initialize file write 
  file_written = False

  # Setup the connection
  conn = http.client.HTTPSConnection("api.cloudflare.com")

  # Iterate over each zone in the list
  for zone_item in zone_items_list:

    # set the variables
    zone_id = zone_item['id']
    zone_name = zone_item['name']

    # Initialize connection object 
    conn.request("GET", f"/client/v4/zones/{zone_id}/waf_migration/check?phase_two=1", headers=headers)

    try:
      # API call endpoint to check if zone is compatible: https://developers.cloudflare.com/waf/reference/migration-guides/waf-managed-rules-migration/

      res = conn.getresponse()
      if res.status != 200:
        print(f"Unexpected status code {res.status} for zone {zone_id}")
        continue
      data = res.read()
      # parse response
      response_data = json.loads(data.decode('utf-8')) 

      # Example compatability response:
      #{
      #	"result": {
      #		"compatible": false
      #	},
      #	"success": true,
      #	"errors": [],
      #	"messages": []
      #}

      # check for compatible value
      compatible_value = response_data['result']['compatible']

      # print to file or screen (sometimes there may be a large number of zones which would be better suited to a file.)
      if write_to_file:

        # print the value to file
        with open('waf_compatibility_check.txt', 'a') as file:
          domain_info = "Domain: " + zone_name + " - with zone ID: " + zone_id + " | " + "WAF Update Eligibility Status: " + str(compatible_value)
          file.write(domain_info + '\n') 
          file_written = True
      else:
      # print all values to screen
        print("Domain: " + zone_name + " - with zone ID: " + zone_id + " | " + "WAF Update Eligibility Status: " + str(compatible_value))

    # Flag Errors
    except Exception as e:
      print(f"There was an error with the request: {e}")
      continue  # Continue to next domain_id in case of an error
    finally:
      conn.close()
      # Reconnect for next iteration
      conn.connect()

    # increment zone counter
    total_items_count += 1
    
  #--- Loop Terminated ---#

  # Close HTTP Connection
  conn.close()

  # Print to screen the total item count
  print(f"Total item count across all responses: {total_items_count}")

  if file_written:
    print(f"Wrote compatability list to file.") 

  # flag process completed successfully  
  print(f"Zone compatability check completed successfully." + '\n')

def main():
  # Prompt for authorization
  auth_email, api_key, account_id, write_to_file = get_auth()

  # Get zone list items
  zone_items_list, headers = get_zone_list(auth_email, api_key, account_id)
  
  # Check if the zone list is empty to see if there is an error 
  if not zone_items_list:
    print("No zones were found, exiting script.")
    return

  # Check for WAF Compatibility across all zones
  check_WAF_compatiblity(zone_items_list, headers, write_to_file)
    
if __name__ == "__main__":
    main()
