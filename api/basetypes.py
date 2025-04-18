from asyncio import Event, Lock, TaskGroup
from fastapi import FastAPI, Request
from typing import Any, Dict

from obdii import Connection

# API and Router

class API(FastAPI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.task_group: TaskGroup
        self.polling_event: Event
        self.obd: Connection
        self.storage_lock: Lock
        self.storage: Dict[str, Any]

class RawRequest(Request):
    @property
    def app(self) -> API:
        return super().app