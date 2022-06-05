from valarie.dao.document import Collection;

inventory = Collection('inventory')

for inventory_item in inventory.find():
    if 'context' in inventory_item.object.keys():
        if 'terminal' in inventory_item.object['context'].keys():
            del inventory_item.object['context']['terminal']
            print(f"{inventory_item.object['name']} removed terminal key") 

        for context_key in inventory_item.object['context'].keys():
            print(inventory_item.object['name'], end=" ")
            print(inventory_item.object['context'][context_key]['action']['route'], end=" --> ")
            inventory_item.object['context'][context_key]['action']['route'] = inventory_item.object['context'][context_key]['action']['route'].replace('ajax_', '')
            print(inventory_item.object['context'][context_key]['action']['route'])

    inventory_item.set()
