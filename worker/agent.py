import asyncio
import os
from livekit.agents import (
    AutoSubscribe,
    JobContext,
    WorkerOptions,
    cli,
)
from livekit.agents.voice import Agent, AgentSession
from livekit.plugins import cartesia, groq, silero

GROQ_KEY = os.environ.get("GROQ_API_KEY", "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")
CARTESIA_KEY = os.environ.get("CARTESIA_API_KEY", "sk_car_PgGSaoajYuvFo3TXJb7nh9")
LIVEKIT_URL = os.environ.get("LIVEKIT_URL", "wss://open-voice-agent-mbfh49s1.livekit.cloud")
LIVEKIT_API_KEY = os.environ.get("LIVEKIT_API_KEY", "APIog2ZEydoX7Aw")
LIVEKIT_API_SECRET = os.environ.get("LIVEKIT_API_SECRET", "9U3CmxVTSAHeogAlFUtNNBVYfyaf8N8SiTKrfEuRNePE")

os.environ["GROQ_API_KEY"] = GROQ_KEY
os.environ["CARTESIA_API_KEY"] = CARTESIA_KEY
os.environ["LIVEKIT_URL"] = LIVEKIT_URL
os.environ["LIVEKIT_API_KEY"] = LIVEKIT_API_KEY
os.environ["LIVEKIT_API_SECRET"] = LIVEKIT_API_SECRET

async def entrypoint(ctx: JobContext):
    print(f"--> [Cloud Agent] Call joined room: {ctx.room.name}")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    agent = Agent(
        instructions="""You are a sharp, articulate conversational assistant speaking on a phone call.
Give intelligent, nuanced, yet concise answers (1-2 short sentences max).
Never use markdown, bullet points, asterisks, or robotic phrasing.
React genuinely to what the user said, then conclude with an engaging question.""",
        vad=silero.VAD.load(),
        stt=groq.STT(model="whisper-large-v3-turbo", api_key=GROQ_KEY),
        llm=groq.LLM(
            model="groq/compound-mini",
            api_key=GROQ_KEY,
        ),
        tts=cartesia.TTS(
            voice="33d406dd-ff6f-4be7-a7f5-8b1ba183b3e4",
            api_key=CARTESIA_KEY,
        ),
    )

    session = AgentSession(
        vad=agent.vad,
        turn_detection="vad",
    )
    await session.start(agent, room=ctx.room)
    await asyncio.sleep(0.5)
    await session.say("Hey! What are we diving into today?", allow_interruptions=True)

if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            ws_url=LIVEKIT_URL,
            api_key=LIVEKIT_API_KEY,
            api_secret=LIVEKIT_API_SECRET,
            agent_name="voice-agent",
        )
    )
