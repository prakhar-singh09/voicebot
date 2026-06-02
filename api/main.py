import os
import logging
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from .token import create_token
from api.agent import dispatch_agent

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

LOG_DIR = Path(__file__).resolve().parents[1] / "logs"
LOG_DIR.mkdir(exist_ok=True)

api_logger = logging.getLogger("voicebot.api")
api_logger.setLevel(logging.INFO)
api_logger.propagate = False

api_log_path = LOG_DIR / "api.log"
if not any(
    isinstance(handler, logging.FileHandler)
    and Path(handler.baseFilename) == api_log_path
    for handler in api_logger.handlers
):
    handler = logging.FileHandler(api_log_path, encoding="utf-8")
    handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    )
    api_logger.addHandler(handler)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    api_logger.info("request start method=%s path=%s", request.method, request.url.path)
    try:
        response = await call_next(request)
    except Exception:
        api_logger.exception("request failed method=%s path=%s", request.method, request.url.path)
        raise

    api_logger.info(
        "request end method=%s path=%s status=%s",
        request.method,
        request.url.path,
        response.status_code,
    )
    return response


@app.get("/token")
def get_token(name: str):
    if not name.strip():
        raise HTTPException(status_code=400, detail="name is required")

    jwt_token = create_token(name)
    livekit_url = os.getenv("LIVEKIT_URL", "ws://localhost:7880")
    room = os.getenv("LIVEKIT_ROOM", "voicebot-room")
    api_logger.info("issued token identity=%s room=%s livekit_url=%s", name, room, livekit_url)

    return {
        "token": jwt_token,
        "url": livekit_url,
        "room": room,
    }


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/agent/start")
async def start_agent():

    room = os.getenv("LIVEKIT_ROOM", "voicebot-room")

    await dispatch_agent(room)

    return {
        "success": True,
        "room": room,
    }   