"""
Database viewer for user behavior tracking
Run this script to view recorded data from the database
"""

import pandas as pd
from psycopg import connect
from config import DATABASE_URL, DATABASE_TIMEOUT


def get_connection():
    return connect(DATABASE_URL, connect_timeout=int(DATABASE_TIMEOUT))

def view_user_selections():
    """View user category selections"""
    with get_connection() as conn:
        df = pd.read_sql_query("SELECT * FROM user_selections ORDER BY timestamp DESC", conn)
    
    print("\n" + "="*80)
    print("USER CATEGORY SELECTIONS")
    print("="*80)
    if len(df) > 0:
        print(df.to_string(index=False))
        print(f"\nTotal records: {len(df)}")
    else:
        print("No data yet.")
    print("="*80)

def view_watch_logs():
    """View video watch duration logs"""
    with get_connection() as conn:
        df = pd.read_sql_query("""
            SELECT user_id, video_id, video_title, video_category, video_index,
                   ROUND(watch_duration::numeric, 2) as watch_duration,
                   video_total_duration,
                   ROUND(completion_rate::numeric, 2) as completion_rate,
                   liked, comment, timestamp
            FROM video_watch_log 
            ORDER BY timestamp DESC
        """, conn)
    
    print("\n" + "="*80)
    print("VIDEO WATCH DURATION LOGS")
    print("="*80)
    if len(df) > 0:
        print(df.to_string(index=False))
        print(f"\nTotal records: {len(df)}")
        print(f"\nSummary Statistics:")
        print(f"  Average watch duration: {df['watch_duration'].mean():.2f} seconds")
        print(f"  Average completion rate: {df['completion_rate'].mean():.2f}%")
        print(f"  Total videos watched: {len(df)}")
    else:
        print("No data yet.")
    print("="*80)

def export_to_excel():
    """Export all data to Excel file"""
    with get_connection() as conn:
        # Read both tables
        df_selections = pd.read_sql_query("SELECT * FROM user_selections", conn)
        df_watch_logs = pd.read_sql_query("SELECT * FROM video_watch_log", conn)
    
    # Export to Excel with multiple sheets
    filename = 'user_behavior_export.xlsx'
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        df_selections.to_excel(writer, sheet_name='Category Selections', index=False)
        df_watch_logs.to_excel(writer, sheet_name='Watch Duration', index=False)
    
    print(f"\n✅ Data exported to: {filename}")

if __name__ == '__main__':
    print("\n📊 USER BEHAVIOR DATABASE VIEWER")
    
    # View all data
    view_user_selections()
    view_watch_logs()
    
    # Export option
    print("\n" + "="*80)
    response = input("Export data to Excel? (y/n): ").strip().lower()
    if response == 'y':
        export_to_excel()
    
    print("\n✨ Done!\n")
