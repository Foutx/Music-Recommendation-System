import pandas as pd

import numpy as np

import sqlite3 as sq

# ============================== Func to generate data ==========================================
def get_data(df_tracks, num_users, n_tracks, RANDOM_STATE):
       try:

              np.random.seed(RANDOM_STATE)

              # Generate fake users dataframe
              user_ids = [f'user{i}' for i in range(1, num_users+1)]

              # Generate random futures for users
              user_means = pd.DataFrame({
              
              "user_id":user_ids,
              "acousticness_mean":np.random.rand(num_users),
              "danceability_mean":np.random.rand(num_users),
              "energy_mean":np.random.rand(num_users),
              "instrumentalness_mean":np.random.rand(num_users),
              "liveness_mean":np.random.rand(num_users),
              "loudness_mean":np.random.rand(num_users),
              "speechiness_mean":np.random.rand(num_users),
              "valence_mean":np.random.rand(num_users),
              "tempo_mean":np.random.rand(num_users),

              })

              # Take random tracks for users
              rows = []
              for user in user_ids:
                     sampled_tracks = df_tracks.sample(n_tracks, random_state=RANDOM_STATE).copy()
                     sampled_tracks['user_id'] = user
                     rows.append(sampled_tracks)

              df_users_tracks = pd.concat(rows, ignore_index=True)

              df_finale = pd.merge(df_users_tracks, user_means, on='user_id', how='left')

              # ========================== Create target labels ================================
              from numpy import dot
              from numpy.linalg import norm

              def cosine_similarity(a, b) -> float:
                     return dot(a, b) / (norm(a) * norm(b))

              track_features = ['acousticness', 'danceability', 'energy', 'instrumentalness',
                            'liveness', 'loudness', 'speechiness', 'valence', 'tempo']

              user_features = [col + '_mean' for col in track_features]

              def like(row, threshold=0.5) -> int:
                     track_vector = row[track_features].values
                     user_vector = row[user_features].values
                     return 1 if cosine_similarity(track_vector, user_vector) > threshold else 0

              df_finale['liked'] = df_finale.apply(like, axis=1)
              
              print(f"Data created! Values target labels: {df_finale['liked'].value_counts()}")
              return df_finale
       
       except Exception as e:
              print(e)
              return None