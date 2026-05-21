import sqlite3
import pandas as pd
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "socialpulse.db")

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    # Create posts table
    c.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform TEXT,
            Date TEXT,
            Tweet TEXT,
            Likes INTEGER,
            Retweets INTEGER,
            Replies INTEGER,
            Views INTEGER,
            Saves INTEGER,
            Username TEXT,
            Hashtags TEXT,
            Category TEXT,
            UNIQUE(platform, Tweet, Date)
        )
    ''')
    conn.commit()
    conn.close()

def save_dataframe_to_db(df: pd.DataFrame, platform: str):
    """Save normalized dataframe to SQLite, ignoring duplicates."""
    init_db()
    conn = get_connection()
    
    # Ensure all required columns exist in df
    cols = ["Date", "Tweet", "Likes", "Retweets", "Replies", "Views", "Saves", "Username", "Hashtags", "Category"]
    
    save_df = pd.DataFrame()
    save_df["platform"] = [platform] * len(df)
    
    for c in cols:
        if c in df.columns:
            save_df[c] = df[c]
        else:
            save_df[c] = None
            
    # Insert safely ignoring duplicates based on platform+Tweet+Date
    try:
        # We can use pd.to_sql for simple insert, but for UPSERT/IGNORE we use executemany
        records = save_df.to_dict('records')
        
        sql = '''
            INSERT OR IGNORE INTO posts 
            (platform, Date, Tweet, Likes, Retweets, Replies, Views, Saves, Username, Hashtags, Category)
            VALUES (:platform, :Date, :Tweet, :Likes, :Retweets, :Replies, :Views, :Saves, :Username, :Hashtags, :Category)
        '''
        c = conn.cursor()
        c.executemany(sql, records)
        conn.commit()
    except Exception as e:
        print(f"Error saving to DB: {e}")
    finally:
        conn.close()

def load_from_db(platform: str) -> pd.DataFrame:
    """Load all posts for a specific platform from DB."""
    init_db()
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM posts WHERE platform = ?", conn, params=(platform,))
    conn.close()
    
    if "id" in df.columns:
        df = df.drop(columns=["id"])
        
    return df
