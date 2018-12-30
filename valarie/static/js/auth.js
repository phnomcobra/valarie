var userObject = {};
var saving = false;
var usersStateFlag = null;
var polling_messages = false;
var polling_users = false;

var loadUserAttributes = function() {
    initAttributes();
    addAttributeText('User UUID', 'objuuid');
    addAttributeText('Session ID', 'session id');
    addAttributeTextBox('User Name', 'name');
    addAttributeTextBox('First Name', 'first name');
    addAttributeTextBox('Last Name', 'last name');
    addAttributeTextBox('Phone', 'phone');
    addAttributeTextBox('Email', 'email');
    addAttributePassword('User Password', 'password');
    addAttributeCheckBox('User Enabled', 'enabled');
}

var loadUser = function(objuuid) {
    $.ajax({
        'url' : '/auth/ajax_get_object',
        'dataType' : 'json',
        'method': 'POST',
        'data' : {
            'objuuid' : objuuid
        },
        'success' : function(resp) {
            addMessage('load user object success');
            userObject = resp;
            //editContainer();
            loadUserAttributes();
            $('.nav-tabs a[href="#attributes"]').tab('show');
        },
        'failure' : function(resp) {
            addMessage('load user object failure');
            userObject = {};
            initAttributes();
            $('.nav-tabs a[href="#console"]').tab('show');
        }
    });
}

var loadUserGrid = function(){
    $("#userGrid").jsGrid({
        width: "calc(100% - 5px)",
        height: "calc(100vh - 120px)",
        autoload: true,
        
        deleteButton: true,
        confirmDeleting: false,
        //editing: true,
        inserting: true,
        
        rowDoubleClick: function(args) {
            //console.log(args);
            //loadAndEditHost(args.item.objuuid);
            loadUser(args.item.objuuid);
            
        },
        
        rowClick: function(args) {
            //loadAndEditHost(args.item.objuuid);
        },
        
        rowClass: function(item, itemIndex) {
            return "client-" + itemIndex;
        },
 
        controller: {
            loadData: function(filter) {
                return $.ajax({
                    type: "POST",
                    url: "/auth/ajax_get_users_grid",
                    //data: {'objuuid' : userObject['objuuid']},
                    dataType: "JSON"
                });
            },
            insertItem: function(item) {
                $.ajax({
                    'url' : '/auth/ajax_create_user',
                    'dataType' : 'json',
                    'method': 'POST',
                    'data' : {
                        'name' : item.name
                    },
                    'success' : function(resp) {
                        $("#userGrid").jsGrid("loadData");
                        userObject = resp;
                        loadUserAttributes();
                        $('.nav-tabs a[href="#attributes"]').tab('show');
                        touchUsers();
                    },
                });
            },
            deleteItem: function(item) {
                //userObject['hosts'].splice(userObject['hosts'].indexOf(item.objuuid), 1);
                //userObject['changed'] = true;
                $('.nav-tabs a[href="#console"]').tab('show');
                
                $.ajax({
                    'url' : '/auth/ajax_delete',
                    'dataType' : 'json',
                    'method': 'POST',
                    'data' : {
                        'objuuid' : item.objuuid
                    },
                    'success' : function(resp) {
                        initAttributes();
                        touchUsers();
                        $('.nav-tabs a[href="#console"]').tab('show');
                    },
                    'failure' : function(resp) {
                        $("#userGrid").jsGrid("loadData");
                        $('.nav-tabs a[href="#console"]').tab('show');
                    }
                });
            }
        },
        
        fields: [
            {name : "name", type : "text", title : "User Name"},
            {name : "objuuid", type : "text", visible: false},
            {type : "control" }
        ],
    });
}

var setUserKey = function (key, div) {
    userObject[key] = document.getElementById(div).value;
    userObject['changed'] = true;
}

var touchUsers = function() {
    $.ajax({
        'url' : '/flags/ajax_touch',
        'dataType' : 'json',
        'method': 'POST',
        'data' : {
            'key' : 'usersState'
        },
        'success' : function(resp) {
            usersStateFlag = resp.value;
        },
    });
}

var usersApp = angular.module('usersApp', []);
usersApp.controller('usersCtrl', function($scope, $interval, $http, $sce) {
    $interval(function () {
        if(userObject['changed'] && !saving) {
            userObject['changed'] = false;
            saving = true;
            document.getElementById('connectionStatus').innerHTML = '<font style="color:#F90">SAVING</font>';
            $http.post('/auth/ajax_post_object', JSON.stringify(userObject)
            ).then(function successCallback(response) {
                addMessage("saving " + userObject['objuuid']);
                saving = false;
                
                $("#userGrid").jsGrid("loadData");
                touchUsers();
                
            }, function errorCallback(response) {
                $('.nav-tabs a[href="#console"]').tab('show');
                addMessage("save failure " + userObject['objuuid']);
                saving = false;
                document.getElementById('connectionStatus').innerHTML = '<font style="color:#F00">NO CONN</font>';
            });
        }
        
        if(!polling_users) {
            polling_users = true;
            
            $.ajax({
                'url' : '/flags/ajax_get',
                'dataType' : 'json',
                'method': 'POST',
                'data' : {
                    'key' : 'usersState'
                },
                'success' : function(resp) {
                    polling_users = false;
                    
                    if(usersStateFlag != resp.value) {
                        usersStateFlag = resp.value;
                        $("#userGrid").jsGrid("loadData");
                    }
                    document.getElementById('connectionStatus').innerHTML = '<font style="color:#0F0">OK</font>';
                },
                'error' : function(resp) {
                    polling_users = false;
                    
                    document.getElementById('connectionStatus').innerHTML = '<font style="color:#F00">NO CONN</font>';
                }
            });
        }
        
        if(!polling_messages) {
            polling_messages = true;
            
            $http.post("/messaging/ajax_get_messages").then(function (response) {
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
    }, 1000);
});

var initAttributes = function() {
    document.getElementById('attributes').innerHTML = '<table id="attributesTable" class="table"></table>';
}

var addAttributeTextBox = function(fieldName, userKey) {
    var attributeTable = document.getElementById("attributesTable");
    var attributeRow = attributeTable.insertRow(-1);
    var attributeCell;
    
    attributeCell = attributeRow.insertCell(-1);
    attributeCell.innerHTML = fieldName;
    
    attributeCell = attributeRow.insertCell(-1);
    var id = 'inventory-obj-key-' + userKey;
    attributeCell.innerHTML = '<input type="text" id="' + id + '" onchange="setUserKey(&quot;' + userKey + '&quot;, &quot;' + id + '&quot;)" onkeyup="setUserKey(&quot;' + userKey + '&quot;, &quot;' + id + '&quot;)" style="width:99%"></input>';
    document.getElementById(id).value = userObject[userKey];
}

var addAttributePassword = function(fieldName, userKey) {
    var attributeTable = document.getElementById("attributesTable");
    var attributeRow = attributeTable.insertRow(-1);
    var attributeCell;
    
    attributeCell = attributeRow.insertCell(-1);
    attributeCell.innerHTML = fieldName;
    
    attributeCell = attributeRow.insertCell(-1);
    var id = 'inventory-obj-key-' + userKey;
    attributeCell.innerHTML = '<input type="password" id="' + id + '" onchange="setUserKey(&quot;' + userKey + '&quot;, &quot;' + id + '&quot;)" onkeyup="setUserKey(&quot;' + userKey + '&quot;, &quot;' + id + '&quot;)" style="width:99%"></input>';
    document.getElementById(id).value = userObject[userKey];
}

var addAttributeRadioGroup = function(fieldName, userKey, radioButtons) {
    var attributeTable = document.getElementById("attributesTable");
    var attributeRow = attributeTable.insertRow(-1);
    var attributeCell;
    
    attributeCell = attributeRow.insertCell(-1);
    attributeCell.innerHTML = fieldName;
    
    attributeCell = attributeRow.insertCell(-1);
    attributeCell.innerHTML = '';
    for(var i = 0; i < radioButtons.length; i++) {
        if(userObject[userKey] == radioButtons[i].value) {
            attributeCell.innerHTML += '<input type="radio" name="radio-' + userKey + 
                                       '" value="' + radioButtons[i].value + 
                                       '" checked=true onclick="userObject[&quot;' + userKey + '&quot;]=this.value;userObject[&quot;changed&quot;]=true;">' +
                                       radioButtons[i].name + '<br>';
        } else {
            attributeCell.innerHTML += '<input type="radio" name="radio-' + userKey + 
                                       '" value="' + radioButtons[i].value + 
                                       '" onclick="userObject[&quot;' + userKey + '&quot;]=this.value;userObject[&quot;changed&quot;]=true;">' +
                                       radioButtons[i].name + '<br>';
        }
    }
}

var addAttributeTextArea = function(fieldName, userKey) {
    var attributeTable = document.getElementById("attributesTable");
    var attributeRow = attributeTable.insertRow(-1);
    var attributeCell;
    
    attributeCell = attributeRow.insertCell(-1);
    attributeCell.innerHTML = fieldName;
    
    attributeCell = attributeRow.insertCell(-1);
    var id = 'inventory-obj-key-' + userKey;
    attributeCell.innerHTML = '<textarea rows = "5" id="' + id + '" onchange="setUserKey(&quot;' + userKey + '&quot;, &quot;' + id + '&quot;)" onkeyup="setUserKey(&quot;' + userKey + '&quot;, &quot;' + id + '&quot;)" style="width:98%;"></textarea>';
    document.getElementById(id).value = userObject[userKey];
}

var addAttributeCheckBox = function(fieldName, userKey) {
    var attributeTable = document.getElementById("attributesTable");
    var attributeRow = attributeTable.insertRow(-1);
    var attributeCell;
    
    attributeCell = attributeRow.insertCell(-1);
    attributeCell.innerHTML = fieldName;
    
    attributeCell = attributeRow.insertCell(-1);
    var id = 'inventory-obj-key-' + userKey;
    attributeCell.innerHTML = '<input type="checkbox" id="' + id + '" onchange="this.value = this.checked;setUserKey(&quot;' + userKey + '&quot;, &quot;' + id + '&quot;)"></input>';
    
    if(userObject[userKey] == 'false') {
        document.getElementById(id).checked = false;
        document.getElementById(id).value = false;
    } else {
        document.getElementById(id).checked = true;
        document.getElementById(id).value = true;
    }
}

var addAttributeColor = function(fieldName, userKey) {
    var attributeTable = document.getElementById("attributesTable");
    var attributeRow = attributeTable.insertRow(-1);
    var attributeCell;
    
    attributeCell = attributeRow.insertCell(-1);
    attributeCell.innerHTML = fieldName;
    
    attributeCell = attributeRow.insertCell(-1);
    var id = 'inventory-obj-key-' + userKey;
    attributeCell.innerHTML = '<input class="jscolor" id="' + id + '" onchange="setUserKey(&quot;' + userKey + '&quot;, &quot;' + id + '&quot;)" onkeyup="setUserKey(&quot;' + userKey + '&quot;, &quot;' + id + '&quot;)" style="width:99%"></input>';
    jsc.tryInstallOnElements([document.getElementById(id)], "jscolor");
    jsc.register();
    document.getElementById(id).jscolor.fromString(userObject[userKey]);
}

var addAttributeText = function(fieldName, userKey) {
    var attributeTable = document.getElementById("attributesTable");
    var attributeRow = attributeTable.insertRow(-1);
    var attributeCell;
    
    attributeCell = attributeRow.insertCell(-1);
    attributeCell.innerHTML = fieldName;
    
    attributeCell = attributeRow.insertCell(-1);
    var id = 'inventory-obj-key-' + userKey;
    attributeCell.innerHTML = '<div id="' + id + '"></div>';
    document.getElementById(id).innerHTML = userObject[userKey];
}

var addMessage = function (message) {
    $.ajax({
        'url' : '/messaging/ajax_add_message',
        'dataType' : 'json',
        'method': 'POST',
        'data' : {
            'message' : message
        },
    });
};

loadUserGrid();