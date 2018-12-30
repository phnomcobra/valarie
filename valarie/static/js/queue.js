var drawQueue = function(resp) {
    queue = document.getElementById('queue');
    queue.innerHTML = '<table class="table" id="queueTable"></table>';
    
    var table = document.getElementById('queueTable');
    var row;
    var cell;
    
    row = table.insertRow(-1);
    cell = row.insertCell(-1);
    cell.innerHTML = '<b>Procedure</b>';
        
    cell = row.insertCell(-1);
    cell.innerHTML = '<b>Host</b>';

    cell = row.insertCell(-1);
    cell.innerHTML = '<b>Progress</b>';
    
    var count = 0;
    for(var i in resp) {
        count++;
        
        row = table.insertRow(-1);
        cell = row.insertCell(-1);
        cell.innerHTML = resp[i].name;
        
        cell = row.insertCell(-1);
        cell.innerHTML = resp[i].host;

        cell = row.insertCell(-1);
        cell.innerHTML = Math.round(resp[i].progress * 100.0) + '%';
    }
    
    if(count == 0)
        $('.nav-tabs a[href="#inventoryContainer"]').tab('show');
    
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