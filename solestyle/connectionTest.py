import psycopg2
from decouple import config

print("key",config('AWS_SECRET_ACCESS_KEY'))
print("id",config('AWS_ACCESS_KEY_ID'))

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
