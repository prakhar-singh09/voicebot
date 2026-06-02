from livekit import api
import os


def create_token(identity: str):
    api_key = os.getenv("LIVEKIT_API_KEY")
    api_secret = os.getenv("LIVEKIT_API_SECRET")
    room = os.getenv("LIVEKIT_ROOM", "voicebot-room")

    if not api_key or not api_secret:
        raise RuntimeError("LIVEKIT_API_KEY and LIVEKIT_API_SECRET must be set")

    token = api.AccessToken(
        api_key,
        api_secret
    )

    token.with_identity(identity)

    token.with_grants(
        api.VideoGrants(
            room_join=True,
            room=room
        )
    )

    return token.to_jwt()
