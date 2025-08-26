from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.metrics import confusion_matrix, roc_auc_score

import xgboost as xgb

# =========================================== Func to create model ==========================================
def create_model(df):
    try:
        # import created dataset

        X = df[['acousticness', 'danceability', 'energy',
            'instrumentalness', 'liveness', 'loudness', 'speechiness', 'valence',
            'tempo', 'acousticness_mean', 'danceability_mean',
            'energy_mean', 'instrumentalness_mean', 'liveness_mean',
            'loudness_mean', 'speechiness_mean', 'valence_mean', 'tempo_mean']]

        y = df['liked']

        # Create model XGBClassifier
        model = xgb.XGBClassifier(
            n_estimators=200,
            max_depth=4,
            learning_rate=0.1,
            random_state=42,
            use_label_encoder=False,
            eval_metric="logloss"
        )

        """
        X_train, X_test, y_train, y_test = train_test_split(X,y, shuffle=True, random_state=42, test_size=0.2)

        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)

        auc = roc_auc_score(y_test, y_pred)
        matrix = confusion_matrix(y_test, y_pred)

        print(f'AUC score: {auc}')
        print(matrix)
        
        Result was:
        AUC score: 0.9905104692130292
        
        Confusion matrix:
            [[5512   12]
            [   8  468]]
        """

        model.fit(X,y)

        print('Model completed!')
        return model
    
    except Exception as e:
        print(e)
        return None