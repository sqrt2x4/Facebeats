import sqlite3

connection = sqlite3.connect("database.db")
cursor = connection.cursor()

try:
    cursor.execute("""
        ALTER TABLE songs
        ADD COLUMN album_cover TEXT
    """)
except:
    pass

connection.commit()
connection.close()