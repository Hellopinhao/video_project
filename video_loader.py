"""
Video loading and playlist management
"""
import os
import random
import logging
import pandas as pd
from config import EXCEL_FILE, VIDEO_DIR, CATEGORY_MAPPING, ROUND_VIDEO_COUNTS


class VideoLoader:
    """Handle video loading and playlist generation"""
    
    def __init__(self):
        self.videos_by_category = self._load_videos_from_excel()
    
    def _load_videos_from_excel(self):
        """Load videos from Excel file and verify local files exist
        
        Returns:
            Dictionary mapping categories to lists of video data
        """
        videos_by_category = {}
        
        if not os.path.exists(EXCEL_FILE):
            logging.warning("Excel file not found at %s", EXCEL_FILE)
            return videos_by_category

        try:
            df = pd.read_excel(EXCEL_FILE)
        except Exception:
            logging.exception("Failed to read Excel file: %s", EXCEL_FILE)
            return videos_by_category

        required_columns = {'id', 'title', 'duration', 'Tags', 'category'}
        missing_columns = required_columns - set(df.columns)
        if missing_columns:
            logging.error("Missing required columns in Excel file: %s", ", ".join(sorted(missing_columns)))
            return videos_by_category
        
        for _, row in df.iterrows():
            category = row['category']
            if pd.isna(category):
                continue
            category = str(category)
            if category not in videos_by_category:
                videos_by_category[category] = []
            
            video_id = str(row['id'])
            video_filename = f"{video_id}.mp4"
            video_path = os.path.join(VIDEO_DIR, video_filename)
            
            # Only add video if file exists locally
            if os.path.exists(video_path):
                videos_by_category[category].append({
                    'id': video_id,
                    'title': str(row['title']),
                    'filename': video_filename,
                    'duration': str(row['duration']),
                    'tags': str(row['Tags']),
                    'category': category
                })
        
        return videos_by_category
    
    def create_playlist(self, selected_categories, current_round=1, excluded_video_ids=None):
        """Create a playlist based on selected categories and round
        
        Args:
            selected_categories: List of dicts with 'name' and 'preference'
            current_round: Current experiment round (1 or 2)
            excluded_video_ids: Set of video IDs to exclude (from previous rounds)
            
        Returns:
            List of video objects for the playlist
        """
        if excluded_video_ids is None:
            excluded_video_ids = set()
        
        video_counts = ROUND_VIDEO_COUNTS.get(current_round, [10, 6, 4])
        playlist = []
        
        for idx, cat_info in enumerate(selected_categories[:3]):
            chinese_name = cat_info['name']
            csv_category = CATEGORY_MAPPING.get(chinese_name)
            
            if csv_category and csv_category in self.videos_by_category:
                # Filter out excluded videos from previous rounds
                videos = self.videos_by_category[csv_category]
                available_videos = [v for v in videos if v['id'] not in excluded_video_ids]
                
                num_videos = min(video_counts[idx], len(available_videos))
                
                if num_videos > 0:
                    selected_videos = random.sample(available_videos, num_videos)
                    for video in selected_videos:
                        video_copy = dict(video)
                        video_copy['chinese_category'] = chinese_name
                        playlist.append(video_copy)
        
        # Shuffle for variety
        random.shuffle(playlist)
        return playlist
    
    def get_video_count_by_category(self):
        """Get count of available videos per category
        
        Returns:
            Dictionary mapping categories to video counts
        """
        return {cat: len(videos) for cat, videos in self.videos_by_category.items()}


# Global video loader instance
video_loader = VideoLoader()
