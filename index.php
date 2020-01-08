<!DOCTYPE html>
<html lang="en">
<?php
// Include the PHP functions
include('functions.php');

// Set of the subsidiary, useful for the prices 
$subsidiary = set_sub();

// Parse the API result line by line
$plans = parse_plans($subsidiary);
    
// Get the currency code
$currency = get_currency($plans);
?>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <title>OVHcloud dedicated servers pricelist</title>
    <!-- Global site tag (gtag.js) - Google Analytics -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=UA-120246315-1"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      gtag('config', 'UA-120246315-1');
    </script>
    <!-- Datatables.net scripts -->
    <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/v/bs4-4.1.1/jq-3.3.1/jszip-2.5.0/dt-1.10.20/b-1.6.1/b-colvis-1.6.1/b-html5-1.6.1/b-print-1.6.1/cr-1.5.2/fh-3.1.6/kt-2.5.1/r-2.2.3/rg-1.1.1/sc-2.0.1/sl-1.3.1/datatables.min.css"/>
    <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.1.36/pdfmake.min.js"></script>
    <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.1.36/vfs_fonts.js"></script>
    <script type="text/javascript" src="https://cdn.datatables.net/v/bs4-4.1.1/jq-3.3.1/jszip-2.5.0/dt-1.10.20/b-1.6.1/b-colvis-1.6.1/b-html5-1.6.1/b-print-1.6.1/cr-1.5.2/fh-3.1.6/kt-2.5.1/r-2.2.3/rg-1.1.1/sc-2.0.1/sl-1.3.1/datatables.min.js"></script>
    <!-- Github button -->
    <script async defer src="https://buttons.github.io/buttons.js"></script>
    <!-- Custom CSS -->
    <link href="css/main.css" rel="stylesheet">
    <!-- Custom JS -->
    <script src="js/custom.js"></script>
</head>
<body class="container-fluid">

    <div class="row">
        <div class="col-9">
            <h1>OVHcloud dedicated servers pricelist</h1>
        </div>
        <div class="col-3">
            <span class="float-right">
                <a href="https://twitter.com/BastienOVH?ref_src=twsrc%5Etfw" class="twitter-follow-button" data-show-count="false">Follow @BastienOVH</a><script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
                <a class="github-button" href="https://github.com/baaastijn/ovh_pricelist/issues" data-color-scheme="no-preference: light; light: light; dark: dark;" data-show-count="true" aria-label="Issue baaastijn/ovh_pricelist on GitHub">Issue</a>
                <h6><span class="badge badge-secondary"><?php echo get_cache_time($subsidiary); ?></span></h6>
            </span>

        </div>
    </div>
    
    <div class="row">
        <div class="col">
            <div class="text">
                <p><?php list_subs() ?> /</p>
                <p class="text-warning"><strong>Warning:</strong> This site is not maintained by or affiliated with OVHcloud. The data shown is not guaranteed to be accurate or current. Please report issues you see on Github. </p>
                <p>Pricelist generated via OVHcloud API. Some highly customizable ranges like HG are not fully shown here, neither Kimsufi nor SoyouStart.</p>
                <p>You can also find here generated <a target="_blank" href="<?php echo "cache/ovhcloud_servers_pricelist_".$subsidiary.".json"; ?>">pricelist JSON</a>, and <a target="_blank" href="https://github.com/baaastijn/ovh_pricelist/">source code on Github</a>.</p>
            </div>
            <hr/>
            <table id='sd' class='table table-striped table-hover table-bordered table-sm display compact' style='width:100%'>
                <thead class="thead-dark">
                    <tr>
                        <th>Country / DC</th>
                        <th>Range</th>
                        <th>Name</th>
                        <th>API Name</th>
                        <th>FQN</th>
                        <th>CPU model</th>
                        <th>CPU cores</th>
                        <th>CPU threads</th>
                        <th>CPU clock speed (GHz)</th>
                        <th>CPU score</th>
                        <th>RAM summary</th>
                        <th>RAM size (GB)</th>
                        <th>RAM clock speed (GHz)</th>
                        <th>RAM type</th>
                        <th>Storage summary</th>
                        <th>Storage RAID type</th>
                        <th>Storage total size</th>
                        <th>Disk #1 amount</th>
                        <th>Disk #1 capacity</th>
                        <th>Disk #1 techno</th>
                        <th>Disk #2 amount</th>
                        <th>Disk #2 capacity</th>
                        <th>Disk #2 techno</th>
                        <th>Storage price per GB (<?php echo $currency; ?>)</th>
                        <th>Public Network</th>
                        <th>Private Network</th>
                        <th>Frame size</th>
                        <th>Frame model</th>
                        <th>Monthly price (<?php echo $currency; ?>)</th>
                        <th>Availability</th>
                        <th>Buy</th>
                    </tr>
                </thead>
                <tbody>
                    <?php
                    foreach($plans as $item) {
                        if ( isset($item['availabilities']) ) {
                             foreach($item['availabilities'] as $availability){
                    ?>
                        <tr>
                            <td data-search="<?php echo $availability['datacenter'] ?>" data-order="<?php echo $availability['datacenter'] ?>">
                                <img src='<?php echo "img/flag-".$availability['datacenter'].".png" ?>' alt='region' width="30"> <?php echo strtoupper($availability['datacenter']); ?>
                            </td>
                            <td><?php echo strtoupper($item['range']) ?></td>
                            <td><?php echo $item['invoiceName'] ?></td>
                            <td><?php echo $item['planCode'] ?></td>
                            <td><?php echo $item['fqn'] ?></td>
                            <td><?php echo $item['cpu']['brand']." ".$item['cpu']['model'] ?></td>
                            <td><?php echo $item['cpu']['cores'] ?></td>
                            <td><?php echo $item['cpu']['threads'] ?></td>
                            <td><?php echo $item['cpu']['frequency'] ?></td>
                            <td><?php echo $item['cpu']['score'] ?></td>
                            <td><?php echo $item['memory']['invoiceName'] ?></td>
                            <td><?php echo $item['memory']['specifications']['size'] ?></td>
                            <td><?php echo $item['memory']['specifications']['frequency'] ?></td>
                            <td><?php echo $item['memory']['specifications']['ramType'] ?></td>
                            <td><?php echo $item['storageSpecs']['invoiceName'] ?></td>
                            <td><?php echo $item['storageSpecs']['specifications']['raid'] ?></td>
                            <td><?php
                                // You can have 1 or 2 disks. If second disk exist, we sum the amount of GB.
                                if ($item['storageSpecs']['specifications']['disks'][1]['number'] != '') {
                                $storage_amount = ($item['storageSpecs']['specifications']['disks'][0]['number'] * $item['storageSpecs']['specifications']['disks'][0]['capacity'] + $item['storageSpecs']['specifications']['disks'][1]['number'] * $item['storageSpecs']['specifications']['disks'][1]['capacity']);
                                } else {
                                $storage_amount = $item['storageSpecs']['specifications']['disks'][0]['number'] * $item['storageSpecs']['specifications']['disks'][0]['capacity'];
                                };
                                echo $storage_amount; ?>
                            </td>
                            <td><?php echo $item['storageSpecs']['specifications']['disks'][0]['number'] ?></td>
                            <td><?php echo $item['storageSpecs']['specifications']['disks'][0]['capacity'] ?></td>
                            <td><?php echo $item['storageSpecs']['specifications']['disks'][0]['technology'] ?></td>
                            <td><?php echo $item['storageSpecs']['specifications']['disks'][1]['number'] ?></td>
                            <td><?php echo $item['storageSpecs']['specifications']['disks'][1]['capacity'] ?></td>
                            <td><?php echo $item['storageSpecs']['specifications']['disks'][1]['technology'] ?></td>
                            <td><?php $ratio = $item['price'] / $storage_amount ; echo round($ratio,5);  ?></td>
                            <td>see website</td>
                            <td>see website</td>
                            <td><?php echo $item['frame']['size'] ?></td>
                            <td><?php echo $item['frame']['model'] ?></td>
                            <td><?php echo $item['price'] ?></td>
                            <td><?php echo $availability['availability'] ?></td>
                            <td><?php 

                                if(in_array($item['range'], array('rise', 'advance', 'infrastructure', 'fs'))){
                                    ?>
                                        <a href="<?php echo 'https://www.ovh.com/fr/serveurs_dedies/'.strtolower($item['range']).'/'.strtolower($item['invoiceName']) ?>" target="_blank">Buy</a>
                                    <?php
                                }
                                else{
                                    ?>
                                    <a href="https://www.ovh.com/world/dedicated-servers/" target="_blank">See options</a>
                                    <?php
                                };
                                ?>
                            </td>
                        </tr>
                    <?php
                            }
                        }
                    } ?>
                </tbody>
            </table>

            <div class="card">
                <div class="card-body bg-light">
                <p>Project initiated by <a href="https://www.twitter.com/BastienOVH" target="_blank">@BastienOVH</a>, with EC2instance.info as an inspiration.</p>
                <p><strong>Credentials:</strong> Flags designed by Freepik from Flaticon.</p>
                </div>
            </div>
        </div>
    </div>


</body>
</html>
