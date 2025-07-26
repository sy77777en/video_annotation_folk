#!/usr/bin/env python3
"""
Google Sheets Export System for Video Caption Annotation Statistics

This script exports comprehensive statistics for video caption annotation and review work
to Google Sheets, creating a master tracking sheet with links to individual user 
performance sheets.

Bug fixes included:
- Fixed hyperlinks to show as smart chips with actual sheet URLs
- Corrected timestamp logic to properly separate annotation vs review timestamps  
- Fixed per-task statistics calculation to properly aggregate across all videos/tasks
"""

import os
import json
import gspread
import argparse
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from caption.core.data_manager import DataManager
from caption.core.auth import load_annotators_from_files, APPROVED_REVIEWERS
from caption.config import get_config


class GoogleSheetExporter:
    """Export caption statistics to Google Sheets with comprehensive tracking"""
    
    # OAuth 2.0 scope required for Google Sheets access
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    
    def __init__(self, credentials_file: str, folder_path: str, root_path: str):
        """Initialize the Google Sheets exporter"""
        self.data_manager = DataManager(folder_path, root_path)
        self._setup_google_auth(credentials_file)
        
        # Load annotators and get task names
        self.annotators = load_annotators_from_files()
        self.approved_reviewers = APPROVED_REVIEWERS
        
        # Configuration mapping for short names with emojis
        self.config_names_to_short_names = {
            "Subject Description Caption": "🧍‍♂️Subject",
            "Scene Composition and Dynamics Caption": "🏞️Scene", 
            "Subject Motion and Dynamics Caption": "🏃‍♂️Motion",
            "Spatial Framing and Dynamics Caption": "🗺️Spatial",
            "Camera Framing and Dynamics Caption": "📷Camera",
            "Color Composition and Dynamics Caption (Raw)": "🎨Color",
            "Lighting Setup and Dynamics Caption (Raw)": "💡Lighting",
            "Lighting Effects and Dynamics Caption (Raw)": "🌟Effects",
        }
        
        # Track any failures during export
        self.export_failures = []
    
    def _setup_google_auth(self, credentials_file: str):
        """Setup Google authentication using OAuth 2.0"""
        creds = None
        token_file = 'caption/token.json'
        
        # Load existing token if available
        if os.path.exists(token_file):
            creds = Credentials.from_authorized_user_file(token_file, self.SCOPES)
        
        # If there are no (valid) credentials available, get authorization
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                # Manual OAuth flow for environments without browser
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_file, self.SCOPES, redirect_uri='http://localhost:8080')
                
                auth_url, _ = flow.authorization_url(prompt='consent')
                
                print('='*60)
                print('GOOGLE SHEETS AUTHORIZATION REQUIRED')
                print('='*60)
                print('1. Go to this URL in your browser:')
                print(auth_url)
                print('\n2. Click "Advanced" -> "Go to [App Name] (unsafe)"')
                print('3. Authorize the application')
                print('4. The browser will show "This site can\'t be reached" - this is expected!')
                print('5. Copy the authorization code from the failed URL')
                print('\n   Example URL: http://localhost:8080/?code=AUTHORIZATION_CODE&scope=...')
                print('   Copy only the part after "code=" and before "&"')
                print('='*60)
                
                auth_code = input('\nEnter the authorization code: ').strip()
                if not auth_code:
                    raise Exception('No authorization code provided')
                
                flow.fetch_token(code=auth_code)
                creds = flow.credentials
            
            # Save the credentials for the next run
            with open(token_file, 'w') as token:
                token.write(creds.to_json())
        
        # Authorize gspread client
        self.client = gspread.authorize(creds)
    
    def _api_call_with_retry(self, func, *args, max_retries=5, **kwargs):
        """Execute API call with rate limiting and retry logic"""
        operation_name = kwargs.pop('operation_name', func.__name__)
        
        for attempt in range(max_retries):
            try:
                # Add delay between API calls to avoid rate limits
                if attempt > 0:
                    delay = min(2 ** attempt, 10)  # Exponential backoff, max 10 seconds
                    print(f"      Retrying {operation_name} in {delay}s (attempt {attempt + 1}/{max_retries})...")
                    time.sleep(delay)
                
                result = func(*args, **kwargs)
                return result
                
            except Exception as e:
                error_str = str(e).lower()
                if 'quota' in error_str or 'rate' in error_str or 'limit' in error_str:
                    if attempt == max_retries - 1:
                        failure_msg = f"RATE LIMIT FAILURE: {operation_name} - Data may not be synced!"
                        print(f"      ❌ {failure_msg}")
                        self.export_failures.append(failure_msg)
                        raise Exception(f"Rate limit failure for {operation_name} after {max_retries} attempts")
                    print(f"      Rate limit detected in {operation_name}: {e}")
                    continue
                else:
                    # Not a rate limit error, re-raise immediately
                    failure_msg = f"UNEXPECTED ERROR: {operation_name} - {str(e)}"
                    print(f"      ❌ {failure_msg}")
                    self.export_failures.append(failure_msg)
                    raise
        
        raise Exception(f"{operation_name} failed after {max_retries} attempts")
    
    def export_all_sheets(self, configs_file: str, video_urls_files: List[str], 
                         output_dir: str, master_sheet_id: str):
        """
        Export all data to Google Sheets
        
        Args:
            configs_file: Path to configs file
            video_urls_files: List of video URL files
            output_dir: Output directory for caption data
            master_sheet_id: Google Sheet ID for the master sheet
        """
        # Load configs to get task names
        configs = self.data_manager.load_config(configs_file)
        configs = [self.data_manager.load_config(config) for config in configs]
        task_names = [config["name"] for config in configs]
        
        # Collect all video URLs
        all_video_urls = []
        video_file_mapping = {}  # video_url -> video_file
        for video_file in video_urls_files:
            try:
                video_urls = self.data_manager.load_json(video_file)
                all_video_urls.extend(video_urls)
                for url in video_urls:
                    video_file_mapping[url] = os.path.basename(video_file)
            except FileNotFoundError:
                print(f"Warning: Video URLs file not found: {video_file}")
                continue
        
        # Calculate statistics for all users
        annotator_stats, reviewer_stats = self._calculate_all_user_stats(
            configs, all_video_urls, video_file_mapping, output_dir
        )
        
        # Export master sheet
        print("="*60)
        print("STARTING GOOGLE SHEETS EXPORT")
        print("="*60)
        self._export_master_sheet(master_sheet_id, annotator_stats, reviewer_stats, task_names)
        
        # Export individual user sheets with progress tracking
        total_users = sum(1 for stats in annotator_stats.values() if self._has_activity(stats)) + \
                     sum(1 for stats in reviewer_stats.values() if self._has_activity(stats))
        
        current_user = 0
        print(f"\nExporting individual user sheets ({total_users} total)...")
        
        # Store sheet IDs for hyperlinks
        user_sheet_ids = {}
        
        for user_name, stats in annotator_stats.items():
            if self._has_activity(stats):
                current_user += 1
                print(f"[{current_user}/{total_users}] Processing {user_name} Annotator...")
                sheet_id = self._export_user_sheet(user_name, "Annotator", stats, task_names, master_sheet_id)
                user_sheet_ids[f"{user_name} Annotator"] = sheet_id
            
        for user_name, stats in reviewer_stats.items():
            if self._has_activity(stats):
                current_user += 1
                print(f"[{current_user}/{total_users}] Processing {user_name} Reviewer...")
                sheet_id = self._export_user_sheet(user_name, "Reviewer", stats, task_names, master_sheet_id)
                user_sheet_ids[f"{user_name} Reviewer"] = sheet_id
        
        # Update master sheet with correct hyperlinks
        print("\nUpdating master sheet hyperlinks...")
        self._update_master_sheet_links(master_sheet_id, annotator_stats, reviewer_stats, user_sheet_ids)
        
        print("="*60)
        if self.export_failures:
            print("EXPORT COMPLETED WITH SOME FAILURES!")
            print("="*60)
            print("❌ The following operations failed:")
            for failure in self.export_failures:
                print(f"   - {failure}")
            print(f"\n⚠️  Some data may not be synced. Consider running the script again.")
            print(f"📊 Master Sheet: https://docs.google.com/spreadsheets/d/{master_sheet_id}/edit")
            print("="*60)
        else:
            print("EXPORT COMPLETED SUCCESSFULLY!")
            print("="*60)
            print(f"📊 Master Sheet: https://docs.google.com/spreadsheets/d/{master_sheet_id}/edit")
            print(f"   - View all annotator and reviewer statistics")
            print(f"   - Links to individual user sheets")
            print("="*60)
    
    def _has_activity(self, stats: Dict) -> bool:
        """Check if user has any activity"""
        return (stats['total_across_tasks'].get('completed', 0) > 0 or 
                stats['total_across_tasks'].get('reviewed', 0) > 0)
    
    def _calculate_all_user_stats(self, configs: List[Dict], all_video_urls: List[str], 
                                 video_file_mapping: Dict[str, str], output_dir: str) -> Tuple[Dict, Dict]:
        """Calculate statistics for all annotators and reviewers"""
        annotator_stats = {}
        reviewer_stats = {}
        
        # Initialize stats for all known users
        for user_name in self.annotators.keys():
            annotator_stats[user_name] = {
                'email': self.annotators[user_name].get('email', ''),
                'total_across_tasks': {'completed': 0, 'reviewed': 0, 'rejected': 0},
                'per_task': {},
                'per_video_file': {},
                'last_annotation_timestamp': None,
                'last_review_timestamp': None
            }
        
        for user_name in self.approved_reviewers:
            reviewer_stats[user_name] = {
                'email': self.annotators.get(user_name, {}).get('email', ''),
                'total_across_tasks': {'reviewed': 0},
                'per_task': {},
                'per_video_file': {},
                'last_annotation_timestamp': None,
                'last_review_timestamp': None
            }
        
        # Initialize per-task stats
        for config in configs:
            task_name = config["name"]
            for user_name in annotator_stats:
                annotator_stats[user_name]['per_task'][task_name] = {
                    'completed': 0, 'reviewed': 0, 'rejected': 0, 'total': 0
                }
            for user_name in reviewer_stats:
                reviewer_stats[user_name]['per_task'][task_name] = {
                    'reviewed': 0, 'total': 0
                }
        
        # Group videos by file for calculations
        videos_by_file = {}
        for video_url in all_video_urls:
            video_file = video_file_mapping.get(video_url, 'Unknown')
            if video_file not in videos_by_file:
                videos_by_file[video_file] = []
            videos_by_file[video_file].append(video_url)
        
        # Calculate stats for each video file
        for video_file, video_urls in videos_by_file.items():
            file_stats = self._calculate_file_stats(video_urls, configs, output_dir)
            
            # Update user stats  
            for user_name in annotator_stats:
                if video_file not in annotator_stats[user_name]['per_video_file']:
                    annotator_stats[user_name]['per_video_file'][video_file] = {
                        'total_possible': len(video_urls) * len(configs),
                        'completed_all_users': 0,
                        'completed_current_user': 0,
                        'reviewed_all_users': 0,
                        'reviewed_current_user_work': 0,
                        'last_annotation_timestamp': None,
                        'last_review_timestamp': None
                    }
                
                user_file_stats = annotator_stats[user_name]['per_video_file'][video_file]
                user_file_stats.update(file_stats['annotators'].get(user_name, {
                    'completed_all_users': file_stats['global']['completed_all_users'],
                    'completed_current_user': 0,
                    'reviewed_all_users': file_stats['global']['reviewed_all_users'],
                    'reviewed_current_user_work': 0,
                    'last_annotation_timestamp': None,
                    'last_review_timestamp': None
                }))
                
                # Update global user stats
                annotator_stats[user_name]['total_across_tasks']['completed'] += user_file_stats['completed_current_user']
                annotator_stats[user_name]['total_across_tasks']['reviewed'] += user_file_stats['reviewed_current_user_work']
                
                # Update per-task stats for annotators
                for config in configs:
                    task_name = config["name"]
                    task_stats = file_stats['per_task_annotators'].get(user_name, {}).get(task_name, {
                        'completed': 0, 'reviewed': 0, 'rejected': 0, 'total': len(video_urls)
                    })
                    
                    annotator_stats[user_name]['per_task'][task_name]['completed'] += task_stats['completed']
                    annotator_stats[user_name]['per_task'][task_name]['reviewed'] += task_stats['reviewed']
                    annotator_stats[user_name]['per_task'][task_name]['rejected'] += task_stats['rejected']
                    annotator_stats[user_name]['per_task'][task_name]['total'] += task_stats['total']
                
                # Update timestamps - only annotation timestamps for annotators
                if user_file_stats['last_annotation_timestamp']:
                    current_ts = annotator_stats[user_name]['last_annotation_timestamp']
                    if not current_ts or user_file_stats['last_annotation_timestamp'] > current_ts:
                        annotator_stats[user_name]['last_annotation_timestamp'] = user_file_stats['last_annotation_timestamp']
            
            # Update reviewer stats
            for user_name in reviewer_stats:
                if video_file not in reviewer_stats[user_name]['per_video_file']:
                    reviewer_stats[user_name]['per_video_file'][video_file] = {
                        'total_possible': len(video_urls) * len(configs),
                        'completed_all_users': 0,
                        'reviewed_all_users': 0,
                        'reviewed_by_current_user': 0,
                        'last_review_timestamp': None
                    }
                
                user_file_stats = reviewer_stats[user_name]['per_video_file'][video_file]
                user_file_stats.update(file_stats['reviewers'].get(user_name, {
                    'completed_all_users': file_stats['global']['completed_all_users'],
                    'reviewed_all_users': file_stats['global']['reviewed_all_users'],
                    'reviewed_by_current_user': 0,
                    'last_review_timestamp': None
                }))
                
                # Update global user stats
                reviewer_stats[user_name]['total_across_tasks']['reviewed'] += user_file_stats['reviewed_by_current_user']
                
                # Update per-task stats for reviewers
                for config in configs:
                    task_name = config["name"]
                    task_stats = file_stats['per_task_reviewers'].get(user_name, {}).get(task_name, {
                        'reviewed': 0, 'total': len(video_urls)
                    })
                    
                    reviewer_stats[user_name]['per_task'][task_name]['reviewed'] += task_stats['reviewed']
                    reviewer_stats[user_name]['per_task'][task_name]['total'] += task_stats['total']
                
                # Update timestamps - only review timestamps for reviewers
                if user_file_stats['last_review_timestamp']:
                    current_ts = reviewer_stats[user_name]['last_review_timestamp']
                    if not current_ts or user_file_stats['last_review_timestamp'] > current_ts:
                        reviewer_stats[user_name]['last_review_timestamp'] = user_file_stats['last_review_timestamp']
        
        return annotator_stats, reviewer_stats
    
    def _calculate_file_stats(self, video_urls: List[str], configs: List[Dict], output_dir: str) -> Dict:
        """Calculate statistics for a single video file"""
        stats = {
            'global': {
                'completed_all_users': 0,
                'reviewed_all_users': 0
            },
            'annotators': {},
            'reviewers': {},
            'per_task_annotators': {},  # user -> task -> stats
            'per_task_reviewers': {}    # user -> task -> stats
        }
        
        for video_url in video_urls:
            video_id = self.data_manager.get_video_id(video_url)
            
            for config in configs:
                config_output_dir = os.path.join(self.data_manager.folder, output_dir, config["output_name"])
                task_name = config["name"]
                
                # Get status and users for this video/task
                status, current_file, prev_file, current_user, prev_user = self.data_manager.get_video_status(
                    video_id, config_output_dir
                )
                
                if status == "not_completed":
                    continue
                
                # Update global stats
                stats['global']['completed_all_users'] += 1
                if status in ["approved", "rejected"]:
                    stats['global']['reviewed_all_users'] += 1
                
                # Determine annotator and reviewer
                annotator, reviewer = self.data_manager.get_annotator_and_reviewer(video_id, config_output_dir)
                
                # Update annotator stats
                if annotator:
                    if annotator not in stats['annotators']:
                        stats['annotators'][annotator] = {
                            'completed_current_user': 0,
                            'reviewed_current_user_work': 0,
                            'last_annotation_timestamp': None,
                            'last_review_timestamp': None
                        }
                    
                    if annotator not in stats['per_task_annotators']:
                        stats['per_task_annotators'][annotator] = {}
                    if task_name not in stats['per_task_annotators'][annotator]:
                        stats['per_task_annotators'][annotator][task_name] = {
                            'completed': 0, 'reviewed': 0, 'rejected': 0, 'total': len(video_urls)
                        }
                    
                    stats['annotators'][annotator]['completed_current_user'] += 1
                    stats['per_task_annotators'][annotator][task_name]['completed'] += 1
                    
                    # Update annotation timestamp from feedback file
                    if current_file and os.path.exists(current_file):
                        try:
                            with open(current_file, 'r') as f:
                                data = json.load(f)
                                timestamp = data.get('timestamp')
                                if timestamp:
                                    current_ts = stats['annotators'][annotator]['last_annotation_timestamp']
                                    if not current_ts or timestamp > current_ts:
                                        stats['annotators'][annotator]['last_annotation_timestamp'] = timestamp
                        except:
                            pass
                    
                    # Check if this annotation was reviewed
                    if status in ["approved", "rejected"]:
                        stats['annotators'][annotator]['reviewed_current_user_work'] += 1
                        stats['per_task_annotators'][annotator][task_name]['reviewed'] += 1
                        
                        if status == "rejected":
                            stats['per_task_annotators'][annotator][task_name]['rejected'] += 1
                
                # Update reviewer stats
                if reviewer and status in ["approved", "rejected"]:
                    if reviewer not in stats['reviewers']:
                        stats['reviewers'][reviewer] = {
                            'reviewed_by_current_user': 0,
                            'last_review_timestamp': None
                        }
                    
                    if reviewer not in stats['per_task_reviewers']:
                        stats['per_task_reviewers'][reviewer] = {}
                    if task_name not in stats['per_task_reviewers'][reviewer]:
                        stats['per_task_reviewers'][reviewer][task_name] = {
                            'reviewed': 0, 'total': len(video_urls)
                        }
                    
                    stats['reviewers'][reviewer]['reviewed_by_current_user'] += 1
                    stats['per_task_reviewers'][reviewer][task_name]['reviewed'] += 1
                    
                    # Update review timestamp from review file
                    review_file = self.data_manager.get_filename(video_id, config_output_dir, 
                                                               self.data_manager.REVIEWER_FILE_POSTFIX)
                    if os.path.exists(review_file):
                        try:
                            with open(review_file, 'r') as f:
                                data = json.load(f)
                                timestamp = data.get('review_timestamp')
                                if timestamp:
                                    current_ts = stats['reviewers'][reviewer]['last_review_timestamp']
                                    if not current_ts or timestamp > current_ts:
                                        stats['reviewers'][reviewer]['last_review_timestamp'] = timestamp
                        except:
                            pass
        
        # Add global stats to each user's stats
        for annotator_stats in stats['annotators'].values():
            annotator_stats['completed_all_users'] = stats['global']['completed_all_users']
            annotator_stats['reviewed_all_users'] = stats['global']['reviewed_all_users']
        
        for reviewer_stats in stats['reviewers'].values():
            reviewer_stats['completed_all_users'] = stats['global']['completed_all_users']
            reviewer_stats['reviewed_all_users'] = stats['global']['reviewed_all_users']
        
        return stats
    
    def _export_master_sheet(self, sheet_id: str, annotator_stats: Dict, reviewer_stats: Dict, task_names: List[str]):
        """Export the master sheet with annotator and reviewer tabs"""
        try:
            sheet = self._api_call_with_retry(self.client.open_by_key, sheet_id, 
                                            operation_name="opening master sheet")
        except:
            print(f"Error: Could not open sheet with ID {sheet_id}")
            return
        
        print("Exporting master sheet...")
        
        # Export Annotators tab
        self._export_master_tab(sheet, "Annotators", annotator_stats, task_names, "Annotator")
        
        # Export Reviewers tab  
        self._export_master_tab(sheet, "Reviewers", reviewer_stats, task_names, "Reviewer")
    
    def _export_master_tab(self, sheet, tab_name: str, user_stats: Dict, task_names: List[str], role: str):
        """Export a single tab in the master sheet"""
        print(f"  Exporting {tab_name} tab...")
        
        try:
            worksheet = sheet.worksheet(tab_name)
            print(f"    Found existing {tab_name} tab")
        except gspread.exceptions.WorksheetNotFound:
            print(f"    Creating new {tab_name} tab...")
            worksheet = self._api_call_with_retry(sheet.add_worksheet, title=tab_name, rows=100, cols=20, 
                                                operation_name=f"creating {tab_name} tab")
        
        # Prepare headers
        headers = [
            "User Name", "Email", "Annotation Sheet Link", "Last Annotated Timestamp", 
            "Review Sheet Link", "Last Review Timestamp"
        ]
        
        # Add task headers with emoji short names
        for task_name in task_names:
            short_name = self.config_names_to_short_names.get(task_name, task_name)
            headers.append(f"{short_name} Total")
        
        # Prepare data rows
        rows = [headers]
        for user_name, stats in user_stats.items():
            if self._has_activity(stats):
                # Create placeholder links (will be updated later with actual URLs)
                annotation_link = "🔗 Link"
                review_link = "🔗 Link"
                
                # Format timestamps
                last_annotation = self._format_timestamp(stats.get('last_annotation_timestamp'))
                last_review = self._format_timestamp(stats.get('last_review_timestamp'))
                
                # Calculate totals per task
                task_totals = []
                for task_name in task_names:
                    if role == "Annotator":
                        total = stats['per_task'][task_name]['completed']
                    else:  # Reviewer
                        total = stats['per_task'][task_name]['reviewed']
                    task_totals.append(total)
                
                row = [
                    user_name, stats['email'], annotation_link, last_annotation, 
                    review_link, last_review
                ] + task_totals
                rows.append(row)
        
        # Update the worksheet
        self._api_call_with_retry(worksheet.clear, operation_name="clearing master sheet")
        if rows:
            # Helper function to convert column number to Excel-style letter
            def col_num_to_letter(col_num):
                result = ""
                while col_num > 0:
                    col_num -= 1
                    result = chr(col_num % 26 + ord('A')) + result
                    col_num //= 26
                return result
            
            end_col = col_num_to_letter(len(headers))
            self._api_call_with_retry(worksheet.update, f'A1:{end_col}{len(rows)}', rows, 
                                    operation_name=f"updating {len(rows)-1} user records")
            print(f"    ✅ Successfully updated {len(rows)-1} users in {tab_name} tab")
    
    def _update_master_sheet_links(self, master_sheet_id: str, annotator_stats: Dict, 
                                  reviewer_stats: Dict, user_sheet_ids: Dict):
        """Update master sheet with correct hyperlinks to user sheets"""
        try:
            sheet = self._api_call_with_retry(self.client.open_by_key, master_sheet_id, 
                                            operation_name="opening master sheet for link updates")
        except:
            print(f"Error: Could not open master sheet for link updates")
            return
        
        # Update Annotators tab links
        try:
            worksheet = sheet.worksheet("Annotators")
            row_num = 2  # Start from row 2 (after headers)
            
            for user_name, stats in annotator_stats.items():
                if self._has_activity(stats):
                    annotation_sheet_name = f"{user_name} Annotator"
                    review_sheet_name = f"{user_name} Reviewer"
                    
                    # Create hyperlink formulas with actual sheet URLs
                    annotation_sheet_id = user_sheet_ids.get(annotation_sheet_name)
                    review_sheet_id = user_sheet_ids.get(review_sheet_name)
                    
                    if annotation_sheet_id:
                        annotation_url = f"https://docs.google.com/spreadsheets/d/{annotation_sheet_id}/edit"
                        annotation_link = f'=HYPERLINK("{annotation_url}","🔗")'
                    else:
                        annotation_link = "🔗 Link"
                    
                    if review_sheet_id:
                        review_url = f"https://docs.google.com/spreadsheets/d/{review_sheet_id}/edit"
                        review_link = f'=HYPERLINK("{review_url}","🔗")'
                    else:
                        review_link = "🔗 Link"
                    
                    # Update the links in columns C and E
                    self._api_call_with_retry(worksheet.update, f'C{row_num}', [[annotation_link]], 
                                            operation_name=f"updating annotation link for {user_name}")
                    self._api_call_with_retry(worksheet.update, f'E{row_num}', [[review_link]], 
                                            operation_name=f"updating review link for {user_name}")
                    row_num += 1
            
            print("    ✅ Updated Annotators tab links")
        except Exception as e:
            print(f"    ❌ Failed to update Annotators tab links: {e}")
        
        # Update Reviewers tab links
        try:
            worksheet = sheet.worksheet("Reviewers")
            row_num = 2  # Start from row 2 (after headers)
            
            for user_name, stats in reviewer_stats.items():
                if self._has_activity(stats):
                    annotation_sheet_name = f"{user_name} Annotator"
                    review_sheet_name = f"{user_name} Reviewer"
                    
                    # Create hyperlink formulas with actual sheet URLs
                    annotation_sheet_id = user_sheet_ids.get(annotation_sheet_name)
                    review_sheet_id = user_sheet_ids.get(review_sheet_name)
                    
                    if annotation_sheet_id:
                        annotation_url = f"https://docs.google.com/spreadsheets/d/{annotation_sheet_id}/edit"
                        annotation_link = f'=HYPERLINK("{annotation_url}","🔗")'
                    else:
                        annotation_link = "🔗 Link"
                    
                    if review_sheet_id:
                        review_url = f"https://docs.google.com/spreadsheets/d/{review_sheet_id}/edit"
                        review_link = f'=HYPERLINK("{review_url}","🔗")'
                    else:
                        review_link = "🔗 Link"
                    
                    # Update the links in columns C and E
                    self._api_call_with_retry(worksheet.update, f'C{row_num}', [[annotation_link]], 
                                            operation_name=f"updating annotation link for {user_name}")
                    self._api_call_with_retry(worksheet.update, f'E{row_num}', [[review_link]], 
                                            operation_name=f"updating review link for {user_name}")
                    row_num += 1
            
            print("    ✅ Updated Reviewers tab links")
        except Exception as e:
            print(f"    ❌ Failed to update Reviewers tab links: {e}")
    
    def _export_user_sheet(self, user_name: str, role: str, stats: Dict, task_names: List[str], master_sheet_id: str) -> str:
        """Export individual user sheet and return sheet ID"""
        sheet_name = f"{user_name} {role}"
        print(f"  Exporting {sheet_name} sheet...")
        
        try:
            # Try to open existing sheet (don't use retry logic here since failure is expected)
            sheet = self.client.open(sheet_name)
            print(f"    Found existing sheet: {sheet_name}")
        except (gspread.exceptions.SpreadsheetNotFound, Exception):
            # Create new sheet
            print(f"    Creating new sheet: {sheet_name}")
            sheet = self._api_call_with_retry(self.client.create, sheet_name, 
                                            operation_name=f"creating sheet '{sheet_name}'")
        
        # Export Payment tab
        self._export_user_tab(sheet, "Payment", user_name, role, stats, task_names, include_payment=True)
        
        # Export Feedback tab
        self._export_user_tab(sheet, "Feedback", user_name, role, stats, task_names, include_payment=False)
        
        return sheet.id
    
    def _export_user_tab(self, sheet, tab_name: str, user_name: str, role: str, stats: Dict, 
                        task_names: List[str], include_payment: bool):
        """Export a single tab in a user sheet with multi-row headers"""
        print(f"    Exporting {tab_name} tab...")
        
        try:
            worksheet = sheet.worksheet(tab_name)
            print(f"      Found existing {tab_name} tab")
        except gspread.exceptions.WorksheetNotFound:
            print(f"      Creating new {tab_name} tab...")
            worksheet = self._api_call_with_retry(sheet.add_worksheet, title=tab_name, rows=100, cols=50, 
                                                operation_name=f"creating {tab_name} worksheet")
        except Exception as e:
            print(f"      Error accessing {tab_name} tab: {e}")
            print(f"      Creating new {tab_name} tab...")
            worksheet = self._api_call_with_retry(sheet.add_worksheet, title=tab_name, rows=100, cols=50, 
                                                operation_name=f"creating {tab_name} worksheet")
        
        # Clear worksheet
        self._api_call_with_retry(worksheet.clear, operation_name="clearing worksheet")
        
        # Prepare multi-row headers
        if role == "Annotator":
            self._create_annotator_headers(worksheet, task_names, include_payment)
        else:  # Reviewer
            self._create_reviewer_headers(worksheet, task_names, include_payment)
        
        # Prepare data rows (starting from row 3)
        data_rows = []
        
        # Add rows for each video file
        for video_file, file_stats in stats['per_video_file'].items():
            if file_stats.get('completed_current_user', 0) > 0 or file_stats.get('reviewed_by_current_user', 0) > 0:
                row = self._create_data_row(video_file, file_stats, stats, task_names, role, include_payment)
                data_rows.append(row)
        
        # Update data rows
        if data_rows:
            # Helper function to convert column number to Excel-style letter
            def col_num_to_letter(col_num):
                result = ""
                while col_num > 0:
                    col_num -= 1
                    result = chr(col_num % 26 + ord('A')) + result
                    col_num //= 26
                return result
            
            start_row = 3
            end_row = start_row + len(data_rows) - 1
            end_col = col_num_to_letter(len(data_rows[0]))
            self._api_call_with_retry(worksheet.update, f'A{start_row}:{end_col}{end_row}', data_rows, 
                                    operation_name=f"updating {len(data_rows)} data rows")
            print(f"      ✅ Successfully updated {len(data_rows)} rows in {tab_name} tab")
        else:
            print(f"      ℹ️  No data to update in {tab_name} tab")
    
    def _create_annotator_headers(self, worksheet, task_names: List[str], include_payment: bool):
        """Create multi-row headers for annotator sheets"""
        # Helper function to convert column number to Excel-style letter
        def col_num_to_letter(col_num):
            result = ""
            while col_num > 0:
                col_num -= 1
                result = chr(col_num % 26 + ord('A')) + result
                col_num //= 26
            return result
        
        # Row 1 headers
        row1 = ["Json Sheet Name", "Completion Ratio", "", "Reviewed Ratio", "", "Last Submitted Timestamp"]
        
        if include_payment:
            row1.extend(["Payment Timestamp", "Base Salary", "Bonus Salary"])
        else:
            row1.append("Feedback to Annotator")
        
        # Add task headers
        for task_name in task_names:
            short_name = self.config_names_to_short_names.get(task_name, task_name)
            row1.extend([short_name, "", "", "", "", ""])  # 6 columns per task
        
        # Row 2 headers
        row2 = ["", "All Users", "Current User", "All Users", "Current User", ""]
        
        if include_payment:
            row2.extend(["", "", ""])
        else:
            row2.append("")
        
        # Add task sub-headers
        for _ in task_names:
            row2.extend(["Accuracy", "Completion", "Reviewed", "Completed", "Reviewed", "Rejected"])
        
        # Update all headers at once to avoid range issues
        if len(row1) > 0:
            end_col = col_num_to_letter(len(row1))
            self._api_call_with_retry(worksheet.update, f'A1:{end_col}2', [row1, row2], 
                                    operation_name="updating headers")
    
    def _create_reviewer_headers(self, worksheet, task_names: List[str], include_payment: bool):
        """Create multi-row headers for reviewer sheets"""
        # Helper function to convert column number to Excel-style letter
        def col_num_to_letter(col_num):
            result = ""
            while col_num > 0:
                col_num -= 1
                result = chr(col_num % 26 + ord('A')) + result
                col_num //= 26
            return result
        
        # Row 1 headers
        row1 = ["Json Sheet Name", "Completion Ratio", "Reviewed Ratio", "", "Last Submitted Timestamp"]
        
        if include_payment:
            row1.extend(["Payment Timestamp", "Base Salary", "Bonus Salary"])
        else:
            row1.append("Feedback to Annotator")
        
        # Add task headers
        for task_name in task_names:
            short_name = self.config_names_to_short_names.get(task_name, task_name)
            row1.extend([short_name, ""])  # 2 columns per task
        
        # Row 2 headers
        row2 = ["", "All Users", "All Users", "Current User", ""]
        
        if include_payment:
            row2.extend(["", "", ""])
        else:
            row2.append("")
        
        # Add task sub-headers
        for _ in task_names:
            row2.extend(["Completion", "Completed"])
        
        # Update all headers at once to avoid range issues
        if len(row1) > 0:
            end_col = col_num_to_letter(len(row1))
            self._api_call_with_retry(worksheet.update, f'A1:{end_col}2', [row1, row2], 
                                    operation_name="updating headers")
    
    def _create_data_row(self, video_file: str, file_stats: Dict, user_stats: Dict, 
                        task_names: List[str], role: str, include_payment: bool) -> List:
        """Create a data row for a video file"""
        row = [video_file]
        
        # Add completion and reviewed ratios
        total_possible = file_stats['total_possible']
        completed_all = file_stats['completed_all_users']
        reviewed_all = file_stats['reviewed_all_users']
        
        if role == "Annotator":
            completed_current = file_stats['completed_current_user']
            reviewed_current = file_stats['reviewed_current_user_work']
            
            completion_ratio_all = completed_all / total_possible if total_possible > 0 else 0
            completion_ratio_current = completed_current / total_possible if total_possible > 0 else 0
            reviewed_ratio_all = reviewed_all / completed_all if completed_all > 0 else 0
            reviewed_ratio_current = reviewed_current / completed_current if completed_current > 0 else 0
            
            row.extend([
                f"{completion_ratio_all:.2%}",
                f"{completion_ratio_current:.2%}",
                f"{reviewed_ratio_all:.2%}",
                f"{reviewed_ratio_current:.2%}"
            ])
            
            # Last submitted timestamp (annotation timestamp)
            timestamp = file_stats.get('last_annotation_timestamp', '')
        else:  # Reviewer
            reviewed_current = file_stats['reviewed_by_current_user']
            
            completion_ratio_all = completed_all / total_possible if total_possible > 0 else 0
            reviewed_ratio_all = reviewed_all / completed_all if completed_all > 0 else 0
            reviewed_ratio_current = reviewed_current / completed_all if completed_all > 0 else 0
            
            row.extend([
                f"{completion_ratio_all:.2%}",
                f"{reviewed_ratio_all:.2%}",
                f"{reviewed_ratio_current:.2%}"
            ])
            
            # Last submitted timestamp (review timestamp)
            timestamp = file_stats.get('last_review_timestamp', '')
        
        # Format timestamp
        formatted_timestamp = self._format_timestamp(timestamp)
        row.append(formatted_timestamp)
        
        # Add placeholders for manual columns
        if include_payment:
            row.extend(['', '', ''])  # Payment Timestamp, Base Salary, Bonus Salary
        else:
            row.append('')  # Feedback to Annotator
        
        # Add per-task statistics
        for task_name in task_names:
            task_stats = user_stats['per_task'][task_name]
            if role == "Annotator":
                # Calculate task-specific ratios
                accuracy = ((task_stats['reviewed'] - task_stats['rejected']) / task_stats['reviewed'] 
                           if task_stats['reviewed'] > 0 else 0)
                completion_ratio = task_stats['completed'] / task_stats['total'] if task_stats['total'] > 0 else 0
                reviewed_ratio = task_stats['reviewed'] / task_stats['completed'] if task_stats['completed'] > 0 else 0
                
                row.extend([
                    f"{accuracy:.2%}",
                    f"{completion_ratio:.2%}",
                    f"{reviewed_ratio:.2%}",
                    task_stats['completed'],
                    task_stats['reviewed'],
                    task_stats['rejected']
                ])
            else:  # Reviewer
                completion_ratio = task_stats['reviewed'] / task_stats['total'] if task_stats['total'] > 0 else 0
                row.extend([
                    f"{completion_ratio:.2%}",
                    task_stats['reviewed']
                ])
        
        return row
    
    def _format_timestamp(self, timestamp: str) -> str:
        """Format timestamp to readable format"""
        if not timestamp:
            return ''
        try:
            dt = datetime.fromisoformat(timestamp)
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            return timestamp


def main():
    """Main function with config support"""
    parser = argparse.ArgumentParser(description="Export caption statistics to Google Sheets")
    parser.add_argument("--config-type", type=str, default="main", 
                       choices=["main", "lighting"],
                       help="Configuration type to use")
    parser.add_argument("--master-sheet-id", type=str, required=True,
                       help="Google Sheet ID for the master sheet")
    
    args = parser.parse_args()
    
    # Get configuration
    app_config = get_config(args.config_type)
    
    # Setup paths
    credentials_file = Path("caption/credentials.json")
    folder_path = Path("caption")
    root_path = Path(".")
    
    # Create exporter and run
    exporter = GoogleSheetExporter(str(credentials_file), folder_path, root_path)
    exporter.export_all_sheets(
        configs_file=app_config.configs_file,
        video_urls_files=app_config.video_urls_files,
        output_dir=app_config.output_dir,
        master_sheet_id=args.master_sheet_id
    )
    
    print(f"Export completed for config type: {args.config_type}")


if __name__ == "__main__":
    main()