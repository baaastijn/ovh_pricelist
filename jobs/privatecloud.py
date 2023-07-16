import json
from utils import *
import re

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
                if '_eu' in addon['plan']['planCode'] and addon['plan']['planCode'].replace('_eu', '') not in plan_codes:
                    plan_codes[addon['plan']['planCode'].replace('_eu', '')] = item
                plan_codes[addon['plan']['planCode']] = item
    return plan_codes

def get_backup_options(pcc_plan_codes):
    managed_backup = list(filter(lambda x: 'backup' in x['family'] and 'legacy' not in x['invoiceName'], dict.values(pcc_plan_codes)))
    for m in managed_backup:
        size, plan = m['invoiceName'].split('-')[-1], m['invoiceName'].split('-')[-2]
        m['description'] = f"{BACKUP_DESCRIPTION[plan]} - {BACKUP_SIZE[size]}"
    return managed_backup

def get_occ_options(sub='FR'):
    occ = get_json(f'{get_base_api(sub)}/1.0/order/catalog/public/ovhCloudConnect?ovhSubsidiary={sub}')
    plans = []
    if 'plans' not in occ:
        return []
    for plan in occ['plans']:
        installPlan = list(filter(lambda x: x['description'] == "Frais d'installation", plan['pricings']))
        mPlan = map(lambda x: x['price'], filter(lambda x: x['description'] != "Frais d'installation", plan['pricings']))
        mPlan = sorted(list(mPlan))

        price = mPlan[-1] / 10**8
        assert price > 0
        plans.append({
            'invoiceName': plan['invoiceName'],
            'install_price': installPlan[0]['price'] / 10**8 if installPlan else 0,
            'price': price,
        })
    return plans

def get_ip_lb(sub='FR'):
    try:
        lbs = get_json(f'{get_base_api(sub)}/1.0/order/catalog/public/ipLoadbalancing?ovhSubsidiary={sub}')
    except urllib.error.HTTPError: # 404
        return []
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
    try:
        ps = get_json(f'{get_base_api(sub)}/1.0/order/catalog/public/packsProfessionalServices?ovhSubsidiary={sub}')
    except urllib.error.HTTPError: # 404
        return []
    plans = []
    for plan in ps['plans']:
        mPlan = map(lambda x: x['price'], filter(lambda x: 'installation' not in x['description'].lower(), plan['pricings']))
        mPlan = sorted(list(mPlan))
        price = mPlan[-1]

        plans.append({
            'invoiceName': plan['invoiceName'],
            'price': price / 10 ** 8,
            'installation': True
        })
    return plans

def parse_windows_licenses(plan_codes, list_of_cores):
    plans = filter(lambda x: x['family'] == 'windows-license' and 'veeam' not in x['invoiceName'].lower(), dict.values(plan_codes))
    
    computed_plans = []
    for p in plans:
        for cores in list_of_cores:
            invoiceName = ' '.join(map(lambda x: x.capitalize(), p['invoiceName'].split('-')))
            computed_plans.append({
                'invoiceName': invoiceName + f' - {cores} Cores',
                'price': p['price_default']
            })
    return computed_plans

def get_veeam_and_zerto_licenses(sub='FR'):
    if sub == 'DE':
        sub = 'en-ie'
    elif sub == 'US':
        sub = 'en'
    tries = [sub, f'en-{sub}', f'fr-{sub}']
    RE_PRICE = r'<span class="price-value">[\D]+([\d]+[,\.]?[\d]+).*<\/span>'
    for s in tries:
        veeam_price = 0
        zerto_price = 0
        try:
            veam_html = get_html(f'https://www.ovhcloud.com/{s.lower()}/storage-solutions/veeam-enterprise/')
            res = re.findall(RE_PRICE, veam_html)
            if bool(res):
                veeam_price = float(res[0].replace(',', '.'))

            zerto_html = get_html(f'https://www.ovhcloud.com/{s.lower()}/hosted-private-cloud/vmware/zerto/')
            res = re.findall(RE_PRICE, zerto_html)
            if bool(res):
                zerto_price = float(res[0].replace(',', '.'))
            break
        except urllib.error.HTTPError: # 404 not found
            veeam_price = 0
    # print(sub, veeam_price, zerto_price)
    return [{'invoiceName': 'Licence Veeam Entreprise plus - per VM', 'price': veeam_price}] if veeam_price > 0 else [], \
        [{'invoiceName': 'Zerto license - per VM', 'price': zerto_price}] if zerto_price > 0 else []

def get_pcc_ranges_and_windows_licenses(sub='FR'):
    pcc_plans = get_json(f'{get_base_api(sub)}/1.0/order/catalog/formatted/privateCloud?ovhSubsidiary={sub}')
    # pcc_plans = json.load(open('privateCloud-us.json'))
    print(f'{get_base_api(sub)}/1.0/order/catalog/formatted/privateCloud?ovhSubsidiary={sub}')

    plan_codes = {}
    for plans in pcc_plans['plans']:
        plan_codes |= get_addon_families(plans)
    # print(*dict.keys(plan_codes), sep='\n')

    cores_quandidates = set([10,6,8,20])

    ranges = {}
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
            if 'hourly' in h['name'].lower() or h['planCode'] not in plan_codes:
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
                
                # CRITICAL PRICING FORMULA FOR PACKS
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
                price['invoiceName'] = price['invoiceName'].replace('RIPE', '') if 'RIPE' in price['invoiceName'] else price['invoiceName'].replace('ARIN', '')
                ip_count = 2**(32 - int(price['invoiceName'].split('/')[-1]))
                price['description'] = f"{ip_count} Public IPs"
                public_ip.append(price)
            elif 'datastore' in price['invoiceName'].lower():
                price['description'] = f"Additional Datastore - {option['specifications']['type']} {option['specifications']['size']['value']} {option['specifications']['size']['unit']}"
                datastore.append(price)

        ranges[cr['name']] = {
            'hosts': hosts,
            'packs': packs,
            'public_ip': public_ip,
            'datastore': datastore,
            'managed_backups': get_backup_options(plan_codes),
            'regions': regions,
        }
    return ranges, parse_windows_licenses(plan_codes, cores_quandidates)


if __name__ == '__main__':
    for sub in SUBSIDIARIES:
        # price_stuct {'invoiceName', description, 'price_...'}
        products = {
            'locale': get_json(f'{get_base_api(sub)}/1.0/order/catalog/public/cloud?ovhSubsidiary={sub}')['locale'],
            'ranges': {}, # packs, hosts, datastore, public_ip, regions, managed_backup
            'other': {
                'occ': get_occ_options(sub),
                'ip_lb': get_ip_lb(sub),
                'windows_licence': [],
                'veeam_licence': [],
                'zerto_licence': [],
                'ps': []
            }
        }
        products['ranges'], products['other']['windows_licences'] = get_pcc_ranges_and_windows_licenses(sub)
        products['other']['ps'] = get_ps(sub)
        products['other']['veeam_license'], products['other']['zerto_license'] = get_veeam_and_zerto_licenses(sub)
        upload_gzip_json(products, f'privatecloud/{sub.lower()}.json', S3_BUCKET)
