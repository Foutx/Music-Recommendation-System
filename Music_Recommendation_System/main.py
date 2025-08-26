import db_funcs

import recommendation

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

def recommend_next_track(user_name: str):
    global track_rec
    print(f"Рекомендация для пользователя: {user_name}")

    # If user exist
    if db_funcs.check_user_exist(user_name):

        # If user has some likes (we know hes taste)
        if db_funcs.has_liked_tracks(user_name):
            user_means = db_funcs.take_mean_user(user_name)
            track_rec = recommendation.recommend_next_track(user_means, user_name, False)

            name_track_rec = track_rec.iloc[0]
            artist_name = track_rec.iloc[1]
            url_track = track_rec.iloc[2]

            db_funcs.add_listened_music(user_name, name_track_rec)

        # If he hasnt got any likes - generate random
        else:
            user_means = db_funcs.generate_random_means()
            db_funcs.update_mean_values_user(user_name, user_means)
            track_rec = recommendation.recommend_next_track(user_means, user_name, False)

            name_track_rec = track_rec.iloc[0]
            artist_name = track_rec.iloc[1]
            url_track = track_rec.iloc[2]

            db_funcs.add_listened_music(user_name, name_track_rec)

    # If user doesnt exist
    else:
        user_means = db_funcs.generate_random_means()
        db_funcs.add_new_user_to_table(user_name, user_means)

        track_rec = recommendation.recommend_next_track(user_means, user_name, False)

        name_track_rec = track_rec.iloc[0]
        artist_name = track_rec.iloc[1]
        url_track = track_rec.iloc[2]

        db_funcs.add_listened_music(user_name, name_track_rec)


    track = {
        "track_url": url_track,
        "title": name_track_rec,
        "artist": artist_name
    }
    return track


@app.get("/recommend")
def recommend(user_name: str):
    track = recommend_next_track(user_name)
    return track

@app.post("/feedback")
def feedback(action: str, track_name: str, user_name: str):

    print(f"User action: {action} on {track_name}")

    if action == "like":
        db_funcs.set_like(user_name, track_name)
        user_means = db_funcs.take_mean_user(user_name)
        new_user_means = db_funcs.update_user_means_weighted(user_means, user_name, track_rec)
        db_funcs.update_mean_values_user(user_name, new_user_means)

    return {"status": "ok"}