from google import genai
import google.genai.types as types
from google.genai.types import Part
from llm import LLM
from typing import List
import os
import PIL.Image
from utils import extract_frames_to_pil

PROJECT_ID = "gen-lang-client-0141537462"

class Gemini(LLM):
    def __init__(self, model="gemini-2.0-flash-001"):
        # If extracted_frames is [], then use the entire video
        assert model in ["gemini-2.0-flash-001", "gemini-2.0-flash-lite-preview-02-05", "gemini-1.5-flash-001", "gemini-1.5-flash-8b-001", "gemini-1.5-pro-001"]
        os.environ["GOOGLE_CLOUD_PROJECT"] = PROJECT_ID
        self.client = genai.Client(vertexai=True, project=PROJECT_ID, location="us-central1")
        self.model = model
    
    def generate(self,
                 prompt: str,
                 images: List[str] = [],
                 video: str = "",
                 extracted_frames: List[int] = [],
                 **kwargs) -> str:
        """Generate text from a prompt. Optionally provide images or video."""
        if len(images) > 0 and len(video) > 0:
            raise ValueError("Error: Cannot provide both images and video")
        
        if len(images) > 0:
            imagery = [PIL.Image.open(image) for image in images]
        elif len(video) > 0:
            if len(extracted_frames) == 0:
                # Since extracted_frames is [], use the entire video
                imagery = [Part.from_uri(
                    file_uri=video,
                    mime_type=f"video/{video.split('.')[-1]}",
                )]
            else:
                # Extract specific frames from the video
                imagery = extract_frames_to_pil(video, extracted_frames)
        else:
            imagery = []
        
        contents = imagery
        contents.append(prompt)
        response = self.client.models.generate_content(
            model=self.model,
            contents=contents,
            config=types.GenerateContentConfig(
                **kwargs
            )
        )
        return response.text.strip()
            
if __name__ == "__main__":
    gemini = Gemini(
        model="gemini-2.0-flash-001",
    )
    print(gemini.generate(
        prompt="Describe this video in a concise and fluent manner.",
        video="https://huggingface.co/datasets/zhiqiulin/video_captioning/resolve/main/OCBYMQzG44U.30.11.mp4",
        extracted_frames=[],
        temperature=0.0,
    ))
    