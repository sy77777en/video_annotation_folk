from socratic_program import SocraticProgram
from video_data import VideoData
from typing import List, Dict
import json
import os

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
            policy += "\n" + read_text_file("policy/subject_description/has_shot_size_description.txt").format(shot_size_description=data.cam_setup.shot_size_description)
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

    def get_description(self, data: VideoData, pov_dir="labels/cam_setup/point_of_view") -> Dict[str, str]:
        if data.cam_motion.has_shot_transition or data.cam_motion.has_transition:
            raise ValueError("Shot transitions are not supported in this policy.")
        
        true_pov_attribute = data.cam_setup.true_pov_attribute
        pov_info = read_text_file(os.path.join(pov_dir, f"{true_pov_attribute}.txt"))
        
        policy = read_text_file("policy/scene_composition_dynamics/policy.txt").format(pov_description=pov_info)
        return policy

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
        policy += "\n" + read_text_file("policy/subject_motion_dynamics/has_subject_description.txt").format(subject_description=data.cam_setup.subject_description)
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
    
    def format_shot_size(self, shot_size: str) -> str:
        # Options: "unknown", "extreme_wide", "wide", "full", "medium_full", "medium",
        # "medium_close_up", "close_up", "extreme_close_up"
        shot_size_info = {
            "unknown": "unknown",
            "extreme_wide": "an extreme wide shot",
            "wide": "a wide shot",
            "full": "a full shot",
            "medium_full": "a medium full shot",
            "medium": "a medium shot",
            "medium_close_up": "a medium close-up shot",
            "close_up": "a close-up shot",
            "extreme_close_up": "an extreme close-up shot"
        }
        return shot_size_info[shot_size]
    
    def format_height_wrt_subject(self, height: str) -> str:
        # Options: "unknown", "above_subject", "at_subject", "below_subject"
        height_info = {
            "unknown": "unknown",
            "above_subject": "above the subject",
            "at_subject": "at the subject's level",
            "below_subject": "below the subject"
        }
        return height_info[height]
    
    def get_description(self, data: VideoData) -> Dict[str, str]:
        if data.cam_motion.has_shot_transition or data.cam_motion.has_transition:
            raise ValueError("Shot transitions are not supported in this policy.")
        
        policy = ""
        policy += read_text_file("policy/spatial_framing_dynamics/framing_subject.txt")
        policy += "\n" + read_text_file("policy/spatial_framing_dynamics/framing_scene.txt")
        policy += "\n" + read_text_file("policy/spatial_framing_dynamics/movement.txt")
        # if data.cam_setup.is_framing_subject is False:
        #     # This much be a Scenery shot
        #     policy += read_text_file("policy/spatial_framing_dynamics/framing_scene.txt")
        # else:
        #     policy += read_text_file("policy/spatial_framing_dynamics/framing_subject.txt")
        
        
        # if data.cam_setup.is_framing_subject is None:
        #     # Including complex shot with description others, or multiple subject without a clear focus
        #     # If is others description, then prompt to use this description to complement the subject description
        #     # Note that there may not be a subject in focus. 
        #     if data.cam_setup.shot_size_description_type == "others":
        #         pass # Do nothing
        #     elif data.cam_setup.is_just_many_subject_no_focus_shot:
        #         policy += "\n" + read_text_file("policy/spatial_framing_dynamics/framing_scenery.txt")
        #         policy += "\n Please note that this video contains **multiple subjects without a clear main focus**. Briefly describe the spatial positions and movements of salient subjects while providing a concise overview of secondary subjects, or describe all the spatial composition of all subjects collectively as a group if that is more appropriate."
        #     else:
        #         raise ValueError("When framing subject is None, the shot size description must be others or many_subject_no_focus.")
            
        assert data.cam_setup.subject_description != "", "Subject description must be provided before subject motion and dynamics description."
        assert data.cam_setup.scene_description != "", "Scene description must be provided before subject motion and dynamics description."
        policy += "\n" + read_text_file("policy/spatial_framing_dynamics/has_subject_scene_description.txt").format(
            subject_description=data.cam_setup.subject_description,
            scene_description=data.cam_setup.scene_description
        )

        shot_size_change = data.cam_setup.shot_size_change
        subject_status = None # 'has_subject', 'no_subject', 'change_of_subject', 'has_description'
        is_height_wrt_subject_applicable = data.cam_setup.is_height_wrt_subject_applicable
        
        if data.cam_setup.is_just_human_shot:
            policy += "\n Please note that the video features **salient human subjects**, so you should focus on describing the spatial framing and movements of them."
            subject_status = "has_subject"
        elif data.cam_setup.is_just_non_human_shot:
            policy += "\n Please note that the video features **salient non-human subjects**, so you should focus on describing the spatial framing and movements of them."
            subject_status = "has_subject"
        elif data.cam_setup.is_just_change_of_subject_shot:
            subject_status = "change_of_subject"
            if data.cam_setup.subject_revealing:
                policy += "\n Please note that the video is a **revealing shot of the subject**."
                policy += "\n Shot Size Information: The video begins with no subject. It then becomes {} of the subject.".format(
                    self.format_shot_size(data.cam_setup.shot_size_info['end'])
                )
                if is_height_wrt_subject_applicable:
                    policy += "\n When the subject is revealed, the camera is positioned {}.".format(
                        self.format_height_wrt_subject(data.cam_setup.height_wrt_subject_info['end'])
                    )
            elif data.cam_setup.subject_hiding:
                policy += "\n Please note that the video features **main subjects disappearing from the frame**."
                policy += "\n Shot Size Information: The video begins with {} of the subject. Then the subject disappears.".format(
                    self.format_shot_size(data.cam_setup.shot_size_info['start'])
                )
                if is_height_wrt_subject_applicable:
                    policy += "\n Before the subject disappears, the camera is positioned {}.".format(
                        self.format_height_wrt_subject(data.cam_setup.height_wrt_subject_info['start'])
                    )
            elif data.cam_setup.subject_switching:
                policy += "\n Please note that the video features **main subjects switching from one to another**."
                policy += "\n Shot Size Information: The video begins with {} of the first subject. Then it becomes {} of the second subject.".format(
                    self.format_shot_size(data.cam_setup.shot_size_info['start']),
                    self.format_shot_size(data.cam_setup.shot_size_info['end'])
                )
                if is_height_wrt_subject_applicable:
                    policy += "\n The camera is positioned {} when the first subject is in focus, and {} when the second subject is in focus.".format(
                        self.format_height_wrt_subject(data.cam_setup.height_wrt_subject_info['start']),
                        self.format_height_wrt_subject(data.cam_setup.height_wrt_subject_info['end'])
                    )
            else:
                raise ValueError("When is_just_change_of_subject_shot is True, either subject_revealing, subject_hiding, or subject_switching must be True.")
        elif data.cam_setup.is_just_clear_subject_dynamic_size_shot:
            policy += "\n Please note that the **main subject’s framing (shot size) is not stable** throughout the video, so the description should emphasize this."
            subject_status = "has_subject"
        elif data.cam_setup.is_just_clear_subject_atypical_shot:
            policy += "\n Please note that the **main subjects exhibit atypical posture or anatomy**, so the description should reflect this."
            subject_status = "has_subject"
        elif data.cam_setup.is_just_many_subject_one_focus_shot:
            policy += "\n Please note that the video features **multiple subjects with a clear main focus**, so the description should focus on the main subject."
            subject_status = "has_subject"
        elif data.cam_setup.is_just_different_subject_in_focus_shot:
            policy += "\n Please note that the video features **multiple different subjects in focus**, so the description should clearly distinguish their types and relationships."
            subject_status = "has_subject"
        elif data.cam_setup.is_just_many_subject_no_focus_shot:
            policy += "\n Please note that this video contains **multiple subjects without a clear main focus**. Briefly describe the spatial positions and movements of salient subjects while providing a concise overview of secondary subjects, or describe all the spatial composition of all subjects collectively as a group if that is more appropriate."
            subject_status = "no_subject"
        else:
            # pass for complex shot with description
            subject_status = "has_description"
            policy += "\n The description below already mentions the spatial framing information about the subjects or scenery in this video. Use this caption as a reference to draft the spatial framing and dynamics description. Simply expand on it to fully capture other spatial positions and movements. Do not infer the any spatial framing information already mentioned below."
            policy += f"\n\n Shot Size Information: {data.cam_setup.shot_size_description}"
            if is_height_wrt_subject_applicable:
                if data.cam_setup.height_wrt_subject_change:
                    policy += "\n Camera Height Relative to Subjects: The camera is initially positioned {} and then changes to {}.".format(
                        self.format_height_wrt_subject(data.cam_setup.height_wrt_subject_info['start']),
                        self.format_height_wrt_subject(data.cam_setup.height_wrt_subject_info['end'])
                    )
                else:
                    policy += "\n Camera Height Relative to Subjects: The camera is positioned {}.".format(
                        self.format_height_wrt_subject(data.cam_setup.height_wrt_subject_info['start'])
                    )
            elif data.cam_setup.height_wrt_subject_description != "":
                policy += f"\n Camera Height Relative to Subjects: {data.cam_setup.height_wrt_subject_description}"
                
        
        if subject_status == "has_subject":
            if shot_size_change:
                policy += "\n Shot Size Information: The video begins with {} of the subjects. It then changes to {}.".format(
                    self.format_shot_size(data.cam_setup.shot_size_info['start']),
                    self.format_shot_size(data.cam_setup.shot_size_info['end'])
                )
            else:
                policy += "\n Shot Size Information: The video shows {} of the subjects.".format(self.format_shot_size(data.cam_setup.shot_size_info['start']))
                
            if is_height_wrt_subject_applicable:
                if data.cam_setup.height_wrt_subject_change:
                    policy += "\n Camera Height Relative to Subjects: The camera is initially positioned {}. It then changes to {}.".format(
                        self.format_height_wrt_subject(data.cam_setup.height_wrt_subject_info['start']),
                        self.format_height_wrt_subject(data.cam_setup.height_wrt_subject_info['end'])
                    )
                else:
                    policy += "\n Camera Height Relative to Subjects: The camera is positioned {}.".format(self.format_height_wrt_subject(data.cam_setup.height_wrt_subject_info['start']))
        elif subject_status == None or subject_status == "no_subject":
            if shot_size_change:
                policy += "\n Shot Size Information: The video begins with {} of the scenery. It then changes to {}.".format(
                    self.format_shot_size(data.cam_setup.shot_size_info['start']),
                    self.format_shot_size(data.cam_setup.shot_size_info['end'])
                )
            else:
                policy += "\n Shot Size Information: The video shows {} of the scenery.".format(self.format_shot_size(data.cam_setup.shot_size_info['start']))
                
            if is_height_wrt_subject_applicable:
                raise ValueError("Height relative to subject is not applicable when there is no subject.")
        
        return policy

    

class VanillaCameraPolicy(SocraticProgram):
    def __init__(self):
        name = "Vanilla Camera Framing and Dynamics Description"
        info = "A policy that use existing labels to prompt a human or model to provide structured captions for Camera Framing and Dynamics."
        caption_fields = ["camera_framing_dynamics"]
        super().__init__(name, info, caption_fields)
    
    def __call__(self, data: VideoData) -> Dict[str, str]:
        """Given a VideoData instance, return a dictionary of prompts for structured captions."""
        return {
            "camera_framing_dynamics": self.get_description(data)
        }
    
    def get_description(self, data: VideoData) -> Dict[str, str]:
        raise NotImplementedError("Camera Framing and Dynamics Description is not yet implemented.")