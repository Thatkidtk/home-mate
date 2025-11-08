import random
from datetime import date, datetime, timedelta
from decimal import Decimal

from app import create_app
from app.extensions import db
from app.models import Asset, Task, User


ASSET_TYPES = ["HVAC", "Plumbing", "Fridge", "Washer", "Roof", "Vehicle"]


def seed():
    app = create_app()
    with app.app_context():
        user = User.query.first()
        if not user:
            raise SystemExit("Create a user first (register via UI) before seeding sample data.")

        if Asset.query.filter_by(user_id=user.id).count() > 0:
            raise SystemExit("User already has assets. Aborting to avoid duplicates.")

        today = date.today()
        cost_options = [Decimal("0"), Decimal("25"), Decimal("49.99"), Decimal("120")]
        for idx in range(5):
            asset = Asset(
                user_id=user.id,
                name=f"{ASSET_TYPES[idx % len(ASSET_TYPES)]} #{idx + 1}",
                type=ASSET_TYPES[idx % len(ASSET_TYPES)],
                make=random.choice(["Acme", "HomePro", "FixIt", "DailyCo"]),
                model=f"{random.randint(100,999)}-X",
                purchase_date=today - timedelta(days=random.randint(200, 1500)),
                warranty_expiration=today + timedelta(days=random.randint(100, 600)),
                notes="Seeded sample asset.",
            )
            db.session.add(asset)
            db.session.flush()

            for _ in range(4):
                due = today + timedelta(days=random.randint(-30, 60))
                status = random.choice(["pending", "pending", "done"])
                task = Task(
                    user_id=user.id,
                    asset_id=asset.id,
                    title=f"Service {asset.name}",
                    description="Auto-generated sample task.",
                    due_date=due,
                    status=status,
                    cost=random.choice(cost_options),
                )
                if status == "done":
                    completed_at = datetime.utcnow() - timedelta(days=random.randint(1, 90))
                    task.updated_at = completed_at
                db.session.add(task)

        db.session.commit()
        print("Seeded sample assets and tasks.")


if __name__ == "__main__":
    seed()
