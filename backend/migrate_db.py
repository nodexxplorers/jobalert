from app.core.database import engine
from sqlalchemy import text
import sqlalchemy

def migrate():
    print("Starting database migration...")
    with engine.connect() as conn:
        try:
            # Postgres specific check for column
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='system_status' AND column_name='twitter_cookies';
            """))
            exists = result.fetchone()
            
            if not exists:
                print("Column 'twitter_cookies' not found. Adding it now...")
                conn.execute(text("ALTER TABLE system_status ADD COLUMN twitter_cookies TEXT;"))
                conn.commit()
                print("Column 'twitter_cookies' added successfully.")
            else:
                print("Column 'twitter_cookies' already exists in system_status table.")
                
        except Exception as e:
            print(f"Migration failed: {e}")
            # Try a direct approach as fallback
            try:
                print("Attempting direct fallback...")
                conn.execute(text("ALTER TABLE system_status ADD COLUMN IF NOT EXISTS twitter_cookies TEXT;"))
                conn.commit()
                print("Fallback succeeded.")
            except Exception as e2:
                print(f"Fallback also failed: {e2}")

if __name__ == "__main__":
    migrate()
