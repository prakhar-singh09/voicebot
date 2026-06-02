import logging
import os

from livekit.agents import Agent, AgentSession, JobContext, WorkerOptions, cli
from livekit.plugins import openai, silero

from bot.config import (
    LIVEKIT_API_KEY,
    LIVEKIT_API_SECRET,
    LIVEKIT_URL,
    LLM_API_KEY,
    LLM_BASE_URL,
    LLM_MODEL,
    TTS_VOICE,
    WHISPER_BASE_URL,
    WHISPER_MODEL,
)
from bot.edge_tts_plugin import EdgeTTS
from bot.logging_setup import setup_file_logger



for key in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy"):
    os.environ.pop(key, None)
os.environ["NO_PROXY"] = "127.0.0.1,localhost"
os.environ["no_proxy"] = "127.0.0.1,localhost"

logger = setup_file_logger("voicebot.agent", "agent.log", logging.DEBUG)
logging.getLogger("livekit").setLevel(logging.DEBUG)
logging.getLogger("livekit").addHandler(logger.handlers[0])
import re

ARABIC_RE = re.compile(r"[\u0600-\u06FF]")

def contains_arabic(text: str) -> bool:
    return bool(ARABIC_RE.search(text))

DEVA_REWRITE_PROMPT = """
Convert the following text to Hindi written ONLY in Devanagari script.

Rules:
- Output only the converted sentence.
- Never use Urdu, Arabic, or Persian script.
- Do not explain anything.
"""


INSTRUCTIONS = """
You are a low-latency voice assistant.

Rules:
- Reply in the same language as the user.
- Hindi MUST always be written in Devanagari.
- Never output Urdu script.
- Never output Arabic script.
- Never output Persian script.
- If input contains Urdu script representing Hindi speech,
  first convert it to Devanagari and then answer.
- Keep replies short and conversational.
"""

async def normalize_for_tts(llm_client, text: str) -> str:
    if not contains_arabic(text):
        return text

    logger.warning("Arabic/Urdu script detected: %s", text)

    response = await llm_client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {
                "role": "system",
                "content": DEVA_REWRITE_PROMPT,
            },
            {
                "role": "user",
                "content": text,
            },
        ],
        temperature=0,
    )

    fixed = response.choices[0].message.content.strip()

    logger.info("Rewritten to Devanagari: %s", fixed)

    return fixed


async def entrypoint(ctx: JobContext):
    print("=" * 50)
    print("ENTRYPOINT EXECUTED")
    print("=" * 50)
    logger.info("ENTRYPOINT EXECUTED")
    participant_identity = getattr(ctx.job, "participant_identity", None)
    logger.info("job received room=%s participant=%s", ctx.room.name, participant_identity)
    await ctx.connect()
    logger.info("connected to LiveKit room=%s", ctx.room.name)

    vad = silero.VAD.load(
        min_speech_duration=0.05,
        min_silence_duration=0.25,
        prefix_padding_duration=0.15,
        activation_threshold=0.45,
    )

    session = AgentSession(
        vad=vad,
          stt=openai.STT(
          model=WHISPER_MODEL,
          base_url=WHISPER_BASE_URL,
          api_key=LLM_API_KEY,
          language="hi",
        ),
        llm=openai.LLM(
            model=LLM_MODEL,
            base_url=LLM_BASE_URL,
            api_key=LLM_API_KEY,
            temperature=0.2,
        ),
        tts=EdgeTTS(voice=TTS_VOICE),
        min_endpointing_delay=0.08,
        max_endpointing_delay=0.45,
        allow_interruptions=True,
    )

    @session.on("user_state_changed")
    def on_user_state_changed(event):
        logger.info("user state changed old=%s new=%s", event.old_state, event.new_state)

    @session.on("agent_state_changed")
    def on_agent_state_changed(event):
        logger.info("agent state changed old=%s new=%s", event.old_state, event.new_state)

    @session.on("user_input_transcribed")
    def on_user_input_transcribed(event):
        logger.info(
            "stt transcript final=%s speaker=%s language=%s text=%r",
            event.is_final,
            event.speaker_id,
            event.language,
            event.transcript,
        )

    @session.on("conversation_item_added")
    def on_conversation_item_added(event):
        item = event.item
        role = getattr(item, "role", "unknown")
        content = getattr(item, "content", "")
        logger.info("conversation item role=%s content=%r", role, content)

    @session.on("speech_created")
    def on_speech_created(event):
        logger.info(
            "tts speech created source=%s user_initiated=%s",
            event.source,
            event.user_initiated,
        )

    @session.on("error")
    def on_error(event):
        logger.exception(
            "pipeline error source=%s error=%r",
            event.source,
            event.error,
        )

    await session.start(
        agent=Agent(instructions=INSTRUCTIONS),
        room=ctx.room,
    )
    logger.info("agent session started")
if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            agent_name="voicebot",
            ws_url=LIVEKIT_URL,
            api_key=LIVEKIT_API_KEY,
            api_secret=LIVEKIT_API_SECRET,
        )
    )