"""
Session management utilities
"""
import uuid
from flask import session


def initialize_session(group=None):
    """Initialize a new user session with unique IDs
    
    Args:
        group: User group number (1-6), if provided
    """
    from database import get_next_user_id
    
    # Set group
    session['group'] = group if group is not None else 1
    
    # Always generate new user_id and session_id
    user_group = session['group']
    session['user_id'] = get_next_user_id(user_group)
    session['session_id'] = str(uuid.uuid4())
    session['round'] = 1
    session['round1_completed'] = False
    
    # Clear all other session data
    for key in ('playlist', 'current_index', 'likes', 'comments', 'shown_videos'):
        session.pop(key, None)


def get_user_info():
    """Get current user information from session
    
    Returns:
        Dictionary with user_id, session_id, round, and group
    """
    return {
        'user_id': session.get('user_id'),
        'session_id': session.get('session_id'),
        'round': session.get('round', 1),
        'group': session.get('group', 1)
    }


def update_likes(video_id, action):
    """Update like status for a video
    
    Args:
        video_id: Video identifier
        action: 'like' or 'dislike'
        
    Returns:
        New like status (or None if toggled off)
    """
    likes = session.get('likes', {})
    current_status = likes.get(video_id)
    
    # Toggle: remove if clicking same button, otherwise set new action
    likes[video_id] = None if current_status == action else action
    
    session['likes'] = likes
    session.modified = True
    
    return likes[video_id]


def add_comment(video_id, comment_text):
    """Add a comment to a video
    
    Args:
        video_id: Video identifier
        comment_text: Comment text
        
    Returns:
        Number of comments for this video
    """
    comments = session.get('comments', {})
    comments.setdefault(video_id, []).append(comment_text)
    session['comments'] = comments
    session.modified = True
    
    return len(comments[video_id])


def get_video_interactions(video_id):
    """Get like status and comments for a video
    
    Args:
        video_id: Video identifier
        
    Returns:
        Tuple of (like_status, comments_list)
    """
    likes = session.get('likes', {})
    comments = session.get('comments', {})
    
    return likes.get(video_id), comments.get(video_id, [])


def increment_round():
    """Increment the experiment round counter and save shown videos"""
    current_round = session.get('round', 1)
    if current_round == 1:
        # Save videos from round 1 before incrementing
        playlist = session.get('playlist', [])
        shown_videos = session.get('shown_videos', {})
        shown_videos[1] = [video['id'] for video in playlist]
        session['shown_videos'] = shown_videos
        session.modified = True
        session['round'] = 2
        session['round1_completed'] = False


def get_shown_video_ids():
    """Get list of video IDs already shown in previous rounds
    
    Returns:
        Set of video IDs shown in previous rounds
    """
    shown_videos = session.get('shown_videos', {})
    return {video_id for video_ids in shown_videos.values() for video_id in video_ids}


def calculate_watch_stats(watch_duration, video_total_duration, video_id):
    """Calculate watch statistics for a video
    
    Args:
        watch_duration: Time watched in seconds
        video_total_duration: Total video duration
        video_id: Video identifier
        
    Returns:
        Dictionary with completion_rate, liked, and comment_text
    """
    # Calculate completion rate
    completion_rate = (watch_duration / video_total_duration * 100) if video_total_duration > 0 else 0
    
    # Get like status
    likes = session.get('likes', {})
    like_status = likes.get(video_id)
    liked = 1 if like_status == 'like' else (-1 if like_status == 'dislike' else 0)
    
    # Get comments
    comments = session.get('comments', {})
    video_comments = comments.get(video_id, [])
    comment_text = '; '.join(video_comments) if video_comments else None
    
    return {
        'completion_rate': completion_rate,
        'liked': liked,
        'comment_text': comment_text
    }
