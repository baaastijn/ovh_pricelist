import requests
import json
import boto3
import os
import logging

BASE_URL = 'https://api.ovh.com/1.0/'
headers = {'Accept': 'application/json'}
SUBSIDIARIES = ['CZ','DE','ES','FI','FR','GB','IE','IT','LT','MA','NL','PL','PT','SN','TN']
S3_ACCESS_KEY_ID = os.getenv('S3_ACCESS_KEY_ID')
S3_SECRET_ACCESS_KEY = os.getenv('S3_SECRET_ACCESS_KEY')
S3_BUCKET = os.getenv('S3_BUCKET')


def build_dataset(js):
    currency = js['locale']['currencyCode']
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

                plans.append({
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
                })
    return plans

def s3():
    # list      s3().Bucket(S3_BUCKET).objects
    # upload    s3().Bucket(S3_BUCKET).upload_file()
    return boto3.resource(
            "s3",
            endpoint_url="https://s3.gra.io.cloud.ovh.net/",
            verify=True,
            region_name='gra',
            aws_access_key_id=S3_ACCESS_KEY_ID,
            aws_secret_access_key=S3_SECRET_ACCESS_KEY,
        )


if __name__ == '__main__':
    for sub in SUBSIDIARIES:
        data1 = requests.get(f'{BASE_URL}order/catalog/public/eco?ovhSubsidiary={sub}', headers=headers).json()
        data2 = requests.get(f'{BASE_URL}order/catalog/public/baremetalServers?ovhSubsidiary={sub}', headers=headers).json()

        dataset = build_dataset(data1)
        dataset += build_dataset(data2)

        assert len(dataset) > 1000, "Must have more than 1k refs"
        filename = f'ovh_pricing_plans_{sub}.json'
        json.dump(dataset, open(filename, 'w'))
        s3().Bucket(S3_BUCKET).upload_file(file)

