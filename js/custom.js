$(document).ready(function() {

    
    var mytable = $('#sd').DataTable( {
        orderCellsTop: true,
        ordering: true,
        "order": [[ 1, "asc" ]],
        "bPaginate": true,
        "bLengthChange": true,
        "pageLength": 2000,
        "select": true,
        "fixedHeader": true,
        "sPaginationType": "full_numbers",
        "dom": 'Bfrtip',
        stateSave: false,
        searching: true,
        rowGroup: {
            dataSrc: 1
        },
        "columnDefs": [
            {
                "targets": [2,3,5,6,7,8,10,11,12,14,16,17,18,19,20,21,22,23,24,25,26],
                "visible": false
            }
        ],
        "buttons": [
            'colvis','copy', 'excel', 'pdf', 'csv'
        ]
    } );
    

    
} );

