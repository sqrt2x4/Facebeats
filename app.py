from flask import Flask, render_template, request
from flask import redirect, url_for, flash, session
import requests, os
import subprocess
import random
import yt_dlp, shutil
from supabase_client import supabase


app = Flask(__name__)
app.secret_key = "facebeats_secret_key"
ADMIN_PASSWORD = "lulumusic"

current_player = None
last_user_played = None
current_playing_user = None
vlc_process = None
current_song = None

def retrain_safe():
    global retraining

    if retraining:
        return   # 🚫 already training

    retraining = True

    print("Training model...")
    subprocess.run(["python3", "retrain_model.py"])

    print("✅ Training complete!")
    retraining = False

def get_audio_url(song, artist):
    query = f"{song} {artist}"

    ydl_opts = {
        "quiet": True,
        "format": "bestaudio/best",
        "noplaylist": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch1:{query}", download=False)
        return info["entries"][0]["url"]


def play_audio(song, artist):
    global current_player

    query = f"{song} {artist}"

    try:
        with yt_dlp.YoutubeDL({
            "quiet": True,
            "format": "bestaudio/best"
        }) as ydl:

            info = ydl.extract_info(
                f"ytsearch1:{query}",
                download=False
            )

            audio_url = info["entries"][0]["url"]

        # stop previous song
        if current_player:
            current_player.terminate()

        current_player = subprocess.Popen([
            "cvlc",
            "--intf", "dummy",
            "--play-and-exit",
            audio_url
        ])
        print("VLC PID:", current_player.pid)
        print("Playing:", query)

    except Exception as e:
        print("Playback error:", e)

def get_random_song(user_name):

    user = (
        supabase
        .table("users")
        .select("id")
        .eq("name", user_name)
        .execute()
    )
    print("Searching user:", user_name)
    print(user.data)
    if not user.data:
        return None

    user_id = user.data[0]["id"]

    songs = (
        supabase
        .table("songs")
        .select("*")
        .eq("user_id", user_id)
        .execute()
    )

    if not songs.data:
        return None

    song = random.choice(songs.data)

    return {
        "title": song["title"],
        "artist": song["artist"],
        "cover": song["cover"],
        "video_id": song["youtube_url"]
    }

def get_album_cover(song, artist):
    query = f"{song} {artist}"
    url = (
        "https://itunes.apple.com/search"
        f"?term={query}"
        "&entity=song"
        "&limit=1"
    )
    response = requests.get(url)
    data = response.json()
    if data["resultCount"] > 0:
        return data["results"][0]["artworkUrl100"]
    return None

def get_users():

    result = (
        supabase
        .table("users")
        .select("name")
        .order("name")
        .execute()
    )

    return [
        (row["name"],)
        for row in result.data
    ]

def train_model():
    print("Training model...")
    subprocess.run(["python3", "train_model.py"])

@app.route("/")
def home():
    global current_song
    global current_playing_user
    global vlc_process

    user = None
    song = None

    try:
        with open("current_user.txt", "r") as f:
            user = f.read().strip()
    except:
        pass

    if user and user != "None":

        if current_playing_user != user:

            current_playing_user = user

            current_song = get_random_song(user)

            if vlc_process:
                vlc_process.terminate()

            audio_url = get_audio_url(
                current_song["title"],
                current_song["artist"]
            )

            vlc_process = subprocess.Popen([
                "vlc",
                "--intf", "dummy",
                "--play-and-exit",
                audio_url
            ])
            song = current_song
            print("Playing:", song["title"])

        song = current_song
    return render_template(
        "main.html",
        user=user,
        song=song
    )

@app.route("/current_user")
def current_user():
    try:
        with open("current_user.txt", "r") as f:
            user = f.read().strip()
    except:
        user = ""

    return {"user": user}

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        result = (
            supabase
            .table("users")
            .insert({
                "name": name
            })
            .execute()
        )

        user_id = result.data[0]["id"]

        songs = [
            (request.form.get("song1"), request.form.get("artist1")),
            (request.form.get("song2"), request.form.get("artist2")),
            (request.form.get("song3"), request.form.get("artist3"))
        ]

        for title, artist in songs:

            if title and artist:

                cover = get_album_cover(title, artist)

                (
                    supabase
                    .table("songs")
                    .insert({
                        "user_id": user_id,
                        "title": title,
                        "artist": artist,
                        "cover": cover,
                        "youtube_url": None
                    })
                    .execute()
                )
                
        subprocess.run(["python3", "capture_user.py", name])
        subprocess.run(["python3", "retrain_model.py"])

        subprocess.run(["python3", "retrain_model.py"])
        flash(f"💖 {name} registered and photo captured!")

        return redirect(url_for("home"))

    return render_template("register.html")

@app.route("/status")
def status():
    """API endpoint for the frontend to check the current recognized user."""
    user = None
    try:
        with open("current_user.txt", "r") as f:
            user = f.read().strip()
    except:
        user = None
    
    # Return empty string if user is "None" or blank
    if not user or user == "None":
        user = ""
        
    return {"user": user}

@app.route("/clear_user")
def clear_user():

    global current_playing_user
    global vlc_process

    with open("current_user.txt", "w") as f:
        f.write("")

    current_playing_user = None

    if vlc_process:
        vlc_process.terminate()
        vlc_process = None

    return redirect(url_for("home"))

@app.route("/admin", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":
        password = request.form["password"]

        if password == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect(url_for("manage_users"))

        return render_template(
            "admin_login.html",
            error="❌ Wrong password"
        )

    return render_template("admin_login.html")

@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect(url_for("home"))

@app.route("/manage_users")
def manage_users():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    users = (
    supabase
    .table("users")
    .select("*")
    .order("name")
    .execute()
    )

    users = supabase.table("users").select("*").execute()

    print("SUPABASE USERS:")
    print(users.data)
    users_data = []
    
    for user in users.data:

        songs = (
            supabase
            .table("songs")
            .select("*")
            .eq("user_id", user["id"])
            .execute()
        )

        users_data.append({
            "id": user["id"],
            "name": user["name"],
            "songs": [
                (
                    s["id"],
                    s["title"],
                    s["artist"]
                )
                for s in songs.data
            ],
            "song_count": len(songs.data)
        })

    return render_template(
        "manage_users.html",
        users=users_data
    )

@app.route("/add_song", methods=["GET", "POST"])
def add_song():

    if request.method == "POST":
        name = request.form["name"]
        song = request.form["song"]
        artist = request.form["artist"]

        cover = get_album_cover(song, artist)
        user = (
            supabase
            .table("users")
            .select("id")
            .eq("name", name)
            .execute()
        )

        if not user.data:

            return render_template(
                "add_song.html",
                error="❌ User not found!"
            )

        user_id = user.data[0]["id"]

        (
            supabase
            .table("songs")
            .insert({
                "user_id": user_id,
                "title": song,
                "artist": artist,
                "cover": cover,
                "youtube_url": None
            })
            .execute()
        )

        flash(f"🎵 '{song}' added for {name}!")
        return redirect(url_for("home"))
    
    return render_template(
        "add_song.html",
        users=get_users()
        )

@app.route("/delete_song/<int:song_id>")
def delete_song(song_id):
    
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    (
        supabase
        .table("songs")
        .delete()
        .eq("id", song_id)
        .execute()
    )

    flash("🗑 Song deleted")
    return redirect(url_for("manage_users"))

@app.route("/recognize")
def recognize():

    with open("current_user.txt", "w") as f:
        f.write("")   # clear old user BEFORE starting

    subprocess.Popen(["python3", "recognise.py"])

    flash("Face recognition started 📷 Looking for users...", "recognition")
    return redirect(url_for("home"))


@app.route("/delete_user/<int:user_id>")
def delete_user(user_id):

    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    
    result = (
        supabase
        .table("users")
        .select("name")
        .eq("id", user_id)
        .execute()
    )

    if result.data:

        name = result.data[0]["name"]

        user_folder = f"dataset/{name}"

        if os.path.exists(user_folder):
            shutil.rmtree(user_folder)

    (
        supabase
        .table("songs")
        .delete()
        .eq("user_id", user_id)
        .execute()
    )

    (
        supabase
        .table("users")
        .delete()
        .eq("id", user_id)
        .execute()
    )

    # 🔥 retrain model automatically
    subprocess.run(["python3", "retrain_model.py"])

    flash("🗑 User deleted and model updated")

    return redirect(url_for("manage_users"))

if __name__ == "__main__":
    app.run(debug=True)
