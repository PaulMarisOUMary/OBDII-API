import logging

from asyncio import sleep

from typing import Any, Dict, Optional, Set
from obd import OBD, commands, scan_serial # type: ignore

logging.getLogger("obd").setLevel(logging.CRITICAL)

class OBDII():
    def __init__(self) -> None:
        self.monitored: Set[str] = set()
        self.monitoring_on: bool = True
        self.connection: Optional[OBD] = None

        self._data: Dict[str, Any] = dict()

    @property
    def data(self) -> Dict[str, Any]:
        return self._data
    
    @data.setter
    def data(self, value: Dict[str, Any]) -> None:
        self._data = value

    def is_connected(self) -> bool:
        return self.connection is not None and self.connection.is_connected()

    def auto_connect(self) -> None:
        self.connection = OBD()

    def connect(self, port: str, baudrate=38400, *args, **kwargs) -> None:
        self.connection = OBD(portstr=port, baudrate=baudrate, *args, **kwargs)

    def query_byname(self, name: str) -> Any:
        if not self.connection or not self.is_connected():
            raise ValueError("Connection not established")
        
        if not commands.has_name(name):
            raise ValueError(f"Invalid command name: {name}")
        
        response = self.connection.query(commands[name])
        if response.is_null():
            return "No response"

        return str(response.value)

    def get_command_names(self) -> Set[str]:
        return {
            name for name in commands.__dict__.keys()
            if commands.has_name(name)
        }
    
    def add_monitor(self, name: str) -> None:
        if not commands.has_name(name):
            raise ValueError(f"Invalid command name: {name}")
        self.monitored.add(name)

    def remove_monitor(self, name: str) -> None:
        if name not in self.monitored:
            raise ValueError(f"Command {name} is not being monitored")
        self.monitored.discard(name)

    async def background_fetch(self) -> None:
        while self.monitoring_on:
            for name in self.monitored:
                self.data[name] = self.query_byname(name)
            await sleep(0.1)