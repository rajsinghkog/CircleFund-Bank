from app.db.database import SessionLocal
from app.db.models import Group

def add_sample_groups():
    db = SessionLocal()
    groups = [
        Group(name="Daily Savers", contribution_amount=5.0, cycle="daily"),
        Group(name="Weekly Warriors", contribution_amount=5.0, cycle="weekly"),
        Group(name="Family Fund", contribution_amount=10.0, cycle="weekly"),
        Group(name="Friends Circle", contribution_amount=20.0, cycle="daily"),
    ]
    for group in groups:
        exists = db.query(Group).filter(Group.name == group.name).first()
        if not exists:
            db.add(group)
    db.commit()
    db.close()
    print("Sample groups added.")

if __name__ == "__main__":
    add_sample_groups()
