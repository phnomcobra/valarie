var editConfig = function() {
    document.getElementById('body').innerHTML = '';
    document.getElementById('menuBarDynamic').innerHTML = '';
    
    document.title = inventoryObject.name;
    document.getElementById('bodyTitle').innerHTML = inventoryObject.type.toUpperCase() + ': ' + inventoryObject.name;
    $('.nav-tabs a[href="#attributes"]').tab('show');
    
    initAttributes();
    addAttributeTextBox('Brand', 'brand');
    addAttributeTextArea('Banner', 'banner');
    addAttributeTextBox('Title', 'title');
    addAttributeTextBox('Global Max Concurrency', 'concurrency');
    addAttributeTextBox('Web Host', 'host');
    addAttributeTextBox('Web Port', 'port');
    addAttributeCheckBox('Enable SSL', 'ssl');
    addAttributeTextBox('Restart Command', 'restartcmd');
}

var restartValarie = function() {
    $.ajax({
        'url' : 'general/ajax_restart',
        'method': 'POST',
        'success' : function(resp){
            window.location.assign("/auth/logout");
        },
        'failure' : function(resp){
            $('.nav-tabs a[href="#console"]').tab('show');
        }
    });
}