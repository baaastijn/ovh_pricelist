import json

# r = requests.get('https://www.ovh.com/engine/apiv6/order/catalog/formatted/privateCloud?ovhSubsidiary=FR', headers={'content-type': 'application/json'})

CONFORMITY = ['default', 'hds', 'hipaa', 'pcidss']
RANGES = ['vsphere', 'essentials', 'nsx-t']
BACKUP_DESCRIPTION = {
    'classic': 'Veeam Managed Backup - Standard',
    'advanced': 'Veeam Managed Backup - Advanced', 
    'premiu;': 'Veeam Managed Backup - Premiu;',
}
BACKUP_SIZE = {
    's': 'Max 250 GB per VM',
    'm': 'Max 1 TB per VM',
    'l': 'Max 2 TB per VM',
}
pcc_plans = json.loads(open('privateCloud.json').read())

# Get plans
plan_codes = {}
def get_addon_families(obj):
    global plan_codes
    for addonFamily in obj['addonsFamily']:
        for addon in addonFamily['addons']:
            if 'addonsFamily' in addon['plan']:
                get_addon_families(addon['plan'])
            
            item = {
                'family': addonFamily['family'],
                'invoiceName': addon['invoiceName'],
            }
            for pricing_key in addon['plan']['details']['pricings']:
                conformity = pricing_key.split('-')[-1] 
                if conformity not in CONFORMITY:
                    continue
                
                for pricing in addon['plan']['details']['pricings'][pricing_key]:
                    # item['desc'] = pricing['description']
                    item[f"price_{conformity}"] = pricing['price']['value']
            
            if 'backup' in item['invoiceName'].lower():
                print(item) 
            if item['price_default'] > 0 and 'hourly' not in item['family']:
                plan_codes[addon['plan']['planCode']] = item
get_addon_families(pcc_plans['plans'][0])
# Debug plans
for k in plan_codes:
    print(plan_codes[k])
print(len(plan_codes))


# Host Specs
# price_stuct {'invoiceName', description, 'price_...'}


products = {
    'ranges': {},
    'snc_network': {}
}

#     'ranges': {
#       'infrastructure': [
#         'pack',
#         'host',
#         'datastore',
#         'public_ip',
#         'managed_backup',
#         'snc_network'
# ],
#     'other": [
#         'occ',
#         'licences': [
#             'windows_licence',
#             'sql_server',
#             'veeam'
#         ],
#         'ps'
#     ]
# ]

# Get Packs and Options
for cr in pcc_plans['commercialRanges']:
    if cr['name'] not in RANGES:
        continue
    packs = []
    hosts = []
    public_ip = []
    datastore = []

    managementFeePlanCode = cr['datacenters'][0]['managementFees']['planCode']
    # hosts = cr['datacenters'][0]['hypervisors'][0]
    if not cr['datacenters'][0]['hypervisors'][0]['orderable']:
        continue

    # List hosts spec
    for host in cr['datacenters'][0]['hypervisors'][0]['hosts']:
        if 'hourly' in host['name'].lower():
            continue

        cpuspec = host['specifications']['cpu']
        cpu_text = f"{cpuspec['model']} - {cpuspec['frequency']['value']} {cpuspec['frequency']['unit']} - {cpuspec['cores']} cores/{cpuspec['threads']} Threads"
        ram_text = f"{host['specifications']['memory']['ram']['value']} {host['specifications']['memory']['ram']['unit']}"

        # Pack
        pack_datastore = plan_codes[host['storagesPack'][0]] # always X2 this value
        pack = {'invoiceName': f"Pack {host['name']}", 'description': f"2x Host {host['name']} \n  - {cpu_text}\n  - {ram_text} \n2x Datastore 3 TB"}

        for conformity in CONFORMITY:
            if cr['name'] == 'essential' and conformity != 'default':
                continue
            price_key = f"price_{conformity}"
            price = pack_datastore[price_key] * 2 + plan_codes[managementFeePlanCode][price_key] + 2 * plan_codes[host['planCode']][price_key]
            pack[price_key] = price
        packs.append(pack)

        # Host
        host = {'description': f"Additional Host {host['name']}\n{cpu_text}\n{ram_text}"} | plan_codes[host['planCode']]
        hosts.append(host)

    # List options
    for option in cr['datacenters'][0]['hypervisors'][0]['options'] + cr['datacenters'][0]['hypervisors'][0]['servicePacks'] + cr['datacenters'][0]['hypervisors'][0]['storages']:
        price = plan_codes[option['planCode']] if option['planCode'] in plan_codes else None
        if price is None:
            continue
        if 'ip' in price['invoiceName'].lower():
            price['invoiceName'] = price['invoiceName'].replace('RIPE', '')
            ip_count = 2**(32 - int(price['invoiceName'].split('/')[-1]))
            price['description'] = f"{ip_count} Public IPs"
            public_ip.append(price)
        elif 'datastore' in price['invoiceName'].lower():
            price['description'] = f"Additional Datastore - {option['specifications']['type']} {option['specifications']['size']['value']} {option['specifications']['size']['unit']}"
            datastore.append(price)

    # Add Backup options


    # print(*options, sep='\n')

# json.dump(data, open('tmp.json', 'w+'))


