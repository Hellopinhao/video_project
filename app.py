"""
Flask application for video viewing experiment
"""
from __future__ import annotations

from typing import Any

from flask import Flask, render_template, request, redirect, session, jsonify, send_from_directory, url_for
import config
from database import (
    init_db,
    save_category_selection,
    save_watch_log,
    get_session_statistics,
    save_summary_page_duration,
)
from video_loader import video_loader
from session_manager import (
    initialize_session, get_user_info, update_likes, 
    add_comment as add_comment_to_session, get_video_interactions,
    increment_round, calculate_watch_stats, get_shown_video_ids
)
from utils import calculate_summary_statistics


VALID_GROUPS = {1, 2, 3, 4, 5, 6, 7}
EMPTY_SUMMARY_STATS = {
    'total_videos': 0,
    'total_minutes': 0,
    'total_seconds': 0,
    'category_data': []
}

# Initialize Flask app
app = Flask(__name__)
app.secret_key = config.SECRET_KEY

# Initialize database on startup
init_db()


def _get_json_payload() -> dict[str, Any]:
    """Safely read JSON payload from request."""
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else {}


def _to_float(value: Any, default: float = 0.0) -> float:
    """Best-effort float conversion with fallback."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _to_int(value: Any, default: int = 0) -> int:
    """Best-effort int conversion with fallback."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _get_selected_categories() -> list[dict[str, int | str]]:
    """Read and rank selected categories from form data."""
    selected = [
        {'name': category, 'preference': score}
        for category in config.CATEGORY_MAPPING
        if (score := _to_int(request.form.get(category), 0)) > 0
    ]
    return sorted(selected, key=lambda item: item['preference'], reverse=True)[:3]


def _has_identity(user_info: dict[str, Any]) -> bool:
    return bool(user_info.get('user_id')) and bool(user_info.get('session_id'))


def _summary_template_name(group: int) -> str:
    """Resolve group-specific summary template name."""
    return f'summary_group{group}.html' if group in VALID_GROUPS else 'summary_group1.html'


# ==================== Routes ====================

@app.route('/')
def index():
    """Welcome/instruction page - default to group 1"""
    initialize_session(group=1)
    return render_template('welcome.html')


@app.route('/group<int:group_num>')
def group_entry(group_num):
    """Group-specific entry point"""
    if group_num not in VALID_GROUPS:
        return redirect(url_for('index'))
    
    initialize_session(group=group_num)
    return render_template('welcome.html', group=group_num)


@app.route('/categories')
def categories():
    """Category selection page with sliders"""
    user_info = get_user_info()
    return render_template('categories.html', 
                         categories=list(config.CATEGORY_MAPPING),
                         current_round=user_info['round'])


@app.route('/select_categories', methods=['POST'])
def select_categories():
    """Process category selection and build video playlist"""
    top_3 = _get_selected_categories()

    if len(top_3) != 3:
        app.logger.warning("Rejected category selection with less than 3 positive preferences")
        return redirect(url_for('categories'))

    preferences = [item['preference'] for item in top_3]
    if len(set(preferences)) != len(preferences):
        app.logger.warning("Rejected category selection with duplicate preference values")
        return redirect(url_for('categories'))
    
    # Get user info
    user_info = get_user_info()
    if user_info['round'] == 1 and session.get('round1_completed'):
        increment_round()
        user_info = get_user_info()

    current_round = user_info['round']
    
    # Get previously shown video IDs to exclude
    excluded_video_ids = get_shown_video_ids() if current_round > 1 else set()
    
    # Build playlist based on current round
    playlist = video_loader.create_playlist(top_3, current_round, excluded_video_ids)
    
    # Store in session
    session['playlist'] = playlist
    session['current_index'] = 0
    session['likes'] = {}
    session['comments'] = {}
    
    # Save category selection to database
    try:
        save_category_selection(
            user_info['user_id'],
            user_info['session_id'],
            top_3,
            user_info['group'],
            current_round,
        )
    except Exception:
        app.logger.exception("Failed to save category selection")
    
    return redirect(url_for('play_video', index=0))


@app.route('/play_video/<int:index>')
def play_video(index):
    """Video player page"""
    playlist = session.get('playlist', [])
    
    if not playlist or index < 0 or index >= len(playlist):
        return redirect(url_for('categories'))
    
    video = playlist[index]
    video_id = video['id']
    
    # Get like/dislike status
    like_status, _ = get_video_interactions(video_id)
    user_info = get_user_info()
    
    return render_template('play_video.html', 
                         video=video,
                         index=index,
                         total=len(playlist),
                         like_status=like_status,
                         current_round=user_info['round'])


@app.route('/videos/<filename>')
def serve_video(filename):
    """Serve video files from local directory"""
    return send_from_directory(config.VIDEO_DIR, filename)


@app.route('/like_video', methods=['POST'])
def like_video():
    """Handle like/dislike actions"""
    data = _get_json_payload()
    video_id = str(data.get('video_id', '')).strip()
    action = data.get('action')

    if not video_id or action not in {'like', 'dislike'}:
        return jsonify({'success': False, 'error': 'Invalid payload'}), 400
    
    status = update_likes(video_id, action)
    
    return jsonify({'success': True, 'status': status})


@app.route('/add_comment', methods=['POST'])
def add_comment():
    """Add comment to video"""
    data = _get_json_payload()
    video_id = str(data.get('video_id', '')).strip()
    comment_text = data.get('comment', '').strip()
    
    if not video_id or not comment_text:
        return jsonify({'success': False, 'error': 'Invalid payload'}), 400
    
    comment_count = add_comment_to_session(video_id, comment_text)
    
    return jsonify({'success': True, 'comment_count': comment_count})


@app.route('/save_watch_duration', methods=['POST'])
def save_watch_duration():
    """Save video watch duration to database"""
    data = _get_json_payload()
    
    # Get user and video info
    user_info = get_user_info()
    if not _has_identity(user_info):
        app.logger.warning("save_watch_duration rejected due to missing session identity")
        return jsonify({'success': False, 'error': 'Session expired'}), 401

    video_id = str(data.get('video_id', '')).strip()
    if not video_id:
        return jsonify({'success': False, 'error': 'Missing video_id'}), 400

    video_data = {
        'video_id': video_id,
        'video_title': str(data.get('video_title', '')),
        'video_category': str(data.get('video_category', '')),
        'video_index': _to_int(data.get('video_index'), 0),
        'video_total_duration': _to_int(data.get('video_total_duration'), 0)
    }
    
    watch_duration = _to_float(data.get('watch_duration'), 0.0)
    
    # Calculate watch statistics
    watch_stats = calculate_watch_stats(
        watch_duration, 
        video_data['video_total_duration'], 
        video_data['video_id']
    )
    
    # Save to database
    try:
        save_watch_log(
            user_info['user_id'],
            user_info['session_id'],
            user_info['round'],
            video_data,
            watch_duration,
            watch_stats['completion_rate'],
            watch_stats['liked'],
            watch_stats['comment_text'],
            user_info['group']
        )
        return jsonify({'success': True})
    except Exception as e:
        app.logger.exception("Failed to save watch duration")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/save_summary_duration', methods=['POST'])
def save_summary_duration():
    """Save round-1 summary page watched duration."""
    data = _get_json_payload()
    user_info = get_user_info()
    if not _has_identity(user_info):
        app.logger.warning("save_summary_duration rejected due to missing session identity")
        return jsonify({'success': False, 'error': 'Session expired'}), 401

    round_num = _to_int(data.get('round'), 1)
    duration_seconds = _to_float(data.get('duration_seconds'), 0.0)

    if round_num != 1 or duration_seconds < 0:
        return jsonify({'success': False, 'error': 'Invalid payload'}), 400

    try:
        save_summary_page_duration(
            user_info['user_id'],
            user_info['session_id'],
            round_num,
            duration_seconds,
            user_info['group'],
        )
        return jsonify({'success': True})
    except Exception as e:
        app.logger.exception("Failed to save summary duration")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/summary')
def summary():
    """Show viewing summary after all videos are watched"""
    user_info = get_user_info()
    playlist = session.get('playlist', [])
    
    if not user_info['user_id'] or not playlist:
        return redirect(url_for('index'))
    
    current_round = user_info['round']
    user_group = user_info['group']
    
    # Get statistics from database
    try:
        category_stats = get_session_statistics(user_info['session_id'], current_round)
        stats = calculate_summary_statistics(category_stats)
    except Exception:
        app.logger.exception("Failed to calculate session statistics")
        stats = EMPTY_SUMMARY_STATS
    
    is_final = (current_round == 2)

    if current_round == 1:
        session['round1_completed'] = True
        session.modified = True

    template_name = 'summary_round2.html' if is_final else _summary_template_name(user_group)

    return render_template(template_name,
                         **stats,
                         current_round=current_round,
                         user_id=user_info['user_id'],
                         user_group=user_group,
                         is_final=is_final)


if __name__ == '__main__':
    app.run(debug=config.DEBUG, host=config.HOST, port=config.PORT)
