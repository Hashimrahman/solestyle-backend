import psycopg2

connection = None
try:
    connection = psycopg2.connect(
        host="solestyledb.cxmgeieuyqo6.ap-south-1.rds.amazonaws.com",
        database="solestyledb",
        user="solestyleadmin",
        password="solestyle1102",
        port=5432
    )
    print("Connection successful!")
except Exception as e:
    print(f"Error: {e}")
finally:
    if connection:
        connection.close()
        print("Connection closed.")
