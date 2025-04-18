from asyncio import to_thread
from typing import Any, Dict

from obdii import commands

from basetypes import API


class StorageUpdater():
    def __init__(self, app: API):
        self.storage_lock = app.storage_lock
        self.storage = app.storage
        self.task_group = app.task_group

    def update_storage(self, cp_storage: Dict[str, Any]):        
        async def update():
            async with self.storage_lock:
                keys_to_remove = set(cp_storage.keys()) - set(self.storage.keys())

                for key in keys_to_remove:
                    cp_storage.pop(key)

                self.storage.update(cp_storage)

        self.task_group.create_task(update())

def background_fetch(app: API) -> None:
    updater = StorageUpdater(app)
    stop = app.polling_event.is_set

    while not stop():
        conn = app.obd
        cp_storage = app.storage.copy()

        for command_name in cp_storage.keys():
            try:
                response = conn.query(commands[command_name])
                cp_storage[command_name] = response.value
            except KeyError:
                cp_storage[command_name] = f"Error: {command_name} not found"
            except Exception as e:
                cp_storage[command_name] = f"CRITError: {str(e)}"

        updater.update_storage(cp_storage)

async def run_blocking(app: API) -> None:
    await to_thread(background_fetch, app)