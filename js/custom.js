$(document).ready(function() {

    
    var mytable = $('#sd').DataTable( {
        orderCellsTop: true,
        ordering: true,
        "order": [[ 28, "asc" ]],
        "bPaginate": true,
        "bLengthChange": true,
        "pageLength": 600,
        "select": true,
        "fixedHeader": true,
        "sPaginationType": "full_numbers",
        "dom": 'Bfrtip',
        stateSave: false,
        searching: true,
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
    

    
} );

