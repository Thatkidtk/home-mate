
from sqlalchemy import func
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="member", nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now())

    assets = db.relationship("Asset", back_populates="owner", lazy="selectin", cascade="all, delete-orphan")
    tasks = db.relationship("Task", back_populates="owner", lazy="selectin", cascade="all, delete-orphan")

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email}>"


class Asset(db.Model):
    __tablename__ = "asset"
    __table_args__ = (
        db.Index("ix_asset_user_type", "user_id", "type"),
        db.Index("ix_asset_user_name", "user_id", "name"),
    )
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    type = db.Column(db.String(50), nullable=True, index=True)   # home, vehicle, appliance, etc.
    make = db.Column(db.String(120))
    model = db.Column(db.String(120))
    serial = db.Column(db.String(120), index=True)
    purchase_date = db.Column(db.Date, nullable=True)
    warranty_expiration = db.Column(db.Date, nullable=True)
    notes = db.Column(db.Text)

    tasks = db.relationship("Task", back_populates="asset", lazy="selectin", cascade="all, delete-orphan")
    attachments = db.relationship("Attachment", back_populates="asset", cascade="all, delete-orphan")
    owner = db.relationship("User", back_populates="assets", lazy="joined")

    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())


class Task(db.Model):
    __tablename__ = "task"
    __table_args__ = (
        db.Index("ix_task_user_status_due", "user_id", "status", "due_date"),
        db.Index("ix_task_user_asset", "user_id", "asset_id"),
    )
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    asset_id = db.Column(db.Integer, db.ForeignKey("asset.id"), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text)
    due_date = db.Column(db.Date, nullable=True, index=True)
    recurrence_rule = db.Column(db.String(255), nullable=True)   # e.g., FREQ=MONTHLY;INTERVAL=3
    status = db.Column(db.Enum("pending","done","skipped","deleted", name="task_status"), default="pending", index=True)
    priority = db.Column(db.Integer, default=0)
    estimated_minutes = db.Column(db.Integer, default=0)
    cost = db.Column(db.Numeric(10,2), nullable=True)
    vendor = db.Column(db.String(120), nullable=True)

    asset = db.relationship("Asset", back_populates="tasks", lazy="joined")
    owner = db.relationship("User", back_populates="tasks", lazy="joined")
    attachments = db.relationship("Attachment", back_populates="task", cascade="all, delete-orphan", lazy="selectin")

    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())


class Attachment(db.Model):
    __tablename__ = "attachment"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    asset_id = db.Column(db.Integer, db.ForeignKey("asset.id"), nullable=True, index=True)
    task_id = db.Column(db.Integer, db.ForeignKey("task.id"), nullable=True, index=True)
    key = db.Column(db.String(255), nullable=False, unique=True)
    original_name = db.Column(db.String(255))
    mime = db.Column(db.String(80))
    size = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, server_default=func.now())

    asset = db.relationship("Asset", back_populates="attachments")
    task = db.relationship("Task", back_populates="attachments")
