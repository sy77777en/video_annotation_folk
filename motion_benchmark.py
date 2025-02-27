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
        

pairwise_labels = {
    "movement_and_steadiness": movement_and_steadiness_tasks,
    "scene_dynamics": scene_dynamics_tasks,
    "camera_movement_speed": camera_movement_speed_tasks,
}

def generate_pairwise_labels(pairwise_labels, root=ROOT, video_root=VIDEO_ROOT, video_labels_dir=VIDEO_LABELS_DIR, labels_filename="label_names.json"):
    pairwise_tasks = {}

    for skill_name in pairwise_labels:
        pairwise_tasks[skill_name] = {}
        
        for task_dict in pairwise_labels[skill_name]:
            video_label_file = VIDEO_LABELS_DIR / task_dict["folder"] / labels_filename
            label_dicts = labels_as_dict(root=root, video_root=video_root, video_label_file=video_label_file)
            pos_videos = label_dicts[task_dict["pos"]["label"]][task_dict["pos"]["type"]]
            neg_videos = label_dicts[task_dict["neg"]["label"]][task_dict["neg"]["type"]]
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
            