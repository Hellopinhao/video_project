# Project Structure (Quick Understanding Guide)

This file is a fast map of the project so you can start debugging or extending it quickly.

---

## 1) High-Level Architecture

The app is a Flask-based video experiment platform with:

- **Backend (Python/Flask):** routing, session state, DB writes/reads
- **Data layer (PostgreSQL):** user selections + video watch logs
- **Video source:** local MP4 files in `douyin_videos/` + metadata in `douyin_videos.xlsx`
- **Frontend:** Jinja templates + CSS + small JS modules

Main execution path:

1. User enters welcome page
2. Selects categories (top-3 by slider value)
3. Server builds playlist by round/group logic
4. User watches videos and interacts (like/dislike/comments)
5. Client sends watch duration to backend
6. Summary page shows round statistics

---

## 2) Actual Directory Layout

```text
vedioproject/
├── app.py
├── config.py
├── database.py
├── session_manager.py
├── video_loader.py
├── utils.py
├── view_database.py
├── README.md
├── STRUCTURE.md
├── requirements.txt
├── douyin_videos.xlsx
├── database connection via `DATABASE_URL`
│
├── templates/
│   ├── welcome.html
│   ├── categories.html
│   ├── play_video.html
│   ├── summary.html                      # legacy/general summary template
│   ├── summary_group1.html
│   ├── summary_group2.html
│   ├── summary_group3.html
│   └── summary_group4.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   ├── categories.js
│   │   ├── play_video.js
│   │   └── summary_chart.js
│   └── videos/                           # currently reserved
│
└── douyin_videos/
        └── *.mp4
```

---

## 3) Backend Files (What each file does)

### `app.py` — Web entrypoint and routes

Responsibilities:

- Flask app setup + DB initialization
- Page routes and API routes
- Input parsing/validation helpers
- Calls service modules (`video_loader`, `session_manager`, `database`, `utils`)

Key page routes:

- `/` → welcome
- `/group<int:group_num>` → group-specific entry
- `/categories` → category sliders
- `/play_video/<int:index>` → video page
- `/summary` → round report

Key API routes:

- `/like_video` (POST)
- `/add_comment` (POST)
- `/save_watch_duration` (POST)

---

### `config.py` — centralized constants

- Flask settings (`SECRET_KEY`, `DEBUG`, `HOST`, `PORT`)
- Paths (`EXCEL_FILE`, `VIDEO_DIR`) + DB connection (`DATABASE_URL`)
- Category mapping (Chinese label -> metadata category key)
- Round distribution rules (`ROUND_VIDEO_COUNTS`)

---

### `video_loader.py` — metadata loading + playlist generation

- Loads Excel rows via pandas
- Validates required columns + local MP4 existence
- Groups videos by category
- Builds randomized playlist per round with exclusion support

Important method:

- `create_playlist(selected_categories, current_round, excluded_video_ids)`

---

### `session_manager.py` — all session state operations

Stores/manages:

- `user_id`, `session_id`, `group`, `round`
- `playlist`, `likes`, `comments`, `shown_videos`

Key functions:

- `initialize_session()`
- `get_user_info()`
- `update_likes()`
- `add_comment()`
- `increment_round()`
- `calculate_watch_stats()`

---

### `database.py` — PostgreSQL schema + CRUD

Tables:

- `user_selections`
- `video_watch_log`
- `user_counters`

Main functions:

- `init_db()`
- `get_next_user_id(group_number)`
- `save_category_selection(...)`
- `save_watch_log(...)` (append-only insert, supports repeated watches)
- `get_session_statistics(session_id, current_round)`

---

### `utils.py`

- `calculate_summary_statistics()` for summary page aggregation

### `view_database.py`

- Local utility script for inspecting/exporting DB data

---

## 4) Frontend Files

### Templates

- `welcome.html`: experiment intro
- `categories.html`: slider form for top-3 preferences
- `play_video.html`: player + reaction UI + comments
- `summary_group*.html`: group-specific summary content (plus final-round complete page)

### JavaScript

- `static/js/categories.js`
    - slider value rendering
    - max-3 selection lock
    - reset behavior

- `static/js/play_video.js`
    - watch-time tracking
    - save watch duration (`fetch` + `sendBeacon` fallback)
    - prev/next navigation
    - like/dislike + comments API calls

- `static/js/summary_chart.js`
    - pie chart rendering from template-provided data

### CSS

- `static/css/style.css`
    - full page styling + responsive rules

---

## 5) Runtime Data Flow (with key state)

### Step A: Session start

- `initialize_session()` creates:
    - `user_id` (by group counter)
    - `session_id` (UUID)
    - `round = 1`

### Step B: Category submit

- Server reads slider values, picks top 3
- `video_loader.create_playlist(...)`
- Saves selection to `user_selections`

### Step C: Video watching

- Each video page tracks watch duration on client
- Sends to `/save_watch_duration`
- Server computes completion/like/comment stats and inserts into `video_watch_log`

### Step D: Summary and round transition

- `/summary` aggregates per-category stats from DB
- `increment_round()` stores shown IDs and moves `round` 1 -> 2

---

## 6) Fast Debug Entry Points

If something looks wrong, start here:

- **Missing/incorrect watch count or duration**
    - `static/js/play_video.js`
    - `/save_watch_duration` in `app.py`
    - `save_watch_log()` in `database.py`

- **Playlist/category mismatch**
    - `select_categories()` in `app.py`
    - `create_playlist()` in `video_loader.py`

- **Round logic issues**
    - `increment_round()` + `get_shown_video_ids()` in `session_manager.py`

---

## 7) One-Minute Mental Model

- `app.py` orchestrates everything.
- `session_manager.py` owns user session state.
- `video_loader.py` decides what videos user sees.
- `database.py` is the source of truth for saved behavior.
- templates + JS render UI and send interactions back.

If you understand those five pieces, you understand the project.
