from app.db.models import Base
from app.db.database import engine

if __name__ == "__main__":
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    print("All tables created.") 