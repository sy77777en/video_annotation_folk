#!/usr/bin/env python3
"""
Policy Comparison Generator

This script generates a markdown file that compares four different versions of policies
for each of the 5 main policy classes:
1. human_short: One sentence summary 
2. human: First paragraph of the human-readable policy
3. human_detailed: Full content from the human-readable policy file  
4. model_without_label: Output from get_prompt_without_video_info() method

Usage:
    python generate_policy_comparison.py [--output output.md]
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime

# Add the project root to the path so we can import from caption_policy
script_dir = Path(__file__).resolve().parent
if script_dir.name == 'caption':
    project_root = script_dir
else:
    project_root = script_dir.parent

sys.path.insert(0, str(project_root))

try:
    from caption_policy.prompt_generator import (
        SubjectPolicy, ScenePolicy, SubjectMotionPolicy, 
        SpatialPolicy, CameraPolicy
    )
except ImportError as e:
    print(f"Error importing policy classes: {e}")
    print("Make sure you're running this script from the project root or caption directory")
    sys.exit(1)


def get_first_paragraph(text):
    """Extract the first paragraph from text"""
    if not text:
        return None
    
    # Split by double newlines to get paragraphs
    paragraphs = text.strip().split('\n\n')
    if paragraphs:
        return paragraphs[0].strip()
    return text.strip()


def get_one_sentence_summary(task_name):
    """Generate a one sentence summary for each task"""
    summaries = {
        "subject_description": "Describe who or what is in the video and their key visual attributes.",
        "scene_composition_dynamics": "Describe the environment, setting, and background elements of the scene.",
        "subject_motion_dynamics": "Describe how subjects move and what they interact with.",
        "spatial_framing_dynamics": "Describe how subjects and elements are framed and positioned within the shot.",
        "camera_framing_dynamics": "Describe how the video is captured and how the camera moves."
    }
    return summaries.get(task_name, "")


def get_human_detailed_content(task_name):
    """Get the full human-readable policy content for each task"""
    
    if task_name == "subject_description":
        return """Provide a concise yet informative description of the subjects in this video, including their types, appearances (e.g., clothing, facial expressions, gender, ethnicity, color, shape), and poses. When multiple subjects are present, clearly distinguish them using unique traits, position, actions, or relationships, and describe them in temporal or prominence-based order to ensure clarity.

#### 1. Subject Type  
1. Identify the subject's type precisely.  
   - **Examples:**  
     1. "man," "woman," "dog," "car," "tree."  
     2. Avoid vague terms like "thing" or "item."  
2. If the subject type is ambiguous, provide your best judgment and explain your reasoning.  

#### 2. Visual Attributes  
1. Describe the subject's key visual characteristics using specific and descriptive language.  
2. Consider the following aspects where relevant:  

   - **Appearance:**  
     1. **People:** Include details like clothing (colors and style), hairstyle, facial hair, age (if discernible), gender, ethnicity (if relevant and clear), and facial expression.  
     2. **Objects:** Describe their color, material, shape, and distinguishing marks (e.g., "smooth," "rough," "furry," "metallic," "black," "red," etc.).  

   - **Pose/Orientation:**  
     1. Describe the subject's posture and orientation within the frame (e.g., "standing," "sitting," "lying down," "walking," "facing left," "arms raised," "facing the camera").  
     2. Pay particular attention to objects not in their usual state (e.g., a tilted lamp, a book lying open face down).  

#### 3. How to Refer to Multiple Subjects  
1. When there is more than one important person or object, make sure it's clear which one you are referring to.  
2. Use the following strategies for clarity:  

   - **Type:** The simplest way to refer to a subject is by its category, e.g., "the man," "the dog," or "the tree."  
   - **Attributes:** If multiple subjects belong to the same category, use distinguishing features:  

     1. **Unique Appearance:** Highlight distinct traits, such as "the woman in the red dress," "the man with the beard," "the blue car," or "the largest tree."  
     2. **Location:** Specify position within the scene, e.g., "the man on the left," "the dog in the background," "the car in the midground," or "the building in the middle."  
     3. **Action:** Describe their activity, e.g., "the person walking," "the child playing with a ball," "the bird flying," or "the cat sitting on the windowsill."  
     4. **Relationship to Each Other:** For example, "the man next to the woman" (spatial relationship), "the first man that enters the frame" (temporal relationship), or "the two cars parked side by side."  

   - **Combining Descriptions:** For maximum clarity, combine multiple attributes.  
     - **Example:**  
       1. "The woman in the red dress on the left, talking on her phone."  
       2. "The dog in the background, running toward the ball."  

3."""
    
    elif task_name == "scene_composition_dynamics":
        return """Provide a concise yet informative description of the overall scene, including the point of view, environment, setting, time of day, and notable visual elements such as overlay elements. If subjects are present, the scene description should complement their descriptions by establishing their location and possible context. Aim to give enough detail to convey the setting while avoiding unnecessary information.

#### 1. Point of View (if relevant)  
1. Indicate how the scene is captured, such as first-person, dashcam, screen recording, drone shot, or an objective or detached view.  
2. Focus on how the perspective influences the viewer's perception of the scene.  

#### 2. Setting (Where does it happen?)  
1. **Scene Type:** Specify whether the setting is indoors or outdoors using precise and descriptive terms. Avoid vague descriptions.  
   - **Good:** "A sunlit café with large windows and wooden tables."  
   - **Avoid:** "An indoor place."  

2. **Visual Attributes:** Provide relevant details about the scene.  
   - **Location:**  
     1. If the setting is a well-known place, state it explicitly (e.g., "Times Square," "Grand Canyon," "Tokyo subway station").  
     2. If the exact location is unclear, describe its defining visual elements, such as:  
        - "A narrow alley with graffiti-covered walls."  
        - "A vast desert with rolling dunes."  
        - "A dimly lit space with metal walls."  
   
   - **Time of Day:** Indicate whether the scene occurs during the day, night, or a transitional period like sunset or dawn.  
   
   - **Architectural and Natural Features:** Mention buildings, roads, vegetation, water bodies, or other landscape elements that structure the scene.  
     - **Examples:**  
       1. "A winding mountain path surrounded by tall pines."  
       2. "A bustling marketplace with food stalls and colorful banners."  
   
   - **Weather Conditions:** If outdoors, describe weather effects.  
     - **Examples:**  
       1. "A rainy street with wet pavement reflecting city lights."  
       2. "A snowy mountain pass covered in thick fog."  
   
   - **Furniture and Props (for indoor scenes):** Identify relevant furnishings that establish the setting.  
     - **Examples:**  
       1. "A wooden desk cluttered with books and a vintage lamp."  
       2. "A hospital room with a bed, medical monitors, and IV stands."  
   
   - **Style:** If notable, describe color schemes or stylistic choices.  
     - **Examples:**  
       1. "A monochromatic, grayscale environment."  
       2. "A vibrant and colorful carnival scene with neon lights."  
  
  - **Overlay:** If overlays are present, describe their apperance and location.
    - **Examples:**
      1. "White sans-serif subtitles reading 'We should leave now' appear at the bottom center of the frame."
      2. "A rectangular minimap HUD with roads and markers is overlaid in the bottom left corner."

#### 3. Movement and Changes in the Environment  
1. Describe any natural or human-made motion within the scene.  

2. **Natural Motion:**  
   - **Examples:**  
     1. "Leaves sway in the wind."  
     2. "Waves crash against the shore."  
     3. "As the sun sets, it casts long shadows on the trees."  

3. **Man-Made Motion:**  
   - **Examples:**  
     1. "Traffic moves steadily on the highway."  
     2. "A train passes in the distance."  
     3. "Factory workers operate machinery in the background."  

4. **Crowd & Background Activity:**  
   - **Examples:**  
     1. "Pedestrians walk along a busy street."  
     2. "A crowd cheers and waves hands."  
     3. "The office starts empty, but employees gradually arrive and take their seats."  

#### 4. Scene Transitions  
1. If the scene changes, describe how it happens in the order it appears.  

2. **Time-Based Transitions:**  
   - **Example:** "The shot begins during the day but transitions to nighttime."  

3. **Movement-Based Transitions:**  
   - **Example:** "The shot begins with a view of a quiet street. Then, the camera pans to reveal a hidden alley behind the main street."  

#### 5. How to Refer to Multiple Scene Elements  
1. Use precise and concise language when referring to different elements within the scene.  
   - **Examples:**  
     1. "In the background, a mountain range is visible."  
     2. "On the left side of the frame, there is a large tree."  
     3. "A wide river runs through the center, with a bridge arching over it."  

2. Prioritize the most prominent and important aspects of the scene.  
3. Start with the overall setting, then move on to more specific details."""
    
    elif task_name == "subject_motion_dynamics":
        return """Provide a concise yet informative description of the subject's motion in this video, including individual actions, subject–object or subject–subject interactions, and group activities when a crowd is present. Please note that event order matters! If multiple actions occur, present them in chronological order (e.g., "The bird first takes flight, then soars in a circle, and finally lands on a branch").

#### 1. Individual Subject Actions  
1. Describe the actions and dynamic changes of individual subjects, ensuring clarity on the manner of movement.
2. **Examples:**  
   - **Good:** "A runner sprints across the finish line."  
     - **Instead of:** "A person is running."  
   - **Good:** "A hummingbird hovers delicately, wings beating rapidly as it sips nectar from a flower."  
     - **Instead of:** "A bird is flying."  
   - **Good:** "A caterpillar slowly inches its way along a leaf."  
     - **Instead of:** "An insect is moving."  
   - **Good:** "A time-lapse shows a sunflower turning its head to follow the sun across the sky."  
     - **Instead of:** "A plant is rotating."  
   - **Good:** "A seed sprouts, sending a root down and a sprout up."  
     - **Instead of:** "A seed is growing."  

#### 2. Subject-Object Interactions
1. Describe the interactions between subjects and objects in the video. Specify the type of interaction and the object involved. If relevant, detail the effect of the interaction.  
2. **Examples:**  
   - **Good:** "A chef flips an omelet in a pan."  
     - **Instead of:** "A person is using a pan."  
   - **Good:** "A dog fetches a tennis ball thrown by its owner."  
     - **Instead of:** "A dog is playing."  
   - **Good:** "A construction worker operates a jackhammer, breaking up the pavement."  
     - **Instead of:** "A person is working."  
   - **Good:** "A car collides with a traffic sign, bending it at a sharp angle."  
     - **Instead of:** "A car crashed."  

#### 3. Subject-Subject Interactions
1. Describe the interactions between different subjects in this video. Describe the nature of the interaction and the relative movements of the subjects.  
2. **Examples:**  
   - **Good:** "Two boxers exchange blows in the ring, circling each other cautiously."  
     - **Instead of:** "People are fighting."  
   - **Good:** "A mother bird feeds worms to her chicks in the nest."  
     - **Instead of:** "Birds are together."  
   - **Good:** "Dancers perform a complex tango, their movements synchronized and graceful."  
     - **Instead of:** "People are dancing."  
   - **Good:** "A pride of lions hunts a zebra, surrounding it and closing in for the kill."  
     - **Instead of:** "Animals are interacting."  

#### 4. Group Activities
1. **Summarize collective behaviors or actions of a group**, describing the overall movement and any coordinated actions. If relevant, specify the type of group.  
2. **Examples:**  
   - **Good:** "A flock of geese flies in a V-formation across the horizon."  
     - **Instead of:** "Birds are flying."  
   - **Good:** "A crowd of protesters marches down the street, carrying signs and banners."  
     - **Instead of:** "People are walking."  
   - **Good:** "A swarm of bees buzzes around a hive."  
     - **Instead of:** "Insects are moving."  
   - **Good:** "A school of fish swims in unison, changing direction as one unit."  
     - **Instead of:** "Fish are swimming."""
    
    elif task_name == "spatial_framing_dynamics":
        return """- **Spatial Positioning:** Specify where key elements appear within the frame.  
     - **Examples:**  
       1. "A symmetrical shot of a hallway positioned at the center of the frame, leading toward a vanishing point."  
       2. "A large tree stands in the bottom-left corner of the frame."  
       3. "A streetlamp is visible on the right side of the frame."  

   - **Depth (Foreground, Midground, and Background Elements):** Describe relationships between elements at different depths.  
     - **Examples:**  
       1. "In the foreground, a bicycle is parked to the right against a fence, while in the background, skyscrapers rise against the sky."  
       2. "The midground features a river cutting through the landscape."  

#### 3. Spatial Motion Within the Frame (How Do Subjects or Scene Elements Move?)  
1. If shot size or spatial position changes within the frame, describe how these transitions happen clearly, specifying both the initial and final state.  

2. **Changes in Shot Size and Spatial Position for Subjects:**  
   - **Examples:**  
     1. "A medium shot of a man's upper body near a doorway transitions into a close-up of his face as he walks toward the camera."  
     2. "A woman walking from the background to the foreground transitions from a wide shot capturing both her and the street scenery to a medium shot focusing on her lower body."  
     3. "A cyclist moves from the left to the right side of the frame, maintaining a full shot throughout."  
     4. "A full-body shot of a child at eye level shifts as the camera tilts upward, reframing them from a low angle looking up."  
     5. "A wide shot captures a person near a park bench, who then walks diagonally from the bottom-left to the top-right corner of the frame."  

3. **Changes in Shot Size and Spatial Composition for Scenery Shots:**  
   - **Examples:**  
     1. "The shot begins with an aerial view of a city skyline, then tilts downward to focus on a busy intersection."  
     2. "The camera moves forward, transitioning from a wide view of a dense forest to a close-up of a single tree trunk covered in moss."  

#### 4. If the Video Contains Multiple Subjects or Complex Subject Transitions  
1. **Determine the Primary Focus:**  
   - If there is a single clear main subject:  
     1. Follow the "Framing of Subjects" section to describe this subject in detail, including shot size and spatial position.  
     2. Follow "Spatial Motion Within the Frame" to describe any spatial motion and changes.  
     3. Provide a less detailed overview of secondary subjects.  

   - If the main subject is unclear:  
     1. Describe subjects' spatial position and movement in prominence-based order (e.g., humans before objects).  
     2. Instead of determining the shot size based on a random subject, specify it based on the most prominent subject (e.g., a human) if one is clearly dominant.  
     3. Otherwise, if the subjects are relatively similar in size, use the average shot size."""
    
    elif task_name == "camera_framing_dynamics":
        return """- Specify which part of the frame is in focus (**Foreground, Midground, Background, Out-of-Focus**).  
   - If the focus changes, describe both the reason for the focus plane transition (e.g., rack/pull focus, focus tracking) and how the focus plane shifts (for example, from the midground to the foreground to focus on a nearby object).

#### 7. Camera Movement  
1. If the camera is completely static, no further description is required.  
2. If the camera is shaking or wobbling, describe the degree.  
   - **Examples:** minimal, moderate, or severe shaking.  
3. If the camera follows or moves with an object, describe how it moves with the subject.  
   - **Examples:** Tracking Shot, Arcing, Craning.  
4. Describe why the camera is moving (e.g., tracking a subject, revealing a scene, creating emphasis).  
5. Use precise movement terms to describe the motion.  
   - **Examples:**  
     1. **Dolly In/Out**: Moving forward or backward toward or away from the subject.  
     2. **Zoom In/Out**: Changing focal length to create the illusion of moving closer or farther.  
     3. **Pan Left/Right**: Rotating the camera horizontally.  
     4. **Truck Left/Right**: Moving the camera laterally left or right.  
     5. **Tilt Up/Down**: Angling the camera up or down.  
     6. **Pedestal Up/Down**: Lifting or lowering the camera while keeping it level.  
     7. **Rolling Clockwise/Counterclockwise**: Rotating the camera around its lens axis.  
     8. **Arcing Clockwise/Counterclockwise**: Circling the camera around a subject or the frame center horizontally.
     9. **Craning Up/Down**: Circling the camera around a subject or the frame center vertically.  
6. Mention the speed of movement if noticeably slow or fast. If different movements occur at different speeds, clearly distinguish them.  
   - **Example:**  
     - "The camera slowly dollies forward while trucking quickly to the right."  
7. Describe motion in temporal order if multiple movements occur.  
   - **Example:**  
     - "The camera first pans right, then tilts upward to follow the subject."  
8. If the movement appears too fragmented or random, avoid excessive detail.  
   - **Excessive Detail (Too much description):**  
     - "As the player explores, the camera moves left, then quickly tilts up, followed by a rapid pan right. The player hesitates, looking down, then abruptly swings the camera left again before slightly tilting upward and making another quick turn to the right."  
   - **Better Description (Concise & clear):**  
     - "The first-person camera moves randomly as the player looks around, frequently changing direction without a clear pattern."""
    
    return ""


def generate_policy_comparison():
    """Generate markdown comparison of all policy versions"""
    
    # Define the policy classes and their corresponding task names
    policy_classes = [
        (SubjectPolicy(), "subject_description", "Subject Description"),
        (ScenePolicy(), "scene_composition_dynamics", "Scene Composition & Dynamics"),
        (SubjectMotionPolicy(), "subject_motion_dynamics", "Subject Motion & Dynamics"),
        (SpatialPolicy(), "spatial_framing_dynamics", "Spatial Framing & Dynamics"),
        (CameraPolicy(), "camera_framing_dynamics", "Camera Framing & Dynamics")
    ]
    
    # Start building the markdown content
    markdown_content = []
    markdown_content.append("# Policy Comparison Report")
    markdown_content.append("")
    markdown_content.append("This document compares four different versions of policies for each of the 5 main policy classes:")
    markdown_content.append("")
    markdown_content.append("1. **human_short**: One sentence summary")
    markdown_content.append("2. **human**: First paragraph of the human-readable policy")
    markdown_content.append("3. **human_detailed**: Full content from the human-readable policy file")
    markdown_content.append("4. **model_without_label**: Output from `get_prompt_without_video_info()` method")
    markdown_content.append("")
    markdown_content.append("---")
    markdown_content.append("")
    
    # Process each policy class
    for policy_instance, task_name, display_name in policy_classes:
        print(f"Processing {display_name}...")
        
        markdown_content.append(f"## {display_name}")
        markdown_content.append("")
        
        # 1. human_short
        human_short = get_one_sentence_summary(task_name)
        markdown_content.append("### 1. human_short")
        markdown_content.append("")
        markdown_content.append("```")
        markdown_content.append(human_short)
        markdown_content.append("```")
        markdown_content.append("")
        
        # Raw text version for copy/paste
        markdown_content.append("<details>")
        markdown_content.append("<summary>📋 Raw text for copy/paste</summary>")
        markdown_content.append("")
        markdown_content.append("```text")
        markdown_content.append(human_short)
        markdown_content.append("```")
        markdown_content.append("")
        markdown_content.append("</details>")
        markdown_content.append("")
        
        # 2. human (first paragraph)
        human_detailed = get_human_detailed_content(task_name)
        human_first_paragraph = get_first_paragraph(human_detailed)
        
        markdown_content.append("### 2. human")
        markdown_content.append("")
        markdown_content.append("```")
        markdown_content.append(human_first_paragraph)
        markdown_content.append("```")
        markdown_content.append("")
        
        # Raw text version for copy/paste
        markdown_content.append("<details>")
        markdown_content.append("<summary>📋 Raw text for copy/paste</summary>")
        markdown_content.append("")
        markdown_content.append("```text")
        markdown_content.append(human_first_paragraph)
        markdown_content.append("```")
        markdown_content.append("")
        markdown_content.append("</details>")
        markdown_content.append("")
        
        # 3. human_detailed
        markdown_content.append("### 3. human_detailed")
        markdown_content.append("")
        markdown_content.append("```")
        markdown_content.append(human_detailed)
        markdown_content.append("```")
        markdown_content.append("")
        
        # Raw text version for copy/paste
        markdown_content.append("<details>")
        markdown_content.append("<summary>📋 Raw text for copy/paste</summary>")
        markdown_content.append("")
        markdown_content.append("```text")
        markdown_content.append(human_detailed)
        markdown_content.append("```")
        markdown_content.append("")
        markdown_content.append("</details>")
        markdown_content.append("")
        
        # 4. model_without_label
        try:
            method_output = policy_instance.get_prompt_without_video_info()
            markdown_content.append("### 4. model_without_label")
            markdown_content.append("")
            markdown_content.append("```")
            markdown_content.append(method_output)
            markdown_content.append("```")
            markdown_content.append("")
            
            # Raw text version for copy/paste
            markdown_content.append("<details>")
            markdown_content.append("<summary>📋 Raw text for copy/paste</summary>")
            markdown_content.append("")
            markdown_content.append("```text")
            markdown_content.append(method_output)
            markdown_content.append("```")
            markdown_content.append("")
            markdown_content.append("</details>")
            markdown_content.append("")
            
        except Exception as e:
            markdown_content.append("### 4. model_without_label")
            markdown_content.append("")
            markdown_content.append(f"**Error**: Could not retrieve method output: {e}")
            markdown_content.append("")
        
        markdown_content.append("---")
        markdown_content.append("")
    
    # Add footer
    markdown_content.append("## Summary")
    markdown_content.append("")
    markdown_content.append("This comparison was generated automatically to help understand the different ")
    markdown_content.append("versions of policy text used throughout the system.")
    markdown_content.append("")
    markdown_content.append(f"**Generated on**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    markdown_content.append("")
    
    return '\n'.join(markdown_content)


def main():
    parser = argparse.ArgumentParser(description="Generate policy comparison markdown")
    parser.add_argument(
        "--output", 
        type=str, 
        default="policy_comparison.md",
        help="Output markdown file path (default: policy_comparison.md)"
    )
    
    args = parser.parse_args()
    
    print("Generating policy comparison...")
    print(f"Project root: {project_root}")
    
    try:
        markdown_content = generate_policy_comparison()
        
        # Write to file
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"✅ Policy comparison generated successfully!")
        print(f"📄 Output saved to: {output_path.resolve()}")
        
    except Exception as e:
        print(f"❌ Error generating policy comparison: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()