from azure_deallocator import AzureDeallocator


azure_deallocator = AzureDeallocator()
azure_deallocator.deallocate_vms(config_source='env')
# azure_deallocator.deallocate_vms(config_source='config.json')
