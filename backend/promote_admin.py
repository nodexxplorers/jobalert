import sys
from app.core.database import SessionLocal
from app.models.user import User
from app.models.job import Job  # Needed for SQLAlchemy registry
from app.models.notification import Notification  # Needed for SQLAlchemy registry

def promote_user(email):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"❌ User with email {email} not found.")
            return

        user.is_admin = True
        db.commit()
        print(f"✅ User {email} is now an admin!")
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python promote_admin.py <email>")
    else:
        promote_user(sys.argv[1])
