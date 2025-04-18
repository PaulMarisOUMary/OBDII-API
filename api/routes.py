from asyncio import to_thread
from typing import Any, Dict
from fastapi import APIRouter, Body, HTTPException

from basetypes import RawRequest
from polling import run_blocking


router = APIRouter()

@router.post("/connect")
async def connect_to_obd(raw_request: RawRequest, kwargs: Dict[str, Any] = Body(default={})):
    app = raw_request.app
    conn = app.obd

    if conn.is_connected():
        return {"status": "Already connected"}

    try:
        if not app.polling_event.is_set():
            app.polling_event.set()

        await to_thread(conn.connect, **kwargs)

        if not conn.is_connected():
            raise HTTPException(status_code=500, detail="Failed to connect")
        
        app.polling_event.clear()
        
        app.task_group.create_task(run_blocking(app))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to connect: {str(e)}")

    return {"status": "Connected successfully", "used_kwargs": kwargs}

@router.post("/disconnect")
async def disconnect_from_obd(raw_request: RawRequest):
    app = raw_request.app
    conn = app.obd

    if not conn.is_connected():
        return {"status": "Already disconnected"}

    app.polling_event.set()

    try:
        await to_thread(conn.close)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to disconnect: {str(e)}")

    return {"status": "Disconnected successfully"}

@router.get("/status")
async def status(raw_request: RawRequest):
    return {"status": raw_request.app.obd.is_connected()}

@router.get("/data")
async def request_data(raw_request: RawRequest):
    async with raw_request.app.storage_lock:
        return {"data": dict(raw_request.app.storage)}

@router.post("/add")
async def add_key(raw_request: RawRequest, key: str):
    key = key.upper()

    async with raw_request.app.storage_lock:
        raw_request.app.storage[key] = None
        return {"status": f"'{key}' added"}

@router.delete("/remove")
async def remove_key(raw_request: RawRequest, key: str):
    key = key.upper()

    async with raw_request.app.storage_lock:
        if key in raw_request.app.storage:
            del raw_request.app.storage[key]
            return {"status": f"'{key}' removed"}
        else:
            raise HTTPException(status_code=404, detail=f"Key '{key}' not found")