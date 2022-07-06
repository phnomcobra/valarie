from valarie.dao.document import Collection;

inventory = Collection('inventory')

for current in inventory.find():
    if 'context' in current.object.keys():
        if 'terminal' in current.object['context'].keys():
            del current.object['context']['terminal']
            print(f"{current.object['name']} removed terminal key")

        for context_key in current.object['context'].keys():
            print(current.object['name'], end=" ")
            print(current.object['context'][context_key]['action']['route'], end=" --> ")
            current.object['context'][context_key]['action']['route'] = current.object['context'][context_key]['action']['route'].replace('ajax_', '')
            print(current.object['context'][context_key]['action']['route'])

    if 'body' in current.object.keys():
        current.object['body'] = str(current.object['body']).replace(
            'valarie.model.datastore',
            'valarie.dao.datastore'
        )

    current.set()
