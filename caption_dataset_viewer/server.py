#!/usr/bin/env python3
"""
Caption Dataset Viewer Server - Annotation Interface for Video Captions

Usage:
    python server.py [--port 8080] [--host 0.0.0.0] [--repo zhiqiulin/video_caption_datasets]
"""

import http.server
import socketserver
import json
import os
import argparse
from pathlib import Path
from urllib.parse import unquote, parse_qs, urlparse
from huggingface_hub import hf_hub_download, list_repo_files
import traceback

# Configuration
PORT = 8080
HOST = "0.0.0.0"
HF_REPO = "zhiqiulin/video_caption_datasets"
ANNOTATIONS_DIR = Path("annotations")  # Local directory for saving annotations


def is_annotation_complete(annotation):
    """Check if an annotation is complete."""
    if not annotation:
        return False
    
    # Check if ALL rating fields are filled (not null/undefined)
    required_fields = ['overall', 'camera', 'subject', 'motion', 'scene', 'spatial']
    all_ratings_complete = all(
        annotation.get(field) is not None 
        for field in required_fields
    )
    
    # Check if segments exist and ALL have character indices
    segments_valid = True
    if annotation.get('segments') and len(annotation['segments']) > 0:
        segments_valid = all(
            seg.get('startIndex') is not None and seg.get('endIndex') is not None
            for seg in annotation['segments']
        )
    
    # Must have ALL ratings AND all segments must have indices (if any segments exist)
    return all_ratings_complete and segments_valid


class ReusableTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """Multi-threaded TCPServer that allows immediate port reuse."""
    allow_reuse_address = True
    daemon_threads = True
    request_queue_size = 50


class CaptionViewerHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler for the caption dataset viewer."""

    def __init__(self, *args, hf_repo=None, annotations_dir=None, **kwargs):
        self.hf_repo = hf_repo
        self.annotations_dir = annotations_dir
        self.annotations_dir.mkdir(exist_ok=True)
        super().__init__(*args, **kwargs)

    def end_headers(self):
        """Override to add cache control headers for development files."""
        if (self.path.endswith('.html') or self.path.endswith('.css') or 
            self.path.endswith('.js') or self.path == '/' or self.path == '/index.html'):
            self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', 'Thu, 01 Jan 1970 00:00:00 GMT')
        super().end_headers()

    def do_GET(self):
        """Handle GET requests."""
        
        # API: Get available datasets
        if self.path == "/api/datasets":
            self.send_json_response(self.get_datasets())
            return
        
        # API: Get dataset samples
        if self.path.startswith("/api/dataset/"):
            dataset_name = unquote(self.path.split("/api/dataset/")[1].split("?")[0])
            data = self.get_dataset_samples(dataset_name)
            if data:
                self.send_json_response(data)
            else:
                self.send_error(404, "Dataset not found")
            return
        
        # API: Get single sample
        if self.path.startswith("/api/sample/"):
            parts = unquote(self.path.split("/api/sample/")[1]).split("/")
            if len(parts) >= 2:
                dataset_name = parts[0]
                sample_index = int(parts[1])
                data = self.get_single_sample(dataset_name, sample_index)
                if data:
                    self.send_json_response(data)
                else:
                    self.send_error(404, "Sample not found")
            return
        
        # API: Get annotation for a sample
        if self.path.startswith("/api/annotation/"):
            parts = unquote(self.path.split("/api/annotation/")[1]).split("/")
            if len(parts) >= 2:
                dataset_name = parts[0]
                sample_index = int(parts[1])
                annotation = self.get_annotation(dataset_name, sample_index)
                self.send_json_response(annotation)
            return
        
        # API: Get annotation statistics
        if self.path.startswith("/api/stats/"):
            dataset_name = unquote(self.path.split("/api/stats/")[1])
            stats = self.get_annotation_stats(dataset_name)
            self.send_json_response(stats)
            return
        
        # Proxy HuggingFace videos
        if self.path.startswith("/videos/"):
            video_path = unquote(self.path.split("/videos/")[1])
            self.proxy_hf_video(video_path)
            return
        
        # Serve static files (HTML, CSS, JS)
        super().do_GET()

    def do_POST(self):
        """Handle POST requests."""
        
        # API: Save annotation
        if self.path.startswith("/api/annotation/"):
            parts = unquote(self.path.split("/api/annotation/")[1]).split("/")
            if len(parts) >= 2:
                dataset_name = parts[0]
                sample_index = int(parts[1])
                
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                annotation_data = json.loads(post_data.decode('utf-8'))
                
                success = self.save_annotation(dataset_name, sample_index, annotation_data)
                if success:
                    self.send_json_response({"success": True, "message": "Annotation saved"})
                else:
                    self.send_error(500, "Failed to save annotation")
            return
        
        self.send_error(404, "Endpoint not found")

    def get_datasets(self):
        """Get list of available datasets from HuggingFace repo."""
        try:
            # List all files in the repo
            files = list_repo_files(repo_id=self.hf_repo, repo_type="dataset")
            
            # Extract dataset names (folders with JSON files)
            datasets = {}
            for file in files:
                if file.endswith('.json') and '/' in file:
                    parts = file.split('/')
                    dataset_name = parts[0]
                    if dataset_name not in datasets:
                        datasets[dataset_name] = {
                            "name": dataset_name,
                            "json_files": []
                        }
                    datasets[dataset_name]["json_files"].append(file)
            
            return list(datasets.values())
        except Exception as e:
            print(f"Error listing datasets: {e}")
            traceback.print_exc()
            return []

    def get_dataset_samples(self, dataset_name):
        """Get samples from a dataset."""
        try:
            # Find JSON files for this dataset
            files = list_repo_files(repo_id=self.hf_repo, repo_type="dataset")
            json_files = [f for f in files if f.startswith(dataset_name + '/') and f.endswith('.json')]
            
            if not json_files:
                return None
            
            # Download and parse the first JSON file
            json_file = json_files[0]
            local_path = hf_hub_download(
                repo_id=self.hf_repo,
                filename=json_file,
                repo_type="dataset",
                cache_dir="/tmp/hf_cache"
            )
            
            with open(local_path, 'r') as f:
                data = json.load(f)
            
            # Add annotation status to each sample
            if 'samples' in data:
                for i, sample in enumerate(data['samples']):
                    annotation = self.get_annotation(dataset_name, i)
                    if annotation:
                        # Check if annotation is complete or incomplete
                        if is_annotation_complete(annotation):
                            sample['annotation_status'] = 'completed'
                        else:
                            sample['annotation_status'] = 'incomplete'
                    else:
                        sample['annotation_status'] = 'pending'
            
            return data
        except Exception as e:
            print(f"Error loading dataset {dataset_name}: {e}")
            traceback.print_exc()
            return None

    def get_single_sample(self, dataset_name, sample_index):
        """Get a single sample from a dataset."""
        try:
            dataset = self.get_dataset_samples(dataset_name)
            if dataset and 'samples' in dataset:
                if 0 <= sample_index < len(dataset['samples']):
                    sample = dataset['samples'][sample_index]
                    annotation = self.get_annotation(dataset_name, sample_index)
                    return {
                        "sample": sample,
                        "annotation": annotation,
                        "dataset_info": {
                            "name": dataset.get("dataset_name", dataset_name),
                            "split": dataset.get("split", "unknown"),
                            "total_samples": len(dataset['samples'])
                        }
                    }
            return None
        except Exception as e:
            print(f"Error loading sample {dataset_name}/{sample_index}: {e}")
            return None

    def get_annotation(self, dataset_name, sample_index):
        """Get annotation for a specific sample."""
        annotation_file = self.annotations_dir / dataset_name / f"sample_{sample_index}.json"
        if annotation_file.exists():
            with open(annotation_file, 'r') as f:
                return json.load(f)
        return None

    def save_annotation(self, dataset_name, sample_index, annotation_data):
        """Save annotation for a specific sample."""
        try:
            dataset_dir = self.annotations_dir / dataset_name
            dataset_dir.mkdir(parents=True, exist_ok=True)
            
            annotation_file = dataset_dir / f"sample_{sample_index}.json"
            with open(annotation_file, 'w') as f:
                json.dump(annotation_data, f, indent=2)
            
            print(f"✓ Saved annotation: {dataset_name}/sample_{sample_index}")
            return True
        except Exception as e:
            print(f"Error saving annotation: {e}")
            traceback.print_exc()
            return False

    def get_annotation_stats(self, dataset_name):
        """Get annotation statistics for a dataset."""
        try:
            dataset_dir = self.annotations_dir / dataset_name
            if not dataset_dir.exists():
                return {
                    "total": 0, 
                    "completed": 0, 
                    "incomplete": 0,
                    "pending": 0,
                    "avg_segments": None,
                    "avg_scores": {
                        "overall": None,
                        "camera": None,
                        "subject": None,
                        "motion": None,
                        "scene": None,
                        "spatial": None
                    }
                }
            
            annotation_files = list(dataset_dir.glob("sample_*.json"))
            
            # Track stats
            total_segments = 0
            segment_count = 0
            scores = {
                "overall": [],
                "camera": [],
                "subject": [],
                "motion": [],
                "scene": [],
                "spatial": []
            }
            completed_count = 0
            incomplete_count = 0
            
            for annotation_file in annotation_files:
                with open(annotation_file, 'r') as f:
                    annotation = json.load(f)
                    
                    # Count segments
                    if annotation.get('segments'):
                        total_segments += len(annotation['segments'])
                        segment_count += 1
                    
                    # Collect scores
                    for field in scores.keys():
                        if annotation.get(field) is not None:
                            scores[field].append(annotation[field])
                    
                    # Count complete vs incomplete
                    if is_annotation_complete(annotation):
                        completed_count += 1
                    else:
                        incomplete_count += 1
            
            # Calculate averages
            avg_segments = total_segments / segment_count if segment_count > 0 else None
            avg_scores = {}
            for field, values in scores.items():
                if values:
                    avg_scores[field] = round(sum(values) / len(values), 2)
                else:
                    avg_scores[field] = None
            
            return {
                "total": len(annotation_files),
                "completed": completed_count,
                "incomplete": incomplete_count,
                "pending": 0,  # Server doesn't track pending
                "avg_segments": round(avg_segments, 2) if avg_segments else None,
                "avg_scores": avg_scores
            }
        except Exception as e:
            print(f"Error calculating stats: {e}")
            traceback.print_exc()
            return {
                "total": 0,
                "completed": 0,
                "incomplete": 0,
                "pending": 0,
                "avg_segments": None,
                "avg_scores": {
                    "overall": None,
                    "camera": None,
                    "subject": None,
                    "motion": None,
                    "scene": None,
                    "spatial": None
                }
            }

    def proxy_hf_video(self, video_path):
        """Proxy video requests to HuggingFace."""
        try:
            # Download video from HuggingFace
            local_path = hf_hub_download(
                repo_id=self.hf_repo,
                filename=video_path,
                repo_type="dataset",
                cache_dir="/tmp/hf_cache"
            )
            
            # Serve the video
            self.send_response(200)
            self.send_header('Content-Type', 'video/mp4')
            self.send_header('Accept-Ranges', 'bytes')
            
            file_size = os.path.getsize(local_path)
            self.send_header('Content-Length', str(file_size))
            self.end_headers()
            
            with open(local_path, 'rb') as f:
                self.wfile.write(f.read())
        except Exception as e:
            print(f"Error serving video {video_path}: {e}")
            self.send_error(404, f"Video not found: {video_path}")

    def send_json_response(self, data):
        """Send JSON response."""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, format, *args):
        """Override to customize logging."""
        if "api" in args[0] or self.command == "POST":
            print(f"{self.address_string()} - {format % args}")


def create_handler(hf_repo, annotations_dir):
    """Create a handler with the specified configuration."""
    def handler(*args, **kwargs):
        return CaptionViewerHandler(*args, hf_repo=hf_repo, 
                                   annotations_dir=annotations_dir, **kwargs)
    return handler


def main():
    parser = argparse.ArgumentParser(description="Caption Dataset Viewer Server")
    parser.add_argument("--port", type=int, default=PORT, help=f"Port (default: {PORT})")
    parser.add_argument("--host", type=str, default=HOST, help=f"Host (default: {HOST})")
    parser.add_argument("--repo", type=str, default=HF_REPO, help=f"HuggingFace repo (default: {HF_REPO})")
    parser.add_argument("--annotations_dir", type=str, default=None, help="Annotations directory")
    args = parser.parse_args()

    script_dir = Path(__file__).parent.resolve()
    annotations_dir = Path(args.annotations_dir) if args.annotations_dir else script_dir / ANNOTATIONS_DIR
    annotations_dir.mkdir(parents=True, exist_ok=True)
    
    os.chdir(script_dir)
    
    handler = create_handler(args.repo, annotations_dir)
    
    with ReusableTCPServer((args.host, args.port), handler) as httpd:
        print("=" * 70)
        print(f"🎬 Caption Dataset Viewer Server")
        print("=" * 70)
        print(f"📦 HuggingFace Repo: {args.repo}")
        print(f"💾 Annotations:      {annotations_dir.resolve()}")
        print(f"🌐 Server:           http://{args.host}:{args.port}")
        if args.host == "0.0.0.0":
            import socket
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            print(f"🔗 Local URL:        http://{local_ip}:{args.port}")
            print(f"🔗 Localhost:        http://localhost:{args.port}")
        print("=" * 70)
        print("\n✨ Server running with multi-threading support")
        print("💡 Annotations saved locally in real-time")
        print("💡 Hard refresh (Ctrl+Shift+R / Cmd+Shift+R) to see changes\n")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n👋 Shutting down server...")
            print("✅ All annotations saved successfully")


if __name__ == "__main__":
    main()