from __future__ import annotations
from typing import List, Dict, Any
from pathlib import Path
import json
import os

from video_data import VideoData


class LabelCollection:
    def __init__(self) -> None:
        self._labels: Dict[str, Label | LabelCollection] = {}
        
    def __getattr__(self, name: str) -> Label | LabelCollection:
        try:
            return self._labels[name]
        except KeyError:
            raise AttributeError(f"'LabelCollection' object has no attribute '{name}'")
    
    def _add_label(self, path_parts: List[str], label: Label) -> None:
        current = self._labels
        *dirs, filename = path_parts
        
        # Create nested structure for directories
        for part in dirs:
            if part not in current:
                current[part] = LabelCollection()
            current = current[part]._labels
            
        # Add the label under its filename (without .json)
        current[filename.replace('.json', '')] = label
    
    def __str__(self, indent: str = "") -> str:
        return "\n".join(
            f"{indent}{key}/" + ("\n" + value.__str__(indent + "  ") if isinstance(value, LabelCollection)
            else f": {value.label}")
            for key, value in self._labels.items()
        )


class Rule:
    def __init__(self, rule: str):
        self.rule = rule
        try:
            compile(f"lambda self: {rule}", "<string>", "eval")
        except SyntaxError as e:
            raise ValueError(f"Invalid lambda syntax in rule: {rule}. Error: {str(e)}")


    def filter(self, items : List[VideoData]):
        """Filter items based on the rule"""
        return list(filter(eval(f"lambda self: {self.rule}"), items))
    
    def eval(self, item : VideoData):
        """Evaluate the rule on a single item"""
        return eval(f"lambda self: {self.rule}")(item)
    
    def __call__(self, item : VideoData):
        return self.eval(item)

class Label:
    def __init__(self,
                 label: str = "",
                 label_name: str = "",
                 def_question: List[str] = [],
                 alt_question: List[str] = [],
                 def_prompt: List[str] = [],
                 alt_prompt: List[str] = [],
                 pos_rule_str: str = "",
                 neg_rule_str: str = "",
                 easy_neg_rule_str: Dict[str, str] = {},
                 hard_neg_rule_str: Dict[str, str] = {}):
        
        self.label = label
        self.label_name = label_name
        self.def_question = def_question
        self.alt_question = alt_question
        self.def_prompt = def_prompt
        self.alt_prompt = alt_prompt

        # Ensure unique elements without preserving order
        self.all_question = list(set(def_question + alt_question))
        self.all_prompt = list(set(def_prompt + alt_prompt))
        
        # Rule objects
        self.pos_rule = Rule(pos_rule_str)
        self.neg_rule = Rule(neg_rule_str)

        # Dictionaries of Rule objects
        self.easy_neg_rules = {key: Rule(value) for key, value in easy_neg_rule_str.items()}
        self.hard_neg_rules = {key: Rule(value) for key, value in hard_neg_rule_str.items()}
        
        # assert 'pos' and 'neg' are not in the easy_neg_rules or hard_neg_rules
        assert 'pos' not in self.easy_neg_rules and 'neg' not in self.easy_neg_rules
        assert 'pos' not in self.hard_neg_rules and 'neg' not in self.hard_neg_rules
    
    def pos(self, items: List[VideoData]):
        """Filter items based on the positive rule"""
        return self.pos_rule.filter(items)

    def neg(self, items: List[VideoData]):
        """Filter items based on the negative rule"""
        return self.neg_rule.filter(items)
    
    def filter(self, key: str, items: List[VideoData]):
        if key == 'pos':
            return self.pos(items)
        elif key == 'neg':
            return self.neg(items)
        elif key in self.easy_neg_rules:
            return self.easy_neg_rules[key].filter(items)
        elif key in self.hard_neg_rules:
            return self.hard_neg_rules[key].filter(items)
        else:
            raise ValueError(f"Invalid key: {key}")
    
    def verify(self, items: List[VideoData]):
        # Make sure that the positives and negatives have no overlap
        # Make sure that the easy and hard negatives are subsets of the negatives
        pos = self.pos_rule.filter(items)
        neg = self.neg_rule.filter(items)
        easy_neg = {key: rule.filter(items) for key, rule in self.easy_neg_rules.items()}
        hard_neg = {key: rule.filter(items) for key, rule in self.hard_neg_rules.items()}
        
        # Check for overlap between pos and neg
        overlap = set(pos) & set(neg)
        if overlap:
            raise ValueError(f"Positives and negatives have overlap for {self.label}: {overlap}")

        # Ensure easy_neg is a strict subset of neg
        for key, easy_set in easy_neg.items():
            if not set(easy_set).issubset(set(neg)):
                raise ValueError(f"easy_neg[{key}] is not a subset of neg for {self.label}")
            if set(easy_set) == set(neg):
                raise ValueError(f"easy_neg[{key}] is equal to neg for {self.label}, not a strict subset")

        # Ensure hard_neg is a strict subset of neg
        for key, hard_set in hard_neg.items():
            if not set(hard_set).issubset(set(neg)):
                raise ValueError(f"hard_neg[{key}] is not a subset of neg for {self.label}")
            if set(hard_set) == set(neg):
                raise ValueError(f"hard_neg[{key}] is equal to neg for {self.label}, not a strict subset")

        return True
    
    @classmethod
    def from_json(cls, filename):
        with open(filename) as f:
            data = json.load(f)
        return cls(**data)

    def __str__(self):
        return f"Label: {self.label}"
    
    @classmethod
    def load_all_labels(cls, labels_dir: str = "labels") -> LabelCollection:
        """Load all label JSON files into a nested LabelCollection structure.
        
        The structure mirrors the directory hierarchy, allowing dot notation access:
        labels.cam_motion.forward.has_forward_wrt_ground
        
        Args:
            labels_dir: Path to the labels directory
            
        Returns:
            A nested LabelCollection matching the directory hierarchy
        """
        labels_path = Path(labels_dir)
        collection = LabelCollection()
        success_count = 0
        
        def process_json_file(file_path: Path) -> None:
            nonlocal success_count
            try:
                label = cls.from_json(file_path)
                rel_path = file_path.relative_to(labels_path)
                collection._add_label(rel_path.parts, label)
                success_count += 1
            except Exception as e:
                print(f"\033[91mError loading {file_path}:\033[0m")
                print(f"  {str(e)}")
        
        # Process all JSON files in directory tree
        json_files = labels_path.rglob("*.json")
        for file_path in json_files:
            process_json_file(file_path)
        
        print(f"\nSuccessfully loaded {success_count} label files")
        return collection
    
    
if __name__ == "__main__":
    from video_data import create_video_data_demo
    data = create_video_data_demo()
    
    # Load all labels with nested structure
    labels = Label.load_all_labels()
    
    # Print the entire label hierarchy
    print("\nLabel Hierarchy:")
    print(labels)
    
    # Example: Access a specific label using dot notation
    try:
        # Access a label (adjust path based on your actual structure)
        label = labels.cam_motion.ground_centric_movement.forward.has_forward_wrt_ground_birds_worms_included
        print(f"\nAccessed specific label: {label}")
        print(f"Label name: {label.label_name}")
        print(f"First question: {label.def_question[0]}")
        print(f"Evaluate pos_rule: {label.pos_rule(data)}")
        print(f"Evaluate neg_rule: {label.neg_rule(data)}")
    except AttributeError as e:
        print(f"\nCouldn't access label: {e}")
    