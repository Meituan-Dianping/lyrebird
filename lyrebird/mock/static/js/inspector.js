var sio = io();
var table;
//
// Updates "Select all" control in a data table
//
function updateDataTableSelectAllCtrl(table) {
    var $table = table.table().node();
    var $chkbox_all = $('tbody input[type="checkbox"]', $table);
    var $chkbox_checked = $('tbody input[type="checkbox"]:checked', $table);
    var chkbox_select_all = $('thead input[name="select_all"]', $table).get(0);

    // If none of the checkboxes are checked
    if ($chkbox_checked.length === 0) {
        chkbox_select_all.checked = false;
        if ('indeterminate' in chkbox_select_all) {
            chkbox_select_all.indeterminate = false;
        }

        // If all of the checkboxes are checked
    } else if ($chkbox_checked.length === $chkbox_all.length) {
        chkbox_select_all.checked = true;
        if ('indeterminate' in chkbox_select_all) {
            chkbox_select_all.indeterminate = false;
        }

        // If some of the checkboxes are checked
    } else {
        chkbox_select_all.checked = true;
        if ('indeterminate' in chkbox_select_all) {
            chkbox_select_all.indeterminate = true;
        }
    }
}

$(document).ready(function () {
    // Array holding selected row IDs
    var rows_selected = [];
    table = $('#requests').DataTable({
        scrollY: 500,
        scrollCollapse: true,
        paging: false,
        ordering: false,
        searching: true,
        'ajax': {
            url: '/api/flow',
            dataSrc: ''
        },
        columns: [
            {
                'data': 'id',
                'searchable': false,
                'orderable': false,
                'width': '1%',
                'className': 'dt-body-center',
                'render': function (data) {
                    return '<input type="checkbox" name="id" value="' + data + '"></input>'
                }
            },
            {
                'data': 'response.code',
                'width': '1%'
            },
            {
                'data': 'response.mock',
                'width': '1%',
                'render': function (data) {
                    if (data === 'proxy') {
                        return '<span class="label label-default">proxy</span>'
                    } else {
                        return '<span class="label label-warning">mock</span>'
                    }
                }
            },
            {
                'data': 'request.method',
                'width': '1%'
            },
            {
                'data': 'request.url',
                'render': function (data) {
                    if (data.length > 120) {
                        return data.substring(0, 120) + ' ...'
                    } else {
                        return data
                    }
                }
            },
            {
                'data': 'id',
                'width': '1%',
                'render': function (data) {
                    return '<a class="btn btn-default" onclick="showDataDetail(\'' + data + '\')">Detail</a>'
                }
            }
        ],
        'order': [[1, 'asc']],
        'rowCallback': function (row, data, dataIndex) {
            // Get row ID
            var rowId = data.id;

            // If row ID is in the list of selected row IDs
            if ($.inArray(rowId, rows_selected) !== -1) {
                $(row).find('input[type="checkbox"]').prop('checked', true);
                $(row).addClass('selected');
            }
        }
    });
    sio.on('action', function (msg) {
        table.ajax.reload();
        console.info('OnEvent', msg)
    });
    // Handle click on checkbox
    $('#requests tbody').on('click', 'input[type="checkbox"]', function (e) {
        var $row = $(this).closest('tr');

        // Get row data
        var data = table.row($row).data();

        // Get row ID
        var rowId = data.id;

        // Determine whether row ID is in the list of selected row IDs
        var index = $.inArray(rowId, rows_selected);

        // If checkbox is checked and row ID is not in list of selected row IDs
        if (this.checked && index === -1) {
            rows_selected.push(rowId);

            // Otherwise, if checkbox is not checked and row ID is in list of selected row IDs
        } else if (!this.checked && index !== -1) {
            rows_selected.splice(index, 1);
        }

        if (this.checked) {
            $row.addClass('selected');
        } else {
            $row.removeClass('selected');
        }

        // Update state of "Select all" control
        updateDataTableSelectAllCtrl(table);

        // Prevent click event from propagating to parent
        e.stopPropagation();
    });

    // Handle click on table cells with checkboxes
    $('#requests').on('click', 'tbody td input[name="id"], thead th:first-child', function (e) {
        $(this).parent().find('input[type="checkbox"]').trigger('click');
    });

    // Handle click on "Select all" control
    $('thead input[name="select_all"]', table.table().container()).on('click', function (e) {
        if (this.checked) {
            $('#requests tbody input[type="checkbox"]:not(:checked)').trigger('click');
        } else {
            $('#requests tbody input[type="checkbox"]:checked').trigger('click');
        }

        // Prevent click event from propagating to parent
        e.stopPropagation();
    });

    // Handle table draw event
    table.on('draw', function () {
        // Update state of "Select all" control
        updateDataTableSelectAllCtrl(table);
    });

    // Handle form submission event
    $('#frm-example').on('submit', function (e) {
        var form = this;

        // Iterate over all selected checkboxes
        $.each(rows_selected, function (index, rowId) {
            // Create a hidden element
            $(form).append(
                $('<input>')
                    .attr('type', 'hidden')
                    .attr('name', 'id[]')
                    .val(rowId)
            );
        });
    });

});

function refreshRequestTable() {
    table.ajax.reload();
}

function showRecordEditor() {
    $.post('/api/flow', $('#req-form').serialize(), function (data) {
        $('#new-record-modal-data').val(JSON.stringify(data, null, 4))
        $('#new-record-modal').modal()
    })
}

function saveRecord() {
    $.post('/api/mock', $('#new-record-form').serialize(), function (data) {
        console.info('Add data group');
        console.info(data);

        $.post('/api/flow/save/as/' + $('#new-record-modal-name').val(), $('#req-form').serialize(), function (data) {
            console.debug(data)
        });
    });
    $('#new-record-modal').modal('hide')
}

function showDataDetail(id) {
    $.get('/api/flow/' + id, function (data) {
        var req = {
            url: data.request.url,
            method: data.request.method,
            headers: data.request.headers
        };
        var resp = {
            code: data.response.code,
            headers: data.response.headers
        };
        $('#data-detail-source').html('Data source : ' + resp.headers.lyrebird);
        $('#data-modal-req').JSONView((JSON.stringify(req, null, 4)));
        $('#data-modal-req-data').JSONView(JSON.stringify(data.request.data, null, 4));
        $('#data-modal-resp').JSONView(JSON.stringify(resp, null, 4));
        $('#data-modal-resp-data').JSONView(JSON.stringify(data.response.data, null, 4));
        $('#data-detail-modal').modal()
    })
}

function clearData() {
    $.ajax({
        url: '/api/flow',
        type: 'DELETE',
        success: function (data) {
            refreshRequestTable()
        }
    })
}