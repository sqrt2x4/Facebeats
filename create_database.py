import sqlite3

connection = sqlite3.connect("database.db")

cursor = connection.cursor()

cursor.execute("""
drop table songs
""")

connection.commit()
connection.close()

print("Database updated!")