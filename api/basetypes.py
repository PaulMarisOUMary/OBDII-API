from asyncio import TaskGroup
from fastapi import Body, FastAPI, Request
from pydantic import BaseModel
from typing import Any, Literal, Optional

from obdii import OBDII

# API and Router

class API(FastAPI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.task_group: TaskGroup
        self.obd: OBDII

# # Requests and Responses

class RawRequest(Request):
    @property
    def app(self) -> API:
        return super().app