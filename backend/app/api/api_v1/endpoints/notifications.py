from fastapi import APIRouter, WebSocket, Depends
from app.services.notification_service import manager

router = APIRouter()

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await manager.connect(user_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except Exception as e:
        manager.disconnect(user_id, websocket)