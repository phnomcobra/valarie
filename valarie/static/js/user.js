var editUser = function() {
    document.getElementById('body').innerHTML = '';
    document.getElementById('menuBarDynamic').innerHTML = '';
    
    document.title = inventoryObject.name;
    document.getElementById('bodyTitle').innerHTML = inventoryObject.type.toUpperCase() + ': ' + inventoryObject.name;
    $('.nav-tabs a[href="#attributes"]').tab('show');
    
    initAttributes();
    addAttributeText('User UUID', 'objuuid');
    addAttributeText('Session ID', 'sessionid');
    addAttributeCheckBox('User Enabled', 'enabled');
    addAttributeTextBox('User Name', 'name');
    addAttributePassword('User Password', 'password');    
}