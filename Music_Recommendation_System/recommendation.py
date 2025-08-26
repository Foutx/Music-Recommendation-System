import model

import generate_data

import db_funcs

import pandas as pd

import sqlite3

import numpy as np

import joblib


def recommend_next_track(user_mean, user_name: str, model_fit: bool, RANDOM_STATE: int=42, n_users: int=3000, n_tracks: int=20, total_tracks: int=1500):    
    try:
        
        df_tracks = pd.read_csv('data\\spotify_global_2019_most_streamed_tracks_audio_features.csv')
        df_tracks = df_tracks.sample(total_tracks, random_state=RANDOM_STATE)

        df_tracks = df_tracks.drop(columns=['Country', 'Rank', 'Track_id', 'Streams', 'time_signature', 'duration_ms', 'key', 'mode', 'Artist_id',
                                'Artist_popularity', 'Artist_follower'])

        # Delete tracks which we listened   
        listened_tracks = db_funcs.get_all_tracks(user_name)

        if listened_tracks:
            df_tracks = df_tracks[~df_tracks['Track Name'].isin(listened_tracks)]

        track_fetures = ['acousticness', 'danceability', 'energy',
                'instrumentalness', 'liveness', 'loudness', 'speechiness', 'valence',
                'tempo']

        # ============================= Create or load xgb model ==================================
        if model_fit:

            df_fake = generate_data.get_data(df_tracks, n_users, n_tracks, RANDOM_STATE)

            xgb_model = model.create_model(df_fake)

            joblib.dump(xgb_model, "xgb_model.pkl")
        
        else:
            try:
                xgb_model = joblib.load('xgb_model.pkl')
            except Exception as e:
                print(e)
                return None

        # ================================== Recommendation ===================================

        def cosine_similarity(a, b) -> float:
            return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

        # Use cosine similarity
        user_vector = user_mean[[f + "_mean" for f in track_fetures]].iloc[0].values
        df_tracks['cos_sim'] = df_tracks[track_fetures].apply(
            lambda row: cosine_similarity(row.values, user_vector), axis=1
        )

        def make_input(row, user_mean):
            data = {}

            for f in track_fetures:
                data[f] = row[f]

            for f in track_fetures:
                data[f+"_mean"] = user_mean[f+"_mean"]

            return pd.DataFrame([data])

        top_tracks = df_tracks.nlargest(10, 'cos_sim')

        # Use model to predict next best track
        X = pd.concat([make_input(row, user_mean) for _, row in top_tracks.iterrows()], ignore_index=True)
        X = X.apply(pd.to_numeric, errors='coerce').fillna(0)

        probs = xgb_model.predict_proba(X)[:, 1]

        top_tracks = top_tracks.copy()
        top_tracks['like_chance'] = probs

        best_track = top_tracks.loc[top_tracks['like_chance'].idxmax()]
        return best_track
        
    except Exception as e:
        print(e)
        return None