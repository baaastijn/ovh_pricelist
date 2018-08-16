<?php

// Set the Subsidiary and by collateral, the currency
// Need to improve it to provide a list of Subs.
function set_sub(){
    // default sub = FR. MA, TN, DE, IT, .. available.
    $subsidiary = 'FR';
    if (isset($_GET['sub'])) {
        $subsidiary = $_GET['sub'];
    }
    return $subsidiary;
}

// CURL GET call to retrive the product catalog
// Since the API call could be long, we cache the output for a 10 minutes duration
function get_from($url, $sub) {
    
    // starting the cache, different one for each subsidiary (due to prices)
    $cache = 'cache/ovh_'.$sub.'.json';
    $expire = time() -60*10 ; // Expiry time = now - 10 minutes

    // If the cache exists, we return the cached JSON
    if(file_exists($cache) && filemtime($cache) > $expire)
    {
            $result = file_get_contents($cache);
            //convert JSON data back to PHP array
            return json_decode($result, true);            
    }
    // If the cache does NOT exist, we CURL GET the API then put the result in cache
    else
    {
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

            file_put_contents($cache, $result) ; // we cache the result in a new file

            //convert JSON data back to PHP array and return it
            return json_decode($result, true);
    }

}

// Find the cache time update to show it on the frontpage
function cache_time($sub){
    
    $cache = 'cache/ovh_'.$sub.'.json';
    date_default_timezone_set('Europe/Paris');
    
    if(file_exists($cache)) {
        $update = "Last modified: ".date("F d Y H:i:s",filemtime($cache));
    }
    else {
        $update = "Last modified: unknown"; 
    }

    return $update;
}


// Check availabilities for the whole json
function availability_parsing() {
    $result = file_get_contents("https://www.ovh.com/engine/api/dedicated/server/availabilities?country=fr".$sub);
    $json = json_decode($result, true); 
    
    $i = 0;
    $availability = array();
    
    // Dirty way to have an exploitable availability array. the source JSON contain to many dimensions, too many loops to look into.
    // here we flatten it, generating for example 1801eg04-gra-24H
    foreach($json as $item){
        foreach($item['datacenters'] as $datacenter) {
            $availability[$i] =  array(
                'product' => $item['hardware']."-".$datacenter['datacenter'],
                'availability' => $datacenter['availability']);
            $i++;
        }  
    };
    return $availability;    
}

// Set the currency for the prices informations.
function set_currency($json) {
    // Set the currency symbol found inside the JSON
    $currency = $json['metadatas']['currency']['symbol']; 
    return $currency;
}
    
// Parse the API results to retrieve the useful informations
function parse($subsidiary) {
    //retrieve availabilities
    $avail = availability_parsing();

    // Retrieve the Availables products from OVH API
    $json = get_from('order/catalog/formatted/dedicated?ovhSubsidiary=', $subsidiary);
    
    // Set the currency by analyzing the JSON metadatas
    $currency = set_currency($json);
    
    // Parse the API result line by line
    foreach($json['products'] as $item) {        
        // Remove some false positive inside the API, we check if CPU info is at least here
        if ($item['specifications']['cpu']['model'] != "") {

            // Storage generation
            if ( $item['specifications']['disks']['0']['number'] != ""){
                $storage = $item['specifications']['disks']['0']['number'] ." x ". ($item['specifications']['disks']['0']['size']/1000) ." TB ". $item['specifications']['disks']['0']['type'] ;
                $total_storage = $item['specifications']['disks']['0']['number'] * $item['specifications']['disks']['0']['size']/1000;
            }
            else {
                $storage = "Custom"; 
                $total_storage = 10000000;
            }

            // Create an array with all the data
            // 1 reference can be in multiple DC, need to check every DC
            
            foreach($item['datacenters'] as $dc) {
                // We also need to remove FR datacenter which is the aggregation of SBG+RBX+GRA
                if ($dc != "fr"){       
                    // flag image generation
                    $flag = "flag-".$dc.".png"; 
                    
                    // Availability generation
                    // looking for the right key
                    $key = array_search($item['code'].'-'.$dc, array_column($avail, 'product')) ;
                    // grabbing the availability key
                    $availability =  $avail[$key]['availability'];

                    $portfolio[] = array(
                        'dc' => $dc,
                        'flag' => $flag,
                        'family' => $item['family'],
                        'name' => $item['invoiceName'],
                        'api_name' => $item['code'],
                        'cpu' => $item['specifications']['cpu']['brand']." ".$item['specifications']['cpu']['model']." ".$item['specifications']['cpu']['frequency'] ."GHz",
                        'memory' => $item['specifications']['memory']['size']." GB",
                        'storage' => $storage ,
                        'total_storage' => $total_storage ,
                        'traffic' => $item['specifications']['network']['outgoing'],
                        'public_network' => ($item['specifications']['network']['outgoing']/1000),
                        'private_network' => ($item['specifications']['network']['privateBandwidth']/1000000),
                        'price' => $item['prices']['default']['renew']['value']." ".$currency,
                        'webpage' => "https://www.ovh.com/world/dedicated-servers/".$item['family']."/".$item['code'].".xml",
                        'availability' => $availability
                    ); 
                    
                    $i = 0;
                    foreach($item['derivatives'] as $derivatives) {
                        $portfolio[] = array(
                            'dc' => $dc,
                            'flag' => $flag,
                            'family' => $item['family'],
                            'name' => $item['invoiceName'],
                            'api_name' => $item['derivatives'][$i]['code'],
                            'cpu' => $item['specifications']['cpu']['brand']." ".$item['specifications']['cpu']['model']." ".$item['specifications']['cpu']['frequency'] ."GHz",
                            'memory' => $item['specifications']['memory']['size']." GB",
                            'storage' => $item['derivatives'][$i]['name'] ,
                            'traffic' => $item['specifications']['network']['outgoing'],
                            'public_network' => ($item['specifications']['network']['outgoing']/1000),
                            'private_network' => ($item['specifications']['network']['privateBandwidth']/1000000),
                            'price' => $item['prices']['default']['renew']['value']+$item['derivatives'][$i]['price']['value']." ".$currency,
                            'webpage' => "https://www.ovh.com/world/dedicated-servers/".$item['family']."/".$item['code'].".xml",
                            'availability' => $availability
                        );
                        $i++;
                    }
                }
  
                
            }
     
        }

    }
    
return $portfolio;
}

?>  