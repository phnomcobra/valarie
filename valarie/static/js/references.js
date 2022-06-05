var loadRequiresGrid = function(){
    $("#requiresGrid").jsGrid({
        width: "calc(100% - 5px)",
        height: "calc(100% - 10px)",
        autoload: true,
        
        rowClick: function(args) {
            if(args.item.type == "host") {
                loadAndEditHost(args.item.objuuid);
            } else if(args.item.type == "console") {
                loadAndEditConsole(args.item.objuuid);
            } else if(args.item.type == "task") {
                loadAndEditTask(args.item.objuuid);
            } else if(args.item.type == "procedure") {
                loadAndEditProcedure(args.item.objuuid);
            } else if(args.item.type == "controller") {
                loadAndEditController(args.item.objuuid);
            } else if(args.item.type == "host group") {
                loadAndEditHostGroup(args.item.objuuid);
            }
        },
        
        rowClass: function(item, itemIndex) {
            return "client-" + itemIndex;
        },
 
        controller: {
            loadData: function(filter) {
                return $.ajax({
                    type: "POST",
                    url: "/inventory/get_required_objects_grid",
                    data: {'objuuid' : inventoryObject.objuuid},
                    dataType: "JSON"
                });
            }
        },
       
        fields: [
            {name : "name", type : "text", title : "Name"},
            {name : "type", type : "text", title : "Type"},
            {name : "objuuid", type : "text", visible: false}
        ],
    });
}

var loadProvidesGrid = function(){
    $("#providesGrid").jsGrid({
        width: "calc(100% - 5px)",
        height: "calc(100% - 10px)",
        autoload: true,
        
        rowClick: function(args) {
            if(args.item.type == "host") {
                loadAndEditHost(args.item.objuuid);
            } else if(args.item.type == "console") {
                loadAndEditConsole(args.item.objuuid);
            } else if(args.item.type == "task") {
                loadAndEditTask(args.item.objuuid);
            } else if(args.item.type == "procedure") {
                loadAndEditProcedure(args.item.objuuid);
            } else if(args.item.type == "controller") {
                loadAndEditController(args.item.objuuid);
            } else if(args.item.type == "host group") {
                loadAndEditHostGroup(args.item.objuuid);
            }
        },
        
        rowClass: function(item, itemIndex) {
            return "client-" + itemIndex;
        },
 
        controller: {
            loadData: function(filter) {
                return $.ajax({
                    type: "POST",
                    url: "/inventory/get_provided_objects_grid",
                    data: {'objuuid' : inventoryObject.objuuid},
                    dataType: "JSON"
                });
            }
        },
        
        fields: [
            {name : "name", type : "text", title : "Name"},
            {name : "type", type : "text", title : "Type"},
            {name : "objuuid", type : "text", visible: false}
        ],
    });
}
