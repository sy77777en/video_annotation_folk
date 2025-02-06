from socratic_program import SocraticProgram
from video_data import VideoData
from typing import List, Dict

PROMPT_SHOT_TRANSITION_YES = f"The video has one or more shot transitions (e.g., hard cuts and soft transitions). Please provide a brief description of video content before and after each transition."
PROMPT_SHOT_TRANSITION_NO = f"The video does not have any shot transitions. You don't need to provide any description."

class VanillaHumanPolicy(SocraticProgram):
    def __init__(self):
        name = "Human Program (Vanilla)"
        info = "A program that prompts a human to provide structured captions for Caption Everything."
        self.caption_fields_dict = {
            "shot_transition": "shot transition",
            "subject_description": "subject description",
            "spatial_framing_and_motion": "spatial framing and motion",
            "single_subject_action": "single subject action",
            "subject_object_interaction": "subject-object interaction",
            "subject_subject_interaction": "subject-subject interaction",
            "group_action": "group action",
            "scene_description": "scene description",
            "scene_motion": "scene motion",
            "camera_description": "camera description",
            "camera_motion": "camera motion",
        }
        caption_fields = list(self.caption_fields_dict.keys())
        super().__init__(name, info, caption_fields)
    
    def __call__(self, data: VideoData) -> Dict[str, str]:
        """Given a VideoData instance, return a dictionary of prompts for structured captions."""
        if data.cam_motion.has_shot_transition or data.cam_motion.has_transition:
            DEFAULT_PROMPT = "Due to shot transitions in the video, you do not need to describe {}."
            policy = {field: DEFAULT_PROMPT.format(self.caption_fields_dict[field]) for field in self.caption_fields if not field == "shot_transition"}
            policy["shot_transition"] = PROMPT_SHOT_TRANSITION_YES
            return policy

        subject_description_policy = self.get_subject_description_policy(data)
        scene_description_policy = self.get_scene_description_policy(data)
        camera_description_policy = self.get_camera_description_policy(data)
        shot_transition_policy = {"shot_transition": PROMPT_SHOT_TRANSITION_NO}
        return {**shot_transition_policy, **subject_description_policy, **scene_description_policy, **camera_description_policy}
        
    def get_subject_description_policy(self, data: VideoData):
        subject_policy = VanillaSubjectPolicy()
        return subject_policy(data)
    
    def get_scene_description_policy(self, data: VideoData):
        scene_policy = VanillaScenePolicy()
        return scene_policy(data)
    
    def get_camera_description_policy(self, data: VideoData):
        camera_policy = VanillaCameraPolicy()
        return camera_policy(data)
    

class VanillaSubjectPolicy(SocraticProgram):
    def __init__(self):
        name = "Human Policy Subject"
        info = "A policy that prompts a human to provide structured captions for Subject."
        caption_fields = ["subject_description", "spatial_framing_and_motion", "single_subject_action", "subject_object_interaction", "subject_subject_interaction"]
        super().__init__(name, info, caption_fields)
    
    def __call__(self, data: VideoData) -> Dict[str, str]:
        """Given a VideoData instance, return a dictionary of prompts for structured captions."""
        policy = {
            "subject_description": "Describe the subject in the video.",
            "spatial_framing_and_motion": "Describe the spatial framing and motion of the subject.",
            "single_subject_action": "Describe the actions of the subject.",
            "subject_object_interaction": "Describe the interactions between the subject and objects.",
            "subject_subject_interaction": "Describe the interactions between the subject and other subjects."
        }
        return policy
    

class VanillaScenePolicy(SocraticProgram):
    def __init__(self):
        name = "Human Policy Scene"
        info = "A policy that prompts a human to provide structured captions for Scene."
        caption_fields = ["scene_description", "scene_motion"]
        super().__init__(name, info, caption_fields)
    
    def __call__(self, data: VideoData) -> Dict[str, str]:
        """Given a VideoData instance, return a dictionary of prompts for structured captions."""
        policy = {
            "scene_description": "Describe the scene in the video.",
            "scene_motion": "Describe the motion of the scene."
        }
        return policy
    

class VanillaCameraPolicy(SocraticProgram):
    def __init__(self):
        name = "Human Policy Camera"
        info = "A policy that prompts a human to provide structured captions for Camera."
        caption_fields = ["camera_description", "camera_motion"]
        super().__init__(name, info, caption_fields)
    
    def __call__(self, data: VideoData) -> Dict[str, str]:
        """Given a VideoData instance, return a dictionary of prompts for structured captions."""
        policy = {
            "camera_description": "Describe the camera in the video.",
            "camera_motion": "Describe the motion of the camera."
        }
        return policy