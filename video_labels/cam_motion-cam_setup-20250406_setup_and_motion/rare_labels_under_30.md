# Rare Labels
Labels with less than 30 positive examples
| Definition | Positive Examples | Negative Examples | Label Name |
| --- | --- | --- | --- |
| Is it a tracking shot with the camera following behind the subject? | 29 | 2085 | cam_motion.object_centric_movement.tail_tracking_shot |
| Is this a stop-motion video where objects are moved frame by frame to create motion? | 29 | 2113 | cam_setup.video_speed.stop_motion |
| Does the camera only move backward (not zooming out) with respect to the ground? | 28 | 1814 | cam_motion.ground_centric_movement.backward.only_backward_wrt_ground |
| Does the camera only move rightward without any other camera movements? | 28 | 2235 | cam_motion.camera_centric_movement.rightward.only_rightward |
| Does the camera start noticeably higher than the subject and then move down to their height? | 28 | 1394 | cam_setup.height_wrt_subject.from_to.height_wrt_subject_from_above_subject_to_at_subject |
| Does the video end with an extreme close-up shot that isolates a very small detail of the subject or scene? | 28 | 1694 | cam_setup.shot_size.end_with.shot_size_end_with_extreme_close_up |
| Is the camera positioned below the subject throughout the video? | 27 | 1395 | cam_setup.height_wrt_subject.is_always.height_wrt_subject_is_below_subject |
| Does the video start with an extreme close-up shot that isolates a very small detail of the subject or scene? | 27 | 1675 | cam_setup.shot_size.start_with.shot_size_start_with_extreme_close_up |
| Is it a side-tracking shot where the camera moves left to follow the subject? | 25 | 2105 | cam_motion.object_centric_movement.side_tracking_shot_leftward |
| Does the focal plane transition from distant to close? | 25 | 1465 | cam_setup.focus.focus_change_from_far_to_near |
| Does the focal plane transition from close to distant? | 25 | 1465 | cam_setup.focus.focus_change_from_near_to_far |
| Does the subject appear smaller during the tracking shot? | 23 | 2107 | cam_motion.object_centric_movement.tracking_subject_smaller_size |
| Is the camera positioned directly above the subject for a top-down perspective? | 23 | 2122 | cam_setup.point_of_view.overhead_pov |
| Does the video maintain an extreme close-up shot throughout, focusing very tightly on specific details or features? | 22 | 1721 | cam_setup.shot_size.is_always.shot_size_is_extreme_close_up |
| Does the video show a medium-full shot that frames the human subject from mid-thigh (or knee) upward? | 22 | 1721 | cam_setup.shot_size.is_always.shot_size_is_medium_full |
| Does the video start with the camera at a low angle and transition to a level angle? | 22 | 1880 | cam_setup.angle.from_to.camera_angle_from_low_to_level |
| Does the main subject disappear from the frame? | 21 | 1745 | cam_setup.shot_size.subject_disappearing |
| Does the video end with the camera fully submerged underwater, capturing scenes beneath the water’s surface? | 20 | 1620 | cam_setup.height_wrt_ground.end_with.height_wrt_ground_end_with_underwater_level |
| Is the video consistently focused on the background using a shallow depth of field? | 20 | 699 | cam_setup.focus.is_always.focus_is_background |
| Is this video played at a faster speed than real-time? | 20 | 2073 | cam_setup.video_speed.fast_motion |
| Does the video feature a clear subject, but changes in framing make shot size classification tricky? | 20 | 2125 | cam_setup.shot_type.is_just_clear_subject_dynamic_size_shot |
| Is the camera fully submerged underwater throughout the video, capturing scenes beneath the water’s surface? | 19 | 1621 | cam_setup.height_wrt_ground.is_always.height_wrt_ground_is_underwater_level |
| Does the video start with the camera fully submerged underwater, capturing scenes beneath the water’s surface? | 19 | 1621 | cam_setup.height_wrt_ground.start_with.height_wrt_ground_start_with_underwater_level |
| Does the camera only zoom in with no other movement? | 18 | 2245 | cam_motion.camera_centric_movement.zoom_in.only_zoom_in |
| Does the camera only move leftward without any other camera movements? | 17 | 2246 | cam_motion.camera_centric_movement.leftward.only_leftward |
| Does the camera only pan leftward without any other camera movements? | 16 | 2247 | cam_motion.camera_centric_movement.pan_left.only_pan_left |
| Is this a professional viewpoint used in television broadcasts? | 16 | 2129 | cam_setup.point_of_view.broadcast_pov |
| Does the camera only pan rightward without any other camera movements? | 15 | 2248 | cam_motion.camera_centric_movement.pan_right.only_pan_right |
| Does the camera only zoom out with no other movement? | 14 | 2249 | cam_motion.camera_centric_movement.zoom_out.only_zoom_out |
| Does the video start with the foreground in focus and then transition to focusing on the middle ground? | 14 | 699 | cam_setup.focus.from_to.focus_from_foreground_to_middle_ground |
| Is this a third-person isometric (2.5D) gaming video with a tilted overhead angle showing the environment in a three-quarters perspective? | 14 | 2131 | cam_setup.point_of_view.third_person_isometric_game_pov |
| Is this a forward-facing view from a dash cam, capturing the road or surroundings? | 14 | 2131 | cam_setup.point_of_view.dashcam_pov |
| Does the camera tilt to track the subjects as they move? | 13 | 2105 | cam_motion.object_centric_movement.tilt_tracking_shot |
| Does the video start completely out of focus? | 13 | 706 | cam_setup.focus.start_with.focus_start_with_out_of_focus |
| Is there focus tracking on a moving subject in the video? | 12 | 1771 | cam_setup.focus.is_focus_tracking |
| Does the video end completely out of focus? | 12 | 705 | cam_setup.focus.end_with.focus_end_with_out_of_focus |
| Is this a gaming video with a camera positioned directly above the character, showing a top-down or top-down oblique view? | 12 | 2133 | cam_setup.point_of_view.third_person_top_down_game_pov |
| Does the camera follow the subject while moving in an arc? | 11 | 2119 | cam_motion.object_centric_movement.arc_tracking_shot |
| Is the camera craning upward in an arc? | 11 | 2006 | cam_motion.arc_crane_movement.crane_up.has_crane_up |
| Is this video played at a slightly faster speed than real-time (e.g., 1x-3x)? | 11 | 2082 | cam_setup.video_speed.fast_motion_without_time_lapse |
| Does the video feature a subject and scene that do not match, making it difficult to classify shot size? | 11 | 2134 | cam_setup.shot_type.is_just_subject_scene_mismatch_shot |
| Does the camera only tilt upward without any other camera movements? | 10 | 2253 | cam_motion.camera_centric_movement.tilt_up.only_tilt_up |
| Does this video capture a screen recording with visible UI elements? | 10 | 2135 | cam_setup.point_of_view.screen_recording_pov |
| Is the camera physically mounted on an object, keeping its perspective locked to that object? | 10 | 2135 | cam_setup.point_of_view.locked_on_pov |
| Does the video start with the middle ground in focus and then shift to the foreground? | 9 | 689 | cam_setup.focus.from_to.focus_from_middle_ground_to_foreground |
| Does this shot speed up time significantly to show changes over minutes or hours? | 9 | 2084 | cam_setup.video_speed.time_lapse |
| Does the video start with the camera at a high angle and transition to a low angle? | 9 | 1893 | cam_setup.angle.from_to.camera_angle_from_high_to_low |
| Does the video have a clear subject with back-and-forth changes in shot size? | 9 | 2136 | cam_setup.shot_type.is_just_back_and_forth_change_shot |
| Does the camera move only upward (not tilting up) in the scene, or only eastward in a bird's eye view, or only westward in a worm's eye view? | 8 | 2255 | cam_motion.ground_centric_movement.upward.only_upward_wrt_ground_birds_worms_included |
| Does the camera start below the subject and move up to their height? | 8 | 1414 | cam_setup.height_wrt_subject.from_to.height_wrt_subject_from_below_subject_to_at_subject |
| Does the video start with the camera positioned at a worm’s eye angle, looking sharply upward to the sky? | 8 | 1894 | cam_setup.angle.start_with.camera_angle_start_with_worm_eye_angle |
| Does the video contain a frame freeze effect at any point? | 7 | 2123 | cam_motion.has_frame_freezing |
| Does the shot feature a dolly zoom effect with the camera moving forward and zooming out? | 7 | 2122 | cam_motion.dolly_zoom_movement.has_dolly_in_zoom_out |
| Does the shot feature a dolly zoom effect with the camera moving backward and zooming in? | 7 | 2122 | cam_motion.dolly_zoom_movement.has_dolly_out_zoom_in |
| Does the camera start at the subject's height and then move down to a lower position than them? | 7 | 1415 | cam_setup.height_wrt_subject.from_to.height_wrt_subject_from_at_subject_to_below_subject |
| Does the video start with the foreground in focus and then transition to focusing on the background? | 7 | 710 | cam_setup.focus.from_to.focus_from_foreground_to_background |
| Does the video start with the camera at a low angle and transition to a high angle? | 7 | 1895 | cam_setup.angle.from_to.camera_angle_from_low_to_high |
| Does the video end with the camera positioned at a worm’s eye angle, looking sharply upward to the sky? | 7 | 1895 | cam_setup.angle.end_with.camera_angle_end_with_worm_eye_angle |
| Is the camera positioned at a worm’s eye angle throughout the video, looking sharply upward to the sky? | 7 | 1895 | cam_setup.angle.is_always.camera_angle_is_worm_eye_angle |
| Does the camera move only downward (not tilting down) in the scene, or only westward in a bird's eye view, or only eastward in a worm's eye view? | 6 | 2257 | cam_motion.ground_centric_movement.downward.only_downward_wrt_ground_birds_worms_included |
| Is it a tracking shot with the camera leading the subject from a front-side angle? | 5 | 2125 | cam_motion.object_centric_movement.front_side_tracking_shot |
| Is it a tracking shot with the camera following behind the subject at a rear-side angle? | 5 | 2125 | cam_motion.object_centric_movement.rear_side_tracking_shot |
| Does the camera only move upward (not tilting up) with respect to the ground? | 5 | 1837 | cam_motion.ground_centric_movement.upward.only_upward_wrt_ground |
| Does the camera only tilt downward without any other camera movements? | 5 | 2258 | cam_motion.camera_centric_movement.tilt_down.only_tilt_down |
| Does the video start with the background in focus and then shift to the foreground? | 5 | 714 | cam_setup.focus.from_to.focus_from_background_to_foreground |
| Does the video start with the background in focus and then shift to the middle ground? | 5 | 714 | cam_setup.focus.from_to.focus_from_background_to_middle_ground |
| Does the camera start above the subject and move down to a position below them? | 4 | 1418 | cam_setup.height_wrt_subject.from_to.height_wrt_subject_from_above_subject_to_below_subject |
| Does the video start out of focus and then become in focus? | 4 | 2141 | cam_setup.focus.focus_change_from_out_to_in_focus |
| Does the camera only move downward (not tilting down) with respect to the ground? | 3 | 1839 | cam_motion.ground_centric_movement.downward.only_downward_wrt_ground |
| Does the camera only roll clockwise without any other camera movements? | 3 | 2260 | cam_motion.camera_centric_movement.roll_clockwise.only_roll_clockwise |
| Is the camera craning downward in an arc? | 3 | 2014 | cam_motion.arc_crane_movement.crane_down.has_crane_down |
| Is this video played in reverse, with events unfolding backward in time? | 3 | 2084 | cam_setup.video_speed.time_reversed |
| Is the camera facing the person holding it? | 3 | 2142 | cam_setup.point_of_view.selfie_pov |
| Is the camera framing the character from the hip up? | 3 | 2142 | cam_setup.point_of_view.third_person_over_hip_pov |
| Does the camera only roll counterclockwise without any other camera movements? | 2 | 2261 | cam_motion.camera_centric_movement.roll_counterclockwise.only_roll_counterclockwise |
| Does the video start with a sharp focus on a subject or area and then become out of focus? | 2 | 2143 | cam_setup.focus.focus_change_from_in_to_out_of_focus |
| Does the video start with the middle ground in focus and then shift to the background? | 2 | 717 | cam_setup.focus.from_to.focus_from_middle_ground_to_background |
| Is the video consistently out of focus throughout? | 2 | 716 | cam_setup.focus.is_always.focus_is_out_of_focus |
| Does the camera start below the subject and move up to a position above them? | 1 | 1421 | cam_setup.height_wrt_subject.from_to.height_wrt_subject_from_below_subject_to_above_subject |
| Does the camera transition from above water to underwater? | 1 | 1563 | cam_setup.height_wrt_ground.above_water_to_underwater |
| Is the scene in the video dynamic? | 0 | 0 | cam_motion.scene_movement.dynamic_scene |
| Is the scene in the video mostly static with minimal movement? | 0 | 0 | cam_motion.scene_movement.mostly_static_scene |
| Is the scene in the video completely static? | 0 | 0 | cam_motion.scene_movement.static_scene |
| Does the camera move downward (not tilting down) with respect to the initial frame? | 0 | 855 | cam_motion.camera_centric_movement.downward.has_downward_wrt_camera |
| Does the camera only move downward (not tilting down) with respect to the initial frame? | 0 | 2263 | cam_motion.camera_centric_movement.downward.only_downward_wrt_camera |
| Does the camera move backward (not zooming out) with respect to the initial frame? | 0 | 855 | cam_motion.camera_centric_movement.backward.has_backward_wrt_camera |
| Does the camera move only backward (not zooming out) with respect to the initial frame? | 0 | 2263 | cam_motion.camera_centric_movement.backward.only_backward_wrt_camera |
| Does the camera move upward (not tilting up) with respect to the initial frame? | 0 | 855 | cam_motion.camera_centric_movement.upward.has_upward_wrt_camera |
| Does the camera only move upward (not tilting up) with respect to the initial frame? | 0 | 2263 | cam_motion.camera_centric_movement.upward.only_upward_wrt_camera |
| Does the camera move forward (not zooming in) with respect to the initial frame? | 0 | 855 | cam_motion.camera_centric_movement.forward.has_forward_wrt_camera |
| Does the camera move only forward (not zooming in) with respect to the initial frame? | 0 | 2263 | cam_motion.camera_centric_movement.forward.only_forward_wrt_camera |
| Does the camera transition from underwater to above water? | 0 | 1564 | cam_setup.height_wrt_ground.underwater_to_above_water |
