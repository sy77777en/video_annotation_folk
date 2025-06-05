import json
import os
from process_json import json_to_video_data
from camera_motion_data import CameraMotionData


def trans_motion_json_to_labelpizza(motion_json_path, labelpizza_json_path):
    res = []
    # Using this dict to record the default value of motion
    attributes = {
        "camera_forward_backward": "no",
        "camera_zoom": "no",
        "camera_left_right": "no",
        "camera_up_down": "no",
        "camera_tilt": "no",
        "camera_pan": "no",
        # "camera_arc": "no",
        # "camera_crane": "no",
        "camera_roll": "no",
    }
    # Tacking types dict
    tracking_types = [
        "side", "tail", "pan", "lead", "tilt", "arc", "aerial"
    ]
    # motion effects
    motion_effects = [
        'frame_freezing', 'dolly_zoom', 'motion_blur', 'cinemagraph'
    ]
    with open(motion_json_path, 'r') as f:
        motion_data = json.load(f)
    for item in motion_data:
        cam_motion_data = item['cam_motion']
        res_item = dict()

        # process shot transition
        if cam_motion_data['shot_transition']:
            for attr, value in attributes.items():
                res_item[attr] = value
            res_item['camera_arc'] = 'no'
            res_item['camera_crane'] = 'no'
            for attr in tracking_types:
                tracking_type = attr + '-tracking'
                res_item[tracking_type] = 'no'
            for attr in motion_effects:
                res_item[attr] = 'no'
            res_item['video_metadata'] = item['workflows']['cam_motion']
            res_item['video_uid'] = item['video_name']
            res_item['complex_motion_description'] = ''
            res_item['is_tracking'] = 'no'
            res_item['subject_size_change'] = 'no'
            res.append(res_item)
            continue

        # process static shot
        if cam_motion_data['steadiness'] == 'static' or cam_motion_data['camera_movement'] == 'no':
            for attr, value in attributes.items():
                res_item[attr] = value

        if ('camera_arc' in cam_motion_data and cam_motion_data['camera_arc'] != 'no') or ('camera_crane' in cam_motion_data and cam_motion_data['camera_crane'] != 'no'):
            for attr in attributes:
                res_item[attr] = 'unclear'

            if 'camera_arc' in cam_motion_data and cam_motion_data['camera_arc'] != 'no':
                res_item['camera_arc'] = cam_motion_data['camera_arc']
                res_item['camera_crane'] = 'no'
            else:
                res_item['camera_crane'] = cam_motion_data['camera_crane']
                res_item['camera_arc'] = 'no'
        else:
            res_item['camera_arc'] = 'no'
            res_item['camera_crane'] = 'no'

            uncertain_if_no = cam_motion_data['steadiness'] in ["unsteady", "very_unsteady"] or cam_motion_data['camera_movement'] in [
                "major_complex", "minor"]
            uncertain_if_gt = cam_motion_data['camera_movement'] in ["minor"]

            def set_motion(data):
                if data == "no" and uncertain_if_no or uncertain_if_gt:
                    value = 'unclear'
                else:
                    value = data
                return value

            for attr, value in attributes.items():
                if attr in cam_motion_data:
                    res_item[attr] = set_motion(cam_motion_data[attr])
        for attr in tracking_types:
            tracking_type = attr + '-tracking'
            if attr in cam_motion_data['tracking_shot_types']:
                res_item[tracking_type] = 'yes'
            else:
                res_item[tracking_type] = 'no'
        for attr in motion_effects:
            res_item[attr] = 'yes' if cam_motion_data[attr] else 'no'
        res_item['video_metadata'] = item['workflows']['cam_motion']
        res_item['video_uid'] = item['video_name']
        res_item['complex_motion_description'] = cam_motion_data['complex_motion_description'] if 'complex_motion_description' in cam_motion_data else ""
        res_item['is_tracking'] = 'yes' if cam_motion_data['is_tracking'] else 'no'
        res_item['subject_size_change'] = res_item['subject_size_change'] if 'subject_size_change' in res_item else 'no'
        res.append(res_item)

    with open(labelpizza_json_path, 'w') as f:
        json.dump(res, f, indent=2)

# "cam_motion": {
#     "steadiness": "smooth",
#     "camera_movement": "no",
#     "camera_motion_speed": "regular",
#     "is_tracking": false,
#     "camera_forward_backward": "no",
#     "camera_zoom": "no",
#     "camera_left_right": "no",
#     "camera_pan": "no",
#     "camera_up_down": "no",
#     "camera_tilt": "no",
#     "camera_arc": "no",
#     "camera_roll": "no",
#     "frame_freezing": false,
#     "dolly_zoom": false,
#     "motion_blur": false,
#     "cinemagraph": false,
#     "tracking_shot_types": [],
#     "shot_transition": false
# }

if __name__ == '__main__':
    motion_json_path = './20250406ground_only/videos.json'
    trans_motion_json_to_labelpizza(motion_json_path, './syc_test.json')