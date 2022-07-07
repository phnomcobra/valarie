var drawQueue = function(resp) {
    queue = document.getElementById('queue');
    queue.innerHTML = '<table id="queueTable"></table>';

    var table = document.getElementById('queueTable');
    var row;

    for (var i in resp) {
        row = table.insertRow(-1);
        row.insertCell(-1).innerHTML = `<button type="button" onclick="cancelJob('${resp[i].jobuuid}')">cancel</button>`;
        row.insertCell(-1).innerHTML = resp[i].runtimestring;
        row.insertCell(-1).innerHTML = resp[i].name;
    }
}

var updateQueueState = function () {
    $.ajax({
        'url' : 'procedure/get_queue_grid',
        'method': 'POST',
        'dataType' : 'json',
        'success' : function(resp) {
            drawQueue(resp);
        }
    });
}

var cancelJob = function (jobuuid) {
    $.ajax({
        'url' : 'procedure/cancel_job',
        'dataType' : 'json',
        'method': 'POST',
        'data' : {
            'jobuuid' : jobuuid,
        }
    });
}