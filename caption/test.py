#!/usr/bin/env python3
"""
Test script to verify the file structure and imports work correctly.
Run this from the ROOT directory: python caption/test_structure.py
"""

import sys
from pathlib import Path

def test_file_structure():
    """Test that all required files exist in the expected locations"""
    print("Testing file structure...")
    
    # Get the root directory (where this script is run from)
    root_dir = Path.cwd()
    caption_dir = root_dir / "caption"
    print(f"Root directory: {root_dir}")
    print(f"Caption directory: {caption_dir}")
    
    # Check required files in caption/ directory
    required_files_caption = [
        "caption/all_configs.json",
        "caption/lighting_configs.json",
    ]
    
    # Check required files in root directory
    required_files_root = [
        "video_data",  # This should be a directory
    ]
    
    required_dirs_caption = [
        "caption/video_urls",
        "caption/prompts", 
        "caption/apps",
        "caption/core",
        "caption/interfaces",
        "caption/config",
        "caption/utils.py",  # This is a file, not directory
    ]
    
    required_dirs_root = [
        "llm",  # This should be a directory/package
    ]
    
    print("\nChecking required files in caption/:")
    for file_name in required_files_caption:
        file_path = root_dir / file_name
        if file_path.exists():
            print(f"✅ {file_name}")
        else:
            print(f"❌ {file_name} - MISSING")
    
    print("\nChecking required files in root/:")
    for file_name in required_files_root:
        file_path = root_dir / file_name
        if file_path.exists():
            print(f"✅ {file_name}")
        else:
            print(f"❌ {file_name} - MISSING")
    
    print("\nChecking required directories/files in caption/:")
    for dir_name in required_dirs_caption:
        dir_path = root_dir / dir_name
        if dir_path.exists():
            print(f"✅ {dir_name}")
        else:
            print(f"❌ {dir_name} - MISSING")
    
    print("\nChecking required directories in root/:")
    for dir_name in required_dirs_root:
        dir_path = root_dir / dir_name
        if dir_path.exists() and dir_path.is_dir():
            print(f"✅ {dir_name}/")
        else:
            print(f"❌ {dir_name}/ - MISSING")

def test_imports():
    """Test that all imports work correctly"""
    print("\nTesting imports...")
    
    try:
        # Test root-level imports (llm package)
        from llm import get_llm
        print("✅ llm package")
    except ImportError as e:
        print(f"❌ llm package - {e}")
    
    try:
        import process_json
        print("✅ process_json")
    except ImportError as e:
        print(f"❌ process_json - {e}")
    
    try:
        from caption.utils import extract_frames
        print("✅ caption.utils")
    except ImportError as e:
        print(f"❌ caption.utils - {e}")
    
    try:
        from caption_policy.vanilla_program import VanillaSubjectPolicy
        print("✅ caption_policy")
    except ImportError as e:
        print(f"❌ caption_policy - {e}")
    
    try:
        # Test our new package imports
        from caption.config import get_config
        print("✅ caption.config")
    except ImportError as e:
        print(f"❌ caption.config - {e}")
    
    try:
        from caption.core import DataManager
        print("✅ caption.core")
    except ImportError as e:
        print(f"❌ caption.core - {e}")
    
    try:
        from caption.interfaces import CaptionInterface
        print("✅ caption.interfaces")
    except ImportError as e:
        print(f"❌ caption.interfaces - {e}")

def test_config_loading():
    """Test that configs can be loaded correctly"""
    print("\nTesting config loading...")
    
    try:
        from caption.config import get_config
        
        # Test main config
        main_config = get_config("main")
        print(f"✅ Main config loaded: {main_config.name}")
        print(f"  - Video data file: {main_config.video_data_file}")
        print(f"  - Configs file: {main_config.configs_file}")
        print(f"  - Video URLs files: {len(main_config.video_urls_files)} files")
        
        # Test lighting config  
        lighting_config = get_config("lighting")
        print(f"✅ Lighting config loaded: {lighting_config.name}")
        print(f"  - Video data file: {lighting_config.video_data_file}")
        print(f"  - Video URLs files: {len(lighting_config.video_urls_files)} files")
        
    except Exception as e:
        print(f"❌ Config loading failed - {e}")

if __name__ == "__main__":
    print("=== Caption System Structure Test ===")
    print("Run this from the ROOT directory: python caption/test_structure.py")
    test_file_structure()
    test_imports()
    test_config_loading()
    print("\n=== Test Complete ===")
    print("\nIf you see any ❌ errors above, those need to be fixed before running the apps.")
    print("\nUsage (from root directory):")
    print("  python caption/apps/app.py --config-type main")
    print("  python caption/apps/app.py --config-type lighting") 
    print("  python caption/apps/onboarding_app.py --config-type main")