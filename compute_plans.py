import urllib.request
import json
import boto3
import os
import ssl
from datetime import datetime
import gzip

ssl._create_default_https_context = ssl._create_unverified_context

SUBSIDIARIES = ['CZ','DE','ES','FI','FR','GB','IE','IT','LT','MA','NL','PL','PT','SN','TN']
S3_ACCESS_KEY_ID = os.getenv('S3_ACCESS_KEY_ID')
S3_SECRET_ACCESS_KEY = os.getenv('S3_SECRET_ACCESS_KEY')
S3_BUCKET = os.getenv('S3_BUCKET')


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

def s3():
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#examples
    return boto3.client(
            "s3",
            endpoint_url="https://s3.gra.io.cloud.ovh.net/",
            region_name='gra',
            aws_access_key_id=S3_ACCESS_KEY_ID,
            aws_secret_access_key=S3_SECRET_ACCESS_KEY,
        )

def upload_json(jsonObject, filename, bucket):
    return s3().put_object(Body=json.dumps(jsonObject), Bucket=bucket, Key=filename, ContentType='application/json', ACL='public-read')


def upload_gzip_json(jsonObject, filename, bucket):
    body = gzip.compress(bytes(json.dumps(jsonObject), encoding='utf-8'))
    return s3().put_object(Body=body, Bucket=bucket, Key=filename, ContentType='application/json', ContentEncoding='gzip', ACL='public-read')


def get_json(url):
    req = urllib.request.Request(url, headers={'Accept': 'application/json'}) 
    return json.loads(urllib.request.urlopen(req).read().decode("utf-8"))


if __name__ == '__main__':
    for sub in SUBSIDIARIES:
        data1 = get_json(f'https://api.ovh.com/1.0/order/catalog/public/eco?ovhSubsidiary={sub}')
        data2 = get_json(f'https://api.ovh.com/1.0/order/catalog/public/baremetalServers?ovhSubsidiary={sub}')

        dataset = build_dataset(data1)
        dataset += build_dataset(data2)

        assert len(dataset) > 1000, "Must have more than 1k refs"
        filename = f'ovh_pricing_plans_{sub.lower()}.json'

        upload_gzip_json({
            'plans': dataset,
            'date': datetime.now().isoformat(),
            'currency': data1['locale']['currencyCode']
        }, filename, S3_BUCKET)
        print(f'INFO: Uploaded {filename}')