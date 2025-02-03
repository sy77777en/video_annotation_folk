from typing import List

class CameraMotionData:
    def __init__(self):
        # Shot transition options
        self.shot_transition = False # Boolean: True or False
        
        # Scene movement options
        self.scene_movement = "unknown"  # Options: "static", "mostly_static", "dynamic", "unknown"
        
        # Camera steadiness options
        self.steadiness = "static"  # Options: "static", "very_smooth", "smooth", "unsteady", "very_unsteady"

        # Camera movement options
        self.camera_movement = "no"  # Options: "no", "major_complex", "major_simple", "minor"

        # Camera motion speed options
        self.camera_motion_speed = "regular"  # Options: "slow", "regular", "fast"

        # Camera tracking options
        self.is_tracking = False  # Boolean: True or False
        self.tracking_shot_types = []  # Options: "side", "tail", "lead", "aerial", "arc", "pan", "tilt"

        # Subject size change options (only for tracking shots)
        self.subject_size_change = "no"  # Options: "no", "larger", "smaller"

        # Camera direction movement options
        self.camera_forward_backward = "no"  # Options: "no", "forward", "backward"
        self.camera_forward_backward_cam_frame = "no"  # Options: "no", "forward", "backward", "unknown"
        self.camera_zoom = "no"  # Options: "no", "in", "out"
        self.camera_left_right = "no"  # Options: "no", "left_to_right", "right_to_left"
        self.camera_pan = "no"  # Options: "no", "left_to_right", "right_to_left"
        self.camera_up_down = "no"  # Options: "no", "up", "down"
        self.camera_up_down_cam_frame = "no"  # Options: "no", "up", "down", "unknown"
        self.camera_tilt = "no"  # Options: "no", "up", "down"
        self.camera_arc = "no"  # Options: "no", "clockwise", "counter_clockwise"
        self.camera_crane = "no"  # Options: "no", "crane_up", "crane_down"
        self.camera_roll = "no"  # Options: "no", "clockwise", "counter_clockwise"

        # Camera motion effects as booleans
        self.frame_freezing = False
        self.dolly_zoom = False
        self.motion_blur = False
        self.cinemagraph = False

        # Text box for complex descriptions
        self.complex_motion_description = ""

        # Change camera_motion_list to store active motions instead of all possible motions
        self.camera_motion_list = []  # Will contain active motions
        self.camera_motion_cam_list = []  # Will contain active camera-centric motions
        
        # Keep these as references of all possible motions (renamed for clarity)
        self.possible_motions = [
            "forward", "backward", "zoom_in", "zoom_out", "up", "down",
            "tilt_up", "tilt_down", "roll_cw", "roll_ccw",
            "pan_right", "pan_left", "left", "right"
        ]

        # Camera motion List (camera_based)
        self.possible_cam_motions = [
            "zoom_in", "zoom_out", "tilt_up", "tilt_down", "left", "right",
            "up_cam", "down_cam", "forward_cam", "backward_cam",
            "roll_cw", "roll_ccw", "pan_right", "pan_left"
        ]
    
    def set_camera_motion_attributes(self):
        # Clear the current motion lists
        self.camera_motion_list = []
        self.camera_motion_cam_list = []
        
        # if shot_transition is True or camera is static, return
        if self.shot_transition or self.steadiness == "static" or self.camera_movement == "no":
            return
            
        # Add ground-centric motions
        if self.camera_forward_backward == "forward":
            self.camera_motion_list.append("forward")
        if self.camera_forward_backward == "backward":
            self.camera_motion_list.append("backward")
        if self.camera_zoom == "in":
            self.camera_motion_list.append("zoom_in")
        if self.camera_zoom == "out":
            self.camera_motion_list.append("zoom_out")
        if self.camera_up_down == "up":
            self.camera_motion_list.append("up")
        if self.camera_up_down == "down":
            self.camera_motion_list.append("down")
        if self.camera_tilt == "up":
            self.camera_motion_list.append("tilt_up")
        if self.camera_tilt == "down":
            self.camera_motion_list.append("tilt_down")
        if self.camera_roll == "clockwise":
            self.camera_motion_list.append("roll_cw")
        if self.camera_roll == "counter_clockwise":
            self.camera_motion_list.append("roll_ccw")
        if self.camera_pan == "left_to_right":
            self.camera_motion_list.append("pan_right")
        if self.camera_pan == "right_to_left":
            self.camera_motion_list.append("pan_left")
        if self.camera_left_right == "left_to_right":
            self.camera_motion_list.append("left")
        if self.camera_left_right == "right_to_left":
            self.camera_motion_list.append("right")

        # Add camera-centric motions
        if self.camera_forward_backward_cam_frame == "forward":
            self.camera_motion_cam_list.append("forward_cam")
        if self.camera_forward_backward_cam_frame == "backward":
            self.camera_motion_cam_list.append("backward_cam")
        if self.camera_up_down_cam_frame == "up":
            self.camera_motion_cam_list.append("up_cam")
        if self.camera_up_down_cam_frame == "down":
            self.camera_motion_cam_list.append("down_cam")
        if self.camera_arc != "no":
            self.camera_motion_cam_list.append("tilt_up" if self.camera_arc == "clockwise" else "tilt_down")
        if self.camera_crane != "no":
            self.camera_motion_cam_list.append("crane_up" if self.camera_crane == "crane_up" else "crane_down")
        if self.camera_arc != "no":
            self.camera_motion_cam_list.append("arc_cw" if self.camera_arc == "clockwise" else "arc_ccw")
        
    def set_steadiness(self, steadiness):
        valid_options = ["static", "very_smooth", "smooth", "unsteady", "very_unsteady"]
        if steadiness in valid_options:
            self.steadiness = steadiness
        else:
            raise ValueError(f"Invalid steadiness option: {steadiness}")
    
    def set_scene_movement(self, scene_movement):
        valid_options = ["static", "mostly_static", "dynamic", "unknown"]
        if scene_movement in valid_options:
            self.scene_movement = scene_movement
        else:
            raise ValueError(f"Invalid scene_movement option: {scene_movement}")

    def set_camera_movement(self, movement):
        valid_options = ["no", "major_complex", "major_simple", "minor"]
        if movement in valid_options:
            self.camera_movement = movement
        else:
            raise ValueError(f"Invalid camera movement option: {movement}")

    def set_camera_motion_speed(self, speed):
        valid_options = ["slow", "regular", "fast"]
        if speed in valid_options:
            self.camera_motion_speed = speed
        else:
            raise ValueError(f"Invalid camera motion speed option: {speed}")

    def set_shot_transition(self, shot_transition):
        if isinstance(shot_transition, bool):
            self.shot_transition = shot_transition
        else:
            raise ValueError("shot_transition must be a boolean value")
        
    def set_is_tracking(self, is_tracking):
        if isinstance(is_tracking, bool):
            self.is_tracking = is_tracking
        else:
            raise ValueError("is_tracking must be a boolean value")
    
    def set_subject_size_change(self, size_change):
        valid_options = ["no", "larger", "smaller"]
        if size_change in valid_options:
            self.subject_size_change = size_change
        else:
            raise ValueError(f"Invalid subject size change option: {size_change}")
        
    def set_camera_forward_backward(self, direction):
        valid_options = ["no", "forward", "backward"]
        if direction in valid_options:
            self.camera_forward_backward = direction
        else:
            raise ValueError(f"Invalid camera forward/backward option: {direction}")
        
    def set_camera_forward_backward_cam_frame(self, direction):
        valid_options = ["no", "forward", "backward", "unknown"]
        if direction in valid_options:
            self.camera_forward_backward_cam_frame = direction
        else:
            raise ValueError(f"Invalid camera forward/backward (camera-centric) option: {direction}")
    
    def set_camera_zoom(self, zoom):
        valid_options = ["no", "in", "out"]
        if zoom in valid_options:
            self.camera_zoom = zoom
        else:
            raise ValueError(f"Invalid camera zoom option: {zoom}")
    
    def set_camera_left_right(self, direction):
        valid_options = ["no", "left_to_right", "right_to_left"]
        if direction in valid_options:
            self.camera_left_right = direction
        else:
            raise ValueError(f"Invalid camera left_right option: {direction}")
        
    def set_camera_pan(self, direction):
        valid_options = ["no", "left_to_right", "right_to_left"]
        if direction in valid_options:
            self.camera_pan = direction
        else:
            raise ValueError(f"Invalid camera pan option: {direction}")
    
    def set_camera_up_down(self, direction):
        valid_options = ["no", "up", "down"]
        if direction in valid_options:
            self.camera_up_down = direction
        else:
            raise ValueError(f"Invalid camera up_down option: {direction}")
    
    def set_camera_up_down_cam_frame(self, direction):
        valid_options = ["no", "up", "down", "unknown"]
        if direction in valid_options:
            self.camera_up_down_cam_frame = direction
        else:
            raise ValueError(f"Invalid camera up_down (camera-centric) option: {direction}")
    
    def set_camera_tilt(self, direction):
        valid_options = ["no", "up", "down"]
        if direction in valid_options:
            self.camera_tilt = direction
        else:
            raise ValueError(f"Invalid camera tilt option: {direction}")
    
    def set_camera_arc(self, direction):
        valid_options = ["no", "clockwise", "counter_clockwise"]
        if direction in valid_options:
            self.camera_arc = direction
        else:
            raise ValueError(f"Invalid camera arc option: {direction}")
    
    def set_camera_crane(self, direction):
        valid_options = ["no", "crane_up", "crane_down"]
        if direction in valid_options:
            self.camera_crane = direction
        else:
            raise ValueError(f"Invalid camera crane option: {direction}")
    
    def set_camera_roll(self, direction):
        valid_options = ["no", "clockwise", "counter_clockwise"]
        if direction in valid_options:
            self.camera_roll = direction
        else:
            raise ValueError(f"Invalid camera roll option: {direction}")
        
    def set_tracking_shot_types(self, types):
        valid_options = ["side", "tail", "lead", "aerial", "arc", "pan", "tilt"]
        if all(t in valid_options for t in types):
            self.tracking_shot_types = types
        else:
            raise ValueError(f"Invalid tracking shot types: {types}")

    def set_frame_freezing(self, freezing):
        if isinstance(freezing, bool):
            self.frame_freezing = freezing
        else:
            raise ValueError("frame_freezing must be a boolean value")
    
    def set_dolly_zoom(self, dolly_zoom):
        if isinstance(dolly_zoom, bool):
            self.dolly_zoom = dolly_zoom
        else:
            raise ValueError("dolly_zoom must be a boolean value")
    
    def set_motion_blur(self, motion_blur):
        if isinstance(motion_blur, bool):
            self.motion_blur = motion_blur
        else:
            raise ValueError("motion_blur must be a boolean value")
    
    def set_cinemagraph(self, cinemagraph):
        if isinstance(cinemagraph, bool):
            self.cinemagraph = cinemagraph
        else:
            raise ValueError("cinemagraph must be a boolean value")
    
    def set_complex_motion_description(self, description):
        if isinstance(description, str):
            self.complex_motion_description = description
        else:
            raise ValueError("Complex motion description must be a string")
        
    def camera_motion_dict(self):
        return {
            "forward_backward": self.camera_forward_backward,
            "zoom": self.camera_zoom,
            "left_right": self.camera_left_right,
            "pan": self.camera_pan,
            "up_down": self.camera_up_down,
            "tilt": self.camera_tilt,
            "arc": self.camera_arc,
            "crane": self.camera_crane,
            "roll": self.camera_roll
        }

    def check_if_any_motion(self, include: List[str] = [], condition: List[str] = [True]):
        """Returns True if any of the specified ground-centric motions are active"""
        if include:
            return any(motion in self.camera_motion_list for motion in include)
        return len(self.camera_motion_list) > 0

    def check_if_any_motion_cam(self, include: List[str] = [], condition: List[str] = [True]):
        """Returns True if any of the specified camera-centric motions are active"""
        if include:
            return any(motion in self.camera_motion_cam_list for motion in include)
        return len(self.camera_motion_cam_list) > 0

    def check_if_no_motion(self, exclude: List[str] = []):
        """Returns True if there are no active ground-centric motions (except excluded ones)"""
        active_motions = set(self.camera_motion_list) - set(exclude)
        return len(active_motions) == 0

    def check_if_no_motion_cam(self, exclude: List[str] = []):
        """Returns True if there are no active camera-centric motions (except excluded ones)"""
        active_motions = set(self.camera_motion_cam_list) - set(exclude)
        return len(active_motions) == 0

    # Add property getters for common motion checks
    @property
    def forward(self):
        return "forward" in self.camera_motion_list
        
    @property
    def backward(self):
        return "backward" in self.camera_motion_list
        
    @property
    def zoom_in(self):
        return "zoom_in" in self.camera_motion_list
        
    @property
    def zoom_out(self):
        return "zoom_out" in self.camera_motion_list

    @property
    def up(self):
        return "up" in self.camera_motion_list
        
    @property
    def down(self):
        return "down" in self.camera_motion_list

    @property
    def left(self):
        return "left" in self.camera_motion_list
        
    @property
    def right(self):
        return "right" in self.camera_motion_list

    # Camera-centric properties
    @property
    def forward_cam(self):
        return "forward_cam" in self.camera_motion_cam_list
        
    @property
    def backward_cam(self):
        return "backward_cam" in self.camera_motion_cam_list

    @property
    def up_cam(self):
        return "up_cam" in self.camera_motion_cam_list
        
    @property
    def down_cam(self):
        return "down_cam" in self.camera_motion_cam_list

    @property
    def arc_cw(self):
        return self.camera_arc == "clockwise"
        
    @property
    def arc_ccw(self):
        return self.camera_arc == "counter_clockwise"

    # Pan properties
    @property
    def pan_left(self):
        return self.camera_pan == "right_to_left"
    
    @property
    def pan_right(self):
        return self.camera_pan == "left_to_right"
    
    # Tilt properties
    @property
    def tilt_up(self):
        return self.camera_tilt == "up"
    
    @property
    def tilt_down(self):
        return self.camera_tilt == "down"
    
    # Roll properties
    @property
    def roll_cw(self):
        return self.camera_roll == "clockwise"
    
    @property
    def roll_ccw(self):
        return self.camera_roll == "counter_clockwise"
    
    # Crane properties
    @property
    def crane_up(self):
        return self.camera_crane == "crane_up"
    
    @property
    def crane_down(self):
        return self.camera_crane == "crane_down"

    def camera_motion_dict_cam_frame(self):
        return {
            "forward_backward": self.camera_forward_backward_cam_frame, # Use this for camera-centric motion
            "zoom": self.camera_zoom,
            "left_right": self.camera_left_right,
            "pan": self.camera_pan,
            "up_down": self.camera_up_down_cam_frame, # Use this for camera-centric motion
            "tilt": self.camera_tilt,
            "arc": self.camera_arc,
            "crane": self.camera_crane,
            "roll": self.camera_roll
        }
        
    def get_raw_camera_motion_list(self):
        return [self.camera_forward_backward, self.camera_zoom, self.camera_left_right,
                self.camera_pan, self.camera_up_down, self.camera_tilt, self.camera_arc,
                self.camera_crane, self.camera_roll]
        
    @classmethod
    def create(cls, **kwargs):
        """Create a CameraMotionData instance ensuring all attributes are set using setters and are verified."""
        instance = cls()
        for key, value in kwargs.items():
            setter_method = getattr(instance, f"set_{key}", None)
            if setter_method and callable(setter_method):
                setter_method(value)
            else:
                raise AttributeError(f"Invalid attribute: {key} or setter method not found")
        instance.verify()
        instance.set_camera_motion_attributes()
        return instance
    
    def update(self, **kwargs):
        """Update attributes of the CameraMotionData instance."""
        for key, value in kwargs.items():
            setter_method = getattr(self, f"set_{key}", None)
            if setter_method and callable(setter_method):
                setter_method(value)
            else:
                raise AttributeError(f"Invalid attribute: {key} or setter method not found")
        self.verify()
        self.set_camera_motion_attributes()
        
    def verify(self):
        if self.steadiness == "static" and self.camera_movement in ["major_simple", "minor"]:
            raise ValueError("When steadiness is 'static', camera_movement cannot be 'major_simple' or 'minor'.")

        if not self.is_tracking:
            if self.tracking_shot_types:
                raise ValueError("When is_tracking is False, tracking_shot_types must be an empty list.")
            if self.subject_size_change != "no":
                raise ValueError("When is_tracking is False, subject_size_change must be 'no'.")

        if self.camera_movement == "major_complex":
            if not self.complex_motion_description:
                raise ValueError("When camera_movement is 'major_complex', complex_motion_description must not be empty.")
        else:
            if self.complex_motion_description:
                raise ValueError("When camera_movement is not 'major_complex', complex_motion_description must be empty.")

        camera_movements = self.get_raw_camera_motion_list()
        if self.camera_movement == "major_simple":
            if all(movement == "no" for movement in camera_movements):
                raise ValueError("When camera_movement is 'major_simple', at least one direction movement must be specified.")

        if self.camera_movement == "no":
            if any(movement != "no" for movement in camera_movements):
                raise ValueError("When camera_movement is 'no', all direction movements must be 'no'.")
            
            if self.steadiness in ["very_smooth"]:
                raise ValueError("When camera_movement is 'no', steadiness cannot be 'very_smooth'.")
            
        if self.dolly_zoom:
            if not ((self.camera_zoom == "out" and self.camera_forward_backward == "forward") or \
                (self.camera_zoom == "in" and self.camera_forward_backward == "backward")):
                raise ValueError("For dolly_zoom effect, camera_zoom and camera_forward_backward must be in opposite directions.")
            elif self.camera_zoom == "no" or self.camera_forward_backward == "no":
                raise ValueError("For dolly_zoom effect, both camera_zoom and camera_forward_backward must be specified.")

camera_motion_params_demo = {
    "shot_transition": False,
    "steadiness": "smooth",
    "scene_movement": "static",
    "camera_movement": "major_complex",
    "camera_motion_speed": "regular",
    "is_tracking": True,
    "tracking_shot_types": ["side", "tail"],
    "subject_size_change": "larger",
    "camera_forward_backward": "forward",
    "camera_forward_backward_cam_frame": "unknown",
    "camera_zoom": "out",
    "camera_left_right": "no",
    "camera_pan": "no",
    "camera_up_down": "no",
    "camera_up_down_cam_frame": "unknown",
    "camera_tilt": "no",
    "camera_arc": "no",
    "camera_crane": "no",
    "camera_roll": "no",
    "dolly_zoom": True,
    "motion_blur": True,
    "complex_motion_description": "The camera starts with a dolly-in and transitions to a crane-down."
}
def create_camera_motion_data_demo():
    data = CameraMotionData.create(**camera_motion_params_demo)
    return data

if __name__ == "__main__":
    create_camera_motion_data_demo()

