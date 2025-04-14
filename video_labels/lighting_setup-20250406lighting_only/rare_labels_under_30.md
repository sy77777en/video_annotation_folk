# Rare Labels
Labels with less than 30 positive examples
| Definition | Positive Examples | Negative Examples | Label Name |
| --- | --- | --- | --- |
| Does the lighting in the video flash, creating sudden bursts of light in an on/off pattern? | 27 | 182 | lighting_setup.dynamic_light.flashing |
| Does the video feature major light source(s) that traverse the scene or change direction? | 25 | 184 | lighting_setup.dynamic_light.moving_light |
| Is the video noticeably dark or underexposed? | 24 | 185 | lighting_setup.color_grading.brightness.brightness_is_darker_than_normal |
| Is there a noticeable light source consistently illuminating the subject from the front as seen from the camera’s perspective? | 23 | 70 | lighting_setup.subject_lighting.light_direction.direction_is_front_light |
| Does the video feature regular daylight with balanced brightness, neither particularly hard nor soft? | 23 | 54 | lighting_setup.light_quality.sunlight_quality.sunlight_level_is_normal |
| Is the video showing a scene with predominantly dim lighting, but some details remain visible and are not completely underexposed? | 22 | 187 | lighting_setup.color_grading.brightness.brightness_is_dark |
| Is the scene type (indoor or outdoor) unclear, ambiguous, or changing throughout the video? | 22 | 187 | lighting_setup.scene.scene_type_is_complex_others |
| Is there a noticeable light source consistently illuminating the subject from behind (backlighting) as seen from the camera’s perspective? | 19 | 73 | lighting_setup.subject_lighting.light_direction.direction_is_back_light |
| Does the video feature concentrated, cone-shaped volumes of light? | 18 | 191 | lighting_setup.volumetric_lighting.volumetric_spot_light |
| Does the video feature lighting that varies in brightness, either through rhythmic pulsing or irregular flickering? | 17 | 192 | lighting_setup.dynamic_light.pulsing_flickering |
| Does the video feature a noticeable specular reflection from light bouncing off a smooth, glossy surface but does not clearly mirror the scene in detail? | 16 | 193 | lighting_setup.reflection.reflection_from_glossy_surface |
| Does the video feature soft, diffused light on an overcast day? | 16 | 61 | lighting_setup.light_quality.sunlight_quality.sunlight_level_is_overcast |
| Does the primary light source in the video change over time or include a rare light source that is not the sun, fire, moon and stars, or artificial light? | 16 | 193 | lighting_setup.light_source.has_complex_light_source |
| Does the overall brightness of the video change over time, with noticeable shifts between brighter and darker levels across large portions of the frame? | 16 | 147 | lighting_setup.color_grading.brightness.brightness_is_changing |
| Is the video set in a synthetic or 2D environment with unrealistic lighting effects? | 16 | 193 | lighting_setup.scene.scene_type_is_synthetic |
| Does the video contain a revealing shot that gradually uncovers a new environment or subject? | 15 | 194 | lighting_setup.dynamic_effect.revealing_shot |
| Does the video mainly feature highly saturated colors, making hues appear vivid and intense? | 15 | 194 | lighting_setup.color_grading.saturation.color_saturation_is_high |
| Does the video mainly feature desaturated colors, making hues appear muted or grayish? | 15 | 194 | lighting_setup.color_grading.saturation.color_saturation_is_low |
| Is the video noticeably bright or overexposed? | 15 | 194 | lighting_setup.color_grading.brightness.brightness_is_brighter_than_normal |
| Is the video showing a bright and well-lit scene, with high light levels and clearly visible details without overexposure? | 15 | 194 | lighting_setup.color_grading.brightness.brightness_is_bright |
| Does the video feature intense light passing through smoke, fog, or liquid, shaping visible light volumes? | 15 | 194 | lighting_setup.volumetric_lighting.light_through_medium |
| Does the lighting color in the video change abruptly and rapidly (a sudden color shift)? | 14 | 195 | lighting_setup.dynamic_light.color_shifting_sudden |
| Is the video predominantly featuring cool colors, such as blues or greens? | 13 | 196 | lighting_setup.color_grading.temperature.color_temperature_is_cool |
| Does the video feature distinct or dynamic shadow patterns or gobo lighting effects other than Venetian blinds, window frames, foliage, or the subject's shape? | 13 | 196 | lighting_setup.shadow_pattern.shadow_patterns_gobo_others |
| Does the video lacks a realistic light source, with lighting that does not follow natural physics? | 12 | 197 | lighting_setup.light_source.is_abstract |
| Does the video feature strong contrasts between warm and cool colors? | 12 | 144 | lighting_setup.color_grading.temperature.color_temperature_is_contrasting |
| Does the video feature volumetric lighting with a well-defined, contained shape (other than beams, god rays, or spotlights)? | 12 | 197 | lighting_setup.volumetric_lighting.volumetric_light_others |
| Does the video feature shadows shaped by the subject to support the narrative, emphasizing form or movement? | 11 | 198 | lighting_setup.shadow_pattern.subject_shape |
| Does the video feature shadow patterns created by foliage, such as leaves or branches? | 11 | 198 | lighting_setup.shadow_pattern.foliage |
| Is there rim lighting that creates a glowing edge around the subject? | 11 | 198 | lighting_setup.special_effect.rim_light |
| Is the subject consistently illuminated by a mix of front and side lighting? | 10 | 80 | lighting_setup.subject_lighting.light_direction.direction_is_front_side |
| Does the light quality in the scene change between hard and soft over time? | 10 | 152 | lighting_setup.light_quality.light_quality_is_changing |
| Does the video feature a visible diffusion effect, where particles, fluids, or other materials spread and disperse over time? | 10 | 199 | lighting_setup.dynamic_effect.diffusion |
| Is the video primarily lit by firelight? | 10 | 199 | lighting_setup.light_source.has_firelight |
| Does the video feature a vignette effect, where the edges gradually darken or fade? | 10 | 199 | lighting_setup.special_effect.vignette |
| Does the video show objects or characters floating or levitating as if unaffected by gravity? | 9 | 200 | lighting_setup.dynamic_effect.levitation_floating |
| Does the video feature visible splashing or wave-like motion in water or other liquids? | 9 | 200 | lighting_setup.dynamic_effect.splashing_waves |
| Is the subject lit with flat lighting, with little to no contrast? | 8 | 153 | lighting_setup.subject_lighting.light_contrast.flat_lighting |
| Does the lighting on the subject have minimal contrast (1:1 to 1:2), creating a flat lighting effect? | 8 | 153 | lighting_setup.subject_lighting.light_contrast.subject_light_contrast_is_minimal |
| Is the subject lit with high-key lighting? | 8 | 153 | lighting_setup.subject_lighting.light_contrast.high_key_lighting |
| Is the video predominantly featuring warm colors, such as reds, oranges, or yellows? | 8 | 201 | lighting_setup.color_grading.temperature.color_temperature_is_warm |
| Does the video contain obvious lens flares? | 8 | 201 | lighting_setup.lens_effect.lens_flares |
| Does the video feature warm, golden sunlight at sunrise or sunset? | 7 | 70 | lighting_setup.light_quality.sunlight_quality.sunlight_level_is_sunset_sunrise |
| Does the video feature striking, separated rays of light (god rays) streaming through gaps in the environment? | 7 | 202 | lighting_setup.volumetric_lighting.god_rays |
| Is there a silhouette lighting effect that creates a dark outline of the foreground subject against a bright background? | 7 | 202 | lighting_setup.special_effect.silhouette |
| Is the subject consistently illuminated by a mix of back and side lighting? | 6 | 79 | lighting_setup.subject_lighting.light_direction.direction_is_rear_side |
| Does the lighting color in the video change gradually and smoothly (a smooth color shift)? | 6 | 203 | lighting_setup.dynamic_light.color_shifting_smooth |
| Does the video feature an explosion with a sudden burst of flames, matter, and outward force? | 6 | 203 | lighting_setup.dynamic_effect.explosion |
| Does the video have noticeable shifts between warm and cool color tones? | 6 | 150 | lighting_setup.color_grading.temperature.color_temperature_is_changing |
| Does the video contain typical lens flares, appearing as circular, polygonal, veiling, scattered, or streak-like artifacts? | 6 | 203 | lighting_setup.lens_effect.lens_flare_regular |
| Is there a noticeable light source consistently illuminating the subject from below (bottom lighting) as seen from the camera’s perspective? | 5 | 82 | lighting_setup.subject_lighting.light_direction.direction_is_bottom_light |
| Does the video capture a lightning effect with intense flashes and jagged, branching streaks? | 5 | 204 | lighting_setup.natural_effect.lightning |
| Does the video feature a noticeable aerial perspective, where distant scenery appears less detailed, desaturated, and hazier due to atmospheric effects? | 5 | 204 | lighting_setup.natural_effect.aerial_perspective |
| Is the video entirely in black and white, with no color present? | 5 | 204 | lighting_setup.color_grading.is_black_white |
| Does the video feature strong contrasts between highly saturated and desaturated hues? | 5 | 171 | lighting_setup.color_grading.saturation.color_saturation_is_contrasting |
| Does the video feature visible beams of light with well-defined edges, creating linear volumes of light? | 5 | 204 | lighting_setup.volumetric_lighting.volumetric_beam_light |
| Does the video feature distinct shadow patterns cast by venetian blinds? | 5 | 204 | lighting_setup.shadow_pattern.venetian_blinds |
| Does the video feature bright and colorful city lighting from various artificial sources? | 5 | 204 | lighting_setup.special_effect.city_light |
| Does the video feature shadows cast by window frames? | 4 | 205 | lighting_setup.shadow_pattern.window_frames |
| Does the video feature soft, out-of-focus light orbs in the background, created by distant lights and a shallow depth of field? | 4 | 205 | lighting_setup.lens_effect.bokeh |
| Does the video feature water caustics, where light creates dynamic rippling patterns? | 4 | 205 | lighting_setup.special_effect.water_caustics |
| Does the video show noticeable shimmering effects or bright highlights from light reflecting off water? | 3 | 206 | lighting_setup.reflection.reflection_from_water |
| Does the video feature a transformation or morphing effect where one object changes into another? | 3 | 206 | lighting_setup.dynamic_effect.transformation_morphing |
| Does the video have noticeable shifts in color saturation between high and low over time? | 3 | 173 | lighting_setup.color_grading.saturation.color_saturation_is_changing |
| Does the video contain anamorphic lens flares as bright, elongated streaks from light interacting with an anamorphic lens? | 3 | 206 | lighting_setup.lens_effect.lens_flares_anamorphic |
| Does the video show objects breaking, shattering, or fragmenting into smaller pieces? | 2 | 207 | lighting_setup.dynamic_effect.shattering_breaking |
| Is the video showing a scene that is extremely dark and underexposed, with minimal lighting and most areas showing barely any visible details? | 2 | 207 | lighting_setup.color_grading.brightness.brightness_is_very_dark |
| Does the video use a mist diffusion filter to soften the image, creating a dreamy, glowing effect? | 2 | 207 | lighting_setup.lens_effect.mist_diffusion |
| Does the video feature light from street lamps? | 2 | 207 | lighting_setup.special_effect.street_light |
| Is there Rembrandt lighting that illuminates one side of the subject’s face, creating a small triangle of light on the other? | 1 | 208 | lighting_setup.subject_lighting.rembrandt_lighting |
| Does the video show strong reflections from light bouncing off a mirror, clearly mirroring the scenery in detail? | 1 | 208 | lighting_setup.reflection.reflection_from_mirror |
| Does the video feature a noticeable rainbow? | 1 | 208 | lighting_setup.natural_effect.rainbow |
| Is the video lit by moonlight or starnight, with the moon or stars visible? | 1 | 208 | lighting_setup.light_source.has_moonlight_starlight |
| Does the video feature a noticeable heat haze effect, with air distortions and shimmering caused by rising heat? | 0 | 209 | lighting_setup.natural_effect.heat_haze |
| Does the video feature an aurora, with flowing, colorful light patterns in the sky? | 0 | 209 | lighting_setup.natural_effect.aurora |
| Is the video excessively bright and overexposed, making details hard to see? | 0 | 209 | lighting_setup.color_grading.brightness.brightness_is_very_bright |
| Does the video feature a headlight or flashlight that illuminates the scene in front with intense, focused light, creating sharp contrast against darker surroundings? | 0 | 209 | lighting_setup.special_effect.headlight_flashlight |
