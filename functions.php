<?php

// Set the Subsidiary for prices.
function set_sub(){
    return (isset($_GET['sub'])) ? $_GET['sub'] : 'FR';
}

// list subs
function list_subs(){
    $subs = array('CZ','DE','ES','FI','FR','GB','IE','IT','LT','MA','NL','PL','PT','SN','TN');
    foreach($subs as $sub){
        echo '/ <a href="/?sub='.$sub.'">'.$sub.'</a> ';
    }
}


// CURL GET call to retrieve OVHcloud API results
function get_from($url, $sub){
    $ch = curl_init();
    //configure CURL
    // NB : it's dirty, should use OVH wrapper instead, but it's ok for a PoC. Go to https://github.com/ovh/php-ovh for more infos.
    curl_setopt_array($ch, array(
        CURLOPT_URL => 'https://api.ovh.com/1.0/'.$url.$sub,
        CURLOPT_HTTPHEADER => array('Content-type: application/json'),
        CURLOPT_SSL_VERIFYPEER => 0,
        CURLOPT_RETURNTRANSFER => true
    ));
    $result = curl_exec($ch);
    curl_close($ch);

    //convert JSON data back to PHP array and return it
    return json_decode($result, true);
}

// GET previously generated JSON in cache. Since the API call could be long, we cache the generated JSON output for a 10 minutes duration
// It requires a "cache" folder with read-write access
function get_json_cache($sub){
    
    // starting the cache, different one for each subsidiary (due to prices)
    $cache = 'cache/ovhcloud_servers_pricelist_'.$sub.'.json';
    $expire = time() - 60*60*24 ; // Expiry time in seconds = now - 24 hours

    // If the cache exists, we return the cached JSON
    if(file_exists($cache) && filemtime($cache) > $expire)
    {
            $result = file_get_contents($cache);
            //convert JSON data back to PHP array
            return json_decode($result, true);
    }
    // If the cache does NOT exist, we return null
    else
    {
        return null;
    }

}

// Find the cache time update to show it on the frontpage.
function get_cache_time($sub){
    
    $cache = 'cache/ovhcloud_servers_pricelist_'.$sub.'.json';
    date_default_timezone_set('Europe/Paris');
    
    if(file_exists($cache)) {
        $update = "Last updated: ".date("F d Y H:i:s",filemtime($cache));
    }
    else {
        $update = "Last updated: unknown";
    }

    return $update;
}


// Set the currency for the prices informations.
function get_currency($json){
    // Get the currency found inside the JSON
    $currency = json[-1];
    return $currency;
}


function parse_plans($subsidiary){
    // Retrieve JSON also for the ECO ranges (Kimsufi / SoYouStart)
    $json_eco = get_from('order/catalog/public/eco?ovhSubsidiary=', $subsidiary);
    $dataset_eco = build_dataset($subsidiary, $json_eco);


    // Retrieve JSON for the products, plans, addons, pricings from OVH API
    $json_baremetal = get_from('order/catalog/public/baremetalServers?ovhSubsidiary=', $subsidiary);   
    $dataset_baremetal = build_dataset($subsidiary, $json_baremetal);
    $dataset_final = array_merge($dataset_eco, $dataset_baremetal);  
        
    // Store the array in a JSON file
    file_put_contents('cache/ovhcloud_servers_pricelist_'.$subsidiary.'.json',json_encode($dataset_final));

    return $dataset_final;
}

// Parse
function build_dataset($subsidiary,$json){
    // before everything, we check if we have the a JSON in cache.
    $cached_plans = get_json_cache($subsidiary);
    if (!empty($cached_plans)) {
        return $cached_plans;
    }
    else {        
        // Store the currency code
        $currency = $json['locale']['currencyCode'];

        // Main loop. We parse all plans and aggregate informations such as prices and technical specifications
        foreach($json['plans'] as $item){


            // MEMORY + STORAGE addons listing
            // 1 plan can contain multiple storage and memory addons. So we retrieve the addons lists here.
            // Few plans also contains 1 x system-storage (like SCALE and HG     range)
            // They does not contain technical specifications, we need to retrieve them in another loop.
            foreach($item['addonFamilies'] as $addon_family){
                if($addon_family['name'] == 'memory'){
                    $memory_addons = $addon_family['addons'];
                }
                if($addon_family['name'] == 'storage' OR $addon_family['name'] == 'disk'){
                    $storage_addons = $addon_family['addons'];
                }
                if($addon_family['name'] == 'system-storage'){
                    $system_storage = $addon_family['addons'];
                    //print_r($system_storage);
                }
                else{
                    unset($system_storage);
                }
            }


            // CPU + FRAME + RANGE informations
            // These informations are stored in the "products" part of the JSON, not in the "plans".
            $products_specs[] = array();
            foreach($json['products'] as $prod){
                // we storage cpu, frame, range informations
                if($prod['name'] == $item['planCode'] OR $prod['name'] == $item['product']) {
                    $tech_specs = $prod['blobs']['technical']['server'];
                }
                // we also store exact specification of memory and storage addons
                $products_specs[$prod['name']] = array(
                    'name' => $prod['name'],
                    'specs' => $prod['blobs']['technical']
                );
            }

            // each server has multiples pricings (no commitment, 12 or 24 months commitment, etc)
            // i chose to display only pricing with no commitment
            // Excel for HGR range where the minimum period is 6 months commitment
            foreach($item['pricings'] as $pricing){
                if($pricing['commitment'] == 0 && $pricing['mode'] == 'default' && $pricing['interval'] == 1 ){
                    $server_price = $pricing['price'] / 100000000;
                }
            }


            // ADDONS LOOP
            // to generate a clean HTML table, I need 1 array per server derivative. If a server has 2 memory addons and 8 storage addons, I want to generate 16 lines.
            // It's a choice. I want a table with all the derivatives, directly.
            if (!is_array($memory_addons) && !is_object($memory_addons)) {
                continue;
            }
            foreach($memory_addons as $memory_addon){
                foreach($storage_addons as $storage_addon){


                    // ADDONS TECHNICAL SPECIFICATIONS + PRICES
                    // We retrieved addons listings before, now we retrieve their pricings and product name
                    foreach($json['addons'] as $addon){
                        foreach($addon['pricings'] as $pricing){
                            if($pricing['commitment'] == 0 && $pricing['mode'] == 'default' && $pricing['interval'] == 1 ){
                                $addon_price = $pricing['price'] / 100000000;
                            }
                        }
                        if($addon['planCode'] == $storage_addon){
                            $storage_specs = array(
                                'planCode' => $addon['planCode'],
                                'product' => $addon['product'],
                                'invoiceName' => $addon['invoiceName'],
                                'specifications' => $products_specs[$addon['product']]['specs']['storage'],
                                'price' => $addon_price
                            );
                        }
                        if($addon['planCode'] == $memory_addon){
                            $memory_specs = array(
                                'planCode' => $addon['planCode'],
                                'product' => $addon['product'],
                                'invoiceName' => $addon['invoiceName'],
                                'specifications' => $products_specs[$addon['product']]['specs']['memory'],
                                'price' => $addon_price
                            );
                        }
                        if($addon['planCode'] == $system_storage[0]){
                            $system_storage = $addon['product'];
                            //print($system_storage);
                        }
                    }

                    // AVAILABILITIES
                    // Only few ranges such as SCALE and HG have a system_storage defined in the fqn. Others don't.
                    if (!empty($system_storage)){
                        $fqn = $item['planCode'].".".$memory_specs['product'].".".$storage_specs['product'].".".$system_storage;
                    }
                    else{
                        $fqn = $item['planCode'].".".$memory_specs['product'].".".$storage_specs['product'];
                    }

                    // Aggregation of all informations in a array
                    // This array will be the main source to generate HTML Table in index.php
                    // 1 plan = 1 product to show. approx 1300 entries
                    $plans[] = array(
                        'planCode' => $item['planCode'],
                        'product' => $item['product'],
                        'invoiceName' => $item['invoiceName'],
                        'fqn' => $fqn,
                        'memory' => $memory_specs,
                        'storageSpecs' => $storage_specs,
                        'cpu' => $tech_specs['cpu'],
                        'range' => $tech_specs['range'],
                        'frame' => $tech_specs['frame'],
                        'setupfee' => $server_price,
                        'price' => $server_price + $storage_specs['price'] + $memory_specs['price']
                    );

                }
            } // END OF ADDONS LOOP
        } // END OF MAIN LOOP
        
        // Store the currency at the end of the JSON
        $plans[] = $currency;
                
        // return the array to the main page to generate HTML table
        return $plans;
    } // END of else

}
?>