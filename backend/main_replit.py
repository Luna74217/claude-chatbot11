from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import json
from datetime import datetime
import os
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

app = FastAPI(title="Claude Chatbot API", version="1.0.0")

# CORS 설정 - Replit 환경에 맞게
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replit에서는 모든 origin 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 연결된 클라이언트들을 관리
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"클라이언트 연결됨. 총 연결 수: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print(f"클라이언트 연결 해제됨. 총 연결 수: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.get("/")
async def root():
    return {
        "message": "Claude Chatbot API Server",
        "status": "running",
        "websocket_endpoint": "/ws",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "connections": len(manager.active_connections)}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)

            # 채팅 메시지 처리
            if message_data.get("type") == "chat":
                user_message = message_data.get("message", "")
                
                # Claude API 키 확인
                api_key = os.getenv("ANTHROPIC_API_KEY")
                
                if api_key:
                    # 실제 Claude API 호출 (여기서는 시뮬레이션)
                    ai_response = f"Claude 응답: {user_message[::-1]} (실제로는 Claude API 호출)"
                else:
                    ai_response = "Claude API 키가 설정되지 않았습니다. .env 파일에 ANTHROPIC_API_KEY를 추가해주세요."

                # AI 응답 전송
                await manager.send_personal_message(json.dumps({
                    "type": "assistant",
                    "content": ai_response,
                    "timestamp": datetime.now().isoformat()
                }), websocket)
                
            # 파일 업로드 처리
            elif message_data.get("type") == "file":
                file_info = message_data.get("file", {})
                await manager.send_personal_message(json.dumps({
                    "type": "file_response",
                    "content": f"파일 '{file_info.get('name', 'unknown')}'을 받았습니다.",
                    "timestamp": datetime.now().isoformat()
                }), websocket)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("클라이언트 연결 해제됨")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 