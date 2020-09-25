from panos.firewall import Firewall
from panos.objects import AddressObject
from panos.objects import AddressGroup
from pprint import pprint
import datetime
from time import sleep
import argparse
import json

#requires a group name in str, panos firewall object, and a dict where results are saved.
def recursive_group_search(group,fw,export_dict):
    #use panos find method to search for the group, then iterate through its entries
    #if it has dynamic_value and/or static_value its a group
    #dynamic groups are added to the the dict with their tags
    #static groups are recursed to see if they have further nesting
    result = fw.find(group)
       
    for i in result.static_value:
        sub_search = fw.find(i)
        if hasattr(sub_search, 'static_value') or hasattr(sub_search,'dynamic_value'):
            if sub_search.dynamic_value is not None:
                export_dict['groups'].append(sub_search.about()) 
            elif sub_search.static_value is not None:
                export_dict['groups'].append(sub_search.about())
                recursive_group_search(sub_search.name,fw,export_dict)
    
    #when we get to the base address objects save them to the dict             
        else: 
            export_dict['addresses'].append(sub_search.about())

    return export_dict

#required a panos firewall object, and the name of a group in str. Exports group data from fw
def firewall_export(export_fw,group, export_username, export_password):
    start = datetime.datetime.now()
    export_dict={'groups':[], 'addresses':[]} #To save data from the recursive function(s)
    pulling_fw = Firewall(export_fw, export_username, export_password)  # Create a firewall object
    AddressObject.refreshall(pulling_fw) #pulls down the address objects in the firewall
    AddressGroup.refreshall(pulling_fw, add=True) # pulls down the address groups in the firewall
    top_level_group = pulling_fw.find(group)
    #recursively search for all entries inside the requested group digging out any nested groups
    
    recursive_group_search(group, pulling_fw, export_dict)
    export_dict['groups'].append(top_level_group.about())
    print(f"Exported {len(export_dict['addresses'])} address objects and {len(export_dict['groups'])} from { export_fw }")
    print(f"took: {datetime.datetime.now() - start}")

    return export_dict

#required a panos firewall object, and the name of a group in str. imports group data from provided dict
#dict must be in the form of {groups:[], addresses:[]} where groups are AddressGroups and addresses are AddressObject
def firewall_import(import_fw, import_dict, import_username, import_password, commit):
    pushing_fw = Firewall(import_fw, import_username, import_password)
    AddressObject.refreshall(pushing_fw) #pulls down the address objects in the firewall
    AddressGroup.refreshall(pushing_fw, add=True) # pulls down the address groups in the firewall
    for i in import_dict['addresses']:
        addr = AddressObject(name=i['name'], value=i['value'], description=i['description'],type=i['type'], tag=i['tag'])
        pushing_fw.add(addr)
    start = datetime.datetime.now()
    addr.create_similar()

    for i in import_dict['groups']:
        group = AddressGroup(i['name'],i['static_value'], i['dynamic_value'],i['tag'])
        pushing_fw.add(group)
    start = datetime.datetime.now()
    group.create_similar()
    print(f"Imported { len(import_dict['addresses']) } addresses and {len(import_dict['groups'])} to { import_fw }")
    print(f"which took: {datetime.datetime.now() - start}")
    
    if commit is True:
        print(f"As requested, commiting to firewall {import_fw}")
        pushing_fw.commit()

    return import_dict


def main(export_username,
            export_password, 
            import_username,
            import_password, 
            import_fw,
            export_fw,
            group,
            output,
            output_file,
            commit,
            file_only): 
    if output is True:
        with open(output_file, 'w') as out_file:
            fw_pull = firewall_export(export_fw, group, export_username, export_password)
            out_file.write(json.dumps(fw_pull, indent=4))
    else:
        fw_pull = firewall_export(export_fw, group, export_username, export_password)
    
    if file_only is False:
        print("Beginning Firewall import of group")
        firewall_import(import_fw, fw_pull, import_username, import_password, commit)
    else:
        print(f"Firewall Group File created at {output_file }")


        

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
    description='This script exports address groups from PAN firewalls, including all nested groups and addresses',
    prefix_chars='-+/',
    )
    parser.add_argument('-if', '--import_fw', help='Firewall IP address to import from')
    parser.add_argument('-ef', '--export_fw', help='Firewall IP address to export to')
    parser.add_argument('-iuser','--import_username', help='Username to login as on Importing Firewall')
    parser.add_argument('-ipass','--import_password', help='Password to login as on Importing Firewall')
    parser.add_argument('-euser','--export_username', help='Username to login as on Exporting Firewall. If not set will default to the username for the import firewall')
    parser.add_argument('-epass','--export_password', help='Password to login as on Exporting Firewall. If not set will default to the username for the import firewall')
    parser.add_argument('-output','--output', action='store_true', help='If set, will output of the export as a text file (in JSON)')
    parser.add_argument('-file','--output_file',default='fw_export.json', help='If outputing to file the File name to export to')
    parser.add_argument('-group','--group', help='Name of the Group you want to export')
    parser.add_argument('-commit','--commit', action='store_true', default=False, help='If set, will commit the changes imported from this script. Default is to NOT commit. This allows you to review your changes from the webui if you wish')
    parser.add_argument('-file_only','--file_only', action='store_true', default=False, help='If set, will NOT import to a firewll. Will only export address group into file')
    args = parser.parse_args()
    if args.export_username is None: 
        args.export_username = args.import_username
    if args.export_password is None:
        args.export_password = args.import_password

    
    main(export_username=args.export_username, 
            export_password=args.export_password, 
            import_username=args.import_username,
            import_password=args.import_password, 
            import_fw=args.import_fw,
            export_fw=args.export_fw,
            group=args.group,
            output=args.output,
            output_file=args.output_file,
            commit=args.commit,
            file_only=args.file_only
            )

