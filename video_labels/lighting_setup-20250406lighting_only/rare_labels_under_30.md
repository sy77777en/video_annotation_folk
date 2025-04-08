# Rare Labels
Labels with less than 30 positive examples
| Definition | Positive Examples | Negative Examples | Label Name |
| --- | --- | --- | --- |
| Does the video include shot transitions? | 28 | 206 | lighting_setup.has_shot_transition_lighting_setup |
| Does the lighting in the video flash, creating sudden bursts of light in an on/off pattern? | 27 | 179 | lighting_setup.dynamic_light.flashing |
| Does the video feature a complex color composition or dynamics that cannot be classified as strictly high, low, or neutral color saturation? | 27 | 179 | lighting_setup.color_grading.saturation.color_saturation_is_complex_others |
| Is the video noticeably dark or underexposed? | 26 | 180 | lighting_setup.color_grading.brightness.brightness_is_darker_than_normal |
| Does the video feature major light source(s) that traverse the scene or change direction? | 24 | 182 | lighting_setup.dynamic_light.moving_light |
| Is the video predominantly dark with dim lighting but not so underexposed that most details are lost? | 24 | 182 | lighting_setup.color_grading.brightness.brightness_is_dark |
| Is there a noticeable light source consistently illuminating the subject from the front as seen from the camera’s perspective? | 23 | 71 | lighting_setup.subject_lighting.light_direction.direction_is_front_light |
| Does the video feature regular daylight with balanced brightness, neither particularly hard nor soft? | 23 | 53 | lighting_setup.light_quality.sunlight_quality.sunlight_level_is_normal |
| Is the scene type (indoor or outdoor) unclear, ambiguous, or changing throughout the video? | 22 | 184 | lighting_setup.scene.scene_type_is_complex_others |
| Does the video’s brightness level change over time? | 21 | 147 | lighting_setup.color_grading.brightness.brightness_is_changing |
| Is there a noticeable light source consistently illuminating the subject from behind (backlighting) as seen from the camera’s perspective? | 20 | 73 | lighting_setup.subject_lighting.light_direction.direction_is_back_light |
| Does the video feature lighting that varies in brightness, either through rhythmic pulsing or irregular flickering? | 17 | 189 | lighting_setup.dynamic_light.pulsing_flickering |
| Does the video feature concentrated, cone-shaped volumes of light? | 17 | 189 | lighting_setup.volumetric_lighting.volumetric_spot_light |
| Does the video feature soft, diffused light on an overcast day? | 16 | 60 | lighting_setup.light_quality.sunlight_quality.sunlight_level_is_overcast |
| Does the primary light source in the video change over time or include a rare light source that is not the sun, fire, moon and stars, or artificial light? | 16 | 190 | lighting_setup.light_source.has_complex_light_source |
| Does the video mainly feature highly saturated colors, making hues appear vivid and intense? | 16 | 190 | lighting_setup.color_grading.saturation.color_saturation_is_high |
| Does the video contain a revealing shot that gradually uncovers a new environment or subject? | 15 | 191 | lighting_setup.dynamic_effect.revealing_shot |
| Does the video mainly feature desaturated colors, making hues appear muted or grayish? | 15 | 191 | lighting_setup.color_grading.saturation.color_saturation_is_low |
| Is the video set in a synthetic or 2D environment with unrealistic lighting effects? | 15 | 191 | lighting_setup.scene.scene_type_is_synthetic |
| Does the video feature a noticeable specular reflection from light bouncing off a smooth, glossy surface but does not clearly mirror the scene in detail? | 14 | 192 | lighting_setup.reflection.reflection_from_glossy_surface |
| Does the video feature intense light passing through smoke, fog, or liquid, shaping visible light volumes? | 14 | 192 | lighting_setup.volumetric_lighting.light_through_medium |
| Does the lighting color in the video change abruptly and rapidly (a sudden color shift)? | 13 | 193 | lighting_setup.dynamic_light.color_shifting_sudden |
| Is the video predominantly featuring cool colors, such as blues or greens? | 13 | 193 | lighting_setup.color_grading.temperature.color_temperature_is_cool |
| Is the video noticeably bright or overexposed? | 13 | 193 | lighting_setup.color_grading.brightness.brightness_is_brighter_than_normal |
| Is the video well-lit with strong lighting, making the scene bright and clear but not overexposed? | 13 | 193 | lighting_setup.color_grading.brightness.brightness_is_bright |
| Does the video feature strong contrasts between warm and cool colors? | 12 | 146 | lighting_setup.color_grading.temperature.color_temperature_is_contrasting |
| Does the video feature volumetric lighting with a well-defined, contained shape (other than beams, god rays, or spotlights)? | 12 | 194 | lighting_setup.volumetric_lighting.volumetric_light_others |
| Does the video feature distinct or dynamic shadow patterns or gobo lighting effects other than Venetian blinds, window frames, foliage, or the subject's shape? | 12 | 194 | lighting_setup.shadow_pattern.shadow_patterns_gobo_others |
| Does the video lacks a realistic light source, with lighting that does not follow natural physics? | 11 | 195 | lighting_setup.light_source.is_abstract |
| Is the subject consistently illuminated by a mix of front and side lighting? | 10 | 81 | lighting_setup.subject_lighting.light_direction.direction_is_front_side |
| Does the light quality in the scene change between hard and soft over time? | 10 | 151 | lighting_setup.light_quality.light_quality_is_changing |
| Does the video feature a visible diffusion effect, where particles, fluids, or other materials spread and disperse over time? | 10 | 196 | lighting_setup.dynamic_effect.diffusion |
| Is the video primarily lit by firelight? | 10 | 196 | lighting_setup.light_source.has_firelight |
| Does the video feature shadows shaped by the subject to support the narrative, emphasizing form or movement? | 10 | 196 | lighting_setup.shadow_pattern.subject_shape |
| Does the video feature shadow patterns created by foliage, such as leaves or branches? | 10 | 196 | lighting_setup.shadow_pattern.foliage |
| Is there rim lighting that creates a glowing edge around the subject? | 10 | 196 | lighting_setup.special_effect.rim_light |
| Does the video show objects or characters floating or levitating as if unaffected by gravity? | 9 | 197 | lighting_setup.dynamic_effect.levitation_floating |
| Does the video feature visible splashing or wave-like motion in water or other liquids? | 9 | 197 | lighting_setup.dynamic_effect.splashing_waves |
| Is the subject lit with flat lighting, with little to no contrast? | 8 | 150 | lighting_setup.subject_lighting.light_contrast.flat_lighting |
| Does the lighting on the subject have minimal contrast (1:1 to 1:2), creating a flat lighting effect? | 8 | 150 | lighting_setup.subject_lighting.light_contrast.subject_light_contrast_is_minimal |
| Does the video have noticeable shifts between warm and cool color tones? | 8 | 150 | lighting_setup.color_grading.temperature.color_temperature_is_changing |
| Is the video predominantly featuring warm colors, such as reds, oranges, or yellows? | 8 | 198 | lighting_setup.color_grading.temperature.color_temperature_is_warm |
| Does the video contain obvious lens flares? | 8 | 198 | lighting_setup.lens_effect.lens_flares |
| Is the subject consistently illuminated by a mix of back and side lighting? | 7 | 79 | lighting_setup.subject_lighting.light_direction.direction_is_rear_side |
| Does the video feature warm, golden sunlight at sunrise or sunset? | 7 | 69 | lighting_setup.light_quality.sunlight_quality.sunlight_level_is_sunset_sunrise |
| Does the video feature striking, separated rays of light (god rays) streaming through gaps in the environment? | 7 | 199 | lighting_setup.volumetric_lighting.god_rays |
| Does the video feature a vignette effect, where the edges gradually darken or fade? | 7 | 199 | lighting_setup.special_effect.vignette |
| Is there a silhouette lighting effect that creates a dark outline of the foreground subject against a bright background? | 7 | 199 | lighting_setup.special_effect.silhouette |
| Does the video feature an explosion with a sudden burst of flames, matter, and outward force? | 6 | 200 | lighting_setup.dynamic_effect.explosion |
| Does the video contain typical lens flares, appearing as circular, polygonal, veiling, scattered, or streak-like artifacts? | 6 | 200 | lighting_setup.lens_effect.lens_flare_regular |
| Is there a noticeable light source consistently illuminating the subject from below (bottom lighting) as seen from the camera’s perspective? | 5 | 83 | lighting_setup.subject_lighting.light_direction.direction_is_bottom_light |
| Does the lighting color in the video change gradually and smoothly (a smooth color shift)? | 5 | 201 | lighting_setup.dynamic_light.color_shifting_smooth |
| Does the video capture a lightning effect with intense flashes and jagged, branching streaks? | 5 | 201 | lighting_setup.natural_effect.lightning |
| Is the video entirely in black and white, with no color present? | 5 | 201 | lighting_setup.color_grading.is_black_white |
| Does the video feature strong contrasts between highly saturated and desaturated hues? | 5 | 174 | lighting_setup.color_grading.saturation.color_saturation_is_contrasting |
| Does the video have noticeable shifts in color saturation between high and low over time? | 5 | 174 | lighting_setup.color_grading.saturation.color_saturation_is_changing |
| Does the video feature visible beams of light with well-defined edges, creating linear volumes of light? | 5 | 201 | lighting_setup.volumetric_lighting.volumetric_beam_light |
| Does the video feature distinct shadow patterns cast by venetian blinds? | 5 | 201 | lighting_setup.shadow_pattern.venetian_blinds |
| Does the video feature bright and colorful city lighting from various artificial sources? | 5 | 201 | lighting_setup.special_effect.city_light |
| Does the video feature a noticeable aerial perspective, where distant scenery appears less detailed, desaturated, and hazier due to atmospheric effects? | 4 | 202 | lighting_setup.natural_effect.aerial_perspective |
| Does the video feature shadows cast by window frames? | 4 | 202 | lighting_setup.shadow_pattern.window_frames |
| Does the video feature soft, out-of-focus light orbs in the background, created by distant lights and a shallow depth of field? | 4 | 202 | lighting_setup.lens_effect.bokeh |
| Does the video feature water caustics, where light creates dynamic rippling patterns? | 4 | 202 | lighting_setup.special_effect.water_caustics |
| Does the video feature a transformation or morphing effect where one object changes into another? | 3 | 203 | lighting_setup.dynamic_effect.transformation_morphing |
| Does the video contain anamorphic lens flares as bright, elongated streaks from light interacting with an anamorphic lens? | 3 | 203 | lighting_setup.lens_effect.lens_flares_anamorphic |
| Does the video show noticeable shimmering effects or bright highlights from light reflecting off water? | 2 | 204 | lighting_setup.reflection.reflection_from_water |
| Does the video show objects breaking, shattering, or fragmenting into smaller pieces? | 2 | 204 | lighting_setup.dynamic_effect.shattering_breaking |
| Is the video extremely dark and underexposed, with barely any visible details due to minimal lighting? | 2 | 204 | lighting_setup.color_grading.brightness.brightness_is_very_dark |
| Does the video use a mist diffusion filter to soften the image, creating a dreamy, glowing effect? | 2 | 204 | lighting_setup.lens_effect.mist_diffusion |
| Does the video feature light from street lamps? | 2 | 204 | lighting_setup.special_effect.street_light |
| Is there Rembrandt lighting that illuminates one side of the subject’s face, creating a small triangle of light on the other? | 1 | 205 | lighting_setup.subject_lighting.rembrandt_lighting |
| Does the video show strong reflections from light bouncing off a mirror, clearly mirroring the scenery in detail? | 1 | 205 | lighting_setup.reflection.reflection_from_mirror |
| Does the video feature a noticeable rainbow? | 1 | 205 | lighting_setup.natural_effect.rainbow |
| Is the video lit by moonlight or starnight, with the moon or stars visible? | 1 | 205 | lighting_setup.light_source.has_moonlight_starlight |
| Is the subject lit with high-key lighting? | 0 | 158 | lighting_setup.subject_lighting.light_contrast.high_key_lighting |
| Does the video feature a noticeable heat haze effect, with air distortions and shimmering caused by rising heat? | 0 | 206 | lighting_setup.natural_effect.heat_haze |
| Does the video feature an aurora, with flowing, colorful light patterns in the sky? | 0 | 206 | lighting_setup.natural_effect.aurora |
| Is the video excessively bright and overexposed, making details hard to see? | 0 | 206 | lighting_setup.color_grading.brightness.brightness_is_very_bright |
| Does the video feature a headlight or flashlight that illuminates the scene in front with intense, focused light, creating sharp contrast against darker surroundings? | 0 | 206 | lighting_setup.special_effect.headlight_flashlight |
