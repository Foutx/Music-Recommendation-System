import sqlite3

import pandas as pd

import numpy as np

# Connect to db with users params
conn = sqlite3.connect("DB/users_params.db")
cusrsor = conn.cursor()

# Create table if it's not exist
cusrsor.execute("""
CREATE TABLE IF NOT EXISTS users (
    name TEXT UNIQUE,
    acousticness_mean REAL DEFAULT 0,
    danceability_mean REAL DEFAULT 0,
    energy_mean REAL DEFAULT 0,
    instrumentalness_mean REAL DEFAULT 0,
    liveness_mean REAL DEFAULT 0,
    loudness_mean REAL DEFAULT 0,
    speechiness_mean REAL DEFAULT 0,
    valence_mean REAL DEFAULT 0,
    tempo_mean REAL DEFAULT 0
)
""")

cusrsor.execute("""
CREATE TABLE IF NOT EXISTS listened_tracks (
    user_name TEXT,
    name_track TEXT,
    like INTEGER DEFAULT 0
)
""")

conn.commit()
conn.close()

def add_new_user_to_table(name: str, user_means: pd.DataFrame):
    try:
        conn = sqlite3.connect("DB/users_params.db")
        cursor = conn.cursor()
        
        sql = """
            INSERT INTO users (
                name, acousticness_mean, danceability_mean, energy_mean,
                instrumentalness_mean, liveness_mean, loudness_mean, speechiness_mean,
                valence_mean, tempo_mean
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?) 
        """
        
        values = user_means.iloc[0].tolist()
        values.insert(0, name)

        cursor.execute(sql, values)
        conn.commit()
        conn.close()

        print("CREATED")
    
    except Exception as e:
        print(e)
        return None
    
def update_mean_values_user(name: str, user_means: pd.DataFrame):
    try:
        conn = sqlite3.connect("DB/users_params.db")
        cursor = conn.cursor()

        sql = """
            UPDATE users SET
                acousticness_mean = ?,
                danceability_mean = ?,
                energy_mean = ?,
                instrumentalness_mean = ?,
                liveness_mean = ?,
                loudness_mean = ?,
                speechiness_mean = ?,
                valence_mean = ?,
                tempo_mean = ?
            WHERE name = ?
        """

        values = user_means.iloc[0].tolist()
        values.append(name)

        cursor.execute(sql, values)
        conn.commit()
        conn.close()

        print("UPDATED")
    except Exception as e:
        print(e)
        return None

def generate_random_means():

    user_means = pd.DataFrame({

                "acousticness_mean":np.random.rand(1),
                "danceability_mean":np.random.rand(1),
                "energy_mean":np.random.rand(1),
                "instrumentalness_mean":np.random.rand(1),
                "liveness_mean":np.random.rand(1),
                "loudness_mean":np.random.rand(1),
                "speechiness_mean":np.random.rand(1),
                "valence_mean":np.random.rand(1),
                "tempo_mean":np.random.rand(1),

                })
    
    return user_means

def check_user_exist(user_name: str) -> bool:
    
    conn = sqlite3.connect("DB/users_params.db")
    cusrsor = conn.cursor()
    
    cusrsor.execute("SELECT * FROM users WHERE name = ?", (user_name,))
    res = cusrsor.fetchone()

    conn.close()

    return res 

def take_mean_user(user_name: str):
    
    conn = sqlite3.connect("DB/users_params.db")
    cursor = conn.cursor()
    cursor.execute("""
            SELECT acousticness_mean, danceability_mean, energy_mean,
                   instrumentalness_mean, liveness_mean, loudness_mean,
                   speechiness_mean, valence_mean, tempo_mean
            FROM users
            WHERE name = ?
        """, (user_name,))
    row = cursor.fetchone()
    
    conn.close()

    columns = ["acousticness_mean", "danceability_mean", "energy_mean",
                   "instrumentalness_mean", "liveness_mean", "loudness_mean",
                   "speechiness_mean", "valence_mean", "tempo_mean"]
    
    return pd.DataFrame([dict(zip(columns, row))])

def add_listened_music(user_name: str, track_name: str):

    conn = sqlite3.connect("DB/users_params.db")
    cursor = conn.cursor()

    cursor.execute("INSERT INTO listened_tracks (user_name, name_track) VALUES (?, ?)", (user_name, track_name))

    conn.commit()
    conn.close()

def get_all_tracks(user_name: str):
    conn = sqlite3.connect("DB/users_params.db")
    cursor = conn.cursor()

    cursor.execute("SELECT name_track FROM listened_tracks WHERE user_name = ?", (user_name,))
    listened_tracks = [row[0] for row in cursor.fetchall()]
    conn.close()

    return listened_tracks

def has_liked_tracks(user_name: str) -> bool:
    try:
        conn = sqlite3.connect("DB/users_params.db")
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 1 FROM listened_tracks 
            WHERE user_name = ? AND like = 1 
            LIMIT 1
        """, (user_name,))
        
        result = cursor.fetchone()
        
        conn.close()
        
        return result is not None
    except Exception as e:
        print(e)
        return None
    
def set_like(user_name: str, track_name: str):
    try:
        conn = sqlite3.connect("DB/users_params.db")
        cursor = conn.cursor()

        sql = """
            UPDATE listened_tracks
            SET like = 1
            WHERE user_name = ? AND name_track = ?
        """

        cursor.execute(sql, (user_name, track_name))
        conn.commit()
        conn.close()

    except Exception as e:
        print(e)
        return None
    
def get_user_likes_count(user_name: str) -> int:
    try:
        conn = sqlite3.connect("DB/users_params.db")
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*) 
            FROM listened_tracks 
            WHERE user_name = ? AND like = 1
        """, (user_name,))
        
        count = cursor.fetchone()[0]

        conn.close()
        return count

    except Exception as e:
        print(e)
        return 0

def update_user_means_weighted(user_means: pd.DataFrame, user_name: str,track_features, ) -> pd.DataFrame:
    updated_means = user_means.copy()

    n_likes = get_user_likes_count(user_name)

    if isinstance(track_features, pd.DataFrame):
        track_features = track_features.iloc[0]

    for col in user_means.columns:
        if col.endswith("_mean"):
            track_col = col.replace("_mean", "")
            if track_col in track_features:
                old_value = float(user_means[col].iloc[0])
                track_value = float(track_features[track_col])
                new_value = (old_value * n_likes + track_value) / (n_likes + 1)
                updated_means.at[0, col] = new_value

    return updated_means