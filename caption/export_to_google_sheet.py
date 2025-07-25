# caption/export_to_google_sheet.py
import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime
from pathlib import Path
import argparse

from caption.config import get_config
from caption.core.data_manager import DataManager
from caption.core.auth import load_annotators_from_files, APPROVED_REVIEWERS


class GoogleSheetExporter:
    """Export caption statistics to Google Sheets"""
    
    def __init__(self, credentials_file: str, folder_path: Path, root_path: Path = None):
        """
        Initialize the exporter with Google Sheets credentials
        
        Args:
            credentials_file: Path to Google Service Account JSON credentials
            folder_path: Caption folder path
            root_path: Project root path
        """
        self.data_manager = DataManager(folder_path, root_path)
        
        # Setup Google Sheets authentication
        scope = ['https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive']
        self.creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, scope)
        self.client = gspread.authorize(self.creds)
        
        # Load annotators and get task names
        self.annotators = load_annotators_from_files()
        self.approved_reviewers = APPROVED_REVIEWERS
        
        # Configuration mapping
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
        self._export_master_sheet(master_sheet_id, annotator_stats, reviewer_stats, task_names)
        
        # Export individual user sheets
        for user_name, stats in annotator_stats.items():
            if self._has_activity(stats):
                self._export_user_sheet(user_name, "Annotator", stats, task_names, master_sheet_id)
            
        for user_name, stats in reviewer_stats.items():
            if self._has_activity(stats):
                self._export_user_sheet(user_name, "Reviewer", stats, task_names, master_sheet_id)
    
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
                
                # Update timestamps
                if user_file_stats['last_annotation_timestamp']:
                    current_ts = annotator_stats[user_name]['last_annotation_timestamp']
                    if not current_ts or user_file_stats['last_annotation_timestamp'] > current_ts:
                        annotator_stats[user_name]['last_annotation_timestamp'] = user_file_stats['last_annotation_timestamp']
                
                if user_file_stats['last_review_timestamp']:
                    current_ts = annotator_stats[user_name]['last_review_timestamp']
                    if not current_ts or user_file_stats['last_review_timestamp'] > current_ts:
                        annotator_stats[user_name]['last_review_timestamp'] = user_file_stats['last_review_timestamp']
            
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
                
                # Update timestamps
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
            'reviewers': {}
        }
        
        for video_url in video_urls:
            video_id = self.data_manager.get_video_id(video_url)
            
            for config in configs:
                config_output_dir = os.path.join(self.data_manager.folder, output_dir, config["output_name"])
                
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
                    
                    stats['annotators'][annotator]['completed_current_user'] += 1
                    
                    # Update timestamps
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
                    
                    # Check if reviewed
                    if status in ["approved", "rejected"]:
                        stats['annotators'][annotator]['reviewed_current_user_work'] += 1
                        
                        # Update review timestamp
                        review_file = self.data_manager.get_filename(video_id, config_output_dir, 
                                                                   self.data_manager.REVIEWER_FILE_POSTFIX)
                        if os.path.exists(review_file):
                            try:
                                with open(review_file, 'r') as f:
                                    data = json.load(f)
                                    timestamp = data.get('review_timestamp')
                                    if timestamp:
                                        current_ts = stats['annotators'][annotator]['last_review_timestamp']
                                        if not current_ts or timestamp > current_ts:
                                            stats['annotators'][annotator]['last_review_timestamp'] = timestamp
                            except:
                                pass
                
                # Update reviewer stats
                if reviewer:
                    if reviewer not in stats['reviewers']:
                        stats['reviewers'][reviewer] = {
                            'reviewed_by_current_user': 0,
                            'last_review_timestamp': None
                        }
                    
                    stats['reviewers'][reviewer]['reviewed_by_current_user'] += 1
                    
                    # Update review timestamp
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
            sheet = self.client.open_by_key(sheet_id)
        except:
            print(f"Error: Could not open sheet with ID {sheet_id}")
            return
        
        # Export Annotators tab
        self._export_master_tab(sheet, "Annotators", annotator_stats, task_names, "Annotator")
        
        # Export Reviewers tab  
        self._export_master_tab(sheet, "Reviewers", reviewer_stats, task_names, "Reviewer")
    
    def _export_master_tab(self, sheet, tab_name: str, user_stats: Dict, task_names: List[str], role: str):
        """Export a single tab in the master sheet"""
        try:
            worksheet = sheet.worksheet(tab_name)
        except:
            worksheet = sheet.add_worksheet(title=tab_name, rows=100, cols=20)
        
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
                # Create links to individual sheets
                annotation_sheet_name = f"{user_name} Annotator"
                review_sheet_name = f"{user_name} Reviewer"
                
                annotation_link = f'=HYPERLINK("https://docs.google.com/spreadsheets/", "🔗")'
                review_link = f'=HYPERLINK("https://docs.google.com/spreadsheets/", "🔗")'
                
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
        worksheet.clear()
        if rows:
            worksheet.update(f'A1:{chr(65 + len(headers) - 1)}{len(rows)}', rows)
    
    def _export_user_sheet(self, user_name: str, role: str, stats: Dict, task_names: List[str], master_sheet_id: str):
        """Export individual user sheet"""
        sheet_name = f"{user_name} {role}"
        
        try:
            # Try to open existing sheet
            sheet = self.client.open(sheet_name)
        except:
            # Create new sheet
            sheet = self.client.create(sheet_name)
            # Share with the same permissions as master sheet (optional)
        
        # Export Payment tab
        self._export_user_tab(sheet, "Payment", user_name, role, stats, task_names, include_payment=True)
        
        # Export Feedback tab
        self._export_user_tab(sheet, "Feedback", user_name, role, stats, task_names, include_payment=False)
    
    def _export_user_tab(self, sheet, tab_name: str, user_name: str, role: str, stats: Dict, 
                        task_names: List[str], include_payment: bool):
        """Export a single tab in a user sheet with multi-row headers"""
        try:
            worksheet = sheet.worksheet(tab_name)
        except:
            worksheet = sheet.add_worksheet(title=tab_name, rows=100, cols=50)
        
        # Clear worksheet
        worksheet.clear()
        
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
            start_row = 3
            end_row = start_row + len(data_rows) - 1
            end_col = chr(65 + len(data_rows[0]) - 1)
            worksheet.update(f'A{start_row}:{end_col}{end_row}', data_rows)
    
    def _create_annotator_headers(self, worksheet, task_names: List[str], include_payment: bool):
        """Create multi-row headers for annotator sheets"""
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
        
        # Update headers
        worksheet.update('A1:A1', [[row1[0]]])  # Json Sheet Name
        worksheet.update('B1:C1', [["Completion Ratio"]])
        worksheet.update('D1:E1', [["Reviewed Ratio"]])
        worksheet.update('F1:F1', [["Last Submitted Timestamp"]])
        
        start_col = 7 if include_payment else 8  # Adjust based on payment columns
        col_offset = 3 if include_payment else 1
        
        # Update payment/feedback headers
        if include_payment:
            worksheet.update('G1:I1', [["Payment Timestamp", "Base Salary", "Bonus Salary"]])
        else:
            worksheet.update('G1:G1', [["Feedback to Annotator"]])
        
        # Update task headers with merging
        for i, task_name in enumerate(task_names):
            short_name = self.config_names_to_short_names.get(task_name, task_name)
            start_col_letter = chr(65 + start_col + col_offset + i * 6)
            end_col_letter = chr(65 + start_col + col_offset + i * 6 + 5)
            worksheet.update(f'{start_col_letter}1:{end_col_letter}1', [[short_name, "", "", "", "", ""]])
        
        # Update row 2
        worksheet.update(f'A2:{chr(65 + len(row2) - 1)}2', [row2])
    
    def _create_reviewer_headers(self, worksheet, task_names: List[str], include_payment: bool):
        """Create multi-row headers for reviewer sheets"""
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
        
        # Update headers (similar logic but with 2 columns per task)
        worksheet.update('A1:A1', [[row1[0]]])
        worksheet.update('B1:B1', [["Completion Ratio"]])
        worksheet.update('C1:D1', [["Reviewed Ratio"]])
        worksheet.update('E1:E1', [["Last Submitted Timestamp"]])
        
        # Update payment/feedback and task headers...
        # (Similar to annotator but with 2 columns per task)
        
        # Update row 2
        worksheet.update(f'A2:{chr(65 + len(row2) - 1)}2', [row2])
    
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
    credentials_file = Path("caption/google_keys.json")
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