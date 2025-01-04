import mysql.connector

def load_states():
    conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1234",
            database="conafe"
        )
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT estado FROM CCT")
    states = cursor.fetchall()
    return states

print(load_states())