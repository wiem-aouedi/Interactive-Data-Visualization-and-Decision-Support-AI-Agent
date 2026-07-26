import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
# Build a path from this file's location, up two folders, to find .env at project root
env_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
load_dotenv(env_path)
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")
db_user = os.getenv("DB_USER")  
db_password = os.getenv("DB_PASSWORD")
readonly_user = os.getenv("READONLY_DB_USER")
readonly_password = os.getenv("READONLY_DB_PASSWORD")
db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
engine = create_engine(db_url,pool_pre_ping=True)
readonly_db_url = f"postgresql://{readonly_user}:{readonly_password}@{db_host}:{db_port}/{db_name}"
readonly_engine = create_engine(readonly_db_url,pool_pre_ping=True)
if __name__ == "__main__":
    try:
        connection = engine.connect()
        print("The connection to the database was successful!")
        connection.close()
    except Exception as e:
        print("Error connecting to the database:", e)

    try:
        readonly_connection = readonly_engine.connect()
        print("The read-only connection was successful!")
        readonly_connection.close()
    except Exception as e:
        print("Error connecting with read-only user:", e)