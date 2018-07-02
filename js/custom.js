$(document).ready(function() {
    $('#sd').DataTable( {
        ordering: true,
        "order": [[ 9, "asc" ]],
        paging: false,
        "bLengthChange": false,
        "pageLength": 500,
        "select": true,
        "fixedHeader": true,
        "sPaginationType": "full_numbers",
        "dom": 'Bfrtip',
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

