from fastapi import FastAPI, Request
import os
import threading
import signal
import logging
import time
from typing import List
import uuid
from .routers import web_socket, backtest

DIR_HOME = os.path.expanduser('~') # To be changed during deployment
DIR_NUFT = os.path.join(DIR_HOME, '.nuft')

logger = logging.getLogger(__name__)

app = FastAPI()
app.include_router(web_socket.router)
app.include_router(backtest.router)

@app.on_event("startup")
async def startup_event():
    # Start interchange
    # Start and connect to redis
    pass


@app.get('/')
async def get_status():
    """Checks whether server is operational"""
    return 200

def main():
    import uvicorn
    uvicorn.run("core.server.app:app", port=5000)

