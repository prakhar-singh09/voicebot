from livekit import api
from bot.config import (
    LIVEKIT_URL,
    LIVEKIT_API_KEY,
    LIVEKIT_API_SECRET,
)


async def dispatch_agent(room_name: str):
    lkapi = api.LiveKitAPI(
        url=LIVEKIT_URL,
        api_key=LIVEKIT_API_KEY,
        api_secret=LIVEKIT_API_SECRET,
    )

    try:
        await lkapi.agent_dispatch.create_dispatch(
            api.CreateAgentDispatchRequest(
                room=room_name,
                agent_name="voicebot",
            )
        )
    finally:
        await lkapi.aclose()