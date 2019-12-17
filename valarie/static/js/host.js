var term;
var outputBuffer = '';
var sending = false;
var receiving = false;
var terminalTimerRunning = false;
var ttyuuid = null;

var editHost = function() {
    document.getElementById('body').innerHTML = '';
    document.getElementById('menuBarDynamic').innerHTML = '';
    
    document.title = inventoryObject.name;
    document.getElementById('bodyTitle').innerHTML = inventoryObject.type.toUpperCase() + ': ' + inventoryObject.name;
    $('.nav-tabs a[href="#attributes"]').tab('show');
    
    initAttributes();
    addAttributeText('Host UUID', 'objuuid');
    addAttributeTextBox('Name', 'name');
    addAttributeTextBox('Host', 'host');
    
    $.ajax({
        'url' : 'console/ajax_get_consoles',
        'dataType' : 'json',
        'method': 'POST',
        'success' : function(resp) {
            var radioButtons = [];
            for(var i = 0; i < resp.length; i++) {
                radioButtons.push({'name' : resp[i].name, 'value' : resp[i].objuuid});
            }
            addAttributeRadioGroup('Console', 'console', radioButtons)
        }
    });
    
    link = document.createElement("a");
    link.setAttribute("href", "#");
    link.innerHTML = "Terminal";
    cell = document.createElement("li");
    cell.setAttribute('onclick', 'launchTerminal()');
    cell.appendChild(link);
    document.getElementById('menuBarDynamic').appendChild(cell);
    
    
}

var loadAndEditHost = function(objuuid) {
    document.getElementById('body').innerHTML = '';
    document.getElementById('menuBarDynamic').innerHTML = '';
    
    $.ajax({
        'url' : 'inventory/ajax_get_object',
        'dataType' : 'json',
        'method': 'POST',
        'data' : {'objuuid' : objuuid},
        'success' : function(resp) {
            inventoryObject = resp;
            editHost();
            expandToNode(inventoryObject.objuuid);
        }
    });
}

var launchTerminal = function() {
    document.getElementById('body').innerHTML = '<div id="terminal"></div>';
    document.getElementById('menuBarDynamic').innerHTML = '';
    
    document.title = inventoryObject.name;
    document.getElementById('bodyTitle').innerHTML = inventoryObject.type.toUpperCase() + ': ' + inventoryObject.name;
    $('.nav-tabs a[href="#body"]').tab('show');
    
    initAttributes();
    addAttributeText('Host UUID', 'objuuid');
    addAttributeTextBox('Name', 'name');
    addAttributeTextBox('Host', 'host');
    addAttributeTextBox('Max Concurrency', 'concurrency');
    addAttributeTextArea('Configuration', 'config');
    
    $.ajax({
        'url' : 'console/ajax_get_consoles',
        'dataType' : 'json',
        'method': 'POST',
        'success' : function(resp) {
            var radioButtons = [];
            for(var i = 0; i < resp.length; i++) {
                radioButtons.push({'name' : resp[i].name, 'value' : resp[i].objuuid});
            }
            addAttributeRadioGroup('Console', 'console', radioButtons)
        }
    });
    
    term = new Terminal({
        cols: 80,
        rows: 24,
        useStyle: true,
        screenKeys: true,
        cursorBlink: true
    });

    term.on('data', function(data) {
        outputBuffer += data;
    });

    term.on('title', function(title) {
        document.title = title;
    });

    term.open(document.getElementById('terminal'));
    
    term.write('Connecting to ' + inventoryObject.name + ' (' + inventoryObject.host + ')...');
    
    $.ajax({
        'url' : 'terminal/ajax_create_session',
        'dataType' : 'json',
        'method': 'POST',
        'data' : {
            'hstuuid' : inventoryObject.objuuid
        },
        'success' : function(resp) {
            ttyuuid = resp.ttyuuid;
            if(!(terminalTimerRunning)) {
                terminalTimer();
                terminalTimerRunning = true;
            }
        },
        'error' : function(resp) {
            term.write('failed!');
        }
    });
    
    link = document.createElement("a");
    link.setAttribute("href", "#");
    link.innerHTML = "Edit";
    cell = document.createElement("li");
    cell.setAttribute('onclick', 'editHost()');
    cell.appendChild(link);
    document.getElementById('menuBarDynamic').appendChild(cell);
    
    link = document.createElement("a");
    link.setAttribute("href", "#");
    link.innerHTML = "Upload";
    cell = document.createElement("li");
    cell.setAttribute('onclick', "$('#uploadFormInput').trigger('click');");
    cell.appendChild(link);
    document.getElementById('menuBarDynamic').appendChild(cell);

    link = document.createElement("p");
    link.setAttribute("id", "termSend");
    link.setAttribute("class", "navbar-text");
    link.innerHTML = "SEND";
    cell = document.createElement("li");
    cell.appendChild(link);
    document.getElementById('menuBarDynamic').appendChild(cell);
    
    link = document.createElement("p");
    link.setAttribute("id", "termRecv");
    link.setAttribute("class", "navbar-text");
    link.innerHTML = "RECV";
    cell = document.createElement("li");
    cell.appendChild(link);
    document.getElementById('menuBarDynamic').appendChild(cell);
    
    $('.nav-tabs a[href="#body"]').tab('show');
    
    
}

var recvTerminalData = function() {
    if(!(receiving)) {
        receiving = true;
        $.ajax({
            'url' : 'terminal/ajax_recv',
            'method': 'POST',
            'data' : {
                'ttyuuid' : ttyuuid
            },
            'success' : function(resp) {
                receiving = false;
                if(resp != '') {
                    term.write(resp);
                    document.getElementById('termRecv').style.color = '#F90';
                } else {
                    document.getElementById('termRecv').style.color = '#0F0';
                }
            },
            'error' : function() {
                receiving = false;
                document.getElementById('termRecv').style.color = '#F00';
            }
        });
    }
}

var sendTerminalData = function() {
    if(outputBuffer != '' && !(sending)) {
        sending = true;
        var buffer = outputBuffer;
        outputBuffer = '';
        
        $.ajax({
            'url' : 'terminal/ajax_send',
            'dataType' : 'json',
            'method': 'POST',
            'data' : {
                'ttyuuid' : ttyuuid,
                'buffer' : buffer
            },
            'success' : function() {
                sending = false;
                document.getElementById('termSend').style.color = '#F90';
            },
            'error' : function() {
                sending = false;
                document.getElementById('termSend').style.color = '#F00';
            }
        });
    } else if(outputBuffer == '') {
        document.getElementById('termSend').style.color = '#0F0';
    }
}

var terminalTimer = function() {
    if(document.getElementById('terminal')) {
        recvTerminalData();
        sendTerminalData();
        setTimeout(terminalTimer, 100);
    } else {
        terminalTimerRunning = false;
        
        $.ajax({
            'url' : 'terminal/ajax_destroy_session',
            'dataType' : 'json',
            'method': 'POST',
            'data' : {
                'ttyuuid' : ttyuuid
            }
        });
    }
}

var uploadFileToTerminal = function(item) {
    var formData = new FormData();
    formData.append("file", item.files[0], item.files[0].name)
    formData.append("ttyuuid", ttyuuid);
          
    $.ajax({
        url: 'terminal/put_file',  //Server script to process data
        type: 'POST',
        data: formData,
        cache: false,
        contentType: false,
        processData: false
    }); 
}