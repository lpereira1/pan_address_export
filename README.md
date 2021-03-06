# pan_address_export

This script exports data for requested address group from a Palo Alto Firewall. If the group has nesting it will export all the attached groups and addresses. 
It will then import the address group with all its nested entries into a different Palo Alto Firewall. 

This is useful if you dont have Panorama and need to get an address group from one firewall to another. 

You can chose to export to a file as JSON and commit or not commit as you feel is needed. See the arguments at the bottom of the readme. 

### Installation and requirements
Requires 
 * Python3 
 * pan-os-python 

```bash
pip3 install -r requirements.txt
```

### Example
#### Export from one firewal and import to another where the same username and password applies to both firewall with file output and commit
```
addressexport.py -if 10.1.1.1 -iuser admin -ipass admin -group CORPORATE_USERS -ef 10.2.2.2 -output -file corp_users.json -commit
```
#### Export from one firewall with file output only
```
addressexport.py -if 10.1.1.1 -iuser admin -ipass admin -group CORPORATE_USERS -output -file_only -file corp_users.json 
```


```
usage: addressexport.py [-h] [-if IMPORT_FW] [-ef EXPORT_FW]
                        [-iuser IMPORT_USERNAME] [-ipass IMPORT_PASSWORD]
                        [-euser EXPORT_USERNAME] [-epass EXPORT_PASSWORD]
                        [-output] [-file OUTPUT_FILE] [-group GROUP] [-commit]

This script exports address groups from PAN firewalls, including all nested
groups and addresses

optional arguments:
  -h, --help            show this help message and exit
  -if IMPORT_FW, --import_fw IMPORT_FW
                        Firewall IP address to import from
  -ef EXPORT_FW, --export_fw EXPORT_FW
                        Firewall IP address to export to
  -iuser IMPORT_USERNAME, --import_username IMPORT_USERNAME
                        Username to login as on Importing Firewall
  -ipass IMPORT_PASSWORD, --import_password IMPORT_PASSWORD
                        Password to login as on Importing Firewall
  -euser EXPORT_USERNAME, --export_username EXPORT_USERNAME
                        Username to login as on Exporting Firewall. If not set will default to the credentials 
                        for the import firewall.
  -epass EXPORT_PASSWORD, --export_password EXPORT_PASSWORD
                        Password to login as on Exporting Firewall. If not setwill default to the credentials 
                        for the import firewall.
  -output, --output     If set, will output of the export as a text file (in JSON).
  -file OUTPUT_FILE, --output_file OUTPUT_FILE
                        if output yes: File name to export to, Default: fw_export.json
  -group GROUP, --group GROUP
                        Name of the Group you want to export.
                        
  -commit, --commit     If set, will commit the changes imported
                        from this script. Default is to not commit. This allows you to review your changes 
                        from the webui if you wish.
```