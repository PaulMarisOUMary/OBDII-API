from asyncio import TaskGroup
from contextlib import asynccontextmanager
from fastapi import APIRouter, HTTPException

from basetypes import API, RawRequest
from obdii import OBDII

@asynccontextmanager
async def lifespan(app: API):
    async with TaskGroup() as tg:
        app.task_group = tg
        app.obd = OBDII()

        # ! TODO Remove this
        app.obd.connect("COM5", fast=False)
        for monitor in app.obd.get_command_names():
            app.obd.add_monitor(monitor)

        background_task = tg.create_task(app.obd.background_fetch())
        yield

        app.obd.monitoring_on = False
        background_task.cancel()

router = APIRouter()

def app_factory():
    app = API(
        title="OBD2 API",
        version="0.1",
        lifespan=lifespan,
    )
    app.include_router(router)
    return app

@router.get("/status")
async def connection_status(raw_request: RawRequest):
    """Returns the current status of the OBD connection."""
    return {"connected": raw_request.app.obd.is_connected()}

@router.get("/data")
async def request_data(raw_request: RawRequest):
    """Returns the current OBD2 data being monitored."""
    return {"active_data": raw_request.app.obd.data}

