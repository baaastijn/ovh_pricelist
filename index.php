<!DOCTYPE html>
<html lang="en">
<?php
// include the PHP functions
include('functions.php');

// Set of the Subsidiary, useful for the currencies
$subsidiary = set_sub();

// Parse the API result line by line
$portfolio = parse($subsidiary);

?>
<head>
    <!-- Global site tag (gtag.js) - Google Analytics -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=UA-120246315-1"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());

      gtag('config', 'UA-120246315-1');
    </script>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <title>OVH Dedicated Servers pricelist</title>
    <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/v/bs4-4.1.1/jq-3.3.1/jszip-2.5.0/dt-1.10.18/b-1.5.2/b-colvis-1.5.2/b-html5-1.5.2/b-print-1.5.2/fh-3.1.4/rg-1.0.3/sl-1.2.6/datatables.min.css"/>
    <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.1.32/pdfmake.min.js"></script>
    <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.1.32/vfs_fonts.js"></script>
    <script type="text/javascript" src="https://cdn.datatables.net/v/bs4-4.1.1/jq-3.3.1/jszip-2.5.0/dt-1.10.18/b-1.5.2/b-colvis-1.5.2/b-html5-1.5.2/b-print-1.5.2/fh-3.1.4/rg-1.0.3/sl-1.2.6/datatables.min.js"></script>
    <!-- Custom CSS -->
    <link href="css/main.css" rel="stylesheet">
    <!-- Custom JS -->
    <script src="js/custom.js"></script>
</head>
<body class="container-fluid">

    <h1 class="text-center">OVH Dedicated Servers pricelist</h1> 
    <h6 class="text-center"><?php echo cache_time($subsidiary); ?></h6> 
    <table id='sd' class='table table-striped table-hover table-sm' style='width:100%'>
        <thead>
            <tr>
                <th>Country / DC</th>
                <th>Family</th>
                <th>Name</th>
                <th>API Name</th>
                <th>CPU Model</th>
                <th>RAM</th>
                <th>Base storage</th>
                <th>Public network</th>
                <th>Private network</th>
                <th>Monthly price</th>
                <th>Availability</th>
                <th>Buy</th>
            </tr>
        </thead>
        <tbody>
            <?php foreach($portfolio as $item) { ?>
            <tr>
                <td data-search="<?php echo $item['dc'] ?>" data-order="<?php echo $item['dc'] ?>"><img src='<?php echo "img/".$item['flag'] ?>' alt='region' width="30"> <?php echo strtoupper($item['dc']); ?></td>
                <td><?php echo $item['family'] ?></td>
                <td><?php echo $item['name'] ?></td>
                <td><?php echo $item['api_name'] ?></td>
                <td><?php echo $item['cpu'] ?></td>
                <td data-order="<?php echo $item['memory'] ?>"><?php echo $item['memory'] ?></td>
                <td data-order="<?php echo $item['total_storage'] ?>"><?php echo $item['storage'] ?></td>
                <td data-order="<?php echo $item['public_network'] ?>"><?php echo $item['public_network'] ?> Mbps</td>
                <td data-order="<?php echo $item['private_network'] ?>"><?php echo $item['private_network'] ?> Gbps</td>
                <td data-order="<?php echo $item['price'] ?>"><?php echo $item['price'] ?></td>
                <td><?php echo $item['availability'] ?></td>
                <td><a href="<?php echo $item['webpage'] ?>" target="_blank">Buy it</a></td>
            </tr>   
            <?php } ?>
        </tbody>
    </table>

    
    <div class="card">
        <div class="card-body bg-light">
        <p><strong>Why ?</strong> Table view of a product portfolio could be useful. Also, I wanted to play with OVH API and Datatables.net.</p>
        <p><strong>Who ?</strong> Initiated by <a href="https://www.twitter.com/BastienOVH" target="_blank">@BastienOVH</a>.</p>
        <p><strong>How ?</strong> It's a PoC. I dirty-coded a Curl call to api.ovh.com to retrieve the data then I parse it in PHP, and build a sexy table with Datatables.net. <a href="https://github.com/baaastijn/ovh_pricelist" target="_blank">Contribute on Github !</a></p>
        <p class="bg-warning"><strong>Warning</strong> This site is not maintained by or affiliated with OVH. The data shown is not guaranteed to be accurate or current. Please report issues you see on Github. </p>
        <p><strong>Credentials</strong> Flags designed by Freepik from Flaticon.</p>
        </div>
    </div>

</body>
</html>
