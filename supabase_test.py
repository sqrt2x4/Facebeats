from supabase import create_client
import sqlite3

url = "https://ilmyjtjplwppmlsjtdec.supabase.co"
key = "sb_publishable_k4FrVQFYFLIdROMQ0P7KtA_Nmuy5B6p"

supabase = create_client(url, key)

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
SELECT
    users.name,
    songs.title,
    songs.artist,
    songs.cover,
    songs.youtube_url
FROM songs
JOIN users
ON users.id = songs.user_id
""")

songs = cursor.fetchall()

for row in songs:

    user_name = row[0]

    result = (
        supabase
        .table("users")
        .select("id")
        .eq("name", user_name)
        .execute()
    )

    if not result.data:
        print(f"User not found: {user_name}")
        continue

    supabase_user_id = result.data[0]["id"]

    supabase.table("songs").insert({
        "user_id": supabase_user_id,
        "title": row[1],
        "artist": row[2],
        "cover": row[3],
        "youtube_url": row[4]
    }).execute()

    print("Added:", row[1])

print("Migration complete.")
print("Success!")