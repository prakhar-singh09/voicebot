import asyncio
import logging
import edge_tts
from livekit.agents import APIConnectOptions, APIConnectionError, DEFAULT_API_CONNECT_OPTIONS, tts
from livekit.agents.utils import aio


logger = logging.getLogger("voicebot.agent")


class EdgeTTS(tts.TTS):
    def __init__(self, *, voice: str = "hi-IN-MadhurNeural") -> None:
        super().__init__(
            capabilities=tts.TTSCapabilities(streaming=False),
            sample_rate=24000,
            num_channels=1,
        )
        self._voice = voice

    @property
    def label(self) -> str:
        return "edge_tts.TTS"

    @property
    def model(self) -> str:
        return "edge-tts"

    @property
    def provider(self) -> str:
        return "edge-tts"

    def synthesize(
        self, text: str, *, conn_options: APIConnectOptions = DEFAULT_API_CONNECT_OPTIONS
    ) -> tts.ChunkedStream:
        return EdgeTTSChunkedStream(tts=self, input_text=text, conn_options=conn_options, voice=self._voice)

class EdgeTTSChunkedStream(tts.ChunkedStream):
    def __init__(self, *, tts: tts.TTS, input_text: str, conn_options: APIConnectOptions, voice: str) -> None:
        super().__init__(tts=tts, input_text=input_text, conn_options=conn_options)
        self._voice = voice

    async def _run(self, output_emitter: tts.AudioEmitter) -> None:
        try:
            output_emitter.initialize(
                request_id="edge-tts",
                sample_rate=24000,
                num_channels=1,
                mime_type="audio/mpeg",
            )
            
            communicate = edge_tts.Communicate(self.input_text, self._voice)
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    output_emitter.push(chunk["data"])
            
            output_emitter.flush()
        except Exception as e:
            logger.exception("Edge TTS synthesis failed voice=%s text=%r", self._voice, self.input_text)
            raise APIConnectionError("Edge TTS synthesis failed") from e
