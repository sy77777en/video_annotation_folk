from benchmark import ROOT, VIDEO_ROOT, VIDEO_LABELS_DIR, VIDEO_LABEL_FILE, labels_as_dict
from pathlib import Path
import random
import json
from collections import defaultdict
from torch.utils.data import Dataset

# SAMPLING = "random"
SAMPLING = "top"
MAX_SAMPLES = 100
# MAX_SAMPLES = 300
# MAX_SAMPLES = 50
SEED = 0
TRAIN_RATIO = 0.5

def get_pairwise_scores(scores_matrix):
    """
    Convert a matrix of scores into a list of dictionaries with labeled scores.
    
    Args:
        scores_matrix: A 3D numpy array [num_sample, 2, 2]
        
    Returns:
        List of dictionaries, each containing labeled similarity scores
    """
    num_samples = scores_matrix.shape[0]
    pairwise_scores = []
    
    for idx in range(num_samples):
        pairwise_scores.append({
            "id": idx,
            "pos_text_pos_image": scores_matrix[idx][0][0],  # t0_i0
            "pos_text_neg_image": scores_matrix[idx][1][0],  # t0_i1
            "neg_text_pos_image": scores_matrix[idx][0][1],  # t1_i0
            "neg_text_neg_image": scores_matrix[idx][1][1]   # t1_i1
        })
    
    return pairwise_scores

def get_retrieval_scores(scores):
    """
    Calculate retrieval performance metrics.
    
    Args:
        scores: List of dictionaries with pairwise scores
        
    Returns:
        Dictionary containing text, image, and group retrieval accuracy
    """
    text_correct_count = 0 # Text Score measures video-to-text retrieval performance
    image_correct_count = 0 # Image Score measures video-to-image retrieval performance
    group_correct_count = 0 # Group Score measures overall retrieval performance
    def text_correct(result):
        """Check if text retrieval is correct for this sample."""
        return (result["pos_text_pos_image"] > result["neg_text_pos_image"] and 
                result["neg_text_neg_image"] > result["pos_text_neg_image"])

    def image_correct(result):
        """Check if image retrieval is correct for this sample."""
        return (result["pos_text_pos_image"] > result["pos_text_neg_image"] and 
                result["neg_text_neg_image"] > result["neg_text_pos_image"])

    def group_correct(result):
        """Check if both text and image retrieval are correct."""
        return image_correct(result) and text_correct(result)
    
    for result in scores:
        text_correct_count += 1 if text_correct(result) else 0
        image_correct_count += 1 if image_correct(result) else 0
        group_correct_count += 1 if group_correct(result) else 0

    denominator = max(1, len(scores))  # Avoid division by zero
    result = {
        'text': text_correct_count / denominator,
        'image': image_correct_count / denominator,
        'group': group_correct_count / denominator,
    }
    return result

def get_vqa_scores(yes_scores, no_scores):
    """
    Calculate Visual Question Answering (VQA) performance metrics.
    
    Args:
        yes_scores: List of dictionaries with pairwise scores for 'yes' answers
        no_scores: List of dictionaries with pairwise scores for 'no' answers
        
    Returns:
        Dictionary containing various VQA accuracy metrics
    """
    # Initialize counters for different metrics
    metrics = {
        'binary_acc': 0.0,              # Binary accuracy (random chance: 0.5)
        'pos_binary_acc': 0.0,          # Binary accuracy for positive questions only (random chance: 0.5)
        'neg_binary_acc': 0.0,          # Binary accuracy for negative questions only (random chance: 0.5)
        'question_acc': 0.0,            # Question accuracy (random chance: 0.25)
        'pos_question_acc': 0.0,        # Question accuracy for positive questions only (random chance: 0.25)
        'neg_question_acc': 0.0,        # Question accuracy for negative questions only (random chance: 0.25)
        'image_acc': 0.0,               # Image accuracy (random chance: 0.25)
        'group_acc': 0.0                # Group accuracy (random chance: 0.125)
    }
    
    # Helper functions to check correctness for each combination
    def pos_text_pos_image_correct(yes_result, no_result):
        """Positive Text, Positive Image: 'yes' should score higher than 'no'"""
        return yes_result["pos_text_pos_image"] > no_result["pos_text_pos_image"]
    
    def pos_text_neg_image_correct(yes_result, no_result):
        """Positive Text, Negative Image: 'no' should score higher than 'yes'"""
        return no_result["pos_text_neg_image"] > yes_result["pos_text_neg_image"]
    
    def neg_text_pos_image_correct(yes_result, no_result):
        """Negative Text, Positive Image: 'no' should score higher than 'yes'"""
        return no_result["neg_text_pos_image"] > yes_result["neg_text_pos_image"]
    
    def neg_text_neg_image_correct(yes_result, no_result):
        """Negative Text, Negative Image: 'yes' should score higher than 'no'"""
        return yes_result["neg_text_neg_image"] > no_result["neg_text_neg_image"]
    
    def pos_binary_acc_correct(yes_result, no_result):
        """Binary accuracy for positive questions"""
        count = 0.0
        count += 1.0 if pos_text_pos_image_correct(yes_result, no_result) else 0.0
        count += 1.0 if pos_text_neg_image_correct(yes_result, no_result) else 0.0
        return count
    
    def neg_binary_acc_correct(yes_result, no_result):
        """Binary accuracy for negative questions"""
        count = 0.0
        count += 1.0 if neg_text_pos_image_correct(yes_result, no_result) else 0.0
        count += 1.0 if neg_text_neg_image_correct(yes_result, no_result) else 0.0
        return count
    
    def binary_acc_correct(yes_result, no_result):
        """Overall binary accuracy"""
        return pos_binary_acc_correct(yes_result, no_result) + neg_binary_acc_correct(yes_result, no_result)
    
    def pos_question_acc_correct(yes_result, no_result):
        """Question accuracy for positive questions (both images correct)"""
        return 1.0 if (pos_text_pos_image_correct(yes_result, no_result) and 
                       pos_text_neg_image_correct(yes_result, no_result)) else 0.0
    
    def neg_question_acc_correct(yes_result, no_result):
        """Question accuracy for negative questions (both images correct)"""
        return 1.0 if (neg_text_pos_image_correct(yes_result, no_result) and 
                       neg_text_neg_image_correct(yes_result, no_result)) else 0.0
    
    def question_acc_correct(yes_result, no_result):
        """Overall question accuracy"""
        return pos_question_acc_correct(yes_result, no_result) + neg_question_acc_correct(yes_result, no_result)
    
    def image_acc_correct(yes_result, no_result):
        """Image accuracy (both questions correct for same image)"""
        count = 0.0
        count += 1.0 if (pos_text_pos_image_correct(yes_result, no_result) and 
                          neg_text_pos_image_correct(yes_result, no_result)) else 0.0
        count += 1.0 if (pos_text_neg_image_correct(yes_result, no_result) and 
                          neg_text_neg_image_correct(yes_result, no_result)) else 0.0
        return count
    
    def group_acc_correct(yes_result, no_result):
        """Group accuracy (all combinations correct)"""
        if (pos_text_pos_image_correct(yes_result, no_result) and 
            pos_text_neg_image_correct(yes_result, no_result) and 
            neg_text_pos_image_correct(yes_result, no_result) and 
            neg_text_neg_image_correct(yes_result, no_result)):
            return 1.0
        return 0.0

    # Calculate metrics for each pair of results
    for yes_result, no_result in zip(yes_scores, no_scores):
        metrics['binary_acc'] += binary_acc_correct(yes_result, no_result)
        metrics['pos_binary_acc'] += pos_binary_acc_correct(yes_result, no_result)
        metrics['neg_binary_acc'] += neg_binary_acc_correct(yes_result, no_result)
        metrics['question_acc'] += question_acc_correct(yes_result, no_result)
        metrics['pos_question_acc'] += pos_question_acc_correct(yes_result, no_result)
        metrics['neg_question_acc'] += neg_question_acc_correct(yes_result, no_result)
        metrics['image_acc'] += image_acc_correct(yes_result, no_result)
        metrics['group_acc'] += group_acc_correct(yes_result, no_result)
    
    # Define denominators for each metric
    sample_count = len(yes_scores)
    denominators = {
        'binary_acc': sample_count * 4.0,
        'pos_binary_acc': sample_count * 2.0,
        'neg_binary_acc': sample_count * 2.0,
        'question_acc': sample_count * 2.0,
        'pos_question_acc': sample_count,
        'neg_question_acc': sample_count,
        'image_acc': sample_count * 2.0,
        'group_acc': sample_count
    }
    
    # Calculate final scores
    result = {key: value / denominators[key] for key, value in metrics.items()}
    return result

    
class PairwiseBenchmark(Dataset):
    """
    Dataset class for pairwise comparison tasks (VQA or retrieval).
    
    Args:
        skills: List of skills, where each skill contains multiple tasks
        mode: Task mode, one of "vqa", "vqa_generation", or "retrieval"
    """
    def __init__(self, skills, mode="vqa"):
        valid_modes = ["vqa", "vqa_generation", "retrieval"]
        if mode not in valid_modes:
            raise ValueError(f"Mode must be one of {valid_modes}, got {mode}")
        
        self.mode = mode
        self.skills = []
        self.tasks = []
        self.skill_to_sample_ids = {}
        self.skill_to_tasks = {}
        self.task_to_sample_ids = {}
        self.samples = []
        self.task_to_metadata = {}
        
        for skill in skills:
            self.skills.append(skill)
            self.skill_to_tasks[skill] = []
            self.skill_to_sample_ids[skill] = []
            
            for task in skills[skill]:
                self.skill_to_tasks[skill].append(task)
                self.tasks.append(task)
                self.task_to_sample_ids[task] = []
                
                pos_videos = skills[skill][task]['pos']
                neg_videos = skills[skill][task]['neg']
                
                pos_prompt = skills[skill][task]['task_dict']['pos_prompt']
                neg_prompt = skills[skill][task]['task_dict']['neg_prompt']
                pos_question = skills[skill][task]['task_dict']['pos_question']
                neg_question = skills[skill][task]['task_dict']['neg_question']
                
                self.task_to_metadata[task] = {
                    "skill": skill,
                    "pos_prompt": pos_prompt,
                    "neg_prompt": neg_prompt,
                    "pos_question": pos_question,
                    "neg_question": neg_question
                }
                
                assert len(pos_videos) == len(neg_videos), f"Number of positive and negative videos must match for task {task}"
                
                for pos_video, neg_video in zip(pos_videos, neg_videos):
                    sample_id = len(self.samples)
                    self.skill_to_sample_ids[skill].append(sample_id)
                    self.task_to_sample_ids[task].append(sample_id)
                    
                    # Important to make 0th the Positive Image and 1st the Negative Image
                    images = [pos_video, neg_video]
                    if self.mode in ["vqa", "vqa_generation"]:
                        texts = [pos_question, neg_question]
                    elif self.mode == "retrieval":
                        texts = [pos_prompt, neg_prompt]
                    
                    self.samples.append({
                        "images": images,
                        "texts": texts
                    })
    
    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        return self.samples[idx]
    
    def evaluate_retrieval_scores(self, scores):
        """
        Evaluate retrieval scores across all skills and tasks.
        
        Args:
            scores: Scores matrix from the model
            
        Returns:
            Dictionary with evaluation results
        """
        pairwise_scores = get_pairwise_scores(scores)
        acc = get_retrieval_scores(pairwise_scores)
        
        results = {
            'overall': acc,
            'skills': {}
        }
        
        for skill in self.skills:
            skill_pairwise_scores = [pairwise_scores[i] for i in self.skill_to_sample_ids[skill]]
            skill_acc = get_retrieval_scores(skill_pairwise_scores)
            
            results['skills'][skill] = {
                'overall': skill_acc,
                'tasks': {}
            }
            
            for task in self.skill_to_tasks[skill]:
                task_pairwise_scores = [pairwise_scores[i] for i in self.task_to_sample_ids[task]]
                task_acc = get_retrieval_scores(task_pairwise_scores)
                results['skills'][skill]['tasks'][task] = task_acc
        
        return results
    
    def evaluate_vqa_scores(self, yes_scores, no_scores):
        """
        Evaluate VQA scores across all skills and tasks.
        
        Args:
            yes_scores: Scores matrix for 'yes' answers
            no_scores: Scores matrix for 'no' answers
            
        Returns:
            Dictionary with evaluation results
        """
        yes_pairwise_scores = get_pairwise_scores(yes_scores)
        no_pairwise_scores = get_pairwise_scores(no_scores)
        
        acc = get_vqa_scores(yes_pairwise_scores, no_pairwise_scores)
        
        results = {
            'overall': acc,
            'skills': {}
        }
        
        for skill in self.skills:
            skill_yes_scores = [yes_pairwise_scores[i] for i in self.skill_to_sample_ids[skill]]
            skill_no_scores = [no_pairwise_scores[i] for i in self.skill_to_sample_ids[skill]]
            skill_acc = get_vqa_scores(skill_yes_scores, skill_no_scores)
            
            results['skills'][skill] = {
                'overall': skill_acc,
                'tasks': {}
            }
            
            for task in self.skill_to_tasks[skill]:
                task_yes_scores = [yes_pairwise_scores[i] for i in self.task_to_sample_ids[task]]
                task_no_scores = [no_pairwise_scores[i] for i in self.task_to_sample_ids[task]]
                task_acc = get_vqa_scores(task_yes_scores, task_no_scores)
                results['skills'][skill]['tasks'][task] = task_acc
        
        return results
    
    def format_retrieval_results(self, results, name_width=70):
        """
        Format retrieval evaluation results as a string.
        Shows overall and skill summaries first, followed by detailed task breakdown.
        
        Args:
            results: Results dictionary from evaluate_retrieval_scores
            name_width: Width for the dataset/skill/task name column (default: 50)
            
        Returns:
            Formatted string with evaluation results
        """
        output = []
        
        # Define column widths
        metric_width = 10
        metrics = ['text', 'image', 'group']
        total_width = name_width + (len(metrics) * (metric_width + 1))
        
        # Create header
        header = f"{'Dataset':{name_width}s}"
        for metric in metrics:
            header += f" {metric.capitalize():{metric_width}s}"
        separator = "-" * total_width
        
        # Part 1: Summary section
        output.append("\n====== Retrieval Performance Summary ======")
        output.append(header)
        output.append(separator)
        
        # Format overall results
        overall = results['overall']
        output.append(f"{'Overall':{name_width}s} {overall['text']:{metric_width}.2%} {overall['image']:{metric_width}.2%} {overall['group']:{metric_width}.2%}")
        
        # Format skill summaries
        for skill, skill_data in results['skills'].items():
            skill_acc = skill_data['overall']
            
            # Truncate skill name if too long
            skill_name = skill
            if len(skill_name) > name_width:
                skill_name = skill_name[:name_width-3] + "..."
                
            output.append(f"{skill_name:{name_width}s} {skill_acc['text']:{metric_width}.2%} {skill_acc['image']:{metric_width}.2%} {skill_acc['group']:{metric_width}.2%}")
        
        # Part 2: Detailed section
        output.append("\n====== Retrieval Performance Details by Task ======")
        output.append(header)
        output.append(separator)
        
        # Format task details grouped by skill
        for skill, skill_data in results['skills'].items():
            # Format skill header
            skill_acc = skill_data['overall']
            
            # Truncate skill name if too long
            skill_name = skill
            if len(skill_name) > name_width:
                skill_name = skill_name[:name_width-3] + "..."
                
            output.append(f"{skill_name:{name_width}s} {skill_acc['text']:{metric_width}.2%} {skill_acc['image']:{metric_width}.2%} {skill_acc['group']:{metric_width}.2%}")
            
            # Format tasks for this skill
            for task, task_acc in skill_data['tasks'].items():
                task_name = f"  - {task}"
                
                # Truncate task name if too long
                if len(task_name) > name_width:
                    task_name = task_name[:name_width-3] + "..."
                    
                output.append(f"{task_name:{name_width}s} {task_acc['text']:{metric_width}.2%} {task_acc['image']:{metric_width}.2%} {task_acc['group']:{metric_width}.2%}")
            
            output.append("")  # Add empty line between skills
        
        return "\n".join(output)


    def format_vqa_results(self, results, name_width=70):
        """
        Format VQA evaluation results as a string.
        Shows overall and skill summaries first, followed by detailed task breakdown.
        
        Args:
            results: Results dictionary from evaluate_vqa_scores
            name_width: Width for the dataset/skill/task name column (default: 70)
            
        Returns:
            Formatted string with evaluation results
        """
        output = []
        
        # All VQA metrics with short display names
        metrics = [
            'binary_acc', 'pos_binary_acc', 'neg_binary_acc', 
            'question_acc', 'pos_question_acc', 'neg_question_acc', 
            'image_acc', 'group_acc'
        ]
        
        # Display names for metrics (shorter for better table layout)
        display_names = {
            'binary_acc': 'acc',
            'pos_binary_acc': 'pos_a',
            'neg_binary_acc': 'neg_a',
            'question_acc': 'q_acc',
            'pos_question_acc': 'pos_q',
            'neg_question_acc': 'neg_q',
            'image_acc': 'i_acc',
            'group_acc': 'g_acc'
        }
        
        # Column width for metric values
        metric_width = 8
        total_width = name_width + (len(metrics) * (metric_width + 1))
        
        # Create header row
        header = f"{'Dataset':{name_width}s}"
        for metric in metrics:
            header += f" {display_names[metric]:{metric_width}s}"
        
        # Create separator line
        separator = "-" * total_width
        
        # PART 1: Summary of overall and skills
        output.append("\n====== VQA Performance Summary ======")
        output.append(header)
        output.append(separator)
        
        # Format overall results
        overall = results['overall']
        overall_row = f"{'Overall':{name_width}s}"
        for metric in metrics:
            overall_row += f" {overall[metric]:{metric_width}.2%}"
        output.append(overall_row)
        
        # Format skill summaries
        for skill, skill_data in results['skills'].items():
            skill_acc = skill_data['overall']
            
            # Truncate skill name if too long
            skill_name = skill
            if len(skill_name) > name_width:
                skill_name = skill_name[:name_width-3] + "..."
                
            skill_row = f"{skill_name:{name_width}s}"
            for metric in metrics:
                skill_row += f" {skill_acc[metric]:{metric_width}.2%}"
            output.append(skill_row)
        
        # PART 2: Detailed breakdown by task
        output.append("\n====== VQA Performance Details by Task ======")
        output.append(header)
        output.append(separator)
        
        # Format task details grouped by skill
        for skill, skill_data in results['skills'].items():
            # Format skill header
            skill_acc = skill_data['overall']
            
            # Truncate skill name if too long
            skill_name = skill
            if len(skill_name) > name_width:
                skill_name = skill_name[:name_width-3] + "..."
                
            skill_row = f"{skill_name:{name_width}s}"
            for metric in metrics:
                skill_row += f" {skill_acc[metric]:{metric_width}.2%}"
            output.append(skill_row)
            
            # Format tasks for this skill
            for task, task_acc in skill_data['tasks'].items():
                task_name = f"  - {task}"
                
                # Truncate task name if too long
                if len(task_name) > name_width:
                    task_name = task_name[:name_width-3] + "..."
                    
                task_row = f"{task_name:{name_width}s}"
                for metric in metrics:
                    task_row += f" {task_acc[metric]:{metric_width}.2%}"
                output.append(task_row)
            
            output.append("")  # Add empty line between skills
        
        return "\n".join(output)


    def format_vqa_generation_results(self, results, name_width=70):
        """
        Format VQA generation evaluation results as a string.
        Shows overall and skill summaries first, followed by detailed task breakdown.
        
        Args:
            results: Results dictionary from evaluate_vqa_generation_scores
            name_width: Width for the dataset/skill/task name column (default: 70)
            
        Returns:
            Formatted string with evaluation results
        """
        # This function uses the same structure as format_vqa_results
        # since the metrics structure is identical
        return self.format_vqa_results(results, name_width)


    # Wrapper functions that print the formatted results
    def print_retrieval_results(self, results, name_width=50):
        """
        Print retrieval evaluation results.
        
        Args:
            results: Results dictionary from evaluate_retrieval_scores
            name_width: Width for the dataset/skill/task name column (default: 50)
        """
        print(self.format_retrieval_results(results, name_width))


    def print_vqa_results(self, results, name_width=70):
        """
        Print VQA evaluation results.
        
        Args:
            results: Results dictionary from evaluate_vqa_scores
            name_width: Width for the dataset/skill/task name column (default: 70)
        """
        print(self.format_vqa_results(results, name_width))


    def evaluate_and_print_retrieval(self, scores, name_width=50):
        """
        Evaluate retrieval scores and print the results.
        
        Args:
            scores: Scores matrix from the model
            name_width: Width for the dataset/skill/task name column (default: 50)
            
        Returns:
            Dictionary with evaluation results
            String with formatted evaluation results
        """
        results = self.evaluate_retrieval_scores(scores)
        results_str = self.format_retrieval_results(results, name_width)
        print(results_str)
        return results, results_str


    def evaluate_and_print_vqa(self, yes_scores, no_scores, name_width=70):
        """
        Evaluate VQA scores and print the results.
        
        Args:
            yes_scores: Scores matrix for 'yes' answers
            no_scores: Scores matrix for 'no' answers
            name_width: Width for the dataset/skill/task name column (default: 70)
            
        Returns:
            Dictionary with evaluation results
            String with formatted evaluation results
        """
        results = self.evaluate_vqa_scores(yes_scores, no_scores)
        results_str = self.format_vqa_results(results, name_width)
        print(results_str)
        return results, results_str


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
        "name": "roll_cc_vs_roll_ccw",
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
        "name": "arc_ccw_vs_arc_cc",
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
        "pos_question": "Does the camera move in a counterclockwise arc?",
        "neg_question": "Is the camera free from any counterclockwise arc movement?",
        "pos_prompt": "The camera moves in a counterclockwise arc.",
        "neg_prompt": "The camera is free from any counterclockwise arc movement.",
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
        "pos_question": "Does the camera crane upward in an arc?",
        "neg_question": "Is the camera not craning upward in an arc?",
        "pos_prompt": "The camera cranes upward in an arc.",
        "neg_prompt": "The camera is not craning upward in an arc.",
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
        "pos_question": "Does the camera crane downward in an arc?",
        "neg_question": "Is the camera not craning downward in an arc?",
        "pos_prompt": "The camera cranes downward in an arc.",
        "neg_prompt": "The camera is not craning downward in an arc.",
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

special_tracking_tasks = [
    {
        "folder": "cam_motion-20250227_0324ground_only",
        "name": "has_aerial_tracking",
        "pos_question": "Does the camera track the subject from an aerial perspective?",
        "neg_question": "Is the video not a tracking shot from an aerial perspective?",
        "pos_prompt": "The camera tracks the subject from an aerial perspective.",
        "neg_prompt": "The camera is not tracking the subject from an aerial perspective.",
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
        "pos_question": "Does the camera follow the subject while moving in an arc?",
        "neg_question": "Is the video not a tracking shot with arc movement?",
        "pos_prompt": "A tracking shot where the camera follows the subject while moving in an arc.",
        "neg_prompt": "A video where the camera is not tracking the subject with arc movement.",
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
        "pos_question": "Is it a tracking shot with the camera leading from the front and to the side of the subject?",
        "neg_question": "Is the video not a tracking shot with the camera leading from the front and to the side of the subject?",
        "pos_prompt": "A tracking shot where the camera leads from the front and to the side of the subject.",
        "neg_prompt": "The camera is not leading from the front and to the side of the subject.",
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
        "pos_question": "Is it a tracking shot with the camera following behind and to the side of the subject?",
        "neg_question": "Is the video not a tracking shot with the camera following behind and to the side of the subject?",
        "pos_prompt": "A tracking shot where the camera follows behind and to the side of the subject.",
        "neg_prompt": "The camera is not following behind and to the side of the subject.",
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
        "pos_question": "Is it a tracking shot with the camera moving ahead of the subject as they move?",
        "neg_question": "Is the camera not moving ahead of the subject in a tracking shot?",
        "pos_prompt": "A tracking shot where the camera moves ahead of the subjects as they move.",
        "neg_prompt": "The camera is not moving ahead of the subject in a tracking shot.",
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
        "name": "has_tail_tracking",
        "pos_question": "Is it a tracking shot with the camera following behind the subject as they move?",
        "neg_question": "Is the camera not following behind the subject in a tracking shot?",
        "pos_prompt": "A tracking shot where the camera moves behind the subjects as they move.",
        "neg_prompt": "The camera is not following behind the subject in a tracking shot.",
        "pos": {
            "label": "cam_motion.object_centric_movement.tail_tracking_shot",
            "type": "pos"
        },
        "neg": {
            "label": "cam_motion.object_centric_movement.tail_tracking_shot",
            "type": "neg"
        }
    },
    {
        "folder": "cam_motion-20250227_0324ground_only",
        "name": "has_tilt_tracking",
        "pos_question": "Does the camera tilt to track the subjects as they move?",
        "neg_question": "Is the camera not tilting to track the subjects?",
        "pos_prompt": "A tracking shot where the camera tilts to follow the subjects.",
        "neg_prompt": "The camera is not tilting to track the subjects.",
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
        "pos_question": "Does the camera pan to track the subjects as they move?",
        "neg_question": "Is the camera not panning to track the subjects?",
        "pos_prompt": "A tracking shot where the camera pans to follow the subjects as they move.",
        "neg_prompt": "The camera is not panning to track the subjects.",
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
        "pos_question": "Is it a tracking shot with the camera moving from the side to follow the subject as they move?",
        "neg_question": "Is the camera not moving from the side to track the subject?",
        "pos_prompt": "A tracking shot where the camera moves from the side to follow the subject.",
        "neg_prompt": "The camera is not moving from the side to track the subject.",
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

general_tracking_tasks = [
    {
        "folder": "cam_motion-20250227_0324ground_only",
        "name": "is_tracking",
        "pos_question": "Does the camera track the subject as they move?",
        "neg_question": "Is the video not a tracking shot?",
        "pos_prompt": "The camera tracks the subject as they move.",
        "neg_prompt": "The video is not a tracking shot.",
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
        "pos_question": "Does the subject appear larger during the tracking shot?",
        "neg_question": "Does the subject being tracked not appear larger in size?",
        "pos_prompt": "The subject looks larger during the tracking shot.",
        "neg_prompt": "The subject being tracked does not appear larger in size.",
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
        "pos_question": "Does the subject appear smaller during the tracking shot?",
        "neg_question": "Does the subject being tracked not appear smaller in size?",
        "pos_prompt": "The subject looks smaller during the tracking shot.",
        "neg_prompt": "The subject being tracked does not appear smaller in size.",
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

only_intrinsic_change_tasks = [
    {
        "folder": "cam_motion-20250227_0324ground_only",
        "name": "only_zoom_in_vs_has_zoom_in_and_not_only",
        "pos_question": "Does the camera only zoom in with no other movement?",
        "neg_question": "Does the camera zoom in along with other types of movement?",
        "pos_prompt": "The camera only zooms in without any other movement.",
        "neg_prompt": "The camera zooms in along with other types of movement.",
        "pos": {
            "label": "cam_motion.camera_centric_movement.zoom_in.only_zoom_in",
            "type": "pos"
        },
        "neg": [
            {
                "label": "cam_motion.camera_centric_movement.zoom_in.has_zoom_in",
                "type": "pos"
            },
            {
                "label": "cam_motion.camera_centric_movement.zoom_in.only_zoom_in",
                "type": "neg"
            }
        ]
    },
    {
        "folder": "cam_motion-20250227_0324ground_only",
        "name": "only_zoom_out_vs_has_zoom_out_and_not_only",
        "pos_question": "Does the camera only zoom out with no other movement?",
        "neg_question": "Does the camera zoom out along with other types of movement?",
        "pos_prompt": "The camera only zooms out with no other movement.",
        "neg_prompt": "The camera zooms out along with other types of movement.",
        "pos": {
            "label": "cam_motion.camera_centric_movement.zoom_out.only_zoom_out",
            "type": "pos"
        },
        "neg": [
            {
                "label": "cam_motion.camera_centric_movement.zoom_out.has_zoom_out",
                "type": "pos"
            },
            {
                "label": "cam_motion.camera_centric_movement.zoom_out.only_zoom_out",
                "type": "neg"
            }
        ]
    }
]

only_translation_tasks = [
    {
        "folder": "cam_motion-cam_setup-20250227_0507ground_and_setup",
        "name": "only_forward_vs_has_forward_and_not_only",
        "pos_question": "Does the camera only move forward (not zooming in) with respect to the ground?",
        "neg_question": "Does the camera move forward with respect to the ground along with other types of movement?",
        "pos_prompt": "The camera only moves forward (not zooming in) relative to the ground.",
        "neg_prompt": "The camera moves forward relative to the ground along with other types of movement.",
        "pos": {
            "label": "cam_motion.ground_centric_movement.forward.only_forward_wrt_ground",
            "type": "pos"
        },
        "neg": [
            {
                "label": "cam_motion.ground_centric_movement.forward.has_forward_wrt_ground",
                "type": "pos"
            },
            {
                "label": "cam_motion.ground_centric_movement.forward.only_forward_wrt_ground",
                "type": "neg"
            }
        ]
    },
    {
        "folder": "cam_motion-cam_setup-20250227_0507ground_and_setup",
        "name": "only_backward_vs_has_backward_and_not_only",
        "pos_question": "Does the camera only move backward (not zooming out) with respect to the ground?",
        "neg_question": "Does the camera move backward with respect to the ground along with other types of movement?",
        "pos_prompt": "The camera only moves backward (not zooming out) relative to the ground.",
        "neg_prompt": "The camera moves backward relative to the ground along with other types of movement.",
        "pos": {
            "label": "cam_motion.ground_centric_movement.backward.only_backward_wrt_ground",
            "type": "pos"
        },
        "neg": [
            {
                "label": "cam_motion.ground_centric_movement.backward.has_backward_wrt_ground",
                "type": "pos"
            },
            {
                "label": "cam_motion.ground_centric_movement.backward.only_backward_wrt_ground",
                "type": "neg"
            }
        ]
    },
    {
        "folder": "cam_motion-20250227_0324ground_only",
        "name": "only_truck_left_vs_has_truck_left_and_not_only",
        "pos_question": "Does the camera only move leftward without any other camera movements?",
        "neg_question": "Does the camera move laterally to the left along with other types of movement?",
        "pos_prompt": "The camera only moves leftward without any other camera movements.",
        "neg_prompt": "The camera moves laterally to the left along with other types of movement.",
        "pos": {
            "label": "cam_motion.camera_centric_movement.leftward.only_leftward",
            "type": "pos"
        },
        "neg": [
            {
                "label": "cam_motion.camera_centric_movement.leftward.has_leftward",
                "type": "pos"
            },
            {
                "label": "cam_motion.camera_centric_movement.leftward.only_leftward",
                "type": "neg"
            }
        ]
    },
    {
        "folder": "cam_motion-20250227_0324ground_only",
        "name": "only_truck_right_vs_has_truck_right_and_not_only",
        "pos_question": "Does the camera only move rightward without any other camera movements?",
        "neg_question": "Does the camera move laterally to the right along with other types of movement?",
        "pos_prompt": "The camera only moves rightward without any other camera movements.",
        "neg_prompt": "The camera moves laterally to the right along with other types of movement.",
        "pos": {
            "label": "cam_motion.camera_centric_movement.rightward.only_rightward",
            "type": "pos"
        },
        "neg": [
            {
                "label": "cam_motion.camera_centric_movement.rightward.has_rightward",
                "type": "pos"
            },
            {
                "label": "cam_motion.camera_centric_movement.rightward.only_rightward",
                "type": "neg"
            }
        ]
    },
    {
        "folder": "cam_motion-cam_setup-20250227_0507ground_and_setup",
        "name": "only_pedestal_up_vs_has_pedestal_up_and_not_only",
        "pos_question": "Does the camera only move upward (not tilting up) with respect to the ground?",
        "neg_question": "Does the camera move physically upward along with other types of movement?",
        "pos_prompt": "The camera only moves upward (not tilting up) relative to the ground.",
        "neg_prompt": "The camera moves physically upward along with other types of movement.",
        "pos": {
            "label": "cam_motion.ground_centric_movement.upward.only_upward_wrt_ground",
            "type": "pos"
        },
        "neg": [
            {
                "label": "cam_motion.ground_centric_movement.upward.has_upward_wrt_ground",
                "type": "pos"
            },
            {
                "label": "cam_motion.ground_centric_movement.upward.only_upward_wrt_ground",
                "type": "neg"
            }
        ]
    },
    {
        "folder": "cam_motion-cam_setup-20250227_0507ground_and_setup",
        "name": "only_pedestal_down_vs_has_pedestal_down_and_not_only",
        "pos_question": "Does the camera only move downward (not tilting down) with respect to the ground?",
        "neg_question": "Does the camera move physically downward along with other types of movement?",
        "pos_prompt": "The camera only moves downward (not tilting down) relative to the ground.",
        "neg_prompt": "The camera moves physically downward along with other types of movement.",
        "pos": {
            "label": "cam_motion.ground_centric_movement.downward.only_downward_wrt_ground",
            "type": "pos"
        },
        "neg": [
            {
                "label": "cam_motion.ground_centric_movement.downward.has_downward_wrt_ground",
                "type": "pos"
            },
            {
                "label": "cam_motion.ground_centric_movement.downward.only_downward_wrt_ground",
                "type": "neg"
            }
        ]
    }
]

only_rotation_tasks = [
    {
        "folder": "cam_motion-20250227_0324ground_only",
        "name": "only_pan_left_vs_has_pan_left_and_not_only",
        "pos_question": "Does the camera only pan leftward without any other camera movements?",
        "neg_question": "Does the camera pan left along with other types of movement?",
        "pos_prompt": "The camera only pans leftward without any other camera movements.",
        "neg_prompt": "The camera pans left along with other types of movement.",
        "pos": {
            "label": "cam_motion.camera_centric_movement.pan_left.only_pan_left",
            "type": "pos"
        },
        "neg": [
            {
                "label": "cam_motion.camera_centric_movement.pan_left.has_pan_left",
                "type": "pos"
            },
            {
                "label": "cam_motion.camera_centric_movement.pan_left.only_pan_left",
                "type": "neg"
            }
        ]
    },
    {
        "folder": "cam_motion-20250227_0324ground_only",
        "name": "only_pan_right_vs_has_pan_right_and_not_only",
        "pos_question": "Does the camera only pan rightward without any other camera movements?",
        "neg_question": "Does the camera pan right along with other types of movement?",
        "pos_prompt": "The camera only pans rightward without any other camera movements.",
        "neg_prompt": "The camera pans right along with other types of movement.",
        "pos": {
            "label": "cam_motion.camera_centric_movement.pan_right.only_pan_right",
            "type": "pos"
        },
        "neg": [
            {
                "label": "cam_motion.camera_centric_movement.pan_right.has_pan_right",
                "type": "pos"
            },
            {
                "label": "cam_motion.camera_centric_movement.pan_right.only_pan_right",
                "type": "neg"
            }
        ]
    },
    {
        "folder": "cam_motion-20250227_0324ground_only",
        "name": "only_tilt_up_vs_has_tilt_up_and_not_only",
        "pos_question": "Does the camera only tilt upward without any other camera movements?",
        "neg_question": "Does the camera tilt up along with other types of movement?",
        "pos_prompt": "The camera only tilts upward without any other camera movements.",
        "neg_prompt": "The camera tilts up along with other types of movement.",
        "pos": {
            "label": "cam_motion.camera_centric_movement.tilt_up.only_tilt_up",
            "type": "pos"
        },
        "neg": [
            {
                "label": "cam_motion.camera_centric_movement.tilt_up.has_tilt_up",
                "type": "pos"
            },
            {
                "label": "cam_motion.camera_centric_movement.tilt_up.only_tilt_up",
                "type": "neg"
            }
        ]
    },
    {
        "folder": "cam_motion-20250227_0324ground_only",
        "name": "only_tilt_down_vs_has_tilt_down_and_not_only",
        "pos_question": "Does the camera only tilt downward without any other camera movements?",
        "neg_question": "Does the camera tilt down along with other types of movement?",
        "pos_prompt": "The camera only tilts downward without any other camera movements.",
        "neg_prompt": "The camera tilts down along with other types of movement.",
        "pos": {
            "label": "cam_motion.camera_centric_movement.tilt_down.only_tilt_down",
            "type": "pos"
        },
        "neg": [
            {
                "label": "cam_motion.camera_centric_movement.tilt_down.has_tilt_down",
                "type": "pos"
            },
            {
                "label": "cam_motion.camera_centric_movement.tilt_down.only_tilt_down",
                "type": "neg"
            }
        ]
    },
    {
        "folder": "cam_motion-20250227_0324ground_only",
        "name": "only_roll_cc_vs_has_roll_cc_and_not_only",
        "pos_question": "Does the camera only roll clockwise without any other camera movements?",
        "neg_question": "Does the camera roll clockwise along with other types of movement?",
        "pos_prompt": "The camera only rolls clockwise without any other camera movements.",
        "neg_prompt": "The camera rolls clockwise along with other types of movement.",
        "pos": {
            "label": "cam_motion.camera_centric_movement.roll_clockwise.only_roll_clockwise",
            "type": "pos"
        },
        "neg": [
            {
                "label": "cam_motion.camera_centric_movement.roll_clockwise.has_roll_clockwise",
                "type": "pos"
            },
            {
                "label": "cam_motion.camera_centric_movement.roll_clockwise.only_roll_clockwise",
                "type": "neg"
            }
        ]
    },
    {
        "folder": "cam_motion-20250227_0324ground_only",
        "name": "only_roll_ccw_vs_has_roll_ccw_and_not_only",
        "pos_question": "Does the camera only roll counterclockwise without any other camera movements?",
        "neg_question": "Does the camera roll counterclockwise along with other types of movement?",
        "pos_prompt": "The camera only rolls counterclockwise without any other camera movements.",
        "neg_prompt": "The camera rolls counterclockwise along with other types of movement.",
        "pos": {
            "label": "cam_motion.camera_centric_movement.roll_counterclockwise.only_roll_counterclockwise",
            "type": "pos"
        },
        "neg": [
            {
                "label": "cam_motion.camera_centric_movement.roll_counterclockwise.has_roll_counterclockwise",
                "type": "pos"
            },
            {
                "label": "cam_motion.camera_centric_movement.roll_counterclockwise.only_roll_counterclockwise",
                "type": "neg"
            }
        ]
    }
]

reference_frame_tasks = [
    {
        # "folder": "cam_motion-20250227_0326ground_and_camera",
        "folder": "cam_motion-20250227_0324ground_only",
        "name": "forward_camera_only_vs_forward_ground_and_camera",
        "pos_question": "Does the camera move forward only relative to its initial viewing direction but not relative to the ground?",
        "neg_question": "Does the camera move forward relative to both the ground and its initial viewing direction?",
        "pos_prompt": "The camera moves forward only relative to its initial viewing direction but not relative to the ground.",
        "neg_prompt": "The camera moves forward relative to both the ground and its initial viewing direction.",
        "pos": [
            {
                "label": "cam_motion.ground_centric_movement.forward.has_forward_wrt_ground_birds_worms_included",
                "type": "neg"
            },
            {
                "label": "cam_motion.camera_centric_movement.forward.has_forward_wrt_camera",
                "type": "pos"
            }
        ],
        "neg": [
            {
                "label": "cam_motion.camera_centric_movement.forward.has_forward_wrt_camera",
                "type": "pos"
            },
            {
                "label": "cam_motion.ground_centric_movement.forward.has_forward_wrt_ground_birds_worms_included",
                "type": "pos"
            }
        ]
    },
    {
        # "folder": "cam_motion-20250227_0326ground_and_camera",
        "folder": "cam_motion-20250227_0324ground_only",
        "name": "backward_camera_only_vs_backward_ground_and_camera",
        "pos_question": "Does the camera move backward only relative to its initial viewing direction but not relative to the ground?",
        "neg_question": "Does the camera move backward relative to both the ground and its initial viewing direction?",
        "pos_prompt": "The camera moves backward only relative to its initial viewing direction but not relative to the ground.",
        "neg_prompt": "The camera moves backward relative to both the ground and its initial viewing direction.",
        "pos": [
            {
                "label": "cam_motion.ground_centric_movement.backward.has_backward_wrt_ground_birds_worms_included",
                "type": "neg"
            },
            {
                "label": "cam_motion.camera_centric_movement.backward.has_backward_wrt_camera",
                "type": "pos"
            }
        ],
        "neg": [
            {
                "label": "cam_motion.camera_centric_movement.backward.has_backward_wrt_camera",
                "type": "pos"
            },
            {
                "label": "cam_motion.ground_centric_movement.backward.has_backward_wrt_ground_birds_worms_included",
                "type": "pos"
            }
        ]
    },
    {
        # "folder": "cam_motion-20250227_0326ground_and_camera",
        "folder": "cam_motion-20250227_0324ground_only",
        "name": "upward_camera_only_vs_upward_camera_and_ground",
        "pos_question": "Does the camera move upward only relative to its initial viewing direction but not relative to the ground?",
        "neg_question": "Does the camera move upward relative to both the ground and its initial viewing direction?",
        "pos_prompt": "The camera moves upward only relative to its initial viewing direction but not relative to the ground.",
        "neg_prompt": "The camera moves upward relative to both the ground and its initial viewing direction.",
        "pos": [
            {
                "label": "cam_motion.ground_centric_movement.upward.has_upward_wrt_ground_birds_worms_included",
                "type": "neg"
            },
            {
                "label": "cam_motion.camera_centric_movement.upward.has_upward_wrt_camera",
                "type": "pos"
            }
        ],
        "neg": [
            {
                "label": "cam_motion.camera_centric_movement.upward.has_upward_wrt_camera",
                "type": "pos"
            },
            {
                "label": "cam_motion.ground_centric_movement.upward.has_upward_wrt_ground_birds_worms_included",
                "type": "pos"
            }
        ]
    },
    {
        # "folder": "cam_motion-20250227_0326ground_and_camera",
        "folder": "cam_motion-20250227_0324ground_only",
        "name": "downward_camera_only_vs_downward_camera_and_ground",
        "pos_question": "Does the camera move downward only relative to its initial viewing direction but not relative to the ground?",
        "neg_question": "Does the camera move downward relative to both the ground and its initial viewing direction?",
        "pos_prompt": "The camera moves downward only relative to its initial viewing direction but not relative to the ground.",
        "neg_prompt": "The camera moves downward relative to both the ground and its initial viewing direction.",
        "pos": [
            {
                "label": "cam_motion.ground_centric_movement.downward.has_downward_wrt_ground_birds_worms_included",
                "type": "neg"
            },
            {
                "label": "cam_motion.camera_centric_movement.downward.has_downward_wrt_camera",
                "type": "pos"
            }
        ],
        "neg": [
            {
                "label": "cam_motion.camera_centric_movement.downward.has_downward_wrt_camera",
                "type": "pos"
            },
            {
                "label": "cam_motion.ground_centric_movement.downward.has_downward_wrt_ground_birds_worms_included",
                "type": "pos"
            }
        ]
    }
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


def get_videos(label_dicts, task_spec):
    """
    Get videos based on task specifications.
    
    Args:
        label_dicts: Dictionary containing labels and their corresponding videos
        task_spec: Either a dictionary with 'label' and 'type' or a list of such dictionaries
        
    Returns:
        List of videos matching the task specification
    """
    if isinstance(task_spec, list):
        # If task_spec is a list, get the intersection of all video sets
        video_sets = []
        for task_dict in task_spec:
            _validate_task_dict(task_dict)
            videos = label_dicts[task_dict["label"]][task_dict["type"]]
            video_sets.append(set(videos))
        
        return list(set.intersection(*video_sets))
    else:
        # If task_spec is a single dictionary
        _validate_task_dict(task_spec)
        return label_dicts[task_spec["label"]][task_spec["type"]]


def _validate_task_dict(task_dict):
    """
    Validate that a task dictionary has the required keys.
    
    Args:
        task_dict: Dictionary to validate
    
    Raises:
        AssertionError: If task_dict is not a dictionary or missing required keys
    """
    assert isinstance(task_dict, dict), "Task specification must be a dictionary"
    assert "label" in task_dict and "type" in task_dict, "Task specification must have 'label' and 'type' keys"
   

def generate_pairwise_tasks(pairwise_labels, root, video_root, video_labels_dir, labels_filename="label_names.json"):
    """
    Generate pairwise tasks from label definitions.
    
    Args:
        pairwise_labels: Dictionary containing skill and task definitions
        root: Root directory
        video_root: Video root directory
        video_labels_dir: Directory containing video labels
        labels_filename: Filename for labels (default: "label_names.json")
        
    Returns:
        Dictionary of pairwise tasks organized by skill and task name
    """
    pairwise_tasks = {}
    video_labels_dir = Path(video_labels_dir)

    for skill_name, tasks in pairwise_labels.items():
        pairwise_tasks[skill_name] = {}
        
        for task_dict in tasks:
            # Load labels for this task
            video_label_file = video_labels_dir / task_dict["folder"] / labels_filename
            label_dicts = labels_as_dict(root=root, video_root=video_root, video_label_file=video_label_file)
            
            # Get positive and negative videos
            pos_videos = get_videos(label_dicts, task_dict["pos"])
            neg_videos = get_videos(label_dicts, task_dict["neg"])
            
            # Convert Path objects to strings
            pos_videos = [str(video) for video in pos_videos]
            neg_videos = [str(video) for video in neg_videos]
            
            # Ensure positive and negative sets are disjoint
            assert set(pos_videos).isdisjoint(neg_videos), \
                f"Positive and negative videos overlap for task {task_dict['name']}"
            
            # Store task information
            pairwise_tasks[skill_name][task_dict["name"]] = {
                "task_dict": task_dict,
                "pos": pos_videos,
                "neg": neg_videos
            }
            
    return pairwise_tasks


def generate_balanced_pairwise_tasks(pairwise_labels, root, video_root, video_labels_dir, 
                                     train_ratio=TRAIN_RATIO, max_test_sample=MAX_SAMPLES, 
                                     labels_filename="label_names.json"):

    """
    Generate balanced pairwise tasks, ensuring exclusive train/test splits while prioritizing tasks with fewer available samples.
    Also returns the original task distribution and lists of train/test videos.

    Test samples are capped at `max_test_sample` per task. 
    If a task has fewer than `max_test_sample / (1 - train_ratio)`, 
    the train/test split follows `train_ratio`. Otherwise, up to `max_test_sample` is allocated to the test set, and the rest go to the train set.

    Args:
        pairwise_labels: Dictionary containing skill and task definitions.
        root: Root directory.
        video_root: Video root directory.
        video_labels_dir: Directory containing video labels.
        train_ratio: Guideline ratio of videos assigned to the training set (only applied when `min_count < max_test_sample / (1 - train_ratio)`).
        max_test_sample: Maximum number of test samples per task (default: 50).
        labels_filename: Filename for labels (default: "label_names.json").

    Returns:
        Dictionary with:
        - "raw": The full set of tasks before splitting.
        - "train": The train set.
        - "test": The test set.
        - "train_videos": Set of all videos assigned to train.
        - "test_videos": Set of all videos assigned to test.
    """

    video_labels_dir = Path(video_labels_dir)
    video_usage = defaultdict(set)  # Track tasks where each video appears
    task_metadata = []  # Store task details for prioritization
    all_videos = set()
    raw_tasks = defaultdict(dict)

    # Step 1: Collect all videos and track their occurrences
    for skill_name, tasks in pairwise_labels.items():
        for task_dict in tasks:
            task_name = task_dict["name"]
            video_label_file = video_labels_dir / task_dict["folder"] / labels_filename
            label_dicts = labels_as_dict(root=root, video_root=video_root, video_label_file=video_label_file)

            # Get positive and negative videos
            pos_videos = get_videos(label_dicts, task_dict["pos"])
            neg_videos = get_videos(label_dicts, task_dict["neg"])

            # Convert Path objects to strings
            pos_videos = [str(video) for video in pos_videos]
            neg_videos = [str(video) for video in neg_videos]

            # Ensure no overlap between positive and negative lists
            assert set(pos_videos).isdisjoint(set(neg_videos)), \
                f"Positive and negative videos overlap for task {task_name}"

            # Store original dataset
            raw_tasks[skill_name][task_name] = {
                "task_dict": task_dict,
                "pos": pos_videos,
                "neg": neg_videos
            }

            # Track video occurrences
            for video in pos_videos:
                video_usage[video].add((skill_name, task_name, "pos"))
            for video in neg_videos:
                video_usage[video].add((skill_name, task_name, "neg"))

            # Collect all videos
            all_videos.update(pos_videos)
            all_videos.update(neg_videos)

            # Store metadata for sorting
            task_metadata.append({
                "skill": skill_name,
                "task": task_name,
                "task_dict": task_dict,
                "pos_videos": pos_videos,
                "neg_videos": neg_videos,
                "min_count": min(len(pos_videos), len(neg_videos))  # Sorting priority
            })

    # Step 2: Sort tasks by the minimum available positive/negative samples (smallest first) and Move tasks["task"] == "has_crane_down" to the first
    task_metadata.sort(key=lambda x: x["min_count"])
    task_metadata = sorted(task_metadata, key=lambda x: x["task"] != "has_crane_down")
    
    # Step 3: Assign videos to train or test, prioritizing constrained tasks
    train_videos = set()
    test_videos = set()

    for task in task_metadata:
        skill_name, task_name = task["skill"], task["task"]
        pos_videos, neg_videos = task["pos_videos"], task["neg_videos"]

        # Filter available videos (ensuring no overlap)
        available_pos = [v for v in pos_videos if v not in train_videos and v not in test_videos]
        available_neg = [v for v in neg_videos if v not in train_videos and v not in test_videos]
        
        existing_pos_train = [v for v in pos_videos if v in train_videos]
        existing_neg_train = [v for v in neg_videos if v in train_videos]
        existing_pos_test = [v for v in pos_videos if v in test_videos]
        existing_neg_test = [v for v in neg_videos if v in test_videos]
        
        expected_train_size = max_test_sample * train_ratio / (1 - train_ratio)
        expected_test_size = max_test_sample
        
        missing_pos_train = max(0, expected_train_size - len(existing_pos_train))
        missing_neg_train = max(0, expected_train_size - len(existing_neg_train))
        missing_train = max(missing_pos_train, missing_neg_train)
        missing_pos_test = max(0, expected_test_size - len(existing_pos_test))
        missing_neg_test = max(0, expected_test_size - len(existing_neg_test))
        missing_test = max(missing_pos_test, missing_neg_test)
        
        available_num = min(len(available_pos), len(available_neg))
        if available_num > missing_train + missing_test:
            # No need to follow `train_ratio`
            continue
        
        # if len(available_pos) <= 1 or len(available_neg) <= 1:
        #     print(f"Skipping task {task_name} due to insufficient samples")
            # import pdb; pdb.set_trace()
        # Determine how many can be assigned to train vs test
        num_train = int(len(available_pos) * train_ratio)
        num_test = len(available_pos) - num_train  # Ensure balance

        # Assign videos to train and test
        train_pos = available_pos[:num_train]
        train_neg = available_neg[:num_train]
        test_pos = available_pos[num_train:num_train + num_test]
        test_neg = available_neg[num_train:num_train + num_test]

        # if task_name == "has_crane_down":
        #     import pdb; pdb.set_trace()
        # Add to the respective sets
        train_videos.update(train_pos + train_neg)
        test_videos.update(test_pos + test_neg)
        
    # Step 4: Construct final train and test task dictionaries
    train_tasks = defaultdict(dict)
    test_tasks = defaultdict(dict)

    for task in task_metadata:
        skill_name, task_name = task["skill"], task["task"]
        pos_videos, neg_videos = task["pos_videos"], task["neg_videos"]

        # Assign based on the video sets
        unassigned_pos = [v for v in pos_videos if v not in train_videos and v not in test_videos]
        unassigned_neg = [v for v in neg_videos if v not in train_videos and v not in test_videos]
        train_videos.update(unassigned_pos + unassigned_neg)
        train_pos = [v for v in pos_videos if v in train_videos]
        train_neg = [v for v in neg_videos if v in train_videos]
        test_pos = [v for v in pos_videos if v in test_videos]
        test_neg = [v for v in neg_videos if v in test_videos]

        # Ensure balance by trimming excess samples
        # min_train_samples = min(len(train_pos), len(train_neg))
        # min_test_samples = min(len(test_pos), len(test_neg))

        train_tasks[skill_name][task_name] = {
            "task_dict": task["task_dict"],
            "pos": train_pos + unassigned_pos,
            "neg": train_neg + unassigned_neg
        }

        test_tasks[skill_name][task_name] = {
            "task_dict": task["task_dict"],
            "pos": test_pos,
            "neg": test_neg
        }

    return {
        "raw": raw_tasks,
        "train": train_tasks,
        "test": test_tasks,
        "train_videos": list(train_videos),
        "test_videos": list(test_videos)
    }

def print_detailed_task_statistics(raw_tasks, train_tasks, test_tasks):
    """
    Print statistics about the original, train, and test task distributions.

    Args:
        raw_tasks: Dictionary of original pairwise tasks.
        train_tasks: Dictionary of train set pairwise tasks.
        test_tasks: Dictionary of test set pairwise tasks.
    """
    print("\n===== Task Statistics =====")
    print(f"{'Skill/Task':<60} {'Orig Pos':<10} {'Orig Neg':<10} {'Train Pos':<10} {'Train Neg':<10} {'Test Pos':<10} {'Test Neg':<10}")
    print("-" * 110)

    total_original_samples, total_train_samples, total_test_samples = 0, 0, 0

    for skill_name in raw_tasks:
        print(f"\n{skill_name}:")
        skill_original, skill_train, skill_test = 0, 0, 0

        for task_name in raw_tasks[skill_name]:
            orig_pos = len(raw_tasks[skill_name][task_name]["pos"])
            orig_neg = len(raw_tasks[skill_name][task_name]["neg"])

            train_pos = len(train_tasks.get(skill_name, {}).get(task_name, {}).get("pos", []))
            train_neg = len(train_tasks.get(skill_name, {}).get(task_name, {}).get("neg", []))
            test_pos = len(test_tasks.get(skill_name, {}).get(task_name, {}).get("pos", []))
            test_neg = len(test_tasks.get(skill_name, {}).get(task_name, {}).get("neg", []))

            skill_original += min(orig_pos, orig_neg)
            skill_train += min(train_pos, train_neg)
            skill_test += min(test_pos, test_neg)

            # Truncate task name if too long
            display_name = task_name if len(task_name) <= 50 else task_name[:47] + "..."

            print(f"  {display_name:<58} {orig_pos:<10} {orig_neg:<10} {train_pos:<10} {train_neg:<10} {test_pos:<10} {test_neg:<10}")

        total_original_samples += skill_original
        total_train_samples += skill_train
        total_test_samples += skill_test

        print(f"  {'Total skill samples:':<58} {skill_original:<10} {'':<10} {skill_train:<10} {'':<10} {skill_test:<10}")

    print("\n" + "-" * 110)
    print(f"{'Total benchmark samples:':<60} {total_original_samples:<10} {'':<10} {total_train_samples:<10} {'':<10} {total_test_samples:<10}")

def verify_tasks(train_tasks, test_tasks, train_videos, test_videos):
    """
    Verify that train and test tasks are correctly split and that no video appears in both sets.

    Args:
        train_tasks: Dictionary of train set pairwise tasks.
        test_tasks: Dictionary of test set pairwise tasks.
        train_videos: List of videos assigned to the train set.
        test_videos: List of videos assigned to the test set.

    Returns:
        None. Raises an assertion error if any violation is found.
    """
    train_videos_set = set(train_videos)
    test_videos_set = set(test_videos)

    assert train_videos_set.isdisjoint(test_videos_set), "Error: Some videos appear in both train and test sets!"

    def check_task_videos(tasks, allowed_videos, split_name):
        """Check that all videos in the tasks belong only to the allowed set."""
        for skill_name, skill_tasks in tasks.items():
            for task_name, task_data in skill_tasks.items():
                pos_videos = set(task_data.get("pos", []))
                neg_videos = set(task_data.get("neg", []))

                # Ensure all videos in this split belong to the correct video set
                assert pos_videos.issubset(allowed_videos), \
                    f"Error: Task {task_name} ({split_name}) has positive videos not in {split_name} set!"
                assert neg_videos.issubset(allowed_videos), \
                    f"Error: Task {task_name} ({split_name}) has negative videos not in {split_name} set!"

    # Check that all train tasks contain only train videos
    check_task_videos(train_tasks, train_videos_set, "train")

    # Check that all test tasks contain only test videos
    check_task_videos(test_tasks, test_videos_set, "test")

    print("Verification passed: No video appears in both train and test sets!")


def sample_from_tasks(
    original_tasks,
    max_samples=None,
    max_train_samples=None,
    max_test_samples=MAX_SAMPLES,
    sampling=SAMPLING,
    seed=SEED):
    """
    Sample a subset of videos from pairwise tasks.
    
    Args:
        pairwise_tasks: Dictionary of pairwise tasks
        max_samples: Maximum number of samples per task (default: 30)
        sampling: Sampling method, either "random" or "top" (default: "random")
        seed: Random seed for reproducibility (default: 0)
        
    Returns:
        Dictionary of sampled pairwise tasks
    """
    assert sampling in ["random", "top"], "Sampling method must be 'random' or 'top'"
    import copy
    sampled_tasks = copy.deepcopy(original_tasks)
    # Create a deep copy to avoid modifying the original
    for split_name, sample_num in [("raw", max_samples), ("train", max_train_samples), ("test", max_test_samples)]:
        for skill_name, skill_tasks in sampled_tasks[split_name].items():
            for task_name, task_data in skill_tasks.items():
                pos_videos = task_data["pos"]
                neg_videos = task_data["neg"]
                
                # Determine number of samples
                if sample_num is None:
                    # Use all available samples
                    sample_count = min(len(pos_videos), len(neg_videos))
                else:
                    sample_count = min(sample_num, len(pos_videos), len(neg_videos))
                
                if sampling == "random":
                    # Use random sampling with seed for reproducibility
                    random.seed(seed)
                    sampled_tasks[split_name][skill_name][task_name]["pos"] = random.sample(pos_videos, sample_count)
                    sampled_tasks[split_name][skill_name][task_name]["neg"] = random.sample(neg_videos, sample_count)
                else:  # "top" sampling
                    # Take the first N videos
                    sampled_tasks[split_name][skill_name][task_name]["pos"] = pos_videos[:sample_count]
                    sampled_tasks[split_name][skill_name][task_name]["neg"] = neg_videos[:sample_count]
    # Update train_videos and test_videos
    new_train_videos = set()
    new_test_videos = set()
    for split_name, videos in [("train", new_train_videos), ("test", new_test_videos)]:
        for skill_name, skill_tasks in sampled_tasks[split_name].items():
            for task_name, task_data in skill_tasks.items():
                videos.update(task_data["pos"])
                videos.update(task_data["neg"])  
    sampled_tasks["train_videos"] = list(new_train_videos)
    sampled_tasks["test_videos"] = list(new_test_videos) 
    return sampled_tasks


def generate_pairwise_datasets(
    max_samples=MAX_SAMPLES,
    sampling=SAMPLING,
    seed=SEED,
    root=ROOT,
    video_root=VIDEO_ROOT,
    video_labels_dir=VIDEO_LABELS_DIR,
    labels_filename="label_names.json",
    pairwise_labels=PAIRWISE_LABELS,
    train_ratio=TRAIN_RATIO,
    folder_name="motion_dataset"
):
    """
    Generate a pairwise benchmark by sampling from pairwise tasks.
    
    Args:
        pairwise_labels: Dictionary containing skill and task definitions
        max_samples: Maximum number of samples per task
        root: Root directory
        video_root: Video root directory
        video_labels_dir: Directory containing video labels
        labels_filename: Filename for labels
        mode: Benchmark mode
        
    Returns:
        Tuple of (sampled_tasks, sampled_config)
    """
    # Get the directory for sampled tasks
    video_labels_dir = Path(video_labels_dir)
    sampling_str = "top" if sampling == "top" else f"random_seed_{seed}"
    sampled_dir = video_labels_dir / folder_name / f"test_ratio_{1 - train_ratio:.2f}_num_{max_samples}_sampling_{sampling_str}"
    
    # Check if sampled tasks already exist
    if not sampled_dir.exists():
        # Generate and sample tasks
        original_tasks = generate_balanced_pairwise_tasks(
            pairwise_labels=pairwise_labels,
            root=root,
            video_root=video_root,
            video_labels_dir=video_labels_dir,
            train_ratio=train_ratio,
            labels_filename=labels_filename
        )
        
        verify_tasks(original_tasks["train"], original_tasks["test"], original_tasks["train_videos"], original_tasks["test_videos"])
        
        sampled_tasks = sample_from_tasks(
            original_tasks,
            max_samples=None,
            max_train_samples=None,
            max_test_samples=max_samples,
            sampling=sampling,
            seed=seed
        )
        
        verify_tasks(sampled_tasks["train"], sampled_tasks["test"], sampled_tasks["train_videos"], sampled_tasks["test_videos"])
        
        
        # Save configuration and tasks
        sampled_config = {
            "max_samples": max_samples,
            "sampling": sampling,
            "train_ratio": train_ratio,
            "seed": seed,
            "video_labels_dir": str(video_labels_dir),
            "root": str(root),
            "video_root": str(video_root),
            "pairwise_labels": pairwise_labels
        }
        
        # Create directory and save files
        sampled_dir.mkdir(parents=True, exist_ok=True)
        
        with open(sampled_dir / "sampled_config.json", "w") as f:
            json.dump(sampled_config, f, indent=4)
            
        with open(sampled_dir / "sampled_tasks.json", "w") as f:
            json.dump(sampled_tasks, f, indent=4)
            
        with open(sampled_dir / "original_tasks.json", "w") as f:
            json.dump(original_tasks, f, indent=4)
    else:
        # Load existing sampled tasks and config
        with open(sampled_dir / "sampled_tasks.json", "r") as f:
            sampled_tasks = json.load(f)
            
        with open(sampled_dir / "sampled_config.json", "r") as f:
            sampled_config = json.load(f)
        
        with open(sampled_dir / "original_tasks.json", "r") as f:
            original_tasks = json.load(f)
    
    return {
        "original_tasks": original_tasks,
        "sampled_tasks": sampled_tasks,
        "sampled_config": sampled_config,
    }


def print_task_statistics(sampled_tasks):
    """
    Print statistics about the sampled tasks.
    
    Args:
        sampled_tasks: Dictionary of sampled pairwise tasks
    """
    total_samples = 0
    
    print("\n===== Task Statistics =====")
    print(f"{'Skill/Task':<60} {'Positive':<10} {'Negative':<10}")
    print("-" * 80)
    
    for skill_name in sampled_tasks:
        print(f"\n{skill_name}:")
        skill_samples = 0
        
        for task_name in sampled_tasks[skill_name]:
            pos_count = len(sampled_tasks[skill_name][task_name]["pos"])
            neg_count = len(sampled_tasks[skill_name][task_name]["neg"])
            skill_samples += pos_count
            
            # Truncate task name if too long
            display_name = task_name
            if len(display_name) > 50:
                display_name = display_name[:47] + "..."
                
            print(f"  {display_name:<58} {pos_count:<10} {neg_count:<10}")
        
        total_samples += skill_samples
        print(f"  {'Total skill samples:':<58} {skill_samples:<10}")
    
    print("\n" + "-" * 80)
    print(f"{'Total benchmark samples:':<60} {total_samples:<10}")



def sample_from_pairwise_tasks(pairwise_tasks, max_samples=30, sampling="random", seed=0):
    """
    Sample a subset of videos from pairwise tasks.
    
    Args:
        pairwise_tasks: Dictionary of pairwise tasks
        max_samples: Maximum number of samples per task (default: 30)
        sampling: Sampling method, either "random" or "top" (default: "random")
        seed: Random seed for reproducibility (default: 0)
        
    Returns:
        Dictionary of sampled pairwise tasks
    """
    assert sampling in ["random", "top"], "Sampling method must be 'random' or 'top'"
    
    # Create a deep copy to avoid modifying the original
    sampled_tasks = pairwise_tasks.copy()
    
    for skill_name, skill_tasks in sampled_tasks.items():
        for task_name, task_data in skill_tasks.items():
            pos_videos = task_data["pos"]
            neg_videos = task_data["neg"]
            
            # Determine number of samples
            sample_count = min(max_samples, len(pos_videos), len(neg_videos))
            
            if sampling == "random":
                # Use random sampling with seed for reproducibility
                random.seed(seed)
                sampled_tasks[skill_name][task_name]["pos"] = random.sample(pos_videos, sample_count)
                sampled_tasks[skill_name][task_name]["neg"] = random.sample(neg_videos, sample_count)
            else:  # "top" sampling
                # Take the first N videos
                sampled_tasks[skill_name][task_name]["pos"] = pos_videos[:sample_count]
                sampled_tasks[skill_name][task_name]["neg"] = neg_videos[:sample_count]
                
    return sampled_tasks


def get_sampled_tasks_dir(video_labels_dir, max_samples=30, sampling="random", seed=0, folder_name="pairwise_tasks"):
    """
    Get the directory for sampled tasks.
    
    Args:
        video_labels_dir: Directory containing video labels
        max_samples: Maximum number of samples per task
        sampling: Sampling method
        seed: Random seed
        folder_name: Folder name for pairwise tasks
        
    Returns:
        Path to the sampled tasks directory
    """
    video_labels_dir = Path(video_labels_dir)
    sampled_dir = video_labels_dir / folder_name / f"sampled_{sampling}_num_{max_samples}_seed_{seed}"
    return sampled_dir


def generate_pairwise_benchmark(
    sampling="random",
    max_samples=30,
    seed=42,
    root=None,
    video_root=None,
    video_labels_dir=None,
    labels_filename="label_names.json",
    pairwise_labels=PAIRWISE_LABELS,
):
    """
    Generate a pairwise benchmark by sampling from pairwise tasks.
    
    Args:
        pairwise_labels: Dictionary containing skill and task definitions
        sampling: Sampling method, either "random" or "top"
        max_samples: Maximum number of samples per task
        seed: Random seed for reproducibility
        root: Root directory
        video_root: Video root directory
        video_labels_dir: Directory containing video labels
        labels_filename: Filename for labels
        mode: Benchmark mode
        
    Returns:
        Tuple of (sampled_tasks, sampled_config)
    """
    # Get the directory for sampled tasks
    sampled_dir = get_sampled_tasks_dir(
        video_labels_dir=video_labels_dir,
        max_samples=max_samples,
        sampling=sampling,
        seed=seed
    )
    
    # Check if sampled tasks already exist
    if not sampled_dir.exists():
        # Generate and sample tasks
        pairwise_tasks = generate_pairwise_tasks(
            pairwise_labels=pairwise_labels,
            root=root,
            video_root=video_root,
            video_labels_dir=video_labels_dir,
            labels_filename=labels_filename
        )
        
        sampled_tasks = sample_from_pairwise_tasks(
            pairwise_tasks,
            max_samples=max_samples,
            sampling=sampling,
            seed=seed
        )
        
        # Save configuration and tasks
        sampled_config = {
            "max_samples": max_samples,
            "sampling": sampling,
            "seed": seed,
            "video_labels_dir": str(video_labels_dir),
            "root": str(root),
            "video_root": str(video_root),
            "pairwise_labels": pairwise_labels
        }
        
        # Create directory and save files
        sampled_dir.mkdir(parents=True, exist_ok=True)
        
        with open(sampled_dir / "sampled_config.json", "w") as f:
            json.dump(sampled_config, f, indent=4)
            
        with open(sampled_dir / "sampled_tasks.json", "w") as f:
            json.dump(sampled_tasks, f, indent=4)
    else:
        # Load existing sampled tasks and config
        with open(sampled_dir / "sampled_tasks.json", "r") as f:
            sampled_tasks = json.load(f)
            
        with open(sampled_dir / "sampled_config.json", "r") as f:
            sampled_config = json.load(f)
    
    return sampled_tasks, sampled_config



if __name__ == "__main__":
    # Import constants from config
    # Generate the benchmark
    # sampled_tasks, sampled_config = generate_pairwise_benchmark(
    #     pairwise_labels=PAIRWISE_LABELS,
    #     sampling=SAMPLING,
    #     max_samples=MAX_SAMPLES,
    #     seed=SEED,
    #     root=ROOT,
    #     video_root=VIDEO_ROOT,
    #     video_labels_dir=VIDEO_LABELS_DIR,
    #     labels_filename="label_names.json"
    # )
    
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--sampling", type=str, default=SAMPLING, help="Sampling method")
    parser.add_argument("--max_samples", type=int, default=MAX_SAMPLES, help="A (rough) maximum number of (test) samples per task")
    args = parser.parse_args()
    
    # # Print statistics
    # print_task_statistics(sampled_tasks)
    datasets = generate_pairwise_datasets(
        max_samples=args.max_samples,
        sampling=SAMPLING,
        seed=SEED,
        root=ROOT,
        video_root=VIDEO_ROOT,
        video_labels_dir=VIDEO_LABELS_DIR,
        labels_filename="label_names.json",
        pairwise_labels=PAIRWISE_LABELS,
        train_ratio=TRAIN_RATIO,
        folder_name="motion_dataset"
    )
    print_detailed_task_statistics(
        datasets['original_tasks']["raw"],
        datasets['sampled_tasks']["train"],
        datasets['sampled_tasks']["test"]
    )
    print(f"Number of train videos: {len(datasets['sampled_tasks']['train_videos'])}")
    print(f"Number of test videos: {len(datasets['sampled_tasks']['test_videos'])}")
    
    # import pdb; pdb.set_trace()
    # Create benchmark
    # benchmark = PairwiseBenchmark(datasets['sampled_tasks']['test'], mode="vqa")
    
    # import numpy as np
    # retrieval_scores = np.random.rand(len(benchmark), 2, 2)
    # yes_scores = np.random.rand(len(benchmark), 2, 2)
    # no_scores = np.random.rand(len(benchmark), 2, 2)
    # benchmark.evaluate_and_print_retrieval(retrieval_scores)
    # benchmark.evaluate_and_print_vqa(yes_scores, no_scores)