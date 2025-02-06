from typing import List, Dict
from video_data import VideoData

class SocraticProgram:
    def __init__(self, name: str, info: str, caption_fields: List[str]):
        self.name = name
        self.info = info
        self.caption_fields = caption_fields
    
    def __str__(self):
        return f"{self.name}: {self.info} \n Caption Fields: {self.caption_fields}"

    def __call__(self, data: VideoData) -> Dict[str, str]:
        """Given a VideoData instance, return a dictionary of prompts for structured captions."""
        raise NotImplementedError("Subclasses must implement this method")