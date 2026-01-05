from app.core.database import Base
from app.models.user import User  # Import ALL your models
from app.models.notification import Notification  # Add all model files
from app.models.job import Job
from app.models.push_subscription import PushSubscription
# ... import any other models you have

target_metadata = Base.metadata