from datetime import datetime
from utils import *

def build_dataset(js):
    plans = []

    for plan in js['plans']:
        memory_addons = None
        storage_addons = None
        system_storage = ''
        tech_specs = None
        products_specs = {}

        for addon_family in plan['addonFamilies']:
            if addon_family['name'] == 'memory':
                memory_addons = addon_family['addons']
            if addon_family['name'] == 'storage' or addon_family['name'] == 'disk':
                storage_addons = addon_family['addons']
            if addon_family['name'] == 'system-storage':
                system_storage = addon_family['addons'][0]

        for prod in js['products']:
            if prod['name'] == plan['planCode'] or prod['name'] == plan['product']:
                if prod['blobs']:
                    tech_specs = prod['blobs']['technical']['server']
                
            if prod['blobs']:
                products_specs[prod['name']] = prod['blobs']['technical']
        
        for pricing in plan['pricings']:
            if pricing['commitment'] == 0 and pricing['mode'] == 'default' and pricing['interval'] == 1:
                server_price = pricing['price'] / 100000000
        if not memory_addons:
            continue
        
        for memory_addon in memory_addons:
            memory_specs = {'product': [''], 'price': 0}
            storage_specs = {'product': [''], 'price': 0}
            
            for storage_addon in storage_addons:
                for addon in js['addons']:
                    addon_price = 0

                    for pricing in addon['pricings']:
                        if pricing['commitment'] == 0 and pricing['mode'] == 'default' and pricing['interval'] == 1:
                            addon_price = pricing['price'] / 100000000
                            break

                    if addon['planCode'] == storage_addon:
                        storage_specs = {
                            'planCode': addon['planCode'],
                            'product': addon['product'],
                            'invoiceName': addon['invoiceName'],
                            'specifications': products_specs[addon['product']]['storage'],
                            'price': addon_price
                        }
                    if addon['planCode'] == memory_addon:
                        memory_specs = {
                            'planCode': addon['planCode'],
                            'product': addon['product'],
                            'invoiceName': addon['invoiceName'],
                            'specifications': products_specs[addon['product']]['memory'],
                            'price': addon_price
                        }
                    if addon['planCode'] == system_storage:
                        system_storage = addon['product']
                    
                fqn = '.'.join(list(filter(None, [plan['planCode'], memory_specs['product'], storage_specs['product'], system_storage])))
                item = {
                    'planCode': plan['planCode'],
                    'product': plan['product'],
                    'invoiceName': plan['invoiceName'],
                    'fqn': fqn,
                    'memory': memory_specs,
                    'storageSpecs': storage_specs,
                    'cpu': tech_specs['cpu'],
                    'range': tech_specs['range'],
                    'frame': tech_specs['frame'],
                    'setupfee': server_price,
                    'price': server_price + storage_specs['price'] + memory_specs['price']
                }
                if item['price'] > 0:
                    plans.append(item)
    return plans


if __name__ == '__main__':
    for sub in SUBSIDIARIES:
        base_api = get_base_api(sub)
        data1 = get_json(f'{base_api}/v1/order/catalog/public/eco?ovhSubsidiary={sub}')
        data2 = get_json(f'{base_api}/v1/order/catalog/public/baremetalServers?ovhSubsidiary={sub}')
        dataset = build_dataset(data1)
        dataset += build_dataset(data2)

        assert len(dataset) > 1000, "Must have more than 1k refs"
        filename = f'baremetal_prices/{sub.lower()}.json'

        upload_gzip_json({
            'plans': dataset,
            'date': datetime.now().isoformat(),
            'currency': data1['locale']['currencyCode']
        }, filename, S3_BUCKET)
        print(f'INFO: Uploaded {filename}')