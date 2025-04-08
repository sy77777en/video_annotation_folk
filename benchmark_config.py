CAMERABENCH_GROUND_ONLY_FOLDER = "cam_motion-20250227_0324ground_only"
CAMERABENCH_GROUND_AND_SETUP_FOLDER = "cam_motion-cam_setup-20250227_0507ground_and_setup"
CAMERABENCH_CAMERA_AND_CAMERA_FOLDER = "cam_motion-20250227_0326ground_and_camera"

def get_movement_and_steadiness_tasks(ground_only_folder=CAMERABENCH_GROUND_ONLY_FOLDER):
    return [
        {
            "folder": ground_only_folder,
            "name": "is_the_camera_clearly_moving_or_not",
            "pos_question": "Does the camera have noticeable motion beyond minor shake or wobble?",
            "neg_question": "Is the camera free from noticeable motion beyond minor shake or wobble?",
            "pos_prompt": "A video where the camera has noticeable motion beyond minor shake or wobble.",
            "neg_prompt": "A video where the camera is free from noticeable motion beyond minor shake or wobble.",
            "pos": {
                "label": "cam_motion.steadiness_and_movement.clear_moving_camera",
                "type": "pos",
            },
            "neg": {
                "label": "cam_motion.steadiness_and_movement.clear_moving_camera",
                "type": "neg",
            },
        },
        {
            "folder": ground_only_folder,
            "name": "is_the_fixed_camera_shaking_or_not",
            "pos_question": "Is the camera completely still without any motion or shaking?",
            "neg_question": "Is the camera stationary with minor vibrations or shaking?",
            "pos_prompt": "A video where the camera remains completely still with no motion or shaking.",
            "neg_prompt": "A video where the camera is mostly stationary but has minor vibrations or shaking.",
            "pos": {
                "label": "cam_motion.steadiness_and_movement.fixed_camera",
                "type": "pos",
            },
            "neg": {
                "label": "cam_motion.steadiness_and_movement.fixed_camera_with_shake",
                "type": "pos",
            },
        },
        {
            "folder": ground_only_folder,
            "name": "is_the_camera_stable_or_shaky",
            "pos_question": "Is the camera movement exceptionally smooth and highly stable?",
            "neg_question": "Does the camera show noticable vibrations, shaking, or wobbling?",
            "pos_prompt": "A video where the camera movement is exceptionally smooth and highly stable.",
            "neg_prompt": "A video where the camera shows noticable vibrations, shaking, or wobbling.",
            "pos": {
                "label": "cam_motion.steadiness_and_movement.very_stable_camera",
                "type": "pos",
            },
            "neg": {
                "label": "cam_motion.steadiness_and_movement.very_shaky_camera",
                "type": "pos",
            },
        },
        {
            "folder": ground_only_folder,
            "name": "is_the_camera_fixed_or_moving",
            "pos_question": "Is the camera completely still without any visible movement?",
            "neg_question": "Is the camera not completely still and shows visible movement?",
            "pos_prompt": "The camera is completely still without any visible movement.",
            "neg_prompt": "The camera is not completely still and shows visible movement.",
            "pos": {
                "label": "cam_motion.steadiness_and_movement.fixed_camera",
                "type": "pos",
            },
            "neg": {
                "label": "cam_motion.steadiness_and_movement.fixed_camera",
                "type": "neg",
            },
        },
    ]

def get_scene_dynamics_tasks(ground_only_folder=CAMERABENCH_GROUND_ONLY_FOLDER):
    return [
        {
            "folder": ground_only_folder,
            "name": "is_scene_static_or_not",
            "pos_question": "Is the scene in the video completely static?",
            "neg_question": "Is the scene in the video dynamic?",
            "pos_prompt": "A video where the scene is completely static.",
            "neg_prompt": "A video where the scene is dynamic and features movement.",
            "pos": {"label": "cam_motion.scene_movement.static_scene", "type": "pos"},
            "neg": {"label": "cam_motion.scene_movement.dynamic_scene", "type": "pos"},
        },
        {
            "folder": ground_only_folder,
            "name": "has_frame_freeze_or_not",
            "pos_question": "Does the video contain a frame freeze effect at any point?",
            "neg_question": "Is the video free from any frame freeze effect?",
            "pos_prompt": "A video that contains a frame freeze effect at some point.",
            "neg_prompt": "A video that is free from any frame freeze effect.",
            "pos": {"label": "cam_motion.has_frame_freezing", "type": "pos"},
            "neg": {"label": "cam_motion.has_frame_freezing", "type": "neg"},
        },
    ]

def get_camera_movement_speed_tasks(ground_only_folder=CAMERABENCH_GROUND_ONLY_FOLDER):
    return [
        {
            "folder": ground_only_folder,
            "name": "is_camera_movement_slow_or_fast",
            "pos_question": "Does the camera have noticeable motion but at a slow motion speed?",
            "neg_question": "Does the camera have noticeable motion but at a fast motion speed?",
            "pos_prompt": "A video where the camera has noticeable motion at a slow speed.",
            "neg_prompt": "A video where the camera has noticeable motion at a fast speed.",
            "pos": {
                "label": "cam_motion.steadiness_and_movement.slow_moving_camera",
                "type": "pos",
            },
            "neg": {
                "label": "cam_motion.steadiness_and_movement.fast_moving_camera",
                "type": "pos",
            },
        },
        {
            "folder": ground_only_folder,
            "name": "has_motion_blur_or_not",
            "pos_question": "Does the video contain noticeable motion blur?",
            "neg_question": "Is the video free from any noticeable motion blur?",
            "pos_prompt": "The video exhibits a motion blur effect.",
            "neg_prompt": "The video is free from any noticeable motion blur.",
            "pos": {"label": "cam_motion.has_motion_blur", "type": "pos"},
            "neg": {"label": "cam_motion.has_motion_blur", "type": "neg"},
        },
    ]

def get_translation_direction_tasks(ground_only_folder=CAMERABENCH_GROUND_ONLY_FOLDER,
                                    ground_and_setup_folder=CAMERABENCH_GROUND_AND_SETUP_FOLDER):
    return [
        # Translation Direction (3 tasks)
        {
            "folder": ground_and_setup_folder,
            "name": "has_forward_vs_backward_ground",
            "pos_question": "Is the camera moving forward in the scene?",
            "neg_question": "Is the camera moving backward in the scene?",
            "pos_prompt": "A shot where the camera is moving forward within the scene.",
            "neg_prompt": "A shot where the camera is moving backward within the scene.",
            "pos": {
                "label": "cam_motion.ground_centric_movement.forward.has_forward_wrt_ground",
                "type": "pos",
            },
            "neg": {
                "label": "cam_motion.ground_centric_movement.backward.has_backward_wrt_ground",
                "type": "pos",
            },
        },
        {
            "folder": ground_and_setup_folder,
            "name": "has_upward_vs_downward_ground",
            "pos_question": "Does the camera move upward relative to the ground?",
            "neg_question": "Does the camera move downward relative to the ground?",
            "pos_prompt": "The camera is moving upward relative to the ground.",
            "neg_prompt": "The camera is moving downward relative to the ground.",
            "pos": {
                "label": "cam_motion.ground_centric_movement.upward.has_upward_wrt_ground",
                "type": "pos",
            },
            "neg": {
                "label": "cam_motion.ground_centric_movement.downward.has_downward_wrt_ground",
                "type": "pos",
            },
        },
        {
            "folder": ground_only_folder,
            "name": "has_leftward_vs_rightward",
            "pos_question": "Does the camera move leftward in the scene?",
            "neg_question": "Does the camera move rightward in the scene?",
            "pos_prompt": "The camera moves leftward.",
            "neg_prompt": "The camera moves rightward.",
            "pos": {
                "label": "cam_motion.camera_centric_movement.leftward.has_leftward",
                "type": "pos",
            },
            "neg": {
                "label": "cam_motion.camera_centric_movement.rightward.has_rightward",
                "type": "pos",
            },
        },
    ]

def get_rotation_direction_tasks(ground_only_folder=CAMERABENCH_GROUND_ONLY_FOLDER):
    return [
        # Rotation Direction (3 tasks)
        {
            "folder": ground_only_folder,
            "name": "pan_left_vs_pan_right",
            "pos_question": "Does the camera pan to the left?",
            "neg_question": "Does the camera pan to the right?",
            "pos_prompt": "The camera pans to the left.",
            "neg_prompt": "The camera pans to the right.",
            "pos": {
                "label": "cam_motion.camera_centric_movement.pan_left.has_pan_left",
                "type": "pos",
            },
            "neg": {
                "label": "cam_motion.camera_centric_movement.pan_right.has_pan_right",
                "type": "pos",
            },
        },
        {
            "folder": ground_only_folder,
            "name": "tilt_up_vs_tilt_down",
            "pos_question": "Does the camera tilt upward?",
            "neg_question": "Does the camera tilt downward?",
            "pos_prompt": "The camera tilts upward.",
            "neg_prompt": "The camera tilts downward.",
            "pos": {
                "label": "cam_motion.camera_centric_movement.tilt_up.has_tilt_up",
                "type": "pos",
            },
            "neg": {
                "label": "cam_motion.camera_centric_movement.tilt_down.has_tilt_down",
                "type": "pos",
            },
        },
        {
            "folder": ground_only_folder,
            "name": "roll_cc_vs_roll_ccw",
            "pos_question": "Does the camera roll clockwise?",
            "neg_question": "Does the camera roll counterclockwise?",
            "pos_prompt": "The camera rolls clockwise.",
            "neg_prompt": "The camera rolls counterclockwise.",
            "pos": {
                "label": "cam_motion.camera_centric_movement.roll_clockwise.has_roll_clockwise",
                "type": "pos",
            },
            "neg": {
                "label": "cam_motion.camera_centric_movement.roll_counterclockwise.has_roll_counterclockwise",
                "type": "pos",
            },
        },
    ]

def get_object_centric_direction_tasks(ground_only_folder=CAMERABENCH_GROUND_ONLY_FOLDER):
    return [
        # Object-Centric Direction (4 tasks)
        {
            "folder": ground_only_folder,
            "name": "side_tracking_leftward_vs_rightward",
            "pos_question": "Is it a side-tracking shot where the camera moves left to follow the subject?",
            "neg_question": "Is it a side-tracking shot where the camera moves right to follow the subject?",
            "pos_prompt": "A side-tracking shot where the camera moves left to follow the subject.",
            "neg_prompt": "A side-tracking shot where the camera moves right to follow the subject.",
            "pos": {
                "label": "cam_motion.object_centric_movement.side_tracking_shot_leftward",
                "type": "pos",
            },
            "neg": {
                "label": "cam_motion.object_centric_movement.side_tracking_shot_rightward",
                "type": "pos",
            },
        },
        {
            "folder": ground_only_folder,
            "name": "lead_tracking_vs_tail_tracking",
            "pos_question": "Is it a tracking shot with the camera moving ahead of the subject?",
            "neg_question": "Is it a tracking shot with the camera following behind the subject?",
            "pos_prompt": "A tracking shot where the camera moves ahead of the subject.",
            "neg_prompt": "A tracking shot where the camera follows behind the subject.",
            "pos": {
                "label": "cam_motion.object_centric_movement.lead_tracking_shot",
                "type": "pos",
            },
            "neg": {
                "label": "cam_motion.object_centric_movement.tail_tracking_shot",
                "type": "pos",
            },
        },
        {
            "folder": ground_only_folder,
            "name": "arc_ccw_vs_arc_cc",
            "pos_question": "Does the camera move in a counterclockwise arc?",
            "neg_question": "Does the camera move in a clockwise arc?",
            "pos_prompt": "The camera arcs counterclockwise.",
            "neg_prompt": "The camera arcs clockwise.",
            "pos": {
                "label": "cam_motion.arc_crane_movement.arc_counterclockwise.has_arc_counterclockwise",
                "type": "pos",
            },
            "neg": {
                "label": "cam_motion.arc_crane_movement.arc_clockwise.has_arc_clockwise",
                "type": "pos",
            },
        },
        {
            "folder": ground_only_folder,
            "name": "crane_up_vs_crane_down",
            "pos_question": "Is the camera craning upward in an arc?",
            "neg_question": "Does the camera move downward in a crane shot?",
            "pos_prompt": "The camera cranes upward in an arc.",
            "neg_prompt": "The camera cranes downward in an arc.",
            "pos": {
                "label": "cam_motion.arc_crane_movement.crane_up.has_crane_up",
                "type": "pos",
            },
            "neg": {
                "label": "cam_motion.arc_crane_movement.crane_down.has_crane_down",
                "type": "pos",
            },
        },
    ]

def get_intrinsic_direction_tasks(ground_only_folder=CAMERABENCH_GROUND_ONLY_FOLDER):
    return [
        # Intrinsic Direction (2 tasks)
        {
            "folder": ground_only_folder,
            "name": "dolly_zoom_in_vs_dolly_zoom_out",
            "pos_question": "Does the shot feature a dolly zoom effect with the camera moving backward and zooming in?",
            "neg_question": "Does the shot feature a dolly zoom effect with the camera moving forward and zooming out?",
            "pos_prompt": "The camera performs a dolly zoom effect with backward movement and zoom-in.",
            "neg_prompt": "The camera performs a dolly zoom effect with forward movement and zoom-out.",
            "pos": {
                "label": "cam_motion.dolly_zoom_movement.has_dolly_out_zoom_in",
                "type": "pos",
            },
            "neg": {
                "label": "cam_motion.dolly_zoom_movement.has_dolly_in_zoom_out",
                "type": "pos",
            },
        },
        {
            "folder": ground_only_folder,
            "name": "zoom_in_vs_zoom_out",
            "pos_question": "Does the camera zoom in?",
            "neg_question": "Does the camera zoom out?",
            "pos_prompt": "The camera zooms in.",
            "neg_prompt": "The camera zooms out.",
            "pos": {
                "label": "cam_motion.camera_centric_movement.zoom_in.has_zoom_in",
                "type": "pos",
            },
            "neg": {
                "label": "cam_motion.camera_centric_movement.zoom_out.has_zoom_out",
                "type": "pos",
            },
        },
    ]

def get_instrinsic_vs_extrinsic_tasks(ground_and_camera_folder=CAMERABENCH_CAMERA_AND_CAMERA_FOLDER,
                                      ground_only_folder=CAMERABENCH_GROUND_ONLY_FOLDER):
                                      
    return [
        # Intrinsic vs. Extrinsic (4 tasks)
        {
            "folder": ground_and_camera_folder,
            "name": "has_zoom_in_not_move_vs_has_move_not_zoom_in",
            "pos_question": "Does the camera zoom in without physically moving forward?",
            "neg_question": "Does the camera physically move forward without zooming in?",
            "pos_prompt": "A video where the camera zooms in without physically moving forward.",
            "neg_prompt": "A video where the camera physically moves forward without zooming in.",
            "pos": [
                {
                    "label": "cam_motion.camera_centric_movement.zoom_in.has_zoom_in",
                    "type": "pos",
                },
                {
                    "label": "cam_motion.camera_centric_movement.forward.has_forward_wrt_camera",
                    "type": "neg",
                },
            ],
            "neg": [
                {
                    "label": "cam_motion.camera_centric_movement.zoom_in.has_zoom_in",
                    "type": "neg",
                },
                {
                    "label": "cam_motion.camera_centric_movement.forward.has_forward_wrt_camera",
                    "type": "pos",
                },
            ],
        },
        {
            "folder": ground_and_camera_folder,
            "name": "has_zoom_out_not_move_vs_has_move_not_zoom_out",
            "pos_question": "Does the camera zoom out without physically moving backward?",
            "neg_question": "Does the camera physically move backward without zooming out?",
            "pos_prompt": "A video where the camera zooms out without physically moving backward.",
            "neg_prompt": "A video where the camera physically moves backward without zooming out.",
            "pos": [
                {
                    "label": "cam_motion.camera_centric_movement.zoom_out.has_zoom_out",
                    "type": "pos",
                },
                {
                    "label": "cam_motion.camera_centric_movement.backward.has_backward_wrt_camera",
                    "type": "neg",
                },
            ],
            "neg": [
                {
                    "label": "cam_motion.camera_centric_movement.zoom_out.has_zoom_out",
                    "type": "neg",
                },
                {
                    "label": "cam_motion.camera_centric_movement.backward.has_backward_wrt_camera",
                    "type": "pos",
                },
            ],
        },
        {
            "folder": ground_only_folder,
            "name": "only_zoom_in_vs_only_forward",
            "pos_question": "Does the camera only zoom in without any other camera movement?",
            "neg_question": "Does the camera only move forward without any other camera movement?",
            "pos_prompt": "A video where the camera only zooms in with no other movement.",
            "neg_prompt": "A video where the camera only moves forward with no other movement.",
            "pos": {
                "label": "cam_motion.camera_centric_movement.zoom_in.only_zoom_in",
                "type": "pos",
            },
            "neg": {
                "label": "cam_motion.camera_centric_movement.forward.only_forward_wrt_camera",
                "type": "pos",
            },
        },
        {
            "folder": ground_only_folder,
            "name": "only_zoom_out_vs_only_backward",
            "pos_question": "Does the camera only zoom out without any other camera movement?",
            "neg_question": "Does the camera only move backward without any other camera movement?",
            "pos_prompt": "A video where the camera only zooms out with no other movement.",
            "neg_prompt": "A video where the camera only moves backward with no other movement.",
            "pos": {
                "label": "cam_motion.camera_centric_movement.zoom_out.only_zoom_out",
                "type": "pos",
            },
            "neg": {
                "label": "cam_motion.camera_centric_movement.backward.only_backward_wrt_camera",
                "type": "pos",
            },
        },
    ]

def get_rotation_vs_translation_tasks(ground_only_folder=CAMERABENCH_GROUND_ONLY_FOLDER,
                                  ground_and_setup_folder=CAMERABENCH_GROUND_AND_SETUP_FOLDER,
                                  ground_and_camera_folder=CAMERABENCH_CAMERA_AND_CAMERA_FOLDER):
    return [
        # Rotation vs. Translation (8 tasks)
        {
            "folder": ground_only_folder,
            "name": "has_pan_right_not_truck_vs_has_truck_not_pan_right",
            "pos_question": "Does the camera pan right without moving laterally to the right?",
            "neg_question": "Does the camera move laterally to the right without panning right?",
            "pos_prompt": "The camera pans right without moving laterally to the right.",
            "neg_prompt": "The camera moves laterally to the right without panning right.",
            "pos": [
                {
                    "label": "cam_motion.camera_centric_movement.pan_right.has_pan_right",
                    "type": "pos",
                },
                {
                    "label": "cam_motion.camera_centric_movement.rightward.has_rightward",
                    "type": "neg",
                },
            ],
            "neg": [
                {
                    "label": "cam_motion.camera_centric_movement.pan_right.has_pan_right",
                    "type": "neg",
                },
                {
                    "label": "cam_motion.camera_centric_movement.rightward.has_rightward",
                    "type": "pos",
                },
            ],
        },
        {
            "folder": ground_only_folder,
            "name": "has_pan_left_not_truck_vs_has_truck_not_pan_left",
            "pos_question": "Does the camera pan left without moving laterally to the left?",
            "neg_question": "Does the camera move laterally to the left without panning left?",
            "pos_prompt": "The camera pans left without moving laterally to the left.",
            "neg_prompt": "The camera moves laterally to the left without panning left.",
            "pos": [
                {
                    "label": "cam_motion.camera_centric_movement.pan_left.has_pan_left",
                    "type": "pos",
                },
                {
                    "label": "cam_motion.camera_centric_movement.leftward.has_leftward",
                    "type": "neg",
                },
            ],
            "neg": [
                {
                    "label": "cam_motion.camera_centric_movement.pan_left.has_pan_left",
                    "type": "neg",
                },
                {
                    "label": "cam_motion.camera_centric_movement.leftward.has_leftward",
                    "type": "pos",
                },
            ],
        },
        {
            "folder": ground_only_folder,
            "name": "only_pan_right_vs_only_truck_right",
            "pos_question": "Does the camera only pan right with no other movement?",
            "neg_question": "Does the camera only move laterally to the right with no other movement?",
            "pos_prompt": "A video where the camera only pans right with no other movement.",
            "neg_prompt": "A video where the camera only moves laterally to the right with no other movement.",
            "pos": {
                "label": "cam_motion.camera_centric_movement.pan_right.only_pan_right",
                "type": "pos",
            },
            "neg": {
                "label": "cam_motion.camera_centric_movement.rightward.only_rightward",
                "type": "pos",
            },
        },
        {
            "folder": ground_only_folder,
            "name": "only_pan_left_vs_only_truck_left",
            "pos_question": "Does the camera only pan left with no other movement?",
            "neg_question": "Does the camera only move laterally to the left with no other movement?",
            "pos_prompt": "A video where the camera only pans left with no other movement.",
            "neg_prompt": "A video where the camera only moves laterally to the left with no other movement.",
            "pos": {
                "label": "cam_motion.camera_centric_movement.pan_left.only_pan_left",
                "type": "pos",
            },
            "neg": {
                "label": "cam_motion.camera_centric_movement.leftward.only_leftward",
                "type": "pos",
            },
        },
        {
            "folder": ground_and_setup_folder,
            "name": "has_tilt_up_not_pedestal_vs_has_pedestal_not_tilt_up",
            "pos_question": "Does the camera tilt up without moving physically upward?",
            "neg_question": "Does the camera move physically upward without tilting up?",
            "pos_prompt": "A video where the camera tilts up without physically moving upward.",
            "neg_prompt": "A video where the camera physically moves upward without tilting up.",
            "pos": [
                {
                    "label": "cam_motion.camera_centric_movement.tilt_up.has_tilt_up",
                    "type": "pos",
                },
                {
                    "label": "cam_motion.camera_centric_movement.upward.has_upward_wrt_camera",
                    "type": "neg",
                },
                {
                    "label": "cam_motion.ground_centric_movement.upward.has_upward_wrt_ground",
                    "type": "neg",
                },
            ],
            "neg": [
                {
                    "label": "cam_motion.camera_centric_movement.tilt_up.has_tilt_up",
                    "type": "neg",
                },
                {
                    "label": "cam_motion.camera_centric_movement.upward.has_upward_wrt_camera",
                    "type": "pos",
                },
                {
                    "label": "cam_motion.ground_centric_movement.upward.has_upward_wrt_ground",
                    "type": "pos",
                },
            ],
        },
        {
            "folder": ground_and_setup_folder,
            "name": "has_tilt_down_not_pedestal_vs_has_pedestal_not_tilt_down",
            "pos_question": "Does the camera tilt down without moving physically downward?",
            "neg_question": "Does the camera move physically downward without tilting down?",
            "pos_prompt": "A video where the camera tilts down without physically moving downward.",
            "neg_prompt": "A video where the camera physically moves downward without tilting down.",
            "pos": [
                {
                    "label": "cam_motion.camera_centric_movement.tilt_down.has_tilt_down",
                    "type": "pos",
                },
                {
                    "label": "cam_motion.camera_centric_movement.downward.has_downward_wrt_camera",
                    "type": "neg",
                },
                {
                    "label": "cam_motion.ground_centric_movement.downward.has_downward_wrt_ground",
                    "type": "neg",
                },
            ],
            "neg": [
                {
                    "label": "cam_motion.camera_centric_movement.tilt_down.has_tilt_down",
                    "type": "neg",
                },
                {
                    "label": "cam_motion.camera_centric_movement.downward.has_downward_wrt_camera",
                    "type": "pos",
                },
                {
                    "label": "cam_motion.ground_centric_movement.downward.has_downward_wrt_ground",
                    "type": "pos",
                },
            ],
        },
        {
            "folder": ground_and_camera_folder,
            "name": "only_tilt_up_vs_only_pedestal_up",
            "pos_question": "Does the camera only tilt up with no other movement?",
            "neg_question": "Does the camera only move physically upward (pedestal up) with no other movement?",
            "pos_prompt": "A video where the camera only tilts up with no other movement.",
            "neg_prompt": "A video where the camera only moves physically upward with no other movement.",
            "pos": {
                "label": "cam_motion.camera_centric_movement.tilt_up.only_tilt_up",
                "type": "pos",
            },
            "neg": {
                "label": "cam_motion.camera_centric_movement.upward.only_upward_wrt_camera",
                "type": "pos",
            },
        },
        {
            "folder": ground_and_camera_folder,
            "name": "only_tilt_down_vs_only_pedestal_down",
            "pos_question": "Does the camera only tilt down with no other movement?",
            "neg_question": "Does the camera only move physically downward (pedestal down) with no other movement?",
            "pos_prompt": "A video where the camera only tilts down with no other movement.",
            "neg_prompt": "A video where the camera only moves physically downward with no other movement.",
            "pos": {
                "label": "cam_motion.camera_centric_movement.tilt_down.only_tilt_down",
                "type": "pos",
            },
            "neg": {
                "label": "cam_motion.camera_centric_movement.downward.only_downward_wrt_camera",
                "type": "pos",
            },
        },
    ]

def get_has_intrinsic_change_tasks(ground_only_folder=CAMERABENCH_GROUND_ONLY_FOLDER):
    return [
        {
            "folder": ground_only_folder,
            "name": "has_zoom_in",
            "pos_question": "Does the camera zoom in?",
            "neg_question": "Is the camera free from any zoom in effects?",
            "pos_prompt": "The camera zooms in.",
            "neg_prompt": "The camera is free from any zoom in effects.",
            "pos": {
                "label": "cam_motion.camera_centric_movement.zoom_in.has_zoom_in",
                "type": "pos",
            },
            "neg": {
                "label": "cam_motion.camera_centric_movement.zoom_in.has_zoom_in",
                "type": "neg",
            },
        },
        {
            "folder": ground_only_folder,
            "name": "has_zoom_out",
            "pos_question": "Does the camera zoom out?",
            "neg_question": "Is the camera free from any zoom out effects?",
            "pos_prompt": "The camera zooms out.",
            "neg_prompt": "The camera is free from any zoom out effects.",
            "pos": {
                "label": "cam_motion.camera_centric_movement.zoom_out.has_zoom_out",
                "type": "pos",
            },
            "neg": {
                "label": "cam_motion.camera_centric_movement.zoom_out.has_zoom_out",
                "type": "neg",
            },
        },
    ]

def get_has_translation_tasks(ground_and_setup_folder=CAMERABENCH_GROUND_AND_SETUP_FOLDER,
                              ground_only_folder=CAMERABENCH_GROUND_ONLY_FOLDER):
    return [
        {
            "folder": ground_and_setup_folder,
            "name": "has_forward_motion",
            "pos_question": "Is the camera moving forward in the scene?",
            "neg_question": "Is the camera free from any forward motion?",
            "pos_prompt": "The camera is moving forward within the scene.",
            "neg_prompt": "The camera is free from any forward motion.",
            "pos": {
                "label": "cam_motion.ground_centric_movement.forward.has_forward_wrt_ground",
                "type": "pos",
            },
            "neg": {
                "label": "cam_motion.ground_centric_movement.forward.has_forward_wrt_ground",
                "type": "neg",
            },
        },
        {
            "folder": ground_and_setup_folder,
            "name": "has_backward_motion",
            "pos_question": "Is the camera moving backward in the scene?",
            "neg_question": "Is the camera free from any backward motion?",
            "pos_prompt": "The camera is moving backward within the scene.",
            "neg_prompt": "The camera is free from any backward motion.",
            "pos": {
                "label": "cam_motion.ground_centric_movement.backward.has_backward_wrt_ground",
                "type": "pos",
            },
            "neg": {
                "label": "cam_motion.ground_centric_movement.backward.has_backward_wrt_ground",
                "type": "neg",
            },
        },
        {
            "folder": ground_only_folder,
            "name": "has_truck_left",
            "pos_question": "Does the camera move laterally to the left?",
            "neg_question": "Is the camera free from any leftward lateral movement?",
            "pos_prompt": "The camera moves laterally to the left.",
            "neg_prompt": "The camera is free from any leftward lateral movement.",
            "pos": {
                "label": "cam_motion.camera_centric_movement.leftward.has_leftward",
                "type": "pos",
            },
            "neg": {
                "label": "cam_motion.camera_centric_movement.leftward.has_leftward",
                "type": "neg",
            },
        },
        {
            "folder": ground_only_folder,
            "name": "has_truck_right",
            "pos_question": "Does the camera move laterally to the right?",
            "neg_question": "Is the camera free from any rightward lateral movement?",
            "pos_prompt": "The camera moves laterally to the right.",
            "neg_prompt": "The camera is free from any rightward lateral movement.",
            "pos": {
                "label": "cam_motion.camera_centric_movement.rightward.has_rightward",
                "type": "pos",
            },
            "neg": {
                "label": "cam_motion.camera_centric_movement.rightward.has_rightward",
                "type": "neg",
            },
        },
        {
            "folder": ground_and_setup_folder,
            "name": "has_pedestal_up",
            "pos_question": "Does the camera move upward relative to the ground?",
            "neg_question": "Is the camera free from any upward pedestal motion?",
            "pos_prompt": "The camera moves upward relative to the ground.",
            "neg_prompt": "The camera is free from any upward pedestal motion.",
            "pos": {
                "label": "cam_motion.ground_centric_movement.upward.has_upward_wrt_ground",
                "type": "pos",
            },
            "neg": {
                "label": "cam_motion.ground_centric_movement.upward.has_upward_wrt_ground",
                "type": "neg",
            },
        },
        {
            "folder": ground_and_setup_folder,
            "name": "has_pedestal_down",
            "pos_question": "Does the camera move downward relative to the ground?",
            "neg_question": "Is the camera free from any downward pedestal motion?",
            "pos_prompt": "The camera moves downward relative to the ground.",
            "neg_prompt": "The camera is free from any downward pedestal motion.",
            "pos": {
                "label": "cam_motion.ground_centric_movement.downward.has_downward_wrt_ground",
                "type": "pos",
            },
            "neg": {
                "label": "cam_motion.ground_centric_movement.downward.has_downward_wrt_ground",
                "type": "neg",
            },
        },
    ]

def get_has_rotation_tasks(ground_only_folder=CAMERABENCH_GROUND_ONLY_FOLDER):
    return [
        {
            "folder": ground_only_folder,
            "name": "has_pan_left",
            "pos_question": "Does the camera pan to the left?",
            "neg_question": "Is the camera free from any leftward panning motion?",
            "pos_prompt": "The camera pans to the left.",
            "neg_prompt": "The camera is free from any leftward panning motion.",
            "pos": {
                "label": "cam_motion.camera_centric_movement.pan_left.has_pan_left",
                "type": "pos",
            },
            "neg": {
                "label": "cam_motion.camera_centric_movement.pan_left.has_pan_left",
                "type": "neg",
            },
        },
        {
            "folder": ground_only_folder,
            "name": "has_pan_right",
            "pos_question": "Does the camera pan to the right?",
            "neg_question": "Is the camera free from any rightward panning motion?",
            "pos_prompt": "The camera pans to the right.",
            "neg_prompt": "The camera is free from any rightward panning motion.",
            "pos": {
                "label": "cam_motion.camera_centric_movement.pan_right.has_pan_right",
                "type": "pos",
            },
            "neg": {
                "label": "cam_motion.camera_centric_movement.pan_right.has_pan_right",
                "type": "neg",
            },
        },
        {
            "folder": ground_only_folder,
            "name": "has_tilt_up",
            "pos_question": "Does the camera tilt upward?",
            "neg_question": "Is the camera free from any upward tilting motion?",
            "pos_prompt": "The camera tilts upward.",
            "neg_prompt": "The camera is free from any upward tilting motion.",
            "pos": {
                "label": "cam_motion.camera_centric_movement.tilt_up.has_tilt_up",
                "type": "pos",
            },
            "neg": {
                "label": "cam_motion.camera_centric_movement.tilt_up.has_tilt_up",
                "type": "neg",
            },
        },
        {
            "folder": ground_only_folder,
            "name": "has_tilt_down",
            "pos_question": "Does the camera tilt downward?",
            "neg_question": "Is the camera free from any downward tilting motion?",
            "pos_prompt": "The camera tilts downward.",
            "neg_prompt": "The camera is free from any downward tilting motion.",
            "pos": {
                "label": "cam_motion.camera_centric_movement.tilt_down.has_tilt_down",
                "type": "pos",
            },
            "neg": {
                "label": "cam_motion.camera_centric_movement.tilt_down.has_tilt_down",
                "type": "neg",
            },
        },
        {
            "folder": ground_only_folder,
            "name": "has_roll_clockwise",
            "pos_question": "Does the camera roll clockwise?",
            "neg_question": "Is the camera free from any clockwise rolling motion?",
            "pos_prompt": "The camera rolls clockwise.",
            "neg_prompt": "The camera is free from any clockwise rolling motion.",
            "pos": {
                "label": "cam_motion.camera_centric_movement.roll_clockwise.has_roll_clockwise",
                "type": "pos",
            },
            "neg": {
                "label": "cam_motion.camera_centric_movement.roll_clockwise.has_roll_clockwise",
                "type": "neg",
            },
        },
        {
            "folder": ground_only_folder,
            "name": "has_roll_counterclockwise",
            "pos_question": "Does the camera roll counterclockwise?",
            "neg_question": "Is the camera free from any counterclockwise rolling motion?",
            "pos_prompt": "The camera rolls counterclockwise.",
            "neg_prompt": "The camera is free from any counterclockwise rolling motion.",
            "pos": {
                "label": "cam_motion.camera_centric_movement.roll_counterclockwise.has_roll_counterclockwise",
                "type": "pos",
            },
            "neg": {
                "label": "cam_motion.camera_centric_movement.roll_counterclockwise.has_roll_counterclockwise",
                "type": "neg",
            },
        },
    ]

def get_has_arc_crane_tasks(ground_only_folder=CAMERABENCH_GROUND_ONLY_FOLDER):
    return [
        {
            "folder": ground_only_folder,
            "name": "has_arc_clockwise",
            "pos_question": "Does the camera move in a clockwise arc?",
            "neg_question": "Is the camera free from any clockwise arc movement?",
            "pos_prompt": "The camera moves in a clockwise arc.",
            "neg_prompt": "The camera is free from any clockwise arc movement.",
            "pos": {
                "label": "cam_motion.arc_crane_movement.arc_clockwise.has_arc_clockwise",
                "type": "pos",
            },
            "neg": {
                "label": "cam_motion.arc_crane_movement.arc_clockwise.has_arc_clockwise",
                "type": "neg",
            },
        },
        {
            "folder": ground_only_folder,
            "name": "has_arc_counterclockwise",
            "pos_question": "Does the camera move in a counterclockwise arc?",
            "neg_question": "Is the camera free from any counterclockwise arc movement?",
            "pos_prompt": "The camera moves in a counterclockwise arc.",
            "neg_prompt": "The camera is free from any counterclockwise arc movement.",
            "pos": {
                "label": "cam_motion.arc_crane_movement.arc_counterclockwise.has_arc_counterclockwise",
                "type": "pos",
            },
            "neg": {
                "label": "cam_motion.arc_crane_movement.arc_counterclockwise.has_arc_counterclockwise",
                "type": "neg",
            },
        },
        {
            "folder": ground_only_folder,
            "name": "has_crane_up",
            "pos_question": "Does the camera crane upward in an arc?",
            "neg_question": "Is the camera not craning upward in an arc?",
            "pos_prompt": "The camera cranes upward in an arc.",
            "neg_prompt": "The camera is not craning upward in an arc.",
            "pos": {
                "label": "cam_motion.arc_crane_movement.crane_up.has_crane_up",
                "type": "pos",
            },
            "neg": {
                "label": "cam_motion.arc_crane_movement.crane_up.has_crane_up",
                "type": "neg",
            },
        },
        {
            "folder": ground_only_folder,
            "name": "has_crane_down",
            "pos_question": "Does the camera crane downward in an arc?",
            "neg_question": "Is the camera not craning downward in an arc?",
            "pos_prompt": "The camera cranes downward in an arc.",
            "neg_prompt": "The camera is not craning downward in an arc.",
            "pos": {
                "label": "cam_motion.arc_crane_movement.crane_down.has_crane_down",
                "type": "pos",
            },
            "neg": {
                "label": "cam_motion.arc_crane_movement.crane_down.has_crane_down",
                "type": "neg",
            },
        },
    ]

def get_special_tracking_tasks(ground_only_folder=CAMERABENCH_GROUND_ONLY_FOLDER):
    return [
        {
            "folder": ground_only_folder,
            "name": "has_aerial_tracking",
            "pos_question": "Does the camera track the subject from an aerial perspective?",
            "neg_question": "Is the video not a tracking shot from an aerial perspective?",
            "pos_prompt": "The camera tracks the subject from an aerial perspective.",
            "neg_prompt": "The camera is not tracking the subject from an aerial perspective.",
            "pos": {
                "label": "cam_motion.object_centric_movement.aerial_tracking_shot",
                "type": "pos",
            },
            "neg": {
                "label": "cam_motion.object_centric_movement.aerial_tracking_shot",
                "type": "neg",
            },
        },
        {
            "folder": ground_only_folder,
            "name": "has_arc_tracking",
            "pos_question": "Does the camera follow the subject while moving in an arc?",
            "neg_question": "Is the video not a tracking shot with arc movement?",
            "pos_prompt": "A tracking shot where the camera follows the subject while moving in an arc.",
            "neg_prompt": "A video where the camera is not tracking the subject with arc movement.",
            "pos": {
                "label": "cam_motion.object_centric_movement.arc_tracking_shot",
                "type": "pos",
            },
            "neg": {
                "label": "cam_motion.object_centric_movement.arc_tracking_shot",
                "type": "neg",
            },
        },
        {
            "folder": ground_only_folder,
            "name": "has_front_side_tracking",
            "pos_question": "Is it a tracking shot with the camera leading the subject from a front-side angle?",
            "neg_question": "Is the camera not leading the subject from a front-side angle in a tracking shot?",
            "pos_prompt": "A tracking shot where the camera leads the subject from a front-side angle.",
            "neg_prompt": "The camera is not leading the subject from a front-side angle in a tracking shot.",
            "pos": {
                "label": "cam_motion.object_centric_movement.front_side_tracking_shot",
                "type": "pos",
            },
            "neg": {
                "label": "cam_motion.object_centric_movement.front_side_tracking_shot",
                "type": "neg",
            },
        },
        {
            "folder": ground_only_folder,
            "name": "has_rear_side_tracking",
            "pos_question": "Is it a tracking shot with the camera following behind the subject at a rear-side angle?",
            "neg_question": "Is the camera not following behind the subject at a rear-side angle?",
            "pos_prompt": "A tracking shot where the camera follows behind the subject at a rear-side angle.",
            "neg_prompt": "The camera is not following behind the subject at a rear-side angle.",
            "pos": {
                "label": "cam_motion.object_centric_movement.rear_side_tracking_shot",
                "type": "pos",
            },
            "neg": {
                "label": "cam_motion.object_centric_movement.rear_side_tracking_shot",
                "type": "neg",
            },
        },
        {
            "folder": ground_only_folder,
            "name": "has_lead_tracking",
            "pos_question": "Is it a tracking shot with the camera moving ahead of the subject as they move?",
            "neg_question": "Is the camera not moving ahead of the subject in a tracking shot?",
            "pos_prompt": "A tracking shot where the camera moves ahead of the subjects as they move.",
            "neg_prompt": "The camera is not moving ahead of the subject in a tracking shot.",
            "pos": {
                "label": "cam_motion.object_centric_movement.lead_tracking_shot",
                "type": "pos",
            },
            "neg": {
                "label": "cam_motion.object_centric_movement.lead_tracking_shot",
                "type": "neg",
            },
        },
        {
            "folder": ground_only_folder,
            "name": "has_tail_tracking",
            "pos_question": "Is it a tracking shot with the camera following behind the subject as they move?",
            "neg_question": "Is the camera not following behind the subject in a tracking shot?",
            "pos_prompt": "A tracking shot where the camera moves behind the subjects as they move.",
            "neg_prompt": "The camera is not following behind the subject in a tracking shot.",
            "pos": {
                "label": "cam_motion.object_centric_movement.tail_tracking_shot",
                "type": "pos",
            },
            "neg": {
                "label": "cam_motion.object_centric_movement.tail_tracking_shot",
                "type": "neg",
            },
        },
        {
            "folder": ground_only_folder,
            "name": "has_tilt_tracking",
            "pos_question": "Does the camera tilt to track the subjects as they move?",
            "neg_question": "Is the camera not tilting to track the subjects?",
            "pos_prompt": "A tracking shot where the camera tilts to follow the subjects.",
            "neg_prompt": "The camera is not tilting to track the subjects.",
            "pos": {
                "label": "cam_motion.object_centric_movement.tilt_tracking_shot",
                "type": "pos",
            },
            "neg": {
                "label": "cam_motion.object_centric_movement.tilt_tracking_shot",
                "type": "neg",
            },
        },
        {
            "folder": ground_only_folder,
            "name": "has_pan_tracking",
            "pos_question": "Does the camera pan to track the subjects as they move?",
            "neg_question": "Is the camera not panning to track the subjects?",
            "pos_prompt": "A tracking shot where the camera pans to follow the subjects as they move.",
            "neg_prompt": "The camera is not panning to track the subjects.",
            "pos": {
                "label": "cam_motion.object_centric_movement.pan_tracking_shot",
                "type": "pos",
            },
            "neg": {
                "label": "cam_motion.object_centric_movement.pan_tracking_shot",
                "type": "neg",
            },
        },
        {
            "folder": ground_only_folder,
            "name": "has_side_tracking",
            "pos_question": "Is it a tracking shot with the camera moving from the side to follow the subject as they move?",
            "neg_question": "Is the camera not moving from the side to track the subject?",
            "pos_prompt": "A tracking shot where the camera moves from the side to follow the subject.",
            "neg_prompt": "The camera is not moving from the side to track the subject.",
            "pos": {
                "label": "cam_motion.object_centric_movement.side_tracking_shot",
                "type": "pos",
            },
            "neg": {
                "label": "cam_motion.object_centric_movement.side_tracking_shot",
                "type": "neg",
            },
        },
    ]

def get_general_tracking_tasks(ground_only_folder=CAMERABENCH_GROUND_ONLY_FOLDER):
    return [
        {
            "folder": ground_only_folder,
            "name": "is_tracking",
            "pos_question": "Does the camera track the subject as they move?",
            "neg_question": "Is the video not a tracking shot?",
            "pos_prompt": "The camera tracks the subject as they move.",
            "neg_prompt": "The video is not a tracking shot.",
            "pos": {
                "label": "cam_motion.object_centric_movement.track_shot",
                "type": "pos",
            },
            "neg": {
                "label": "cam_motion.object_centric_movement.track_shot",
                "type": "neg",
            },
        },
        {
            "folder": ground_only_folder,
            "name": "tracking_subject_larger",
            "pos_question": "Does the subject appear larger during the tracking shot?",
            "neg_question": "Does the subject being tracked not appear larger in size?",
            "pos_prompt": "The subject looks larger during the tracking shot.",
            "neg_prompt": "The subject being tracked does not appear larger in size.",
            "pos": {
                "label": "cam_motion.object_centric_movement.tracking_subject_larger_size",
                "type": "pos",
            },
            "neg": {
                "label": "cam_motion.object_centric_movement.tracking_subject_larger_size",
                "type": "neg",
            },
        },
        {
            "folder": ground_only_folder,
            "name": "tracking_subject_smaller",
            "pos_question": "Does the subject appear smaller during the tracking shot?",
            "neg_question": "Does the subject being tracked not appear smaller in size?",
            "pos_prompt": "The subject looks smaller during the tracking shot.",
            "neg_prompt": "The subject being tracked does not appear smaller in size.",
            "pos": {
                "label": "cam_motion.object_centric_movement.tracking_subject_smaller_size",
                "type": "pos",
            },
            "neg": {
                "label": "cam_motion.object_centric_movement.tracking_subject_smaller_size",
                "type": "neg",
            },
        },
    ]

def get_only_intrinsic_change_tasks(ground_only_folder=CAMERABENCH_GROUND_ONLY_FOLDER):
    return [
        {
            "folder": ground_only_folder,
            "name": "only_zoom_in_vs_has_zoom_in_and_not_only",
            "pos_question": "Does the camera only zoom in with no other movement?",
            "neg_question": "Does the camera not just zoom in?",
            "pos_prompt": "The camera only zooms in without any other movement.",
            "neg_prompt": "The camera does not just zoom in.",
            "pos": {
                "label": "cam_motion.camera_centric_movement.zoom_in.only_zoom_in",
                "type": "pos",
            },
            "neg": [
                {
                    "label": "cam_motion.camera_centric_movement.zoom_in.has_zoom_in",
                    "type": "neg",
                },
                {
                    "label": "cam_motion.camera_centric_movement.zoom_in.only_zoom_in",
                    "type": "neg",
                },
            ],
        },
        {
            "folder": ground_only_folder,
            "name": "only_zoom_out_vs_has_zoom_out_and_not_only",
            "pos_question": "Does the camera only zoom out with no other movement?",
            "neg_question": "Does the camera not just zoom out?",
            "pos_prompt": "The camera only zooms out with no other movement.",
            "neg_prompt": "The camera does not just zoom out.",
            "pos": {
                "label": "cam_motion.camera_centric_movement.zoom_out.only_zoom_out",
                "type": "pos",
            },
            "neg": [
                {
                    "label": "cam_motion.camera_centric_movement.zoom_out.has_zoom_out",
                    "type": "neg",
                },
                {
                    "label": "cam_motion.camera_centric_movement.zoom_out.only_zoom_out",
                    "type": "neg",
                },
            ],
        },
    ]

def get_only_translation_tasks(ground_and_setup_folder=CAMERABENCH_GROUND_AND_SETUP_FOLDER,
                               ground_only_folder=CAMERABENCH_GROUND_ONLY_FOLDER):
    return [
        {
            "folder": ground_and_setup_folder,
            "name": "only_forward_vs_has_forward_and_not_only",
            "pos_question": "Does the camera only move forward (not zooming in) with respect to the ground?",
            "neg_question": "Does the camera not just move forward with respect to the ground?",
            "pos_prompt": "The camera only moves forward (not zooming in) relative to the ground.",
            "neg_prompt": "The camera not just moves forward relative to the ground.",
            "pos": {
                "label": "cam_motion.ground_centric_movement.forward.only_forward_wrt_ground",
                "type": "pos",
            },
            "neg": [
                {
                    "label": "cam_motion.ground_centric_movement.forward.has_forward_wrt_ground",
                    "type": "neg",
                },
                {
                    "label": "cam_motion.ground_centric_movement.forward.only_forward_wrt_ground",
                    "type": "neg",
                },
            ],
        },
        {
            "folder": ground_and_setup_folder,
            "name": "only_backward_vs_has_backward_and_not_only",
            "pos_question": "Does the camera only move backward (not zooming out) with respect to the ground?",
            "neg_question": "Does the camera not just move backward with respect to the ground?",
            "pos_prompt": "The camera only moves backward (not zooming out) relative to the ground.",
            "neg_prompt": "The camera not just moves backward relative to the ground.",
            "pos": {
                "label": "cam_motion.ground_centric_movement.backward.only_backward_wrt_ground",
                "type": "pos",
            },
            "neg": [
                {
                    "label": "cam_motion.ground_centric_movement.backward.has_backward_wrt_ground",
                    "type": "neg",
                },
                {
                    "label": "cam_motion.ground_centric_movement.backward.only_backward_wrt_ground",
                    "type": "neg",
                },
            ],
        },
        {
            "folder": ground_only_folder,
            "name": "only_truck_left_vs_has_truck_left_and_not_only",
            "pos_question": "Does the camera only move leftward without any other camera movements?",
            "neg_question": "Does the camera not just move laterally to the left?",
            "pos_prompt": "The camera only moves leftward without any other camera movements.",
            "neg_prompt": "The camera not just moves laterally to the left.",
            "pos": {
                "label": "cam_motion.camera_centric_movement.leftward.only_leftward",
                "type": "pos",
            },
            "neg": [
                {
                    "label": "cam_motion.camera_centric_movement.leftward.has_leftward",
                    "type": "neg",
                },
                {
                    "label": "cam_motion.camera_centric_movement.leftward.only_leftward",
                    "type": "neg",
                },
            ],
        },
        {
            "folder": ground_only_folder,
            "name": "only_truck_right_vs_has_truck_right_and_not_only",
            "pos_question": "Does the camera only move rightward without any other camera movements?",
            "neg_question": "Does the camera not just move laterally to the right?",
            "pos_prompt": "The camera only moves rightward without any other camera movements.",
            "neg_prompt": "The camera not just moves laterally to the right.",
            "pos": {
                "label": "cam_motion.camera_centric_movement.rightward.only_rightward",
                "type": "pos",
            },
            "neg": [
                {
                    "label": "cam_motion.camera_centric_movement.rightward.has_rightward",
                    "type": "neg",
                },
                {
                    "label": "cam_motion.camera_centric_movement.rightward.only_rightward",
                    "type": "neg",
                },
            ],
        },
        {
            "folder": ground_and_setup_folder,
            "name": "only_pedestal_up_vs_has_pedestal_up_and_not_only",
            "pos_question": "Does the camera only move upward (not tilting up) with respect to the ground?",
            "neg_question": "Does the camera not just move physically upward?",
            "pos_prompt": "The camera only moves upward (not tilting up) relative to the ground.",
            "neg_prompt": "The camera not just moves physically upward.",
            "pos": {
                "label": "cam_motion.ground_centric_movement.upward.only_upward_wrt_ground",
                "type": "pos",
            },
            "neg": [
                {
                    "label": "cam_motion.ground_centric_movement.upward.has_upward_wrt_ground",
                    "type": "neg",
                },
                {
                    "label": "cam_motion.ground_centric_movement.upward.only_upward_wrt_ground",
                    "type": "neg",
                },
            ],
        },
        {
            "folder": ground_and_setup_folder,
            "name": "only_pedestal_down_vs_has_pedestal_down_and_not_only",
            "pos_question": "Does the camera only move downward (not tilting down) with respect to the ground?",
            "neg_question": "Does the camera not just move physically downward?",
            "pos_prompt": "The camera only moves downward (not tilting down) relative to the ground.",
            "neg_prompt": "The camera not just moves physically downward.",
            "pos": {
                "label": "cam_motion.ground_centric_movement.downward.only_downward_wrt_ground",
                "type": "pos",
            },
            "neg": [
                {
                    "label": "cam_motion.ground_centric_movement.downward.has_downward_wrt_ground",
                    "type": "neg",
                },
                {
                    "label": "cam_motion.ground_centric_movement.downward.only_downward_wrt_ground",
                    "type": "neg",
                },
            ],
        },
    ]

def get_only_rotation_tasks(ground_only_folder=CAMERABENCH_GROUND_ONLY_FOLDER):
    return [
        {
            "folder": ground_only_folder,
            "name": "only_pan_left_vs_has_pan_left_and_not_only",
            "pos_question": "Does the camera only pan leftward without any other camera movements?",
            "neg_question": "Does the camera not just pan left?",
            "pos_prompt": "The camera only pans leftward without any other camera movements.",
            "neg_prompt": "The camera not just pans left.",
            "pos": {
                "label": "cam_motion.camera_centric_movement.pan_left.only_pan_left",
                "type": "pos",
            },
            "neg": [
                {
                    "label": "cam_motion.camera_centric_movement.pan_left.has_pan_left",
                    "type": "neg",
                },
                {
                    "label": "cam_motion.camera_centric_movement.pan_left.only_pan_left",
                    "type": "neg",
                },
            ],
        },
        {
            "folder": ground_only_folder,
            "name": "only_pan_right_vs_has_pan_right_and_not_only",
            "pos_question": "Does the camera only pan rightward without any other camera movements?",
            "neg_question": "Does the camera not just pan right?",
            "pos_prompt": "The camera only pans rightward without any other camera movements.",
            "neg_prompt": "The camera not just pans right.",
            "pos": {
                "label": "cam_motion.camera_centric_movement.pan_right.only_pan_right",
                "type": "pos",
            },
            "neg": [
                {
                    "label": "cam_motion.camera_centric_movement.pan_right.has_pan_right",
                    "type": "neg",
                },
                {
                    "label": "cam_motion.camera_centric_movement.pan_right.only_pan_right",
                    "type": "neg",
                },
            ],
        },
        {
            "folder": ground_only_folder,
            "name": "only_tilt_up_vs_has_tilt_up_and_not_only",
            "pos_question": "Does the camera only tilt upward without any other camera movements?",
            "neg_question": "Does the camera not just tilt up?",
            "pos_prompt": "The camera only tilts upward without any other camera movements.",
            "neg_prompt": "The camera not just tilts up.",
            "pos": {
                "label": "cam_motion.camera_centric_movement.tilt_up.only_tilt_up",
                "type": "pos",
            },
            "neg": [
                {
                    "label": "cam_motion.camera_centric_movement.tilt_up.has_tilt_up",
                    "type": "neg",
                },
                {
                    "label": "cam_motion.camera_centric_movement.tilt_up.only_tilt_up",
                    "type": "neg",
                },
            ],
        },
        {
            "folder": ground_only_folder,
            "name": "only_tilt_down_vs_has_tilt_down_and_not_only",
            "pos_question": "Does the camera only tilt downward without any other camera movements?",
            "neg_question": "Does the camera not just tilt down?",
            "pos_prompt": "The camera only tilts downward without any other camera movements.",
            "neg_prompt": "The camera not just tilts down.",
            "pos": {
                "label": "cam_motion.camera_centric_movement.tilt_down.only_tilt_down",
                "type": "pos",
            },
            "neg": [
                {
                    "label": "cam_motion.camera_centric_movement.tilt_down.has_tilt_down",
                    "type": "neg",
                },
                {
                    "label": "cam_motion.camera_centric_movement.tilt_down.only_tilt_down",
                    "type": "neg",
                },
            ],
        },
        {
            "folder": ground_only_folder,
            "name": "only_roll_cc_vs_has_roll_cc_and_not_only",
            "pos_question": "Does the camera only roll clockwise without any other camera movements?",
            "neg_question": "Does the camera not just roll clockwise?",
            "pos_prompt": "The camera only rolls clockwise without any other camera movements.",
            "neg_prompt": "The camera not just rolls clockwise.",
            "pos": {
                "label": "cam_motion.camera_centric_movement.roll_clockwise.only_roll_clockwise",
                "type": "pos",
            },
            "neg": [
                {
                    "label": "cam_motion.camera_centric_movement.roll_clockwise.has_roll_clockwise",
                    "type": "neg",
                },
                {
                    "label": "cam_motion.camera_centric_movement.roll_clockwise.only_roll_clockwise",
                    "type": "neg",
                },
            ],
        },
        {
            "folder": ground_only_folder,
            "name": "only_roll_ccw_vs_has_roll_ccw_and_not_only",
            "pos_question": "Does the camera only roll counterclockwise without any other camera movements?",
            "neg_question": "Does the camera not just roll counterclockwise?",
            "pos_prompt": "The camera only rolls counterclockwise without any other camera movements.",
            "neg_prompt": "The camera not just rolls counterclockwise.",
            "pos": {
                "label": "cam_motion.camera_centric_movement.roll_counterclockwise.only_roll_counterclockwise",
                "type": "pos",
            },
            "neg": [
                {
                    "label": "cam_motion.camera_centric_movement.roll_counterclockwise.has_roll_counterclockwise",
                    "type": "neg",
                },
                {
                    "label": "cam_motion.camera_centric_movement.roll_counterclockwise.only_roll_counterclockwise",
                    "type": "neg",
                },
            ],
        },
    ]

def get_reference_frame_tasks(ground_only_folder=CAMERABENCH_GROUND_ONLY_FOLDER):
    return [
        {
            # "folder": ground_and_camera_folder,
            "folder": ground_only_folder,
            "name": "forward_camera_only_vs_forward_ground_and_camera",
            "pos_question": "Does the camera move forward only relative to its initial viewing direction but not relative to the ground?",
            "neg_question": "Does the camera move forward relative to both the ground and its initial viewing direction?",
            "pos_prompt": "The camera moves forward only relative to its initial viewing direction but not relative to the ground.",
            "neg_prompt": "The camera moves forward relative to both the ground and its initial viewing direction.",
            "pos": [
                {
                    "label": "cam_motion.ground_centric_movement.forward.has_forward_wrt_ground_birds_worms_included",
                    "type": "neg",
                },
                {
                    "label": "cam_motion.camera_centric_movement.forward.has_forward_wrt_camera",
                    "type": "pos",
                },
            ],
            "neg": [
                {
                    "label": "cam_motion.camera_centric_movement.forward.has_forward_wrt_camera",
                    "type": "pos",
                },
                {
                    "label": "cam_motion.ground_centric_movement.forward.has_forward_wrt_ground_birds_worms_included",
                    "type": "pos",
                },
            ],
        },
        {
            # "folder": ground_and_camera_folder,
            "folder": ground_only_folder,
            "name": "backward_camera_only_vs_backward_ground_and_camera",
            "pos_question": "Does the camera move backward only relative to its initial viewing direction but not relative to the ground?",
            "neg_question": "Does the camera move backward relative to both the ground and its initial viewing direction?",
            "pos_prompt": "The camera moves backward only relative to its initial viewing direction but not relative to the ground.",
            "neg_prompt": "The camera moves backward relative to both the ground and its initial viewing direction.",
            "pos": [
                {
                    "label": "cam_motion.ground_centric_movement.backward.has_backward_wrt_ground_birds_worms_included",
                    "type": "neg",
                },
                {
                    "label": "cam_motion.camera_centric_movement.backward.has_backward_wrt_camera",
                    "type": "pos",
                },
            ],
            "neg": [
                {
                    "label": "cam_motion.camera_centric_movement.backward.has_backward_wrt_camera",
                    "type": "pos",
                },
                {
                    "label": "cam_motion.ground_centric_movement.backward.has_backward_wrt_ground_birds_worms_included",
                    "type": "pos",
                },
            ],
        },
        {
            # "folder": ground_and_camera_folder,
            "folder": ground_only_folder,
            "name": "upward_camera_only_vs_upward_camera_and_ground",
            "pos_question": "Does the camera move upward only relative to its initial viewing direction but not relative to the ground?",
            "neg_question": "Does the camera move upward relative to both the ground and its initial viewing direction?",
            "pos_prompt": "The camera moves upward only relative to its initial viewing direction but not relative to the ground.",
            "neg_prompt": "The camera moves upward relative to both the ground and its initial viewing direction.",
            "pos": [
                {
                    "label": "cam_motion.ground_centric_movement.upward.has_upward_wrt_ground_birds_worms_included",
                    "type": "neg",
                },
                {
                    "label": "cam_motion.camera_centric_movement.upward.has_upward_wrt_camera",
                    "type": "pos",
                },
            ],
            "neg": [
                {
                    "label": "cam_motion.camera_centric_movement.upward.has_upward_wrt_camera",
                    "type": "pos",
                },
                {
                    "label": "cam_motion.ground_centric_movement.upward.has_upward_wrt_ground_birds_worms_included",
                    "type": "pos",
                },
            ],
        },
        {
            # "folder": ground_and_camera_folder,
            "folder": ground_only_folder,
            "name": "downward_camera_only_vs_downward_camera_and_ground",
            "pos_question": "Does the camera move downward only relative to its initial viewing direction but not relative to the ground?",
            "neg_question": "Does the camera move downward relative to both the ground and its initial viewing direction?",
            "pos_prompt": "The camera moves downward only relative to its initial viewing direction but not relative to the ground.",
            "neg_prompt": "The camera moves downward relative to both the ground and its initial viewing direction.",
            "pos": [
                {
                    "label": "cam_motion.ground_centric_movement.downward.has_downward_wrt_ground_birds_worms_included",
                    "type": "neg",
                },
                {
                    "label": "cam_motion.camera_centric_movement.downward.has_downward_wrt_camera",
                    "type": "pos",
                },
            ],
            "neg": [
                {
                    "label": "cam_motion.camera_centric_movement.downward.has_downward_wrt_camera",
                    "type": "pos",
                },
                {
                    "label": "cam_motion.ground_centric_movement.downward.has_downward_wrt_ground_birds_worms_included",
                    "type": "pos",
                },
            ],
        },
    ]

PAIRWISE_LABELS = {
    "movement_and_steadiness": movement_and_steadiness_tasks,
    "scene_dynamics": scene_dynamics_tasks,
    "camera_movement_speed": camera_movement_speed_tasks,
    "translation_direction": translation_direction_tasks,
    "rotation_direction": rotation_direction_tasks,
    "object_centric_direction": object_centric_direction_tasks,
    "intrinsic_direction": intrinsic_direction_tasks,
    "instrinsic_vs_extrinsic": instrinsic_vs_extrinsic,
    "rotation_vs_translation": rotation_vs_translation,
    "has_intrinsic_change": has_intrinsic_change_tasks,
    "has_translation": has_translation_tasks,
    "has_rotation": has_rotation_tasks,
    "has_arc_crane": has_arc_crane_tasks,
    "special_tracking": special_tracking_tasks,
    "general_tracking": general_tracking_tasks,
    "only_intrinsic_change": only_intrinsic_change_tasks,
    "only_translation": only_translation_tasks,
    "only_rotation": only_rotation_tasks,
    "reference_frame": reference_frame_tasks,
}
