from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict
import json

router = APIRouter()

active_driver_connections: Dict[str, WebSocket] = {}
active_rider_connections: Dict[str, WebSocket] = {}


async def connect_driver(driver_key: str, websocket: WebSocket):
  await websocket.accept()
  active_driver_connections[driver_key] = websocket


async def connect_rider(rider_key: str, websocket: WebSocket):
  await websocket.accept()
  active_rider_connections[rider_key] = websocket


@router.websocket("/ws/driver/{driver_key}")
async def driver_ws(websocket: WebSocket, driver_key: str):
  await connect_driver(driver_key, websocket)
  try:
    while True:
      data = await websocket.receive_text()
      try:
        payload = json.loads(data)
      except Exception:
        payload = {"raw": data}
      for rider_ws in active_rider_connections.values():
        await rider_ws.send_text(json.dumps({
          "event": "driver_location",
          "driver_key": driver_key,
          "location": payload,
        }))
  except WebSocketDisconnect:
    active_driver_connections.pop(driver_key, None)


@router.websocket("/ws/rider/{rider_key}")
async def rider_ws(websocket: WebSocket, rider_key: str):
  await connect_rider(rider_key, websocket)
  try:
    while True:
      await websocket.receive_text()
  except WebSocketDisconnect:
    active_rider_connections.pop(rider_key, None)


async def broadcast_ride_request(ride_data: dict):
  for driver_ws in active_driver_connections.values():
    await driver_ws.send_text(json.dumps({
      "event": "new_request",
      "ride": ride_data,
    }))


async def broadcast_ride_status(ride_id: int, status: str, driver_name: str = ""):
  msg = json.dumps({
    "event": "ride_status",
    "ride_id": ride_id,
    "status": status,
    "driver_name": driver_name,
  })
  for ws in list(active_driver_connections.values()) + list(active_rider_connections.values()):
    await ws.send_text(msg)
