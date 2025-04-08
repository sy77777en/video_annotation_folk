# Rare Labels
Labels with less than 30 positive examples
| Definition | Positive Examples | Negative Examples | Label Name |
| --- | --- | --- | --- |
| Is there focus tracking on a moving subject in the video? | 27 | 2755 | cam_setup.focus.is_focus_tracking |
| Is this video played at a faster speed than real-time? | 27 | 3286 | cam_setup.video_speed.fast_motion |
| Does the video start completely out of focus? | 26 | 1118 | cam_setup.focus.start_with.focus_start_with_out_of_focus |
| Is the camera positioned directly above the subject for a top-down perspective? | 26 | 3358 | cam_setup.point_of_view.overhead_pov |
| Is the video consistently focused on the background using a shallow depth of field? | 25 | 1119 | cam_setup.focus.is_always.focus_is_background |
| Is this a professional viewpoint used in television broadcasts? | 22 | 3362 | cam_setup.point_of_view.broadcast_pov |
| Is this a third-person isometric (2.5D) gaming video with a tilted overhead angle showing the environment in a three-quarters perspective? | 19 | 3365 | cam_setup.point_of_view.third_person_isometric_game_pov |
| Is the camera physically mounted on an object, keeping its perspective locked to that object? | 18 | 3366 | cam_setup.point_of_view.locked_on_pov |
| Does the video end completely out of focus? | 17 | 1123 | cam_setup.focus.end_with.focus_end_with_out_of_focus |
| Does the video start with the middle ground in focus and then shift to the foreground? | 16 | 1092 | cam_setup.focus.from_to.focus_from_middle_ground_to_foreground |
| Does the video start with the camera at a high angle and transition to a low angle? | 15 | 2989 | cam_setup.angle.from_to.camera_angle_from_high_to_low |
| Does the video feature a subject and scene that do not match, making it difficult to classify shot size? | 15 | 3369 | cam_setup.shot_type.is_just_subject_scene_mismatch_shot |
| Does the camera start below the subject and move up to their height? | 14 | 2283 | cam_setup.height_wrt_subject.from_to.height_wrt_subject_from_below_subject_to_at_subject |
| Does the camera start at the subject's height and then move down to a lower position than them? | 14 | 2283 | cam_setup.height_wrt_subject.from_to.height_wrt_subject_from_at_subject_to_below_subject |
| Does the video start with the foreground in focus and then transition to focusing on the background? | 14 | 1126 | cam_setup.focus.from_to.focus_from_foreground_to_background |
| Does this shot speed up time significantly to show changes over minutes or hours? | 14 | 3299 | cam_setup.video_speed.time_lapse |
| Does this video capture a screen recording with visible UI elements? | 14 | 3370 | cam_setup.point_of_view.screen_recording_pov |
| Is this a forward-facing view from a dash cam, capturing the road or surroundings? | 14 | 3370 | cam_setup.point_of_view.dashcam_pov |
| Is this a gaming video with a camera positioned directly above the character, showing a top-down or top-down oblique view? | 14 | 3370 | cam_setup.point_of_view.third_person_top_down_game_pov |
| Does the video start with the camera positioned at a worm’s eye angle, looking sharply upward to the sky? | 14 | 2990 | cam_setup.angle.start_with.camera_angle_start_with_worm_eye_angle |
| Is this video played at a slightly faster speed than real-time (e.g., 1x-3x)? | 13 | 3300 | cam_setup.video_speed.fast_motion_without_time_lapse |
| Does the video have a clear subject with back-and-forth changes in shot size? | 12 | 3372 | cam_setup.shot_type.is_just_back_and_forth_change_shot |
| Does the video start with the camera at a low angle and transition to a high angle? | 11 | 2993 | cam_setup.angle.from_to.camera_angle_from_low_to_high |
| Does the video end with the camera positioned at a worm’s eye angle, looking sharply upward to the sky? | 10 | 2994 | cam_setup.angle.end_with.camera_angle_end_with_worm_eye_angle |
| Is the camera positioned at a worm’s eye angle throughout the video, looking sharply upward to the sky? | 10 | 2994 | cam_setup.angle.is_always.camera_angle_is_worm_eye_angle |
| Does the video start out of focus and then become in focus? | 9 | 3375 | cam_setup.focus.focus_change_from_out_to_in_focus |
| Does the video start with the background in focus and then shift to the foreground? | 6 | 1138 | cam_setup.focus.from_to.focus_from_background_to_foreground |
| Is the camera facing the person holding it? | 6 | 3378 | cam_setup.point_of_view.selfie_pov |
| Does the camera start above the subject and move down to a position below them? | 5 | 2292 | cam_setup.height_wrt_subject.from_to.height_wrt_subject_from_above_subject_to_below_subject |
| Does the video start with the background in focus and then shift to the middle ground? | 5 | 1139 | cam_setup.focus.from_to.focus_from_background_to_middle_ground |
| Is this video played in reverse, with events unfolding backward in time? | 5 | 3299 | cam_setup.video_speed.time_reversed |
| Does the video start with the middle ground in focus and then shift to the background? | 4 | 1140 | cam_setup.focus.from_to.focus_from_middle_ground_to_background |
| Is the camera framing the character from the hip up? | 3 | 3381 | cam_setup.point_of_view.third_person_over_hip_pov |
| Does the camera start below the subject and move up to a position above them? | 2 | 2295 | cam_setup.height_wrt_subject.from_to.height_wrt_subject_from_below_subject_to_above_subject |
| Does the camera transition from above water to underwater? | 2 | 2470 | cam_setup.height_wrt_ground.above_water_to_underwater |
| Does the video start with a sharp focus on a subject or area and then become out of focus? | 2 | 3382 | cam_setup.focus.focus_change_from_in_to_out_of_focus |
| Is the video consistently out of focus throughout? | 2 | 1140 | cam_setup.focus.is_always.focus_is_out_of_focus |
| Does the camera transition from underwater to above water? | 0 | 2472 | cam_setup.height_wrt_ground.underwater_to_above_water |
