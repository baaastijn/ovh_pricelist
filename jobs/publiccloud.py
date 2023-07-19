from utils import *
import json
from datetime import datetime
import pandas as pd
import bs4
import re

EXCLUDE_FAMILY = [
    'option-dc-adp',
]

EXCLUDE_PRODUCTS = [
    'serco-asp-r2-256 monthly instance'
]

def get_cloud_prices(sub):
    # cloud = get_json(f'{get_base_api(sub)}/1.0/order/catalog/formatted/cloud?ovhSubsidiary={sub}')
    cloud = json.load(open('cloud.json'))
    families = next(filter(lambda x: x['invoiceName'] == 'Public Cloud Project', cloud['plans']))['addonsFamily']
    currency = cloud['plans'][0]['details']['pricings']['default'][0]['price']['currencyCode']

    rows = []
    for family in families:
        if family['family'] in EXCLUDE_FAMILY:
            continue
        for addon in family['addons']:
            for price in addon['plan']['details']['pricings']['default']:
                duration = price['description'].lower()
                invoiceName = addon['invoiceName'].replace(' on region #REGION#', '').replace(' on #REGION#', '')
                invoiceName = invoiceName.replace('Monthly usage for ', '')
                invoiceName = invoiceName.replace('Public Cloud Database', '').strip()
                if invoiceName in EXCLUDE_PRODUCTS:
                    continue
                
                if 'month' in duration:
                    duration = 'month'
                elif 'minute' in duration:
                    duration = 'minute'
                elif 'hour' in duration or 'consumption' in duration:
                    duration = 'hour'

                item = {
                    'family': family['family'],
                    'invoiceName': invoiceName,
                    'price': price['price']['value'],
                    'duration': duration
                }
                if item['price'] > 0 and not 'hour' in duration:
                    rows.append(item)
    return { 'currency': currency, 'catalog': rows, 'date': datetime.now().isoformat() }



COLUMNS_RENAME = {
    'Dedicated node(s)': 'node(s)',
    'Memory': 'RAM',
    'Usable storage': 'SSD',
    'vCore': 'vCPU'
}
def merge_columns(columns):
    merged_cols = []
    for cols in columns:
        if isinstance(cols, str) or len(cols) == 1:
            merged_cols = list(columns)
            break
        if 'unnamed' in cols[0].lower() or 'informations' in cols[0].lower():
            merged_cols.append(cols[1])
        else:
            merged_cols.append(cols[0])
    
    for i in range(len(merged_cols)):
        if merged_cols[i] in COLUMNS_RENAME:
            merged_cols[i] = COLUMNS_RENAME[merged_cols[i]]
    return merged_cols

def build_key_description(df, family, title):
    keys, descriptions = [], []
    if len(df.columns) < 2:
        return []
    for i, row in df.iterrows():
        desc = title.strip() + ' '
        key = ''
        if family == 'compute':
            desc = 'Linux Instance '

        for i in range(len(df.columns)):
            col = df.columns[i]
            if col == 'Name':
                name = row['Name'].strip()
                key = name.lower()
                if 'win-' in name:
                    desc = desc.replace('Linux', 'Windows')
                desc += f"{name} -"
                if family == 'databases':
                    key = f'{title} {name}'.lower().replace('™', '')
                elif family == 'storage' and 'volume' in name.lower(): # Volume Block Storage
                    print('HERE')
                    key = f'volume.{name.replace("Volume","").strip().replace(" ", "-")}'
                continue
            if pd.isna(row[col]) or '_' == row[col]:
                continue

            if family == 'databases' and col == 'SSD':
                ret = re.findall(r'From (.*?) to.+', row[col])
                desc += ' ' + ret[0] if bool(ret) else row[col] + f" {col},"
            else:
                desc += f" {row[col]} {col},"
        desc = re.sub(r'\s\s+', ' ', desc)[:-1].strip();
        keys.append(key)
        descriptions.append(desc)
    return keys, descriptions


def get_product_description():
    # html = get_html('https://www.ovhcloud.com/en/public-cloud/prices/#')
    html = open('/Users/tducrot/Downloads/pci.html').read()
    soup = bs4.BeautifulSoup(html, 'lxml')
    container = soup.css.select('#compute')[0].parent
    family, title, = '', ''
    keys, descriptions = [], []
    for div in container.find_all('div', recursive=False):
        if div.get('id'):
            family = div.get('id').strip()

        h3s = div.css.select('h3.public-cloud-prices-title')
        if bool(h3s):
            title = h3s[0].get_text().strip()
            try:
                dfs = pd.read_html(str(div))
                df = pd.concat(dfs)
                df.columns = merge_columns(df.columns)
                for col_to_drop in ['Price', 'Total price']:
                    if col_to_drop in df.columns:
                        df.drop(col_to_drop, axis=1, inplace=True)

                if family == 'compute':
                    win_df = df.copy()
                    win_df['Name'] = win_df['Name'].apply(lambda x: 'win-' + x)
                    df = pd.concat([df, win_df])
                
                k, d = build_key_description(df, family, title)
                keys += k
                descriptions += d
            except ValueError:
                pass
    
    return pd.DataFrame(zip(keys, descriptions), columns=['key', 'description'])

if __name__ == '__main__':
    sub = 'FR'
    
    # publiccloud = get_cloud_prices(sub)
    # print(*publiccloud['catalog'], sep='\n')

    df = get_product_description()
    pd.set_option('display.max_rows', 250)
    # print(df)

