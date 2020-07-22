var drawQueue = function(resp) {
    queue = document.getElementById('queue');
    queue.innerHTML = '<table id="queueTable"></table>';
    
    var table = document.getElementById('queueTable');
    var row;
    
    for(var i in resp) {
        row = table.insertRow(-1);
        row.insertCell(-1).innerHTML = resp[i].name;
        row.insertCell(-1).innerHTML = resp[i].hostname;
        row.insertCell(-1).innerHTML = resp[i].status;
        row.insertCell(-1).innerHTML = resp[i].runtime;
        row.insertCell(-1).innerHTML = `${Math.round(resp[i].progress * 100)}%`;
    }
}

var updateQueueState = function() {
    $.ajax({
        'url' : 'procedure/ajax_get_queue_grid',
        'method': 'POST',
        'dataType' : 'json',
        'success' : function(resp) {
            drawQueue(resp);
        }
    });
}
