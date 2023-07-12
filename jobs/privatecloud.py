import json
from utils import *


CONFORMITY = ['default', 'hds', 'hipaa', 'pcidss'] # snc computed
SNC_MARKUP = 1.12
RANGES = ['vsphere', 'essentials', 'nsx-t']
STORAGE_PACK_DESCRIPTION = '2x Datastore 3 TB'
BACKUP_DESCRIPTION = {
    'classic': 'Veeam Managed Backup - Standard',
    'advanced': 'Veeam Managed Backup - Advanced', 
    'premium': 'Veeam Managed Backup - Premium',
}
BACKUP_SIZE = {
    's': 'Max 250 GB per VM',
    'm': 'Max 1 TB per VM',
    'l': 'Max 2 TB per VM',
}
# price_stuct {'invoiceName', description, 'price_...'}
products = {
    'ranges': [], # packs, hosts, datastore, public_ip, regions, managed_backup
    'other': {
        'occ': [],
        'ip_lb': [],
        'windows_licence': [],
        # 'veeam_licence': {'invoiceName': 'Licence Veeam Entreprise plus - per VM', 'price': 6},
        'ps': [{'invoiceName': 'Professinal Service', 'description': '8h d\'accompagnement avec un solution architecte Senior', 'price': 1300}]
    }
}

def get_addon_families(obj):
    plan_codes = {}
    for addonFamily in obj['addonsFamily']:
        for addon in addonFamily['addons']:
            if 'addonsFamily' in addon['plan']:
                plan_codes = plan_codes | get_addon_families(addon['plan'])
            
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
            
            if item['price_default'] > 0 and 'hourly' not in item['family']:
                plan_codes[addon['plan']['planCode']] = item
    return plan_codes

def get_backup_options(pcc_plan_codes):
    managed_backup = list(filter(lambda x: 'backup' in x['family'] and 'legacy' not in x['invoiceName'], dict.values(pcc_plan_codes)))
    for m in managed_backup:
        size, plan = m['invoiceName'].split('-')[-1], m['invoiceName'].split('-')[-2]
        m['description'] = f"{BACKUP_DESCRIPTION[plan]} - {BACKUP_SIZE[size]}"
    return managed_backup

def get_occ_options(sub='FR'):
    occ = get_json(f'https://www.ovh.com/engine/apiv6/order/catalog/public/ovhCloudConnect?ovhSubsidiary={sub}')
    plans = []
    for plan in occ['plans']:
        installPlan = list(filter(lambda x: x['description'] == "Frais d'installation", plan['pricings']))
        mPlan = map(lambda x: x['price'], filter(lambda x: x['description'] != "Frais d'installation", plan['pricings']))
        mPlan = sorted(list(mPlan))

        price = mPlan[-1] / 10**8
        assert price > 0
        plans.append({
            'invoiceName': plan['invoiceName'],
            'install_price': installPlan[0]['price'] / 10**8,
            'price': price,
        })
    return plans

def get_ip_lb(sub='FR'):
    lbs = get_json(f'https://www.ovh.com/engine/apiv6/order/catalog/public/ipLoadbalancing?ovhSubsidiary={sub}')
    plans = []

    for plan in lbs['addons']:
        mPlan = map(lambda x: x['price'], filter(lambda x: 'installation' not in x['description'].lower(), plan['pricings']))
        mPlan = sorted(list(mPlan))

        price = mPlan[-1]

        desc = 'Certificates'
        if 'lb1' in plan['planCode']:
            desc = 'IP LB - Pack 1'
        elif 'lb2' in plan['planCode']:
            desc = 'IP LB - Pack 2'
        elif 'dedicated' in plan['planCode']:
            desc = 'IP LB - Dedicated'
        assert price > 0

        plans.append({
            'invoiceName': desc + ' - ' + plan['invoiceName'],
            'price': price / 10 ** 8,
            'planCode': plan['planCode']
        })
    return plans

def get_ps(sub='FR'):
    ps = get_json(f'https://www.ovh.com/engine/apiv6/order/catalog/public/packsProfessionalServices?ovhSubsidiary={sub}')
    plans = []
    for plan in ps['plans']:
        mPlan = map(lambda x: x['price'], filter(lambda x: 'installation' not in x['description'].lower(), plan['pricings']))
        mPlan = sorted(list(mPlan))
        price = mPlan[-1]

        plans.append({
            'invoiceName': plan['invoiceName'],
            'price': price / 10 ** 8,
            'planCode': plan['planCode']
        })
    return plans

def parse_windows_licenses(plan_codes, list_of_cores):
    plans = filter(lambda x: x['family'] == 'windows-license' and 'veeam' not in x['invoiceName'].lower(), plan_codes)
    
    computed_plans = []
    for p in plans:
        for cores in list_of_cores:
            invoiceName = ' '.join(map(lambda x: x.capitalize(), p['invoiceName'].split('-')))
            computed_plans.append({
                'invoiceName': invoiceName + f' - {cores} Cores',
                'price': p['price_default']
            })
    return computed_plans

def get_pcc_ranges_and_windows_licenses(sub='FR'):
    # pcc_plans = get_json(f'https://www.ovh.com/engine/apiv6/order/catalog/formatted/privateCloud?ovhSubsidiary={sub}')
    pcc_plans = json.loads(open('privateCloud.json').read()) ## TODO use request
    plan_codes = get_addon_families(pcc_plans['plans'][0])
    # print(*dict.values(plan_codes), sep='\n')
    
    cores_quandidates = set()
    ranges = []
    for cr in pcc_plans['commercialRanges']:
        if cr['name'] not in RANGES:
            continue

        packs = []
        hosts = []
        datastore = []
        public_ip = []
        regions = list(map(lambda dc: {'dc': dc['cityCode'], 'country': dc['countryCode']}, cr['datacenters']))

        managementFeePlanCode = cr['datacenters'][0]['managementFees']['planCode']
        if not cr['datacenters'][0]['hypervisors'][0]['orderable']:
            continue

        # List hosts spec
        for h in cr['datacenters'][0]['hypervisors'][0]['hosts']:
            if 'hourly' in h['name'].lower():
                continue

            cpuspec = h['specifications']['cpu']
            cpu_text = f"{cpuspec['model']} - {cpuspec['frequency']['value']} {cpuspec['frequency']['unit']} - {cpuspec['cores']} cores/{cpuspec['threads']} Threads"
            ram_text = f"{h['specifications']['memory']['ram']['value']} {h['specifications']['memory']['ram']['unit']}"

            # Pack & Host
            pack_datastore = plan_codes[h['storagesPack'][0]] # always X2 this value
            pack = {'invoiceName': f"Pack {h['name']}", 'description': f"2x Host {h['name']} \n  - {cpu_text}\n  - {ram_text} \n{STORAGE_PACK_DESCRIPTION}"}
            host = {'invoiceName': f"Pack {h['name']}", 'description': f"Additional Host {h['name']}\n{cpu_text}\n{ram_text}"} | plan_codes[h['planCode']]
            cores_quandidates.add(h['specifications']['cpu']['cores'])

            for conformity in CONFORMITY:
                if cr['name'] == 'essential' and conformity != 'default':
                    continue
                price_key = f"price_{conformity}"
                price_host = plan_codes[h['planCode']][price_key]
                
                # CRITICAL FORMULA
                price = pack_datastore[price_key] * 2 + plan_codes[managementFeePlanCode][price_key] + 2 * price_host 
                pack[price_key] = price

                if cr['name'] != 'essential' and conformity == 'default':
                    pack['price_snc'] = price * SNC_MARKUP
                    host['price_snc'] = price_host

            packs.append(pack)
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

        ranges.append({
            'hosts': hosts,
            'packs': packs,
            'public_ip': public_ip,
            'datastore': datastore,
            'managed_backups': get_backup_options(plan_codes),
            'regions': regions,
        })
    return ranges, parse_windows_licenses(cores_quandidates)


if __name__ == '__main__':
    sub = 'FR'
    
    ranges, windows_licences = get_pcc_ranges_and_windows_licenses(sub)
    print(ranges[0]['hosts'])
    # products['other']['occ'] = get_occ_options(sub)
    # products['other']['ip_lb'] = get_ip_lb(sub)
    # products['other']['ps'] = get_ps(sub)
    # print(*products['other']['ps'], sep='\n')

    # json.dump(data, open('tmp.json', 'w+'))
