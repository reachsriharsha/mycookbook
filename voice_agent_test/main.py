import logging
from dotenv import load_dotenv
from livekit.agents import JobContext, WorkerOptions, cli
from livekit.agents.voice import Agent, AgentSession
from livekit.plugins import openai, sarvam

# Load environment variables
load_dotenv()

# Set up logging
logger = logging.getLogger("voice-agent")
logger.setLevel(logging.INFO)


class VoiceAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            # Your agent's personality and instructions
            instructions="""
                You are a helpful voice assistant.
                Be friendly, concise, and conversational.
                Speak naturally as if you're having a real conversation.
            """,
            
            # Saarika STT - Converts speech to text
            stt=sarvam.STT(
                language="unknown",  # Auto-detect language, or use "en-IN", "hi-IN", etc.
                model="saarika:v2.5"
            ),
            
            # OpenAI LLM - The "brain" that processes and generates responses
            #llm=openai.LLM(model="gpt-4o"),
            llm=openai.LLM.with_ollama(
                    model="gemma3:4b",
                    base_url="http://172.29.136.30:11435",
            ),
            
            # Bulbul TTS - Converts text to speech
            tts=sarvam.TTS(
                target_language_code="en-IN",
                model="bulbul:v2",
                speaker="anushka"  # Female: anushka, manisha, vidya, arya | Male: abhilash, karun, hitesh
            ),
        )
    
    async def on_enter(self):
        """Called when user joins - agent starts the conversation"""
        self.session.generate_reply()


async def entrypoint(ctx: JobContext):
    """Main entry point - LiveKit calls this when a user connects"""
    logger.info(f"User connected to room: {ctx.room.name}")
    
    # Create and start the agent session
    session = AgentSession()
    await session.start(
        agent=VoiceAgent(),
        room=ctx.room
    )


if __name__ == "__main__":
    # Run the agent
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
