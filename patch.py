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

    if 'type' in current.object.keys():
        if current.object['type'] == 'config':
            current.destroy()

# Remove the old templating and config objects
CONFIG_OBJUUID = "bec8aa75-575e-4014-961c-d2df363c66bf"
TASK_PROTO_OBJUUID = "4d22259a-8000-49c7-bb6b-cf8526dbff70"
CONSOLE_PROTO_OBJUUID = "d64e5c18-2fe8-495b-ace1-a3f0321b1629"
SETTINGS_CONTAINER_OBJUUID = "bcde4d54-9456-4b09-9bff-51022e799b30"
for objuuid in (
        CONFIG_OBJUUID,
        TASK_PROTO_OBJUUID,
        CONSOLE_PROTO_OBJUUID,
        SETTINGS_CONTAINER_OBJUUID
    ):
    inventory.get_object(objuuid).destroy()
