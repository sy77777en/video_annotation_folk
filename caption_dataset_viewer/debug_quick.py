#!/usr/bin/env python3
"""
Debug Video URLs - Investigate why some dataset video_urls work and others don't

This script:
1. Downloads JSON files from HuggingFace datasets
2. Extracts video URLs from different datasets
3. Tests the URLs with HEAD requests
4. Compares URL patterns and responses
5. Identifies what makes TUNA-Bench work but not ShareGPT4Video/VDC
"""

import json
import argparse
from pathlib import Path
from huggingface_hub import hf_hub_download, list_repo_files
import requests
from urllib.parse import urlparse, unquote
from collections import defaultdict
import traceback


# ANSI color codes for pretty output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}\n")


def print_success(text):
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")


def print_error(text):
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")


def print_warning(text):
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")


def print_info(text):
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")


def download_dataset_json(repo_id, dataset_name):
    """Download the JSON file for a specific dataset."""
    try:
        # List files in the repo
        files = list_repo_files(repo_id=repo_id, repo_type="dataset")
        
        # Find JSON files for this dataset
        json_files = [f for f in files if f.startswith(dataset_name + '/') and f.endswith('.json')]
        
        if not json_files:
            print_error(f"No JSON files found for dataset: {dataset_name}")
            return None
        
        json_file = json_files[0]
        print_info(f"Downloading: {json_file}")
        
        # Download the file
        local_path = hf_hub_download(
            repo_id=repo_id,
            filename=json_file,
            repo_type="dataset",
            cache_dir="/tmp/hf_debug_cache"
        )
        
        # Load JSON
        with open(local_path, 'r') as f:
            data = json.load(f)
        
        print_success(f"Downloaded: {json_file}")
        return data
    
    except Exception as e:
        print_error(f"Error downloading {dataset_name}: {e}")
        traceback.print_exc()
        return None


def extract_video_info(data, dataset_name):
    """Extract video URL information from dataset."""
    video_info = []
    
    if 'samples' not in data:
        print_warning(f"No 'samples' key found in {dataset_name}")
        return video_info
    
    for idx, sample in enumerate(data['samples'][:5]):  # Check first 5 samples
        info = {
            'dataset': dataset_name,
            'sample_index': idx,
            'video_url': sample.get('video_url'),
            'video_path': sample.get('video_path'),
            'video': sample.get('video'),
            'video_id': sample.get('video_id'),
        }
        video_info.append(info)
    
    return video_info


def test_url(url, timeout=10):
    """Test a URL with HEAD and GET requests."""
    result = {
        'url': url,
        'accessible': False,
        'status_code': None,
        'content_type': None,
        'content_length': None,
        'headers': {},
        'error': None,
        'redirect_url': None
    }
    
    if not url:
        result['error'] = "No URL provided"
        return result
    
    try:
        # First try HEAD request
        print_info(f"  Testing HEAD: {url[:80]}...")
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        
        result['status_code'] = response.status_code
        result['headers'] = dict(response.headers)
        result['content_type'] = response.headers.get('Content-Type', 'Unknown')
        result['content_length'] = response.headers.get('Content-Length', 'Unknown')
        
        if response.url != url:
            result['redirect_url'] = response.url
            print_info(f"  Redirected to: {response.url[:80]}...")
        
        if response.status_code == 200:
            result['accessible'] = True
            print_success(f"  Status: {response.status_code} (Accessible)")
        elif response.status_code == 405:  # Method Not Allowed - try GET
            print_warning(f"  HEAD not allowed, trying GET...")
            
            # Try GET with range request to avoid downloading entire file
            headers = {'Range': 'bytes=0-1023'}  # Just get first 1KB
            response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
            
            result['status_code'] = response.status_code
            result['headers'] = dict(response.headers)
            result['content_type'] = response.headers.get('Content-Type', 'Unknown')
            
            if response.status_code in [200, 206]:  # 206 = Partial Content
                result['accessible'] = True
                print_success(f"  Status: {response.status_code} (Accessible via GET)")
            else:
                print_error(f"  Status: {response.status_code} (Not accessible)")
        else:
            print_error(f"  Status: {response.status_code} (Not accessible)")
    
    except requests.exceptions.Timeout:
        result['error'] = f"Timeout after {timeout}s"
        print_error(f"  Error: Timeout")
    except requests.exceptions.ConnectionError as e:
        result['error'] = f"Connection error: {str(e)[:100]}"
        print_error(f"  Error: Connection failed")
    except Exception as e:
        result['error'] = f"Error: {str(e)[:100]}"
        print_error(f"  Error: {str(e)[:100]}")
    
    return result


def analyze_url_pattern(url):
    """Analyze URL structure and pattern."""
    if not url:
        return {}
    
    parsed = urlparse(url)
    path_parts = parsed.path.split('/')
    
    return {
        'scheme': parsed.scheme,
        'netloc': parsed.netloc,
        'path': parsed.path,
        'path_parts': path_parts,
        'filename': path_parts[-1] if path_parts else None,
        'extension': Path(path_parts[-1]).suffix if path_parts and path_parts[-1] else None,
        'has_resolve': '/resolve/' in url,
        'has_blob': '/blob/' in url,
        'is_hf_url': 'huggingface.co' in parsed.netloc,
    }


def compare_datasets(datasets_info):
    """Compare video URL patterns across datasets."""
    print_header("URL PATTERN COMPARISON")
    
    working_patterns = []
    broken_patterns = []
    
    for dataset_name, info_list in datasets_info.items():
        print(f"\n{Colors.BOLD}Dataset: {dataset_name}{Colors.ENDC}")
        print("-" * 80)
        
        for info in info_list:
            url = info['video_url']
            test_result = info.get('test_result', {})
            url_pattern = info.get('url_pattern', {})
            
            print(f"\n  Sample {info['sample_index']}:")
            print(f"    video_url:  {url[:100] if url else 'None'}...")
            print(f"    video:      {info['video']}")
            print(f"    video_path: {info['video_path']}")
            
            if url:
                print(f"    Extension:  {url_pattern.get('extension', 'N/A')}")
                print(f"    Has /resolve/: {url_pattern.get('has_resolve', False)}")
                print(f"    Has /blob/:    {url_pattern.get('has_blob', False)}")
                print(f"    Status:     {test_result.get('status_code', 'Not tested')}")
                print(f"    Accessible: {test_result.get('accessible', False)}")
                
                if test_result.get('content_type'):
                    print(f"    Content-Type: {test_result.get('content_type')}")
                
                if test_result.get('error'):
                    print(f"    Error: {test_result.get('error')}")
                
                if test_result.get('accessible'):
                    working_patterns.append((dataset_name, url_pattern, url))
                else:
                    broken_patterns.append((dataset_name, url_pattern, url, test_result.get('error')))
    
    # Summary
    print_header("SUMMARY")
    
    print(f"{Colors.BOLD}Working URLs:{Colors.ENDC} {len(working_patterns)}")
    if working_patterns:
        print("\nCommon patterns in working URLs:")
        for dataset, pattern, url in working_patterns[:3]:
            print(f"  • {dataset}")
            print(f"    - URL format: ...{url[-60:]}")
            print(f"    - Has /resolve/: {pattern.get('has_resolve')}")
            print(f"    - Extension: {pattern.get('extension')}")
    
    print(f"\n{Colors.BOLD}Broken URLs:{Colors.ENDC} {len(broken_patterns)}")
    if broken_patterns:
        print("\nCommon patterns in broken URLs:")
        for dataset, pattern, url, error in broken_patterns[:3]:
            print(f"  • {dataset}")
            print(f"    - URL format: ...{url[-60:]}")
            print(f"    - Has /resolve/: {pattern.get('has_resolve')}")
            print(f"    - Extension: {pattern.get('extension')}")
            print(f"    - Error: {error}")
    
    # Identify differences
    print_header("KEY DIFFERENCES")
    
    if working_patterns and broken_patterns:
        working_has_resolve = all(p[1].get('has_resolve', False) for p in working_patterns)
        broken_has_resolve = any(p[1].get('has_resolve', False) for p in broken_patterns)
        
        print(f"Working URLs use /resolve/: {working_has_resolve}")
        print(f"Broken URLs use /resolve/:  {broken_has_resolve}")
        
        working_extensions = set(p[1].get('extension', '') for p in working_patterns)
        broken_extensions = set(p[1].get('extension', '') for p in broken_patterns)
        
        print(f"\nWorking extensions: {working_extensions}")
        print(f"Broken extensions:  {broken_extensions}")


def main():
    parser = argparse.ArgumentParser(description="Debug Video URLs in HuggingFace Datasets")
    parser.add_argument("--repo", type=str, default="zhiqiulin/video_caption_datasets",
                       help="HuggingFace repo")
    parser.add_argument("--datasets", nargs="+", 
                       default=["TUNA-Bench", "ShareGPT4Video", "VDC"],
                       help="Dataset names to test")
    parser.add_argument("--samples", type=int, default=3,
                       help="Number of samples to test per dataset")
    parser.add_argument("--timeout", type=int, default=10,
                       help="Request timeout in seconds")
    args = parser.parse_args()
    
    print_header("VIDEO URL DEBUG TOOL")
    print(f"Repository: {args.repo}")
    print(f"Datasets: {', '.join(args.datasets)}")
    print(f"Samples per dataset: {args.samples}")
    
    # Collect data from all datasets
    all_datasets_info = {}
    
    for dataset_name in args.datasets:
        print_header(f"ANALYZING: {dataset_name}")
        
        # Download dataset JSON
        data = download_dataset_json(args.repo, dataset_name)
        if not data:
            continue
        
        # Extract video info
        video_info = extract_video_info(data, dataset_name)[:args.samples]
        
        if not video_info:
            print_warning(f"No video information found in {dataset_name}")
            continue
        
        print(f"\nFound {len(video_info)} samples to test\n")
        
        # Test each video URL
        for info in video_info:
            url = info['video_url']
            
            if url:
                print(f"{Colors.BOLD}Sample {info['sample_index']}:{Colors.ENDC}")
                
                # Analyze URL pattern
                url_pattern = analyze_url_pattern(url)
                info['url_pattern'] = url_pattern
                
                print(f"  URL: {url[:100]}...")
                
                # Test URL
                test_result = test_url(url, timeout=args.timeout)
                info['test_result'] = test_result
                
                print()  # Blank line between samples
            else:
                print_warning(f"Sample {info['sample_index']}: No video_url found")
        
        all_datasets_info[dataset_name] = video_info
    
    # Compare all datasets
    if len(all_datasets_info) > 1:
        compare_datasets(all_datasets_info)
    
    # Save debug report
    report_path = Path("video_url_debug_report.json")
    with open(report_path, 'w') as f:
        json.dump(all_datasets_info, f, indent=2)
    
    print_header("REPORT SAVED")
    print_success(f"Debug report saved to: {report_path.resolve()}")
    
    # Recommendations
    print_header("RECOMMENDATIONS")
    
    has_working = any(
        info.get('test_result', {}).get('accessible', False)
        for dataset_info in all_datasets_info.values()
        for info in dataset_info
    )
    
    has_broken = any(
        not info.get('test_result', {}).get('accessible', False) and info.get('video_url')
        for dataset_info in all_datasets_info.values()
        for info in dataset_info
    )
    
    if has_working and has_broken:
        print("\n💡 Based on the analysis:")
        print("\n1. Check if broken URLs need authentication or special headers")
        print("2. Verify the URL format (should use /resolve/ not /blob/)")
        print("3. Check if videos exist at the specified paths")
        print("4. Consider downloading videos to a local cache")
        print("5. Check if the HuggingFace repo has the videos or just metadata")
    
    print()


if __name__ == "__main__":
    main()