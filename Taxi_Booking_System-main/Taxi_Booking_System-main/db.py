import mysql.connector

def create_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="CPNnabin@2004dhakal",
            database="taxi_booking_system_test"
        )
        return conn
    except mysql.connector.Error as e:
        print("Database Error:", e)
        return None
