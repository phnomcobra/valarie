from valarie.dao.document import Collection;

inventory = Collection('inventory')

for inventory_item in inventory.find():
    for context_key in inventory_item.object['context'].keys():
        print(inventory_item.object['name'], end=" ")
        print(inventory_item.object['context'][context_key]['action']['route'], end=" --> ")
        inventory_item.object['context'][context_key]['action']['route'] = inventory_item.object['context'][context_key]['action']['route'].replace('ajax_', '')
        print(inventory_item.object['context'][context_key]['action']['route'])
        inventory_item.set()
