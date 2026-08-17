import asyncio
import time
import os
from dotenv import load_dotenv

load_dotenv()

from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.task import PipelineTask
from pipecat.pipeline.runner import PipelineRunner
from pipecat.frames.frames import TranscriptionFrame, TextFrame, AudioRawFrame, EndFrame, LLMFullResponseStartFrame
from pipecat.processors.frame_processor import FrameProcessor, FrameDirection
from pipecat.services.openai.llm import OpenAILLMService
from pipecat.services.cartesia.tts import CartesiaTTSService
from app.adapters.pipecat.adapter import FastSentenceAggregator
from pipecat.processors.aggregators.llm_response_universal import LLMUserAggregator
from pipecat.processors.aggregators.llm_context import LLMContext

class LatencyTracker(FrameProcessor):
    def __init__(self):
        super().__init__()
        self.t_start = 0
        self.t_llm_first = 0
        self.t_first_sentence = 0
        self.t_tts_first = 0

    async def process_frame(self, frame, direction):
        now = time.perf_counter()
        
        if isinstance(frame, TranscriptionFrame):
            self.t_start = now
            print(f"[{now:.3f}] STT Final Transcript received (0ms)")
        elif isinstance(frame, LLMFullResponseStartFrame) and not self.t_llm_first:
            self.t_llm_first = now
            print(f"[{now:.3f}] LLM First Token (+{(self.t_llm_first - self.t_start)*1000:.0f}ms)")
        elif isinstance(frame, TextFrame) and len(frame.text) >= 5 and frame.text.strip()[-1] in '.?!':
            if not self.t_first_sentence:
                self.t_first_sentence = now
                print(f"[{now:.3f}] First Complete Sentence for TTS (+{(self.t_first_sentence - self.t_start)*1000:.0f}ms): {frame.text}")
        elif isinstance(frame, AudioRawFrame):
            if not self.t_tts_first:
                self.t_tts_first = now
                print(f"[{now:.3f}] TTS First Audio (+{(self.t_tts_first - self.t_start)*1000:.0f}ms)")
                await self.push_frame(EndFrame())
                return
                
        await super().process_frame(frame, direction)

async def main():
    llm = OpenAILLMService(
        api_key=os.getenv("OPENAI_API_KEY"),
        settings=OpenAILLMService.Settings(model="gpt-4o-mini", extra={"reasoning_effort": "none"})
    )
    tts = CartesiaTTSService(
        api_key=os.getenv("CARTESIA_API_KEY"),
        settings=CartesiaTTSService.Settings(voice=os.getenv("CARTESIA_VOICE_ID", "95d51f79-c397-46f9-b49a-23763d3eaa2d"))
    )
    
    context = LLMContext(messages=[{"role": "system", "content": "You are a helpful assistant. Keep your answer under 10 words."}])
    user_agg = LLMUserAggregator(context)
    
    tracker = LatencyTracker()
    aggregator = FastSentenceAggregator()
    
    pipeline = Pipeline([tracker, user_agg, llm, aggregator, tracker, tts, tracker])
    task = PipelineTask(pipeline)
    runner = PipelineRunner()
    
    async def push_transcript():
        await asyncio.sleep(1)
        from pipecat.frames.frames import UserStartedSpeakingFrame, UserStoppedSpeakingFrame
        await task.queue_frame(UserStartedSpeakingFrame())
        await task.queue_frame(TranscriptionFrame(text="Hi there! Can you tell me a joke?", user_id="user", timestamp="now"))
        await task.queue_frame(UserStoppedSpeakingFrame())
        
    asyncio.create_task(push_transcript())
    await runner.run(task)

if __name__ == "__main__":
    asyncio.run(main())
