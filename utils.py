"""
Statistics calculation utilities
"""


def calculate_summary_statistics(category_stats):
    """Calculate summary statistics from database results
    
    Args:
        category_stats: List of database rows with category statistics
        
    Returns:
        Dictionary with formatted statistics
    """
    # Calculate totals
    total_watch_time = sum(row['total_duration'] for row in category_stats)
    total_videos = sum(row['video_count'] for row in category_stats)
    
    # Format time as minutes and seconds
    minutes = int(total_watch_time // 60)
    seconds = int(total_watch_time % 60)
    
    # Calculate percentages for each category
    category_data = []
    for row in category_stats:
        percentage = (row['total_duration'] / total_watch_time * 100) if total_watch_time > 0 else 0
        category_data.append({
            'name': row['video_category'],
            'duration': row['total_duration'],
            'percentage': round(percentage, 2),
            'video_count': row['video_count']
        })
    
    # Sort by percentage (highest first)
    category_data.sort(key=lambda x: x['percentage'], reverse=True)
    
    return {
        'total_videos': total_videos,
        'total_minutes': minutes,
        'total_seconds': seconds,
        'category_data': category_data
    }
