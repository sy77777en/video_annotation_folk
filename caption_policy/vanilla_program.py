from socratic_program import SocraticProgram
from video_data import VideoData
from typing import List, Dict
import json

def read_text_file(file_path: str) -> str:
    """Reads and returns the content of a text file as a string."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read().strip()

def read_json_file(file_path: str) -> Dict:
    """Reads and returns the content of a JSON file as a dictionary."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

class VanillaPolicy(SocraticProgram):
    def __init__(self):
        name = "Vanilla Program based on existing labels"
        info = "A program that prompts VLMs to provide structured captions for Caption Everything."
        self.caption_fields_dict = {
            "subject_description": "subject description",
            "subject_motion_dynamics": "subject motion and dynamics",
            "scene_composition_dynamics": "scene composition and dynamics",
            "spatial_framing_dynamic": "spatial framing and dynamics",
            "camera_motion_dynamics": "camera motion and dynamics",
        }
        caption_fields = list(self.caption_fields_dict.keys())
        super().__init__(name, info, caption_fields)
    
    def __call__(self, data: VideoData) -> Dict[str, str]:
        """Given a VideoData instance, return a dictionary of prompts for structured captions."""
        if data.cam_motion.has_shot_transition or data.cam_motion.has_transition:
            raise ValueError("Shot transitions are not supported in this policy.")

        subject_description_policy = self.get_subject_description_policy(data)
        subject_motion_dynamics_policy = self.get_subject_motion_dynamics_policy(data)
        scene_composition_dynamics_policy = self.get_scene_composition_dynamics_policy(data)
        spatial_framing_dynamics_policy = self.get_spatial_framing_dynamics_policy(data)
        camera_framing_dynamics_policy = self.get_camera_framing_dynamics_policy(data)
        return {**subject_description_policy, **scene_composition_dynamics_policy, **camera_framing_dynamics_policy}
        
    def get_subject_description_policy(self, data: VideoData):
        subject_policy = VanillaSubjectPolicy()
        return subject_policy(data)
    
    def get_subject_motion_dynamics_policy(self, data: VideoData):
        subject_motion_policy = VanillaSubjectMotionPolicy()
        return subject_motion_policy(data)
    
    def get_scene_composition_dynamics_policy(self, data: VideoData):
        scene_policy = VanillaScenePolicy()
        return scene_policy(data)
    
    def get_spatial_framing_dynamics_policy(self, data: VideoData):
        spatial_policy = VanillaSpatialPolicy()
        return spatial_policy(data)
    
    def get_camera_framing_dynamics_policy(self, data: VideoData):
        camera_policy = VanillaCameraPolicy()
        return camera_policy(data)
    

class VanillaSubjectPolicy(SocraticProgram):
    def __init__(self):
        name = "Vanilla Subject Description"
        info = "A policy that use existing labels to prompt a human or model to provide structured captions for Subject."
        caption_fields = ["subject_description"]
        super().__init__(name, info, caption_fields)
    
    def __call__(self, data: VideoData) -> Dict[str, str]:
        """Given a VideoData instance, return a dictionary of prompts for structured captions."""
        return {
            "subject_description": self.get_description(data)
        }
    
    def get_description(self, data: VideoData) -> Dict[str, str]:
        if data.cam_motion.has_shot_transition or data.cam_motion.has_transition:
            raise ValueError("Shot transitions are not supported in this policy.")
        
        if data.cam_setup.is_framing_subject is False:
            # This much be a Scenery shot
            return ("The video is a scenery shot. You do not need to describe the subject. "
                    "Please concisely specify the type of scenery shot (e.g., a landscape or cityscape scenery shot)."
                    "Explain why there is no main subject, such as the focus being on the environment, atmosphere, "
                    "or scale rather than a specific object. If relevant, describe the shot's purpose, whether it is an "
                    "establishing shot setting the scene or providing context, or a FPV shot that creates an immersive experience.")
        
        policy = read_text_file("policy/subject_description/policy.txt")
        if data.cam_setup.is_framing_subject is None:
            # Including complex shot with description others, or multiple subject without a clear focus
            # If is others description, then prompt to use this description to complement the subject description
            # Note that there may not be a subject in focus. 
            if data.cam_setup.shot_size_description_type == "others":
                pass # Do nothing
            elif data.cam_setup.is_just_many_subject_no_focus_shot:
                policy += "\n Please note that this video contains **multiple subjects without a clear main focus**. Briefly describe the salient subjects while providing a concise overview of secondary subjects, or describe all subjects collectively as a group if that is more appropriate."
                return policy
            else:
                raise ValueError("When framing subject is None, the shot size description must be others or many_subject_no_focus.")
        else:
            
            if data.cam_setup.is_just_human_shot:
                policy += "\n Please note that the video features salient **human** subjects, so the description should focus on them."
            elif data.cam_setup.is_just_non_human_shot:
                policy += "\n Please note that the video features salient **non-human** subjects, so the description should focus on them."
            elif data.cam_setup.is_just_change_of_subject_shot:
                if data.cam_setup.subject_revealing:
                    policy += "\b Please note that the video is a **revealing shot of the subject**, so the description should reflect this by explaining how the subject is revealed through either subject movement or camera movement."
                elif data.cam_setup.subject_hiding:
                    policy += "\n Please note that the video features the main subjects **disappearing from the frame**, so the description should reflect this by explaining how they exit, whether through subject movement or camera movement."
                elif data.cam_setup.subject_switching:
                    policy += "\n Please note that the video features the main subjects **switching from one to another**, so the description should reflect this by explaining how the transition occurs, whether through subject movement or camera movement."
                else:
                    raise ValueError("When is_just_change_of_subject_shot is True, either subject_revealing, subject_hiding, or subject_switching must be True.")
            elif data.cam_setup.is_just_clear_subject_dynamic_size_shot:
                policy += "\n Please note that the **main subject’s framing is not stable** throughout the video, so the description should reflect this."
            elif data.cam_setup.is_just_clear_subject_atypical_shot:
                policy += "\n Please note that the main subjects in this video exhibit **atypical posture or anatomy**, so the description should reflect this."
            elif data.cam_setup.is_just_many_subject_one_focus_shot:
                policy += "\n Please note that the video features **multiple subjects with a clear main focus**, so the description should focus on the main subject while providing a concise overview of secondary subjects."
            elif data.cam_setup.is_just_different_subject_in_focus_shot:
                policy += "\n Please note that the video features **multiple different subjects in focus**, so the description should clearly distinguish their types and relationships."
            else:
                assert data.cam_setup.shot_size_description != ""
                policy += "\n" + read_text_file("policy/subject_description/has_shot_size_description.txt").format(data.cam_setup.shot_size_description)
        return policy
    
class VanillaScenePolicy(SocraticProgram):
    def __init__(self):
        name = "Vanilla Scene Description"
        info = "A policy that use existing labels to prompt a human or model to provide structured captions for Scene."
        caption_fields = ["scene_composition_dynamics"]
        super().__init__(name, info, caption_fields)
    
    def __call__(self, data: VideoData) -> Dict[str, str]:
        """Given a VideoData instance, return a dictionary of prompts for structured captions."""
        policy = {
            "scene_composition_dynamics": self.get_description(data)
        }
        return policy

    def get_description(self, data: VideoData) -> Dict[str, str]:
        if data.cam_motion.has_shot_transition or data.cam_motion.has_transition:
            raise ValueError("Shot transitions are not supported in this policy.")
        
        if data.cam_setup.is_framing_subject is False:
            # This much be a Scenery shot
            return read_text_file("policy/scene_composition_dynamics/scenery.txt")
        
        policy = read_text_file("policy/scene_composition_dynamics/policy.txt")
        if data.cam_setup.is_framing_subject is None:
            # Including complex shot with description others, or multiple subject without a clear focus
            # If is others description, then prompt to use this description to complement the subject description
            # Note that there may not be a subject in focus. 
            if data.cam_setup.shot_size_description_type == "others":
                pass

class VanillaSubjectMotionPolicy(SocraticProgram):
    def __init__(self):
        name = "Vanilla Subject Motion & Dynamics Description"
        info = "A policy that use existing labels to prompt a human or model to provide structured captions for Subject Motion and Dynamics."
        caption_fields = ["subject_motion_dynamics"]
        super().__init__(name, info, caption_fields)
    
    def __call__(self, data: VideoData) -> Dict[str, str]:
        """Given a VideoData instance, return a dictionary of prompts for structured captions."""
        return {
            "subject_motion_dynamics": self.get_description(data)
        }
    
    def get_description(self, data: VideoData) -> Dict[str, str]:
        if data.cam_motion.has_shot_transition or data.cam_motion.has_transition:
            raise ValueError("Shot transitions are not supported in this policy.")
        
        if data.cam_setup.is_framing_subject is False:
            # This much be a Scenery shot
            return read_text_file("policy/subject_motion_dynamics/scenery.txt")
        
        
        policy = read_text_file("policy/subject_motion_dynamics/policy.txt")
        if data.cam_setup.is_framing_subject is None:
            # Including complex shot with description others, or multiple subject without a clear focus
            # If is others description, then prompt to use this description to complement the subject description
            # Note that there may not be a subject in focus. 
            if data.cam_setup.shot_size_description_type == "others":
                pass # Do nothing
            elif data.cam_setup.is_just_many_subject_no_focus_shot:
                policy += "\n Please note that this video contains **multiple subjects without a clear main focus**. Briefly describe the salient motions and dynamics of the primary subjects while providing a concise overview of secondary movements, or describe all subjects' collective motion if that is more appropriate."
                return policy
            else:
                raise ValueError("When framing subject is None, the shot size description must be others or many_subject_no_focus.")
        else:
            
            if data.cam_setup.is_just_human_shot:
                policy += "\n Please note that the video features salient **human** subjects, so the description should focus on their motion and dynamics."
            elif data.cam_setup.is_just_non_human_shot:
                policy += "\n Please note that the video features salient **non-human** subjects, so the description should focus on their motion and dynamics."
            elif data.cam_setup.is_just_change_of_subject_shot:
                if data.cam_setup.subject_revealing:
                    policy += "\b Please note that the video is a **revealing shot of the subject**, so the description should reflect this by explaining how the subject is revealed through either subject movement or camera movement."
                elif data.cam_setup.subject_hiding:
                    policy += "\n Please note that the video features the main subjects **disappearing from the frame**, so the description should reflect this by explaining how they exit, whether through subject movement or camera movement."
                elif data.cam_setup.subject_switching:
                    policy += "\n Please note that the video features the main subjects **switching from one to another**, so the description should first describe the first subject’s motion and dynamics, followed by the second’s."
                else:
                    raise ValueError("When is_just_change_of_subject_shot is True, either subject_revealing, subject_hiding, or subject_switching must be True.")
            elif data.cam_setup.is_just_clear_subject_dynamic_size_shot:
                policy += "\n Please note that the **main subject’s framing is not stable** throughout the video, so the description should reflect how their motion and dynamics contribute to this instability."
            elif data.cam_setup.is_just_clear_subject_atypical_shot:
                policy += "\n Please note that the main subjects in this video exhibit **atypical motion, posture, or anatomy**, so the description should reflect this."
            elif data.cam_setup.is_just_many_subject_one_focus_shot:
                policy += "\n Please note that the video features **multiple subjects with a clear main focus**, so the description should focus on the motion and dynamics of the main subject while providing a concise overview of secondary subjects' movements."
            elif data.cam_setup.is_just_different_subject_in_focus_shot:
                policy += "\n Please note that the video features **multiple different subjects in focus**, so the description should clearly distinguish their types, movement patterns, and interactions."
            else:
                # pass for complex shot with description
                pass
                
        assert data.cam_setup.subject_description != "", "Subject description must be provided before subject motion and dynamics description."
        policy += "\n" + read_text_file("policy/subject_motion_dynamics/has_subject_description.txt").format(data.cam_setup.subject_description)
        return policy


class VanillaSpatialPolicy(SocraticProgram):
    def __init__(self):
        name = "Vanilla Spatial Framing and Dynamics Description"
        info = "A policy that use existing labels to prompt a human or model to provide structured captions for Spatial Framing and Dynamics."
        caption_fields = ["spatial_framing_dynamics"]
        super().__init__(name, info, caption_fields)
    
    def __call__(self, data: VideoData) -> Dict[str, str]:
        """Given a VideoData instance, return a dictionary of prompts for structured captions."""
        return {
            "spatial_framing_dynamics": self.get_description(data)
        }
    
    def get_description(self, data: VideoData) -> Dict[str, str]:
        if data.cam_motion.has_shot_transition or data.cam_motion.has_transition:
            raise ValueError("Shot transitions are not supported in this policy.")
        
        if data.cam_setup.is_framing_subject is False:
            # This much be a Scenery shot
            return ("The video is a scenery shot. You do not need to describe the subject. "
                    "Please concisely specify the type of scenery shot (e.g., a landscape or cityscape scenery shot)."
                    "Explain why there is no main subject, such as the focus being on the environment, atmosphere, "
                    "or scale rather than a specific object. If relevant, describe the shot's purpose, whether it is an "
                    "establishing shot setting the scene or providing context, or a FPV shot that creates an immersive experience.")
        
        policy = read_text_file("policy/subject_description/policy.txt")
        if data.cam_setup.is_framing_subject is None:
            # Including complex shot with description others, or multiple subject without a clear focus
            # If is others description, then prompt to use this description to complement the subject description
            # Note that there may not be a subject in focus. 
            if data.cam_setup.shot_size_description_type == "others":
                pass # Do nothing
            elif data.cam_setup.is_just_many_subject_no_focus_shot:
                policy += "\n Please note that this video contains **multiple subjects without a clear main focus**. Briefly describe the salient subjects while providing a concise overview of secondary subjects, or describe all subjects collectively as a group if that is more appropriate."
                return policy
            else:
                raise ValueError("When framing subject is None, the shot size description must be others or many_subject_no_focus.")
        else:
            
            if data.cam_setup.is_just_human_shot:
                policy += "\n Please note that the video features salient **human** subjects, so the description should focus on them."
            elif data.cam_setup.is_just_non_human_shot:
                policy += "\n Please note that the video features salient **non-human** subjects, so the description should focus on them."
            elif data.cam_setup.is_just_change_of_subject_shot:
                if data.cam_setup.subject_revealing:
                    policy += "\b Please note that the video is a **revealing shot of the subject**, so the description should reflect this by explaining how the subject is revealed through either subject movement or camera movement."
                elif data.cam_setup.subject_hiding:
                    policy += "\n Please note that the video features the main subjects **disappearing from the frame**, so the description should reflect this by explaining how they exit, whether through subject movement or camera movement."
                elif data.cam_setup.subject_switching:
                    policy += "\n Please note that the video features the main subjects **switching from one to another**, so the description should reflect this by explaining how the transition occurs, whether through subject movement or camera movement."
                else:
                    raise ValueError("When is_just_change_of_subject_shot is True, either subject_revealing, subject_hiding, or subject_switching must be True.")
            elif data.cam_setup.is_just_clear_subject_dynamic_size_shot:
                policy += "\n Please note that the **main subject’s framing is not stable** throughout the video, so the description should reflect this."
            elif data.cam_setup.is_just_clear_subject_atypical_shot:
                policy += "\n Please note that the main subjects in this video exhibit **atypical posture or anatomy**, so the description should reflect this."
            elif data.cam_setup.is_just_many_subject_one_focus_shot:
                policy += "\n Please note that the video features **multiple subjects with a clear main focus**, so the description should focus on the main subject while providing a concise overview of secondary subjects."
            elif data.cam_setup.is_just_different_subject_in_focus_shot:
                policy += "\n Please note that the video features **multiple different subjects in focus**, so the description should clearly distinguish their types and relationships."
            else:
                assert data.cam_setup.shot_size_description != ""
                policy += "\n" + read_text_file("policy/subject_description/has_shot_size_description.txt").format(data.cam_setup.shot_size_description)
        return policy

    

class VanillaCameraPolicy(SocraticProgram):
    def __init__(self):
        name = "Human Policy Camera"
        info = "A policy that prompts a human to provide structured captions for Camera."
        caption_fields = ["camera_framing_dynamics", "camera_motion"]
        super().__init__(name, info, caption_fields)
    
    def __call__(self, data: VideoData) -> Dict[str, str]:
        """Given a VideoData instance, return a dictionary of prompts for structured captions."""
        policy = {
            "camera_framing_dynamics": "Describe the camera in the video.",
            "camera_motion": "Describe the motion of the camera."
        }
        return policy