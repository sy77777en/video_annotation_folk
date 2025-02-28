from benchmark import ROOT, VIDEO_ROOT, VIDEO_LABELS_DIR, VIDEO_LABEL_FILE, labels_as_dict

movement_and_steadiness_tasks = [
    {
        "folder": "cam_motion-20250227_0324ground_only",
        "name": "is_the_camera_clearly_moving_or_not",
        "pos_question": "Does the camera have noticeable motion beyond minor shake or wobble?",
        "neg_question": "Is the camera free from noticeable motion beyond minor shake or wobble?",
        "pos_prompt": "A video where the camera has noticeable motion beyond minor shake or wobble.",
        "neg_prompt": "A video where the camera is free from noticeable motion beyond minor shake or wobble.",
        "pos": {
            "label": "cam_motion.steadiness_and_movement.clear_moving_camera",
            "type": "pos"
        },
        "neg": {
            "label": "cam_motion.steadiness_and_movement.clear_moving_camera",
            "type": "neg"
        }
    },
    {
        "folder": "cam_motion-20250227_0324ground_only",
        "name": "is_the_fixed_camera_shaking_or_not",
        "pos_question": "Is the camera completely still without any motion or shaking?",
        "neg_question": "Is the camera stationary with minor vibrations or shaking?",
        "pos_prompt":  "A video where the camera remains completely still with no motion or shaking.",
        "neg_prompt": "A video where the camera is mostly stationary but has minor vibrations or shaking.",
        "pos": {
            "label": "cam_motion.steadiness_and_movement.fixed_camera",
            "type": "pos"
        },
        "neg": {
            "label": "cam_motion.steadiness_and_movement.fixed_camera_with_shake",
            "type": "pos"
        }
    },
    {
        "folder": "cam_motion-20250227_0324ground_only",
        "name": "is_the_camera_stable_or_shaky",
        "pos_question": "Is the camera movement exceptionally smooth and highly stable?",
        "neg_question": "Does the camera show noticable vibrations, shaking, or wobbling?",
        "pos_prompt": "A video where the camera movement is exceptionally smooth and highly stable.",
        "neg_prompt":  "A video where the camera shows noticable vibrations, shaking, or wobbling.",
        "pos": {
            "label": "cam_motion.steadiness_and_movement.very_stable_camera",
            "type": "pos"
        },
        "neg": {
            "label": "cam_motion.steadiness_and_movement.very_shaky_camera",
            "type": "pos"
        }
    }
]

scene_dynamics_tasks = [
    {
        "folder": "cam_motion-20250227_0324ground_only",
        "name": "is_scene_static_or_not",
        "pos_question": "Is the scene in the video completely static?",
        "neg_question": "Is the scene in the video dynamic?",
        "pos_prompt": "A video where the scene is completely static.",
        "neg_prompt": "A video where the scene is dynamic and features movement.",
        "pos": {
            "label": "cam_motion.scene_movement.static_scene",
            "type": "pos"
        },
        "neg": {
            "label": "cam_motion.scene_movement.dynamic_scene",
            "type": "pos"
        }
    },
    {
        "folder": "cam_motion-20250227_0324ground_only",
        "name": "has_frame_freeze_or_not",
        "pos_question": "Does the video contain a frame freeze effect at any point?",
        "neg_question": "Is the video free from any frame freeze effect?",
        "pos_prompt": "A video that contains a frame freeze effect at some point.",
        "neg_prompt": "A video that is free from any frame freeze effect.",
        "pos": {
            "label": "cam_motion.has_frame_freezing",
            "type": "pos"
        },
        "neg": {
            "label": "cam_motion.has_frame_freezing",
            "type": "neg"
        }
    }
]

camera_movement_speed_tasks = [
    {
        "folder": "cam_motion-20250227_0324ground_only",
        "name": "is_camera_movement_slow_or_fast",
        "pos_question": "Does the camera have noticeable motion but at a slow motion speed?",
        "neg_question": "Does the camera have noticeable motion but at a fast motion speed?",
        "pos_prompt": "A video where the camera has noticeable motion at a slow speed.",
        "neg_prompt": "A video where the camera has noticeable motion at a fast speed.",
        "pos": {
            "label": "cam_motion.steadiness_and_movement.slow_moving_camera",
            "type": "pos"
        },
        "neg": {
            "label": "cam_motion.steadiness_and_movement.fast_moving_camera",
            "type": "pos"
        }
    },
    {
        "folder": "cam_motion-20250227_0324ground_only",
        "name": "has_motion_blur_or_not",
        "pos_question": "Does the video contain noticeable motion blur?",
        "neg_question": "Is the video free from any noticeable motion blur?",
        "pos_prompt": "The video exhibits a motion blur effect.",
        "neg_prompt": "The video is free from any noticeable motion blur.",
        "pos": {
            "label": "cam_motion.has_motion_blur",
            "type": "pos"
        },
        "neg": {
            "label": "cam_motion.has_motion_blur",
            "type": "neg"
        }
    }
]

translation_direction_tasks = [
    # Translation Direction (3 tasks)
    {
        "folder": "cam_motion-cam_setup-20250227_0507ground_and_setup",
        "name": "has_forward_vs_backward_ground",
        "pos_question": "Is the camera moving forward in the scene?",
        "neg_question": "Is the camera moving backward in the scene?",
        "pos_prompt": "A shot where the camera is moving forward within the scene.",
        "neg_prompt": "A shot where the camera is moving backward within the scene.",
        "pos": {
            "label": "cam_motion.ground_centric_movement.forward.has_forward_wrt_ground",
            "type": "pos"
        },
        "neg": {
            "label": "cam_motion.ground_centric_movement.backward.has_backward_wrt_ground",
            "type": "pos"
        }
    },
    {
        "folder": "cam_motion-cam_setup-20250227_0507ground_and_setup",
        "name": "has_upward_vs_downward_ground",
        "pos_question": "Does the camera move upward relative to the ground?",
        "neg_question": "Does the camera move downward relative to the ground?",
        "pos_prompt": "The camera is moving upward relative to the ground.",
        "neg_prompt": "The camera is moving downward relative to the ground.",
        "pos": {
            "label": "cam_motion.ground_centric_movement.upward.has_upward_wrt_ground",
            "type": "pos"
        },
        "neg": {
            "label": "cam_motion.ground_centric_movement.downward.has_downward_wrt_ground",
            "type": "pos"
        }
    },
    {
        "folder": "cam_motion-20250227_0324ground_only",
        "name": "has_leftward_vs_rightward",
        "pos_question": "Does the camera move leftward in the scene?",
        "neg_question": "Does the camera move rightward in the scene?",
        "pos_prompt": "The camera moves leftward.",
        "neg_prompt": "The camera moves rightward.",
        "pos": {
            "label": "cam_motion.camera_centric_movement.leftward.has_leftward",
            "type": "pos"
        },
        "neg": {
            "label": "cam_motion.camera_centric_movement.rightward.has_rightward",
            "type": "pos"
        }
    },
]

rotation_direction_tasks = [    
    # Rotation Direction (3 tasks)
    {
        "folder": "cam_motion-20250227_0324ground_only",
        "name": "pan_left_vs_pan_right",
        "pos_question": "Does the camera pan to the left?",
        "neg_question": "Does the camera pan to the right?",
        "pos_prompt": "The camera pans to the left.",
        "neg_prompt": "The camera pans to the right.",
        "pos": {
            "label": "cam_motion.camera_centric_movement.pan_left.has_pan_left",
            "type": "pos"
        },
        "neg": {
            "label": "cam_motion.camera_centric_movement.pan_right.has_pan_right",
            "type": "pos"
        }
    },
    {
        "folder": "cam_motion-20250227_0324ground_only",
        "name": "tilt_up_vs_tilt_down",
        "pos_question": "Does the camera tilt upward?",
        "neg_question": "Does the camera tilt downward?",
        "pos_prompt": "The camera tilts upward.",
        "neg_prompt": "The camera tilts downward.",
        "pos": {
            "label": "cam_motion.camera_centric_movement.tilt_up.has_tilt_up",
            "type": "pos"
        },
        "neg": {
            "label": "cam_motion.camera_centric_movement.tilt_down.has_tilt_down",
            "type": "pos"
        }
    },
    {
        "folder": "cam_motion-20250227_0324ground_only",
        "name": "roll_clockwise_vs_roll_counterclockwise",
        "pos_question": "Does the camera roll clockwise?",
        "neg_question": "Does the camera roll counterclockwise?",
        "pos_prompt": "The camera rolls clockwise.",
        "neg_prompt": "The camera rolls counterclockwise.",
        "pos": {
            "label": "cam_motion.camera_centric_movement.roll_clockwise.has_roll_clockwise",
            "type": "pos"
        },
        "neg": {
            "label": "cam_motion.camera_centric_movement.roll_counterclockwise.has_roll_counterclockwise",
            "type": "pos"
        }
    },
    
]

object_centric_direction_tasks = [
    # Object-Centric Direction (4 tasks)
    {
        "folder": "cam_motion-20250227_0324ground_only",
        "name": "side_tracking_leftward_vs_rightward",
        "pos_question": "Is it a side-tracking shot where the camera moves left to follow the subject?",
        "neg_question": "Is it a side-tracking shot where the camera moves right to follow the subject?",
        "pos_prompt": "A side-tracking shot where the camera moves left to follow the subject.",
        "neg_prompt": "A side-tracking shot where the camera moves right to follow the subject.",
        "pos": {
            "label": "cam_motion.object_centric_movement.side_tracking_shot_leftward",
            "type": "pos"
        },
        "neg": {
            "label": "cam_motion.object_centric_movement.side_tracking_shot_rightward",
            "type": "pos"
        }
    },
    {
        "folder": "cam_motion-20250227_0324ground_only",
        "name": "lead_tracking_vs_tail_tracking",
        "pos_question": "Is it a tracking shot with the camera moving ahead of the subject?",
        "neg_question": "Is it a tracking shot with the camera following behind the subject?",
        "pos_prompt": "A tracking shot where the camera moves ahead of the subject.",
        "neg_prompt": "A tracking shot where the camera follows behind the subject.",
        "pos": {
            "label": "cam_motion.object_centric_movement.lead_tracking_shot",
            "type": "pos"
        },
        "neg": {
            "label": "cam_motion.object_centric_movement.tail_tracking_shot",
            "type": "pos"
        }
    },
    {
        "folder": "cam_motion-20250227_0324ground_only",
        "name": "arc_counterclockwise_vs_arc_clockwise",
        "pos_question": "Does the camera move in a counterclockwise arc?",
        "neg_question": "Does the camera move in a clockwise arc?",
        "pos_prompt": "The camera arcs counterclockwise.",
        "neg_prompt": "The camera arcs clockwise.",
        "pos": {
            "label": "cam_motion.arc_crane_movement.arc_counterclockwise.has_arc_counterclockwise",
            "type": "pos"
        },
        "neg": {
            "label": "cam_motion.arc_crane_movement.arc_clockwise.has_arc_clockwise",
            "type": "pos"
        }
    },
    {
        "folder": "cam_motion-20250227_0324ground_only",
        "name": "crane_up_vs_crane_down",
        "pos_question": "Is the camera craning upward in an arc?",
        "neg_question": "Does the camera move downward in a crane shot?",
        "pos_prompt": "The camera cranes upward in an arc.",
        "neg_prompt": "The camera cranes downward in an arc.",
        "pos": {
            "label": "cam_motion.arc_crane_movement.crane_up.has_crane_up",
            "type": "pos"
        },
        "neg": {
            "label": "cam_motion.arc_crane_movement.crane_down.has_crane_down",
            "type": "pos"
        }
    },
]

intrinsic_direction_tasks = [
    # Intrinsic Direction (2 tasks)
    {
        "folder": "cam_motion-20250227_0324ground_only",
        "name": "dolly_zoom_in_vs_dolly_zoom_out",
        "pos_question": "Does the shot feature a dolly zoom effect with the camera moving backward and zooming in?",
        "neg_question": "Does the shot feature a dolly zoom effect with the camera moving forward and zooming out?",
        "pos_prompt": "The camera performs a dolly zoom effect with backward movement and zoom-in.",
        "neg_prompt": "The camera performs a dolly zoom effect with forward movement and zoom-out.",
        "pos": {
            "label": "cam_motion.dolly_zoom_movement.has_dolly_out_zoom_in",
            "type": "pos"
        },
        "neg": {
            "label": "cam_motion.dolly_zoom_movement.has_dolly_in_zoom_out",
            "type": "pos"
        }
    },
    {
        "folder": "cam_motion-20250227_0324ground_only",
        "name": "zoom_in_vs_zoom_out",
        "pos_question": "Does the camera zoom in?",
        "neg_question": "Does the camera zoom out?",
        "pos_prompt": "The camera zooms in.",
        "neg_prompt": "The camera zooms out.",
        "pos": {
            "label": "cam_motion.camera_centric_movement.zoom_in.has_zoom_in",
            "type": "pos"
        },
        "neg": {
            "label": "cam_motion.camera_centric_movement.zoom_out.has_zoom_out",
            "type": "pos"
        }
    }
]

instrinsic_vs_extrinsic = [
    # Intrinsic vs. Extrinsic (4 tasks)
    {
        "folder": "cam_motion-20250227_0326ground_and_camera",
        "name": "has_zoom_in_not_move_vs_has_move_not_zoom_in",
        "pos_question": "Does the camera zoom in without physically moving forward?",
        "neg_question": "Does the camera physically move forward without zooming in?",
        "pos_prompt": "A video where the camera zooms in without physically moving forward.",
        "neg_prompt": "A video where the camera physically moves forward without zooming in.",
        "pos": [
            {
                "label": "cam_motion.camera_centric_movement.zoom_in.has_zoom_in",
                "type": "pos"
            },
            {
                "label": "cam_motion.camera_centric_movement.forward.has_forward_wrt_camera",
                "type": "neg"
            }
        ],
        "neg": [
            {
                "label": "cam_motion.camera_centric_movement.zoom_in.has_zoom_in",
                "type": "neg"
            },
            {
                "label": "cam_motion.camera_centric_movement.forward.has_forward_wrt_camera",
                "type": "pos"
            }
        ]
    },
    {
        "folder": "cam_motion-20250227_0326ground_and_camera",
        "name": "has_zoom_out_not_move_vs_has_move_not_zoom_out",
        "pos_question": "Does the camera zoom out without physically moving backward?",
        "neg_question": "Does the camera physically move backward without zooming out?",
        "pos_prompt": "A video where the camera zooms out without physically moving backward.",
        "neg_prompt": "A video where the camera physically moves backward without zooming out.",
        "pos": [
            {
                "label": "cam_motion.camera_centric_movement.zoom_out.has_zoom_out",
                "type": "pos"
            },
            {
                "label": "cam_motion.camera_centric_movement.backward.has_backward_wrt_camera",
                "type": "neg"
            }
        ],
        "neg": [
            {
                "label": "cam_motion.camera_centric_movement.zoom_out.has_zoom_out",
                "type": "neg"
            },
            {
                "label": "cam_motion.camera_centric_movement.backward.has_backward_wrt_camera",
                "type": "pos"
            }
        ]
    },
    {
        "folder": "cam_motion-20250227_0324ground_only",
        "name": "only_zoom_in_vs_only_forward",
        "pos_question": "Does the camera only zoom in without any other camera movement?",
        "neg_question": "Does the camera only move forward without any other camera movement?",
        "pos_prompt": "A video where the camera only zooms in with no other movement.",
        "neg_prompt": "A video where the camera only moves forward with no other movement.",
        "pos": {
            "label": "cam_motion.camera_centric_movement.zoom_in.only_zoom_in",
            "type": "pos"
        },
        "neg": {
            "label": "cam_motion.camera_centric_movement.forward.only_forward_wrt_camera",
            "type": "pos"
        }
    },
    {
        "folder": "cam_motion-20250227_0324ground_only",
        "name": "only_zoom_out_vs_only_backward",
        "pos_question": "Does the camera only zoom out without any other camera movement?",
        "neg_question": "Does the camera only move backward without any other camera movement?",
        "pos_prompt": "A video where the camera only zooms out with no other movement.",
        "neg_prompt": "A video where the camera only moves backward with no other movement.",
        "pos": {
            "label": "cam_motion.camera_centric_movement.zoom_out.only_zoom_out",
            "type": "pos"
        },
        "neg": {
            "label": "cam_motion.camera_centric_movement.backward.only_backward_wrt_camera",
            "type": "pos"
        }
    },
]

rotation_vs_translation = [
    # Rotation vs. Translation (8 tasks)
    {
        "folder": "cam_motion-20250227_0324ground_only",
        "name": "has_pan_right_not_truck_vs_has_truck_not_pan_right",
        "pos_question": "Does the camera pan right without moving laterally to the right?",
        "neg_question": "Does the camera move laterally to the right without panning right?",
        "pos_prompt": "The camera pans right without moving laterally to the right.",
        "neg_prompt": "The camera moves laterally to the right without panning right.",
        "pos": [
            {
                "label": "cam_motion.camera_centric_movement.pan_right.has_pan_right",
                "type": "pos"
            },
            {
                "label": "cam_motion.camera_centric_movement.rightward.has_rightward",
                "type": "neg"
            }
        ],
        "neg": [
            {
                "label": "cam_motion.camera_centric_movement.pan_right.has_pan_right",
                "type": "neg"
            },
            {
                "label": "cam_motion.camera_centric_movement.rightward.has_rightward",
                "type": "pos"
            }
        ]
    },
    {
        "folder": "cam_motion-20250227_0324ground_only",
        "name": "has_pan_left_not_truck_vs_has_truck_not_pan_left",
        "pos_question": "Does the camera pan left without moving laterally to the left?",
        "neg_question": "Does the camera move laterally to the left without panning left?",
        "pos_prompt": "The camera pans left without moving laterally to the left.",
        "neg_prompt": "The camera moves laterally to the left without panning left.",
        "pos": [
            {
                "label": "cam_motion.camera_centric_movement.pan_left.has_pan_left",
                "type": "pos"
            },
            {
                "label": "cam_motion.camera_centric_movement.leftward.has_leftward",
                "type": "neg"
            }
        ],
        "neg": [
            {
                "label": "cam_motion.camera_centric_movement.pan_left.has_pan_left",
                "type": "neg"
            },
            {
                "label": "cam_motion.camera_centric_movement.leftward.has_leftward",
                "type": "pos"
            }
        ]
    },
    {
        "folder": "cam_motion-20250227_0324ground_only",
        "name": "only_pan_right_vs_only_truck_right",
        "pos_question": "Does the camera only pan right with no other movement?",
        "neg_question": "Does the camera only move laterally to the right with no other movement?",
        "pos_prompt": "A video where the camera only pans right with no other movement.",
        "neg_prompt": "A video where the camera only moves laterally to the right with no other movement.",
        "pos": {
            "label": "cam_motion.camera_centric_movement.pan_right.only_pan_right",
            "type": "pos"
        },
        "neg": {
            "label": "cam_motion.camera_centric_movement.rightward.only_rightward",
            "type": "pos"
        }
    },
    {
        "folder": "cam_motion-20250227_0324ground_only",
        "name": "only_pan_left_vs_only_truck_left",
        "pos_question": "Does the camera only pan left with no other movement?",
        "neg_question": "Does the camera only move laterally to the left with no other movement?",
        "pos_prompt": "A video where the camera only pans left with no other movement.",
        "neg_prompt": "A video where the camera only moves laterally to the left with no other movement.",
        "pos": {
            "label": "cam_motion.camera_centric_movement.pan_left.only_pan_left",
            "type": "pos"
        },
        "neg": {
            "label": "cam_motion.camera_centric_movement.leftward.only_leftward",
            "type": "pos"
        }
    },
    {
        "folder": "cam_motion-20250227_0326ground_and_camera",
        "name": "has_tilt_up_not_pedestal_vs_has_pedestal_not_tilt_up",
        "pos_question": "Does the camera tilt up without moving physically upward?",
        "neg_question": "Does the camera move physically upward without tilting up?",
        "pos_prompt": "A video where the camera tilts up without physically moving upward.",
        "neg_prompt": "A video where the camera physically moves upward without tilting up.",
        "pos": [
            {
                "label": "cam_motion.camera_centric_movement.tilt_up.has_tilt_up",
                "type": "pos"
            },
            {
                "label": "cam_motion.camera_centric_movement.upward.has_upward_wrt_camera",
                "type": "neg"
            }
        ],
        "neg": [
            {
                "label": "cam_motion.camera_centric_movement.tilt_up.has_tilt_up",
                "type": "neg"
            },
            {
                "label": "cam_motion.camera_centric_movement.upward.has_upward_wrt_camera",
                "type": "pos"
            }
        ]
    },
    {
        "folder": "cam_motion-20250227_0326ground_and_camera",
        "name": "has_tilt_down_not_pedestal_vs_has_pedestal_not_tilt_down",
        "pos_question": "Does the camera tilt down without moving physically downward?",
        "neg_question": "Does the camera move physically downward without tilting down?",
        "pos_prompt": "A video where the camera tilts down without physically moving downward.",
        "neg_prompt": "A video where the camera physically moves downward without tilting down.",
        "pos": [
            {
                "label": "cam_motion.camera_centric_movement.tilt_down.has_tilt_down",
                "type": "pos"
            },
            {
                "label": "cam_motion.camera_centric_movement.downward.has_downward_wrt_camera",
                "type": "neg"
            }
        ],
        "neg": [
            {
                "label": "cam_motion.camera_centric_movement.tilt_down.has_tilt_down",
                "type": "neg"
            },
            {
                "label": "cam_motion.camera_centric_movement.downward.has_downward_wrt_camera",
                "type": "pos"
            }
        ]
    },
    {
        "folder": "cam_motion-20250227_0326ground_and_camera",
        "name": "only_tilt_up_vs_only_pedestal_up",
        "pos_question": "Does the camera only tilt up with no other movement?",
        "neg_question": "Does the camera only move physically upward (pedestal up) with no other movement?",
        "pos_prompt": "A video where the camera only tilts up with no other movement.",
        "neg_prompt": "A video where the camera only moves physically upward with no other movement.",
        "pos": {
            "label": "cam_motion.camera_centric_movement.tilt_up.only_tilt_up",
            "type": "pos"
        },
        "neg": {
            "label": "cam_motion.camera_centric_movement.upward.only_upward_wrt_camera",
            "type": "pos"
        }
    },
    {
        "folder": "cam_motion-20250227_0326ground_and_camera",
        "name": "only_tilt_down_vs_only_pedestal_down",
        "pos_question": "Does the camera only tilt down with no other movement?",
        "neg_question": "Does the camera only move physically downward (pedestal down) with no other movement?",
        "pos_prompt": "A video where the camera only tilts down with no other movement.",
        "neg_prompt": "A video where the camera only moves physically downward with no other movement.",
        "pos": {
            "label": "cam_motion.camera_centric_movement.tilt_down.only_tilt_down",
            "type": "pos"
        },
        "neg": {
            "label": "cam_motion.camera_centric_movement.downward.only_downward_wrt_camera",
            "type": "pos"
        }
    }
]


has_intrinsic_change_tasks = [
    {
        "folder": "cam_motion-20250227_0324ground_only",
        "name": "has_zoom_in",
        "pos_question": "Does the camera zoom in?",
        "neg_question": "Is the camera free from any zoom in effects?",
        "pos_prompt": "The camera zooms in.",
        "neg_prompt": "The camera is free from any zoom in effects.",
        "pos": {
            "label": "cam_motion.camera_centric_movement.zoom_in.has_zoom_in",
            "type": "pos"
        },
        "neg": {
            "label": "cam_motion.camera_centric_movement.zoom_in.has_zoom_in",
            "type": "neg"
        }
    },
    {
        "folder": "cam_motion-20250227_0324ground_only",
        "name": "has_zoom_out",
        "pos_question": "Does the camera zoom out?",
        "neg_question": "Is the camera free from any zoom out effects?",
        "pos_prompt": "The camera zooms out.",
        "neg_prompt": "The camera is free from any zoom out effects.",
        "pos": {
            "label": "cam_motion.camera_centric_movement.zoom_out.has_zoom_out",
            "type": "pos"
        },
        "neg": {
            "label": "cam_motion.camera_centric_movement.zoom_out.has_zoom_out",
            "type": "neg"
        }
    }
]

has_translation_tasks = [
    {
        "folder": "cam_motion-cam_setup-20250227_0507ground_and_setup",
        "name": "has_forward_motion",
        "pos_question": "Is the camera moving forward in the scene?",
        "neg_question": "Is the camera free from any forward motion?",
        "pos_prompt": "The camera is moving forward within the scene.",
        "neg_prompt": "The camera is free from any forward motion.",
        "pos": {
            "label": "cam_motion.ground_centric_movement.forward.has_forward_wrt_ground",
            "type": "pos"
        },
        "neg": {
            "label": "cam_motion.ground_centric_movement.forward.has_forward_wrt_ground",
            "type": "neg"
        }
    },
    {
        "folder": "cam_motion-cam_setup-20250227_0507ground_and_setup",
        "name": "has_backward_motion",
        "pos_question": "Is the camera moving backward in the scene?",
        "neg_question": "Is the camera free from any backward motion?",
        "pos_prompt": "The camera is moving backward within the scene.",
        "neg_prompt": "The camera is free from any backward motion.",
        "pos": {
            "label": "cam_motion.ground_centric_movement.backward.has_backward_wrt_ground",
            "type": "pos"
        },
        "neg": {
            "label": "cam_motion.ground_centric_movement.backward.has_backward_wrt_ground",
            "type": "neg"
        }
    },
    {
        "folder": "cam_motion-20250227_0324ground_only",
        "name": "has_truck_left",
        "pos_question": "Does the camera move laterally to the left?",
        "neg_question": "Is the camera free from any leftward lateral movement?",
        "pos_prompt": "The camera moves laterally to the left.",
        "neg_prompt": "The camera is free from any leftward lateral movement.",
        "pos": {
            "label": "cam_motion.camera_centric_movement.leftward.has_leftward",
            "type": "pos"
        },
        "neg": {
            "label": "cam_motion.camera_centric_movement.leftward.has_leftward",
            "type": "neg"
        }
    },
    {
        "folder": "cam_motion-20250227_0324ground_only",
        "name": "has_truck_right",
        "pos_question": "Does the camera move laterally to the right?",
        "neg_question": "Is the camera free from any rightward lateral movement?",
        "pos_prompt": "The camera moves laterally to the right.",
        "neg_prompt": "The camera is free from any rightward lateral movement.",
        "pos": {
            "label": "cam_motion.camera_centric_movement.rightward.has_rightward",
            "type": "pos"
        },
        "neg": {
            "label": "cam_motion.camera_centric_movement.rightward.has_rightward",
            "type": "neg"
        }
    },
    {
        "folder": "cam_motion-cam_setup-20250227_0507ground_and_setup",
        "name": "has_pedestal_up",
        "pos_question": "Does the camera move upward relative to the ground?",
        "neg_question": "Is the camera free from any upward pedestal motion?",
        "pos_prompt": "The camera moves upward relative to the ground.",
        "neg_prompt": "The camera is free from any upward pedestal motion.",
        "pos": {
            "label": "cam_motion.ground_centric_movement.upward.has_upward_wrt_ground",
            "type": "pos"
        },
        "neg": {
            "label": "cam_motion.ground_centric_movement.upward.has_upward_wrt_ground",
            "type": "neg"
        }
    },
    {
        "folder": "cam_motion-cam_setup-20250227_0507ground_and_setup",
        "name": "has_pedestal_down",
        "pos_question": "Does the camera move downward relative to the ground?",
        "neg_question": "Is the camera free from any downward pedestal motion?",
        "pos_prompt": "The camera moves downward relative to the ground.",
        "neg_prompt": "The camera is free from any downward pedestal motion.",
        "pos": {
            "label": "cam_motion.ground_centric_movement.downward.has_downward_wrt_ground",
            "type": "pos"
        },
        "neg": {
            "label": "cam_motion.ground_centric_movement.downward.has_downward_wrt_ground",
            "type": "neg"
        }
    }
]

has_rotation_tasks = [
    {
        "folder": "cam_motion-20250227_0324ground_only",
        "name": "has_pan_left",
        "pos_question": "Does the camera pan to the left?",
        "neg_question": "Is the camera free from any leftward panning motion?",
        "pos_prompt": "The camera pans to the left.",
        "neg_prompt": "The camera is free from any leftward panning motion.",
        "pos": {
            "label": "cam_motion.camera_centric_movement.pan_left.has_pan_left",
            "type": "pos"
        },
        "neg": {
            "label": "cam_motion.camera_centric_movement.pan_left.has_pan_left",
            "type": "neg"
        }
    },
    {
        "folder": "cam_motion-20250227_0324ground_only",
        "name": "has_pan_right",
        "pos_question": "Does the camera pan to the right?",
        "neg_question": "Is the camera free from any rightward panning motion?",
        "pos_prompt": "The camera pans to the right.",
        "neg_prompt": "The camera is free from any rightward panning motion.",
        "pos": {
            "label": "cam_motion.camera_centric_movement.pan_right.has_pan_right",
            "type": "pos"
        },
        "neg": {
            "label": "cam_motion.camera_centric_movement.pan_right.has_pan_right",
            "type": "neg"
        }
    },
    {
        "folder": "cam_motion-20250227_0324ground_only",
        "name": "has_tilt_up",
        "pos_question": "Does the camera tilt upward?",
        "neg_question": "Is the camera free from any upward tilting motion?",
        "pos_prompt": "The camera tilts upward.",
        "neg_prompt": "The camera is free from any upward tilting motion.",
        "pos": {
            "label": "cam_motion.camera_centric_movement.tilt_up.has_tilt_up",
            "type": "pos"
        },
        "neg": {
            "label": "cam_motion.camera_centric_movement.tilt_up.has_tilt_up",
            "type": "neg"
        }
    },
    {
        "folder": "cam_motion-20250227_0324ground_only",
        "name": "has_tilt_down",
        "pos_question": "Does the camera tilt downward?",
        "neg_question": "Is the camera free from any downward tilting motion?",
        "pos_prompt": "The camera tilts downward.",
        "neg_prompt": "The camera is free from any downward tilting motion.",
        "pos": {
            "label": "cam_motion.camera_centric_movement.tilt_down.has_tilt_down",
            "type": "pos"
        },
        "neg": {
            "label": "cam_motion.camera_centric_movement.tilt_down.has_tilt_down",
            "type": "neg"
        }
    },
    {
        "folder": "cam_motion-20250227_0324ground_only",
        "name": "has_roll_clockwise",
        "pos_question": "Does the camera roll clockwise?",
        "neg_question": "Is the camera free from any clockwise rolling motion?",
        "pos_prompt": "The camera rolls clockwise.",
        "neg_prompt": "The camera is free from any clockwise rolling motion.",
        "pos": {
            "label": "cam_motion.camera_centric_movement.roll_clockwise.has_roll_clockwise",
            "type": "pos"
        },
        "neg": {
            "label": "cam_motion.camera_centric_movement.roll_clockwise.has_roll_clockwise",
            "type": "neg"
        }
    },
    {
        "folder": "cam_motion-20250227_0324ground_only",
        "name": "has_roll_counterclockwise",
        "pos_question": "Does the camera roll counterclockwise?",
        "neg_question": "Is the camera free from any counterclockwise rolling motion?",
        "pos_prompt": "The camera rolls counterclockwise.",
        "neg_prompt": "The camera is free from any counterclockwise rolling motion.",
        "pos": {
            "label": "cam_motion.camera_centric_movement.roll_counterclockwise.has_roll_counterclockwise",
            "type": "pos"
        },
        "neg": {
            "label": "cam_motion.camera_centric_movement.roll_counterclockwise.has_roll_counterclockwise",
            "type": "neg"
        }
    }
]

has_arc_crane_tasks = [
    {
        "folder": "cam_motion-20250227_0324ground_only",
        "name": "has_arc_clockwise",
        "pos_question": "Does the camera move in a clockwise arc?",
        "neg_question": "Is the camera free from any clockwise arc movement?",
        "pos_prompt": "The camera moves in a clockwise arc.",
        "neg_prompt": "The camera is free from any clockwise arc movement.",
        "pos": {
            "label": "cam_motion.arc_crane_movement.arc_clockwise.has_arc_clockwise",
            "type": "pos"
        },
        "neg": {
            "label": "cam_motion.arc_crane_movement.arc_clockwise.has_arc_clockwise",
            "type": "neg"
        }
    },
    {
        "folder": "cam_motion-20250227_0324ground_only",
        "name": "has_arc_counterclockwise",
        "pos_question": "Does the camera move in a counterclockwise arc around a subject?",
        "neg_question": "Is the camera free from any counterclockwise arc movement around a subject?",
        "pos_prompt": "A video where the camera moves in a counterclockwise arc around a subject.",
        "neg_prompt": "A video where the camera does not move in a counterclockwise arc around a subject.",
        "pos": {
            "label": "cam_motion.arc_crane_movement.arc_counterclockwise.has_arc_counterclockwise",
            "type": "pos"
        },
        "neg": {
            "label": "cam_motion.arc_crane_movement.arc_counterclockwise.has_arc_counterclockwise",
            "type": "neg"
        }
    },
    {
        "folder": "cam_motion-20250227_0324ground_only",
        "name": "has_crane_up",
        "pos_question": "Does the camera move upward in a crane shot?",
        "neg_question": "Is the camera free from any upward crane movement?",
        "pos_prompt": "A video where the camera moves upward in a crane shot.",
        "neg_prompt": "A video where the camera does not move upward in a crane shot.",
        "pos": {
            "label": "cam_motion.arc_crane_movement.crane_up.has_crane_up",
            "type": "pos"
        },
        "neg": {
            "label": "cam_motion.arc_crane_movement.crane_up.has_crane_up",
            "type": "neg"
        }
    },
    {
        "folder": "cam_motion-20250227_0324ground_only",
        "name": "has_crane_down",
        "pos_question": "Does the camera move downward in a crane shot?",
        "neg_question": "Is the camera free from any downward crane movement?",
        "pos_prompt": "A video where the camera moves downward in a crane shot.",
        "neg_prompt": "A video where the camera does not move downward in a crane shot.",
        "pos": {
            "label": "cam_motion.arc_crane_movement.crane_down.has_crane_down",
            "type": "pos"
        },
        "neg": {
            "label": "cam_motion.arc_crane_movement.crane_down.has_crane_down",
            "type": "neg"
        }
    }
]

# 2. Tracking Perspective Tasks (8 tasks)
tracking_perspective_tasks = [
    {
        "folder": "cam_motion-20250227_0324ground_only",
        "name": "has_aerial_tracking",
        "pos_question": "Does the camera track a subject from an aerial perspective?",
        "neg_question": "Is the camera free from any aerial tracking movement?",
        "pos_prompt": "A video where the camera tracks a subject from an aerial perspective.",
        "neg_prompt": "A video where the camera does not track a subject from an aerial perspective.",
        "pos": {
            "label": "cam_motion.object_centric_movement.aerial_tracking_shot",
            "type": "pos"
        },
        "neg": {
            "label": "cam_motion.object_centric_movement.aerial_tracking_shot",
            "type": "neg"
        }
    },
    {
        "folder": "cam_motion-20250227_0324ground_only",
        "name": "has_arc_tracking",
        "pos_question": "Does the camera track a subject while moving in an arc around them?",
        "neg_question": "Is the camera free from any arc tracking movement?",
        "pos_prompt": "A video where the camera tracks a subject while moving in an arc around them.",
        "neg_prompt": "A video where the camera does not track a subject in an arc.",
        "pos": {
            "label": "cam_motion.object_centric_movement.arc_tracking_shot",
            "type": "pos"
        },
        "neg": {
            "label": "cam_motion.object_centric_movement.arc_tracking_shot",
            "type": "neg"
        }
    },
    {
        "folder": "cam_motion-20250227_0324ground_only",
        "name": "has_front_side_tracking",
        "pos_question": "Does the camera track a subject from their front-side angle?",
        "neg_question": "Is the camera free from any front-side tracking movement?",
        "pos_prompt": "A video where the camera tracks a subject from their front-side angle.",
        "neg_prompt": "A video where the camera does not track a subject from their front-side angle.",
        "pos": {
            "label": "cam_motion.object_centric_movement.front_side_tracking_shot",
            "type": "pos"
        },
        "neg": {
            "label": "cam_motion.object_centric_movement.front_side_tracking_shot",
            "type": "neg"
        }
    },
    {
        "folder": "cam_motion-20250227_0324ground_only",
        "name": "has_rear_side_tracking",
        "pos_question": "Does the camera track a subject from their rear-side angle?",
        "neg_question": "Is the camera free from any rear-side tracking movement?",
        "pos_prompt": "A video where the camera tracks a subject from their rear-side angle.",
        "neg_prompt": "A video where the camera does not track a subject from their rear-side angle.",
        "pos": {
            "label": "cam_motion.object_centric_movement.rear_side_tracking_shot",
            "type": "pos"
        },
        "neg": {
            "label": "cam_motion.object_centric_movement.rear_side_tracking_shot",
            "type": "neg"
        }
    },
    {
        "folder": "cam_motion-20250227_0324ground_only",
        "name": "has_lead_tracking",
        "pos_question": "Does the camera track a subject from in front of them?",
        "neg_question": "Is the camera free from any lead tracking movement?",
        "pos_prompt": "A video where the camera tracks a subject from in front of them.",
        "neg_prompt": "A video where the camera does not track a subject from in front of them.",
        "pos": {
            "label": "cam_motion.object_centric_movement.lead_tracking_shot",
            "type": "pos"
        },
        "neg": {
            "label": "cam_motion.object_centric_movement.lead_tracking_shot",
            "type": "neg"
        }
    },
    {
        "folder": "cam_motion-20250227_0324ground_only",
        "name": "has_tilt_tracking",
        "pos_question": "Does the camera track a subject while tilting up or down?",
        "neg_question": "Is the camera free from any tilt tracking movement?",
        "pos_prompt": "A video where the camera tracks a subject while tilting up or down.",
        "neg_prompt": "A video where the camera does not track a subject while tilting.",
        "pos": {
            "label": "cam_motion.object_centric_movement.tilt_tracking_shot",
            "type": "pos"
        },
        "neg": {
            "label": "cam_motion.object_centric_movement.tilt_tracking_shot",
            "type": "neg"
        }
    },
    {
        "folder": "cam_motion-20250227_0324ground_only",
        "name": "has_pan_tracking",
        "pos_question": "Does the camera track a subject while panning?",
        "neg_question": "Is the camera free from any pan tracking movement?",
        "pos_prompt": "A video where the camera tracks a subject while panning.",
        "neg_prompt": "A video where the camera does not track a subject while panning.",
        "pos": {
            "label": "cam_motion.object_centric_movement.pan_tracking_shot",
            "type": "pos"
        },
        "neg": {
            "label": "cam_motion.object_centric_movement.pan_tracking_shot",
            "type": "neg"
        }
    },
    {
        "folder": "cam_motion-20250227_0324ground_only",
        "name": "has_side_tracking",
        "pos_question": "Does the camera track a subject from the side?",
        "neg_question": "Is the camera free from any side tracking movement?",
        "pos_prompt": "A video where the camera tracks a subject from the side.",
        "neg_prompt": "A video where the camera does not track a subject from the side.",
        "pos": {
            "label": "cam_motion.object_centric_movement.side_tracking_shot",
            "type": "pos"
        },
        "neg": {
            "label": "cam_motion.object_centric_movement.side_tracking_shot",
            "type": "neg"
        }
    }
]

# 3. General Tracking Tasks (3 tasks)
general_tracking_tasks = [
    {
        "folder": "cam_motion-20250227_0324ground_only",
        "name": "is_tracking",
        "pos_question": "Does the camera track a subject in any way?",
        "neg_question": "Is the camera free from any tracking movement?",
        "pos_prompt": "A video where the camera tracks a subject in some way.",
        "neg_prompt": "A video where the camera does not track any subject.",
        "pos": {
            "label": "cam_motion.object_centric_movement.track_shot",
            "type": "pos"
        },
        "neg": {
            "label": "cam_motion.object_centric_movement.track_shot",
            "type": "neg"
        }
    },
    {
        "folder": "cam_motion-20250227_0324ground_only",
        "name": "tracking_subject_larger",
        "pos_question": "Does the tracking shot make the subject appear larger over time?",
        "neg_question": "Does the tracking shot maintain the subject's apparent size?",
        "pos_prompt": "A video where the tracking shot makes the subject appear larger over time.",
        "neg_prompt": "A video where the tracking shot maintains the subject's apparent size.",
        "pos": {
            "label": "cam_motion.object_centric_movement.tracking_subject_larger_size",
            "type": "pos"
        },
        "neg": {
            "label": "cam_motion.object_centric_movement.tracking_subject_larger_size",
            "type": "neg"
        }
    },
    {
        "folder": "cam_motion-20250227_0324ground_only",
        "name": "tracking_subject_smaller",
        "pos_question": "Does the tracking shot make the subject appear smaller over time?",
        "neg_question": "Does the tracking shot maintain the subject's apparent size?",
        "pos_prompt": "A video where the tracking shot makes the subject appear smaller over time.",
        "neg_prompt": "A video where the tracking shot maintains the subject's apparent size.",
        "pos": {
            "label": "cam_motion.object_centric_movement.tracking_subject_smaller_size",
            "type": "pos"
        },
        "neg": {
            "label": "cam_motion.object_centric_movement.tracking_subject_smaller_size",
            "type": "neg"
        }
    }
]

pairwise_labels = {
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
    "has_rotation": has_rotation_tasks
}


def get_videos(label_dicts, task_dict_instance):
    if isinstance(task_dict_instance, list):
        video_sets = []
        for task_dict in task_dict_instance:
            assert "label" in task_dict and "type" in task_dict, "task_dict must have 'label' and 'type' keys"
            videos = label_dicts[task_dict["label"]][task_dict["type"]]
            video_sets.append(set(videos))
        # Return the intersection of all video sets
        return list(set.intersection(*video_sets))
    else:
        assert isinstance(task_dict_instance, dict), "task_dict_instance must be a list or dict"
        assert "label" in task_dict_instance and "type" in task_dict_instance, "task_dict_instance must have 'label' and 'type' keys"
        return label_dicts[task_dict_instance["label"]][task_dict_instance["type"]]
            
def generate_pairwise_labels(pairwise_labels, root=ROOT, video_root=VIDEO_ROOT, video_labels_dir=VIDEO_LABELS_DIR, labels_filename="label_names.json"):
    pairwise_tasks = {}

    for skill_name in pairwise_labels:
        pairwise_tasks[skill_name] = {}
        
        for task_dict in pairwise_labels[skill_name]:
            video_label_file = VIDEO_LABELS_DIR / task_dict["folder"] / labels_filename
            label_dicts = labels_as_dict(root=root, video_root=video_root, video_label_file=video_label_file)
            # pos_videos = label_dicts[task_dict["pos"]["label"]][task_dict["pos"]["type"]]
            # neg_videos = label_dicts[task_dict["neg"]["label"]][task_dict["neg"]["type"]]
            pos_videos = get_videos(label_dicts, task_dict["pos"])
            neg_videos = get_videos(label_dicts, task_dict["neg"])
            assert set(pos_videos).isdisjoint(neg_videos), f"Positive and negative videos are not disjoint for task {task_dict['name']}"
            pairwise_tasks[skill_name][task_dict["name"]] = {
                "task_dict": task_dict,
                "pos": pos_videos,
                "neg": neg_videos
            }
    return pairwise_tasks

if __name__ == "__main__":
    pairwise_tasks = generate_pairwise_labels(pairwise_labels)
    # Print the number of positive and negative videos for each task
    for skill_name in pairwise_tasks:
        print(f"Skill: {skill_name}")
        for task_name in pairwise_tasks[skill_name]:
            task_dict = pairwise_tasks[skill_name][task_name]["task_dict"]
            pos_len = len(pairwise_tasks[skill_name][task_name]["pos"])
            neg_len = len(pairwise_tasks[skill_name][task_name]["neg"])
            print(f"Task: {task_name:100} Pos: {pos_len:5} Neg: {neg_len:5}")
        print()
            