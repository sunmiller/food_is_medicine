import os
from dotenv import load_dotenv
import psycopg2
from sqlalchemy import create_engine, text

# Load environment variables
load_dotenv()

def test_database_connection():
    """Test if we can connect to the database"""
    database_url = os.getenv("DATABASE_URL")
    print(f"Testing connection to: {database_url}")
    
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        return
    
    # Test 1: Basic psycopg2 connection
    try:
        print("\n1. Testing basic psycopg2 connection...")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ PostgreSQL version: {version[0]}")
        cursor.close()
        conn.close()
    except psycopg2.OperationalError as e:
        print(f"❌ Connection failed: {e}")
        print("\nCheck:")
        print("1. Is PostgreSQL running on port 5433?")
        print("2. Does the database 'eatforhealing' exist?")
        print("3. Is the password 'password' correct for user 'postgres'?")
        return
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return
    
    # Test 2: SQLAlchemy connection
    try:
        print("\n2. Testing SQLAlchemy connection...")
        engine = create_engine(database_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test"))
            test_value = result.fetchone()[0]
            print(f"✅ SQLAlchemy test query result: {test_value}")
    except Exception as e:
        print(f"❌ SQLAlchemy connection failed: {e}")
        return
    
    print("\n🎉 All database tests passed! The connection is working.")

if __name__ == "__main__":
    test_database_connection()