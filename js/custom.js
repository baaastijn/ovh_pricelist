$(document).ready(function() {
    
    
    // create a second header row
    $("#sd thead tr").clone(true).appendTo("#sd thead");
    // Setup - add a text input to each footer cell
    $('#sd thead tr:eq(1) th').each( function () {
        var title = $(this).text();
        $(this).html( '<input type="text" placeholder="Search" class="column_search" />' );
    } );
    
    var mytable = $('#sd').DataTable( {
        orderCellsTop: true,
        ordering: true,
        "order": [[ 25, "asc" ]],
        paging: false,
        "bLengthChange": false,
        "pageLength": 1500,
        "select": true,
        "fixedHeader": true,
        "sPaginationType": "full_numbers",
        "dom": 'Bfrtip',
        stateSave : false,
        rowGroup: {
            dataSrc: 2
        },
        "columnDefs": [
            {
                "targets": [3,4,8,11,12,13,15,17,18,19,20,21,22,23,24,25,26,27],
                "visible": false
            }
        ],
        "buttons": [

            {
        extend: 'collection',
        text: 'Datacenter Selection',
        buttons: [
            {
                text: 'ALL countries',
                action: function ( e, dt, node, config ) {
                    dt.column( 0 ).search('').draw();
                }
            },
            {
                text: 'Canada (BHS)',
                action: function ( e, dt, node, config ) {
                    dt.column( 0 ).search("^"+"bhs"+"$", true, false).draw();
                }
            },
            {
                text: 'France - North (GRA)',
                action: function ( e, dt, node, config ) {
                    dt.column( 0 ).search("^"+"gra"+"$", true, false).draw();
                }
            },
            {
                text: 'France - North (RBX)',
                action: function ( e, dt, node, config ) {
                    dt.column( 0 ).search("^"+"rbx"+"$", true, false).draw();
                }
            },
            {
                text: 'France - East (SBG)',
                action: function ( e, dt, node, config ) {
                    dt.column( 0 ).search("^"+"sbg"+"$", true, false).draw();
                }
            },
            {
                text: 'Germany (FRA)',
                action: function ( e, dt, node, config ) {
                    dt.column( 0 ).search("^"+"fra"+"$", true, false).draw();
                }
            },
            {
                text: 'Poland (WAW)',
                action: function ( e, dt, node, config ) {
                    dt.column( 0 ).search("^"+"waw"+"$", true, false).draw();
                }
            },
            {
                text: 'Singapore (SGP)',
                action: function ( e, dt, node, config ) {
                    dt.column( 0 ).search("^"+"sgp"+"$", true, false).draw();
                }
            },
            {
                text: 'Sydney (SYD)',
                action: function ( e, dt, node, config ) {
                    dt.column( 0 ).search("^"+"syd"+"$", true, false).draw();
                }
            },
            {
                text: 'United Kingdom (LON)',
                action: function ( e, dt, node, config ) {
                    dt.column( 0 ).search("^"+"lon"+"$", true, false).draw();
                }
            },
        ]
    },
            'colvis','copy', 'excel', 'pdf', 'csv'
        ]
    } );
    
    // Apply the search
    $( '#sd thead'  ).on( 'keyup', ".column_search",function () {
   
        mytable
            .column( $(this).parent().index() + ':visible' )
            .search( this.value )
            .draw();
    } );

    
} );

