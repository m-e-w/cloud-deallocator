import os
import json
import datetime
from azure.mgmt.compute import ComputeManagementClient
from azure.identity import EnvironmentCredential, ClientSecretCredential


class AzureDeallocator:

    # Grab credentials, sub ID & resoure group from env vars & create compute client object
    def __load_config(self, config_source):
        resource_group_names = None
        resource_groups = None
        credential = None
        subscription_id = None
        if(config_source == 'env'):
            print(datetime.datetime.now(), ": Loading environment variables")
            resource_group_names = os.getenv("AZURE_RESOURCE_GROUP_NAMES")
            if(resource_group_names is not None):
                resource_groups = resource_group_names.split(',')
            subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
            credential = EnvironmentCredential()
        elif(config_source == 'json'):
            print(datetime.datetime.now(), ": Loading config.json")
            with open('config.json') as json_file:
                config = json.load(json_file)
                tenant_id = config['tenant_id']
                client_id = config['client_id']
                client_secret = config['client_secret']
                resource_groups = config['resource_groups']
                subscription_id = config['subscription_id']
                credential = ClientSecretCredential(
                    tenant_id=tenant_id, client_id=client_id, client_secret=client_secret)

        return credential, subscription_id, resource_groups

    def deallocate_vms(self, config_source):
        print(datetime.datetime.now(),
              ": Task: Start -- Deallocating Azure Virtual Machines")

        credential, subscription_id, resource_groups = self.__load_config(
            config_source=config_source)

        if(credential is not None and subscription_id is not None and resource_groups is not None):
            compute_client = ComputeManagementClient(
                credential=credential, subscription_id=subscription_id)

            sub_already_deallocated_count = 0
            sub_newly_deallocated_count = 0
            for resource_group in resource_groups:
                resource_group = resource_group.strip()
                print(datetime.datetime.now(),
                      ": Retrieving Virtual Machines from:", resource_group)

                # Get all vms in a specific resource group (need to loop through them in the next step)
                compute_list = list(compute_client.virtual_machines.list(
                    resource_group_name=resource_group))
                compute_count = len(compute_list)

                print(datetime.datetime.now(), ":", compute_count, "vms found")

                # Loop through all vms. Check the vm state (this requires 1 request per vm)
                # Log VM payload to stdout and send begin_deallocate request to each vm that is currently not in a "PowerState/deallocated" state
                rg_already_deallocated_count = 0
                rg_newly_deallocated_count = 0
                for compute in compute_list:
                    compute_dict = compute.as_dict()
                    vm = compute_dict['name']

                    print(datetime.datetime.now(),
                          ":", vm, "-- Checking state")

                    vm_state = compute_client.virtual_machines.instance_view(
                        resource_group_name=resource_group, vm_name=vm)
                    vm_dict = {
                        'id': compute_dict['id'],
                        'name': vm,
                        'type': compute_dict['type'],
                        'size': compute_dict['hardware_profile']['vm_size'],
                        'status': vm_state.statuses[1].code,
                        'location': compute_dict['location'],
                        'tags': compute_dict['tags']
                    }

                    print(datetime.datetime.now(), ": VM Payload --", vm_dict)

                    if(vm_dict['status'] != 'PowerState/deallocated'):
                        print(datetime.datetime.now(),
                              ": Begin Deallocating VM: ", vm)

                        compute_client.virtual_machines.begin_deallocate(
                            resource_group_name=resource_group, vm_name=vm)

                        print(datetime.datetime.now(),
                              ": End Deallocating VM: ", vm)
                        rg_newly_deallocated_count += 1

                    else:
                        print(datetime.datetime.now(), ":", vm,
                              "is already deallocated. Skipping.")
                        rg_already_deallocated_count += 1

                print(datetime.datetime.now(), ": Resource Group:", resource_group, "-- Already Deallocated:",
                      rg_already_deallocated_count, "| Newly Deallocated:", rg_newly_deallocated_count)
                sub_already_deallocated_count += rg_already_deallocated_count
                sub_newly_deallocated_count += rg_newly_deallocated_count

            print(datetime.datetime.now(), ": Subscription:", subscription_id, "-- Already Deallocated:",
                  sub_already_deallocated_count, "| Newly Deallocated:", sub_newly_deallocated_count)

        else:
            print(datetime.datetime.now(),
                  ": Error -- One or more configuration parameters are missing")

        print(datetime.datetime.now(),
              ": Task: End -- Deallocating Azure Virtual Machines\n")
