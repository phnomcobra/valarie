var showEvents = function(resp) {
    document.getElementById('body').innerHTML = '<div id="aceInstance"></div>';
    
    $('.nav-tabs a[href="#body"]').tab('show');
    
    var editor = new ace.edit(document.getElementById('aceInstance'));
    
    editor.setReadOnly(true);
    editor.setValue(resp);
    editor.selection.moveTo(0, 0);
}

var loadEvents = function(maxAge) {
    document.getElementById('body').innerHTML = '';
    document.getElementById('menuBarDynamic').innerHTML = '';
    document.title = 'Event Log';
    document.getElementById('bodyTitle').innerHTML = 'Event Log'
    
    initAttributes();

    $.ajax({
        'url' : 'eventlog/ajax_get_events_str',
        'method': 'POST',
        'data' : {'max_age' : maxAge},
        'success' : function(resp) {
            showEvents(resp);
        }
    });
}

