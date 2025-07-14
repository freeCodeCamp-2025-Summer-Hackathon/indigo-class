from datetime import datetime, timezone

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

db = SQLAlchemy()


class User(db.Model, UserMixin):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_email_opt_in = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )

    roles = relationship("Role", secondary="user_roles", back_populates="users")
    affirmations = relationship("Affirmation", back_populates="user")
    daily_mail_history = relationship("DailyMailHistory", back_populates="user")

    def get_id(self):
        """Return the user ID as a string for Flask-Login."""
        return str(self.user_id)

    def is_admin(self):
        """Check if the user is an admin."""
        return self.roles.filter(Role.name == "admin").first() is not None


class Role(db.Model):
    __tablename__ = "roles"

    role_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )

    users = relationship("User", secondary="user_roles", back_populates="roles")


class UserRole(db.Model):
    __tablename__ = "user_roles"

    user_id = Column(
        Integer, ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True
    )
    role_id = Column(
        Integer, ForeignKey("roles.role_id", ondelete="CASCADE"), primary_key=True
    )


class Category(db.Model):
    __tablename__ = "categories"

    category_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)

    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )

    affirmations = relationship("AffirmationCategory", back_populates="category")


class Affirmation(db.Model):
    __tablename__ = "affirmations"

    affirmation_id = Column(Integer, primary_key=True, autoincrement=True)
    affirmation_text = Column(Text, nullable=False)
    user_id = Column(
        Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )

    is_admin_set = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )

    user = relationship("User", back_populates="affirmations")
    categories = relationship("AffirmationCategory", back_populates="affirmation")
    daily_history = relationship("DailyMailHistory", back_populates="affirmation")


class AffirmationCategory(db.Model):
    __tablename__ = "affirmations_categories"

    affirmation_id = Column(
        Integer,
        ForeignKey("affirmations.affirmation_id", ondelete="CASCADE"),
        primary_key=True,
    )
    category_id = Column(
        Integer,
        ForeignKey("categories.category_id", ondelete="CASCADE"),
        primary_key=True,
    )
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )

    affirmation = relationship("Affirmation", back_populates="categories")
    category = relationship("Category", back_populates="affirmations")


class DailyMailHistory(db.Model):
    __tablename__ = "daily_mail_history"

    daily_mail_history_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    affirmation_id = Column(
        Integer,
        ForeignKey("affirmations.affirmation_id", ondelete="CASCADE"),
        nullable=False,
    )
    sent_email_at = Column(DateTime)
    scheduled_for = Column(DateTime)

    user = relationship("User", back_populates="daily_mail_history")
    affirmation = relationship("Affirmation", back_populates="daily_history")
