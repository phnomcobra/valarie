var contextMenu = {};
var inventoryObject = {};
var saving = false;
var inventoryStateFlag = null;
var queueStateFlag = null;
var polling_messages = false;
var polling_queue = false;
var polling_inventory = false;
var selected_objuuids = [];

 $('#inventory').jstree({
    'contextmenu': {
        'items': 
            function (obj) {
                return contextMenu;
        }
    },
    'core' : {
        'check_callback' : true,
        'data' : {
            'url' : function (node) {
                return node.id === '#' ?
                'inventory/ajax_roots' :
                'ajax_children';
            },
            'data' : function (node) {
                return { 'objuuid' : node.id };
            },
            'dataType' : "json",
            'method': 'POST',
        }
    },
    'search': {
        'case_insensitive': true,
        'show_only_matches' : true
    },
    'plugins' : ['contextmenu', 'dnd', 'checkbox', 'search', 'sort']
});

var to = false;
 $('#inventorySearchTextBox').keyup(function () {
            if(to) { clearTimeout(to); }
            to = setTimeout(function () {
                var v = $('#inventorySearchTextBox').val();
                $('#inventory').jstree(true).search(v);
            }, 500);
        });

var searchInventoryTree = function(item) {
    $('#inventory').jstree(true).search(item.value);
}

$(document).on('dnd_stop.vakata', function (e, data) {
    if(data.event.target.className == 'jsgrid-grid-body' ||
       data.event.target.className == 'jsgrid-cell') {
        var nodes = $('#inventory').jstree().get_selected(true);
        
        if(nodes.length == 0) {
            $.ajax({
                'url' : 'inventory/ajax_get_object',
                'dataType' : 'json',
                'method': 'POST',
                'data' : {'objuuid' : data.data.nodes[0]},
                'success' : function(resp) {
                    $('#inventory').jstree("deselect_all");
                    
                    if(resp['type'] == 'task' && document.getElementById('taskGrid')) {
                        addProcedureTask(resp['objuuid']);
                    } else if(resp['type'] == 'host' &&
                              inventoryObject['hosts'].indexOf(resp['objuuid']) == -1 &&
                              document.getElementById('hostGrid')) {
                        addControllerHost(resp['objuuid']);
                    } else if(resp['type'] == 'host group' &&
                              inventoryObject['hosts'].indexOf(resp['objuuid']) == -1 &&
                              document.getElementById('hostGrid')) {
                        addControllerHost(resp['objuuid']);
                    } else if(resp['type'] == 'procedure' &&
                              inventoryObject['procedures'].indexOf(resp['objuuid']) == -1 &&
                              document.getElementById('procedureGrid')) {
                        addControllerProcedure(resp['objuuid']);
                    } else if(resp['type'] == 'task' && 
                              inventoryObject['procedures'].indexOf(resp['objuuid']) == -1 &&
                              document.getElementById('procedureGrid')) {
                        addControllerProcedure(resp['objuuid']);
                    }
                }
            });
        }
        
        for(i in nodes) {
            $.ajax({
                'url' : 'inventory/ajax_get_object',
                'dataType' : 'json',
                'data' : {'objuuid' : nodes[i].id},
                'method': 'POST',
                'success' : function(resp) {
                    $('#inventory').jstree("deselect_all");
                    
                    if(resp['type'] == 'task' && document.getElementById('taskGrid')) {
                        addProcedureTask(resp['objuuid']);
                    } else if(resp['type'] == 'host' &&
                              inventoryObject['hosts'].indexOf(resp['objuuid']) == -1 &&
                              document.getElementById('hostGrid')) {
                        addControllerHost(resp['objuuid']);
                    } else if(resp['type'] == 'host group' &&
                              inventoryObject['hosts'].indexOf(resp['objuuid']) == -1 &&
                              document.getElementById('hostGrid')) {
                        addControllerHost(resp['objuuid']);
                    } else if(resp['type'] == 'procedure' &&
                              inventoryObject['procedures'].indexOf(resp['objuuid']) == -1 &&
                              document.getElementById('procedureGrid')) {
                        addControllerProcedure(resp['objuuid']);
                    } else if(resp['type'] == 'task' && 
                              inventoryObject['procedures'].indexOf(resp['objuuid']) == -1 &&
                              document.getElementById('procedureGrid')) {
                        addControllerProcedure(resp['objuuid']);
                    }
                }
            });
        }
    }
});

var exportObjectsZipFromInventory = function() {
    $('.nav-tabs a[href="#console"]').tab('show');
    
    var nodes = $('#inventory').jstree().get_selected(true);
    
    var objuuids = []
    for(i in nodes)
        objuuids.push(nodes[i].id);
    
    window.location = 'inventory/export_objects_zip?objuuids=' + objuuids.join(',');
}

var exportFilesZipFromInventory = function() {
    $('.nav-tabs a[href="#console"]').tab('show');
    
    var nodes = $('#inventory').jstree().get_selected(true);
    
    var objuuids = []
    for(i in nodes)
        objuuids.push(nodes[i].id);
    
    window.location = 'inventory/export_files_zip?objuuids=' + objuuids.join(',');
}

var importFileToInventory = function(item) {
    $('.nav-tabs a[href="#console"]').tab('show');
    
    var formData = new FormData();
    formData.append("file", item.files[0], item.files[0].name);
         
    $.ajax({
        url: 'inventory/import_file',  //Server script to process data
        type: 'POST',
        data: formData,
        cache: false,
        contentType: false,
        processData: false,
        success: function(resp) {
            $('#inventory').jstree('refresh');
        }
    }); 
}

var importObjectsZipToInventory = function(item) {
    $('.nav-tabs a[href="#console"]').tab('show');
    
    var formData = new FormData();
    formData.append("file", item.files[0], item.files[0].name);
     
    $.ajax({
        url: 'inventory/import_objects_zip',  //Server script to process data
        type: 'POST',
        data: formData,
        cache: false,
        contentType: false,
        processData: false,
        success: function(resp) {
            $('#inventory').jstree('refresh');
        }
    }); 
}

var importFilesZipToInventory = function(item) {
    $('.nav-tabs a[href="#console"]').tab('show');
    
    var formData = new FormData();
    formData.append("file", item.files[0], item.files[0].name);
     
    $.ajax({
        url: 'inventory/import_files_zip',  //Server script to process data
        type: 'POST',
        data: formData,
        cache: false,
        contentType: false,
        processData: false,
        success: function(resp) {
            $('#inventory').jstree('refresh');
        }
    }); 
}

var createNode = function(object) {
    var parentNode = $('#inventory').find("[id='" + object['parent'] + "']");
    $('#inventory').jstree('create_node', parentNode, {'id' : object['objuuid'], 'parent' : object['parent'], 'text' : object['name'], 'icon' : object['icon']}, 'last', false, false);
}

var deleteNode = function(objuuid) {
    $('.nav-tabs a[href="#console"]').tab('show');
    var node = $('#inventory').find("[id='" + objuuid + "']");
    $('#inventory').jstree('delete_node', node);
    if(inventoryObject['objuuid'] == objuuid) {
        inventoryObject = {}
        document.getElementById('attributes').innerHTML = '';
        document.getElementById('body').innerHTML = '';
    }
    touchInventory();
}

$('#inventory').on('dblclick.jstree', function (evt, data) {
    obj = {};
    if('run' in contextMenu) {
        if(contextMenu.run.method == "run controller") {
            obj['item'] = contextMenu.run;
            contextMenu.run.action(obj);
        } else {
            obj['item'] = contextMenu.edit;
            contextMenu.edit.action(obj);
        }
    } else {
        obj['item'] = contextMenu.edit;
        contextMenu.edit.action(obj);
    }
});

$('#inventory').on('select_node.jstree', function (evt, data) {
        contextMenu = {};
        
        $.ajax({
            'url' : 'inventory/ajax_context',
            'dataType' : 'json',
            'method': 'POST',
            'data' : {
                'objuuid' : data.node.id
            },
            'success' : function(resp) {
                for(var item in resp) {
                    contextMenu[item] = {
                        'label' : resp[item]['label'],
                        'route' : resp[item]['action']['route'],
                        'params' : resp[item]['action']['params'],
                        'method' : resp[item]['action']['method'],
                        'action' : function (obj) {
                            $.ajax({
                                'url' : obj.item.route,
                                'dataType' : 'json',
                                'method': 'POST',
                                'data' : obj.item.params,
                                'success' : function(resp) {
                                    $('#inventory').jstree("deselect_all");
                                    if(obj.item.method == 'create container') {
                                        addMessage('create container success');
                                        inventoryObject = resp;
                                        createNode(resp);
                                        editContainer();
                                    } else if(obj.item.method == 'create task') {
                                        addMessage('create task success');
                                        inventoryObject = resp;
                                        createNode(resp);
                                        editTask();
                                        $('.nav-tabs a[href="#attributes"]').tab('show');
                                    } else if(obj.item.method == 'create user') {
                                        addMessage('create user success');
                                        inventoryObject = resp;
                                        createNode(resp);
                                        editUser();
                                        $('.nav-tabs a[href="#attributes"]').tab('show');
                                    } else if(obj.item.method == 'create text file') {
                                        addMessage('create text file success');
                                        inventoryObject = resp;
                                        createNode(resp);
                                        editTextFile();
                                        $('.nav-tabs a[href="#attributes"]').tab('show');
                                    } else if(obj.item.method == 'create host group') {
                                        addMessage('create host group success');
                                        inventoryObject = resp;
                                        createNode(resp);
                                        editHostGroup();
                                        $('.nav-tabs a[href="#attributes"]').tab('show');
                                    } else if(obj.item.method == 'create procedure') {
                                        document.title = resp.name;
                                        inventoryObject = resp;
                                        createNode(resp);
                                        editProcedure();
                                        $('.nav-tabs a[href="#attributes"]').tab('show');
                                    } else if(obj.item.method == 'create status') {
                                        addMessage('create status success');
                                        inventoryObject = resp;
                                        createNode(resp);
                                        editStatusCode();
                                    } else if(obj.item.method == 'create host') {
                                        addMessage('create host success');
                                        inventoryObject = resp;
                                        createNode(resp);
                                        editHost();
                                    } else if(obj.item.method == 'create console') {
                                        addMessage('create console success');
                                        inventoryObject = resp;
                                        createNode(resp);
                                        editConsole();
                                        $('.nav-tabs a[href="#attributes"]').tab('show');
                                    } else if(obj.item.method == 'create controller') {
                                        addMessage('create controller success');
                                        inventoryObject = resp;
                                        createNode(resp);
                                        editController();
                                        $('.nav-tabs a[href="#attributes"]').tab('show');
                                    } else if(obj.item.method == 'edit task') {
                                        addMessage("edit task success");
                                        inventoryObject = resp;
                                        editTask();
                                    } else if(obj.item.method == 'edit user') {
                                        addMessage("edit user success");
                                        inventoryObject = resp;
                                        editUser();
                                    } else if(obj.item.method == 'edit configuration') {
                                        addMessage("edit configuration success");
                                        inventoryObject = resp;
                                        editConfig();
                                    } else if(obj.item.method == 'edit text file') {
                                        addMessage("edit text file success");
                                        inventoryObject = resp;
                                        editTextFile();
                                    } else if(obj.item.method == 'edit binary file') {
                                        addMessage("edit binary file success");
                                        inventoryObject = resp;
                                        editBinaryFile();
                                    } else if(obj.item.method == 'edit task hosts') {
                                        addMessage("edit task success");
                                        inventoryObject = resp;
                                        editTaskHosts();
                                    } else if(obj.item.method == 'edit host group') {
                                        addMessage("edit task success");
                                        inventoryObject = resp;
                                        editHostGroup();
                                    } else if(obj.item.method == 'edit container') {
                                        addMessage("edit container success");
                                        inventoryObject = resp;
                                        editContainer();
                                    } else if(obj.item.method == 'edit procedure') {
                                        addMessage("edit procedure success");
                                        inventoryObject = resp;
                                        editProcedure();
                                    } else if(obj.item.method == 'edit status code') {
                                        addMessage("edit status success");
                                        inventoryObject = resp;
                                        editStatusCode();
                                    } else if(obj.item.method == 'edit host') {
                                        addMessage("edit host success");
                                        inventoryObject = resp;
                                        editHost();
                                    } else if(obj.item.method == 'edit controller') {
                                        addMessage("edit controller success");
                                        inventoryObject = resp;
                                        editController();
                                        $('.nav-tabs a[href="#body"]').tab('show');
                                    } else if(obj.item.method == 'edit console') {
                                        addMessage("edit console success");
                                        inventoryObject = resp;
                                        editConsole();
                                    } else if(obj.item.method == 'run procedure') {
                                        addMessage("run procedure success");
                                        inventoryObject = resp;
                                        executeProcedure();
                                    } else if(obj.item.method == 'run controller') {
                                        addMessage("run controller success");
                                        inventoryObject = resp;
                                        executeController();
                                    } else if(obj.item.method == 'restart valarie') {
                                        addMessage("restart success");
                                        restartValarie();
                                    } else if(obj.item.method == 'run task') {
                                        document.title = resp.name;
                                        document.getElementById('bodyTitle').innerHTML = resp.type.toUpperCase() + ': ' + resp.name;
                                        addMessage("run task success");
                                        inventoryObject = resp;
                                        executeTask();
                                        $('.nav-tabs a[href="#body"]').tab('show');
                                    } else if(obj.item.method == 'delete node') {
                                        document.title = "ValARIE WebApp";
                                        document.getElementById('bodyTitle').innerHTML = '';
                                        addMessage("delete success");
                                        deleteNode(resp['id']);
                                        touchInventory();
                                        $('.nav-tabs a[href="#console"]').tab('show');
                                    } else if(obj.item.method == 'copy node') {
                                        addMessage("copy success");
                                        createNode(resp);
                                    } else if(obj.item.method == 'create terminal') {
                                        addMessage("start terminal success");
                                        inventoryObject = resp;
                                        launchTerminal();
                                    }
                                },
                                'error' : function(resp, status, error) {
                                    $('.nav-tabs a[href="#console"]').tab('show');
                                    addMessage("console select failure " + resp);
                                    console.log(resp);
                                    console.log(status);
                                    console.log(error);
                                }
                            });
                        }
                    }
                }
            },
            'error' : function(resp, status, error) {
                $('.nav-tabs a[href="#console"]').tab('show');
                addMessage("context failure " + resp);
            }
        });
    }
);

$('#inventory').on("move_node.jstree", function(event, data) {
        $('#inventory').jstree("deselect_all");
        $.ajax({
            'url' : 'inventory/ajax_move',
            'dataType' : 'json',
            'method': 'POST',
            'data' : {
                'objuuid' : data.node.id,
                'parent_objuuid' : data.node.parent
            },
            'success' : function(resp) {
                $('.nav-tabs a[href="#console"]').tab('show');
                addMessage('move success');
                touchInventory();
            },
            'error' : function(resp, status, error) {
                addMessage('move failure');
                $('.nav-tabs a[href="#console"]').tab('show');
                $('#inventory').jstree('refresh');
            }
        });
});

var initAttributes = function() {
    document.getElementById('attributes').innerHTML = '<table id="attributesTable" class="table"></table>';
}

var addAttributeTextBox = function(fieldName, inventoryKey) {
    var attributeTable = document.getElementById("attributesTable");
    var attributeRow = attributeTable.insertRow(-1);
    var attributeCell;
    
    attributeCell = attributeRow.insertCell(-1);
    attributeCell.innerHTML = fieldName;
    
    attributeCell = attributeRow.insertCell(-1);
    var id = 'inventory-obj-key-' + inventoryKey;
    attributeCell.innerHTML = '<input type="text" id="' + id + '" onchange="setInventoryKey(&quot;' + inventoryKey + '&quot;, &quot;' + id + '&quot;)" onkeyup="setInventoryKey(&quot;' + inventoryKey + '&quot;, &quot;' + id + '&quot;)" style="width:99%"></input>';
    document.getElementById(id).value = inventoryObject[inventoryKey];
}

var addAttributeRadioGroup = function(fieldName, inventoryKey, radioButtons) {
    var attributeTable = document.getElementById("attributesTable");
    var attributeRow = attributeTable.insertRow(-1);
    var attributeCell;
    
    attributeCell = attributeRow.insertCell(-1);
    attributeCell.innerHTML = fieldName;
    
    attributeCell = attributeRow.insertCell(-1);
    attributeCell.innerHTML = '';
    for(var i = 0; i < radioButtons.length; i++) {
        if(inventoryObject[inventoryKey] == radioButtons[i].value) {
            attributeCell.innerHTML += '<input type="radio" name="radio-' + inventoryKey + 
                                       '" value="' + radioButtons[i].value + 
                                       '" checked=true onclick="inventoryObject[&quot;' + inventoryKey + '&quot;]=this.value;inventoryObject[&quot;changed&quot;]=true;">' +
                                       radioButtons[i].name + '<br>';
        } else {
            attributeCell.innerHTML += '<input type="radio" name="radio-' + inventoryKey + 
                                       '" value="' + radioButtons[i].value + 
                                       '" onclick="inventoryObject[&quot;' + inventoryKey + '&quot;]=this.value;inventoryObject[&quot;changed&quot;]=true;">' +
                                       radioButtons[i].name + '<br>';
        }
    }
}

var addAttributeTextArea = function(fieldName, inventoryKey) {
    var attributeTable = document.getElementById("attributesTable");
    var attributeRow = attributeTable.insertRow(-1);
    var attributeCell;
    
    attributeCell = attributeRow.insertCell(-1);
    attributeCell.innerHTML = fieldName;
    
    attributeCell = attributeRow.insertCell(-1);
    var id = 'inventory-obj-key-' + inventoryKey;
    attributeCell.innerHTML = '<textarea rows = "5" id="' + id + '" onchange="setInventoryKey(&quot;' + inventoryKey + '&quot;, &quot;' + id + '&quot;)" onkeyup="setInventoryKey(&quot;' + inventoryKey + '&quot;, &quot;' + id + '&quot;)" style="width:98%;"></textarea>';
    document.getElementById(id).value = inventoryObject[inventoryKey];
}

var addAttributePassword = function(fieldName, inventoryKey) {
    var attributeTable = document.getElementById("attributesTable");
    var attributeRow = attributeTable.insertRow(-1);
    var attributeCell;
    
    attributeCell = attributeRow.insertCell(-1);
    attributeCell.innerHTML = fieldName;
    
    attributeCell = attributeRow.insertCell(-1);
    var id = 'inventory-obj-key-' + inventoryKey;
    attributeCell.innerHTML = '<input type="password" id="' + id + '" onchange="setInventoryKey(&quot;' + inventoryKey + '&quot;, &quot;' + id + '&quot;)" onkeyup="setInventoryKey(&quot;' + inventoryKey + '&quot;, &quot;' + id + '&quot;)" style="width:99%"></input>';
    document.getElementById(id).value = inventoryObject[inventoryKey];
}

var addAttributeCheckBox = function(fieldName, inventoryKey) {
    var attributeTable = document.getElementById("attributesTable");
    var attributeRow = attributeTable.insertRow(-1);
    var attributeCell;
    
    attributeCell = attributeRow.insertCell(-1);
    attributeCell.innerHTML = fieldName;
    
    attributeCell = attributeRow.insertCell(-1);
    var id = 'inventory-obj-key-' + inventoryKey;
    attributeCell.innerHTML = '<input type="checkbox" id="' + id + '" onchange="this.value = this.checked;setInventoryKey(&quot;' + inventoryKey + '&quot;, &quot;' + id + '&quot;)"></input>';
    
    if(inventoryObject[inventoryKey] == 'true' || inventoryObject[inventoryKey] == true) {
        document.getElementById(id).checked = true;
        document.getElementById(id).value = true;
    } else {
        document.getElementById(id).checked = false;
        document.getElementById(id).value = false;
    }
}

var addAttributeColor = function(fieldName, inventoryKey) {
    var attributeTable = document.getElementById("attributesTable");
    var attributeRow = attributeTable.insertRow(-1);
    var attributeCell;
    
    attributeCell = attributeRow.insertCell(-1);
    attributeCell.innerHTML = fieldName;
    
    attributeCell = attributeRow.insertCell(-1);
    var id = 'inventory-obj-key-' + inventoryKey;
    attributeCell.innerHTML = '<input class="jscolor" id="' + id + '" onchange="setInventoryKey(&quot;' + inventoryKey + '&quot;, &quot;' + id + '&quot;)" onkeyup="setInventoryKey(&quot;' + inventoryKey + '&quot;, &quot;' + id + '&quot;)" style="width:99%"></input>';
    jsc.tryInstallOnElements([document.getElementById(id)], "jscolor");
    jsc.register();
    document.getElementById(id).jscolor.fromString(inventoryObject[inventoryKey]);
}

var addAttributeText = function(fieldName, inventoryKey) {
    var attributeTable = document.getElementById("attributesTable");
    var attributeRow = attributeTable.insertRow(-1);
    var attributeCell;
    
    attributeCell = attributeRow.insertCell(-1);
    attributeCell.innerHTML = fieldName;
    
    attributeCell = attributeRow.insertCell(-1);
    var id = 'inventory-obj-key-' + inventoryKey;
    attributeCell.innerHTML = '<div id="' + id + '"></div>';
    document.getElementById(id).innerHTML = inventoryObject[inventoryKey];
}

var addAttributeStatic = function(fieldName, value) {
    var attributeTable = document.getElementById("attributesTable");
    var attributeRow = attributeTable.insertRow(-1);
    var attributeCell;
    
    attributeCell = attributeRow.insertCell(-1);
    attributeCell.innerHTML = fieldName;
    
    attributeCell = attributeRow.insertCell(-1);
    attributeCell.innerHTML = value;
}


var inventoryApp = angular.module('inventoryApp', []);
inventoryApp.controller('inventoryCtrl', function($scope, $interval, $http, $sce) {
    $interval(function () {
        if(inventoryObject['changed'] && !saving) {
            inventoryObject['changed'] = false;
            document.getElementById('connectionStatus').innerHTML = '<font style="color:#F90">SAVING</font>';
            saving = true;
            $http.post('inventory/ajax_post_object', JSON.stringify(inventoryObject)
            ).then(function successCallback(response) {
                addMessage("saving " + inventoryObject['objuuid']);
                saving = false;
                
                if(inventoryObject['refreshTree']) {
                    $('#inventory').jstree('refresh');
                    inventoryObject['refreshTree'] = false;
                }
                
            }, function errorCallback(response) {
                $('.nav-tabs a[href="#console"]').tab('show');
                addMessage("save failure " + inventoryObject['objuuid']);
                saving = false;
                document.getElementById('connectionStatus').innerHTML = '<font style="color:#F00">NO CONN</font>';
            });
        }
        
        if(!polling_messages) {
            polling_messages = true;
            
            $http.post("messaging/ajax_get_messages").then(function (response) {
                polling_messages = false;
                var messageData = '<table>';
                var responseJSON = angular.fromJson(response)['data']['messages'];
                for(item in responseJSON) {
                    messageData += '<tr><td>' + responseJSON[item]['timestamp'] + '</td><td>' + responseJSON[item]['message'] + '</td></tr>';
                }
                messageData += '</table>'
            
                $scope.messages = $sce.trustAsHtml(messageData);
            }, function errorCallback(response) {
                polling_messages = false;
            });
        }
        
        if(!polling_inventory) {
            polling_inventory = true;
            
            $.ajax({
                'url' : 'flags/ajax_get',
                'dataType' : 'json',
                'method': 'POST',
                'data' : {
                    'key' : 'inventoryState'
                },
                'success' : function(resp) {
                    polling_inventory = false;
                    
                    if(inventoryStateFlag != resp.value) {
                        inventoryStateFlag = resp.value;
                        $('#inventory').jstree('refresh');
                    }
                },
                'error' : function(resp) {
                    polling_inventory = false;
                }
            });
        }
        
        if(!polling_queue) {
            polling_queue = true;
            
            $.ajax({
                'url' : 'flags/ajax_get',
                'dataType' : 'json',
                'method': 'POST',
                'data' : {
                    'key' : 'queueState'
                },
                'success' : function(resp) {
                    polling_queue = false;
                    
                    if(queueStateFlag != resp.value) {
                        queueStateFlag = resp.value;
                        updateQueueState();
                    }
                    document.getElementById('connectionStatus').innerHTML = '<font style="color:#0F0">OK</font>';
                },
                'error' : function(resp) {
                    polling_queue = false;
                    
                    document.getElementById('connectionStatus').innerHTML = '<font style="color:#F00">NO CONN</font>';
                }
            });
        }
    }, 1000);
});

var addMessage = function (message) {
    $.ajax({
        'url' : 'messaging/ajax_add_message',
        'method': 'POST',
        'dataType' : 'json',
        'data' : {
            'message' : message
        },
    });
};

var setInventoryKey = function (key, div) {
    inventoryObject[key] = document.getElementById(div).value;
    inventoryObject['changed'] = true;
    
    if(key == 'name') {
        $("#inventory").jstree('rename_node', inventoryObject['objuuid'] , inventoryObject[key]);
        document.title = inventoryObject.name;
        document.getElementById('bodyTitle').innerHTML = inventoryObject.type.toUpperCase() + ': ' + inventoryObject.name;
    }
}

var touchInventory = function() {
    $.ajax({
        'url' : 'flags/ajax_touch',
        'method': 'POST',
        'dataType' : 'json',
        'data' : {
            'key' : 'inventoryState'
        },
        'success' : function(resp) {
            inventoryStateFlag = resp.value;
        },
    });
}

/* Exists to mitigate css race condition 
between BS transitions and jsgrid instantiation. */
var refreshJSGrids = function() {
    $('.jsgrid').each(function(){
        $(this).jsGrid('refresh');
    });
}

var selectDependencies = function() {
    //$('#inventory').jstree("deselect_all");
    
    var nodes = $('#inventory').jstree().get_selected(true);
    
    var objuuids = []
    for(i in nodes)
        objuuids.push(nodes[i].id);
    
    $.ajax({
        'type' : 'POST',
        'url' : 'inventory/ajax_get_dependencies',
        'dataType' : 'json',
        'contentType' : 'application/json',
        'data' : JSON.stringify(objuuids),
        'success' : function(objuuids) {
            for(var i in objuuids) {
                $('#inventory').jstree(true).select_node(objuuids[i]);
            }
        },
    });
}

var cutInventoryItems = function() {
    var nodes = $('#inventory').jstree().get_selected(true);
    var objuuids = [];
    
    for(i in nodes)
        objuuids.push(nodes[i].id);
    
    for(i in objuuids) {
        var node = $("#inventory").jstree("get_node", "#" + objuuids[i]);
        var parent = $("#inventory").jstree("get_node", "#" + node.parent);
        if(!parent.state.selected) {
            selected_objuuids.push(objuuids[i]);
            $("#" + objuuids[i] + " >a").css("background", "yellow");
        }
        
    }
    
    $('#inventory').jstree("deselect_all");
}

var unCutInventoryItems = function() {
    for(i in selected_objuuids)
        $("#" + selected_objuuids[i] + " >a").css("background", "white");    
    selected_objuuids = [];
}

var deleteInventoryItems = function() {
    var nodes = $('#inventory').jstree().get_selected(true);
    
    $('#inventory').jstree("deselect_all");
    
    var objuuids = [];
    
    for(i in nodes)
        objuuids.push(nodes[i].id);
    
    for(i in objuuids) {
        var node = $("#inventory").jstree("get_node", "#" + objuuids[i]);
        var parent = $("#inventory").jstree("get_node", "#" + node.parent);
        if(!parent.state.selected) {
            deleteNode(objuuids[i]);
        
            $.ajax({
                'url' : 'inventory/ajax_delete',
                'dataType' : 'json',
                'method': 'POST',
                'data' : {
                    'objuuid' : objuuids[i]
                },
                'success' : function(resp) {
                    $('.nav-tabs a[href="#console"]').tab('show');
                    addMessage('delete success');
                    touchInventory();
                },
                'error' : function(resp, status, error) {
                    addMessage('delete failure');
                    $('.nav-tabs a[href="#console"]').tab('show');
                    $('#inventory').jstree('refresh');
                }
            });
        }
    }
}

var pasteInventoryItems = function() {
    var parent_objuuid = $('#inventory').jstree().get_selected(true)[0];
    
    for(i in selected_objuuids) {
        $('#inventory').jstree("move_node", selected_objuuids[i], parent_objuuid.id, 0);
        $("#" + selected_objuuids[i] + " >a").css("background", "white");
                
        $.ajax({
            'url' : 'inventory/ajax_move',
            'dataType' : 'json',
            'method': 'POST',
            'data' : {
                'objuuid' : selected_objuuids[i],
                'parent_objuuid' : parent_objuuid.id
            },
            'success' : function(resp) {
                $('.nav-tabs a[href="#console"]').tab('show');
                addMessage('move success');
                touchInventory();
            },
            'error' : function(resp, status, error) {
                addMessage('move failure');
                $('.nav-tabs a[href="#console"]').tab('show');
                $('#inventory').jstree('refresh');
            }
        });
    }    
    selected_objuuids = [];
}

var expandToNode = function(nodeID) {
    $('#inventory').jstree("deselect_all");
    $('#inventory').jstree(true).select_node(nodeID);
}