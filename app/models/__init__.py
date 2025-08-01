from datetime import datetime, timezone

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.schema import UniqueConstraint

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
    saved_affirmations = relationship("SavedAffirmation", back_populates="user")
    categories = relationship("Category", back_populates="user")
    user_affirmations = relationship("UserAffirmation", back_populates="user")

    def get_id(self):
        """Return the user ID as a string for Flask-Login."""
        return str(self.user_id)

    def is_admin(self):
        """Check if the user is an admin."""
        return any(role.name == "admin" for role in self.roles)


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

    user_id = Column(
        Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    __table_args__ = (
        UniqueConstraint("user_id", "name", name="unique_user_category_name"),
    )

    is_admin_set = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )

    # Cascade delete ensures related AffirmationCategory rows are deleted when a Category is deleted
    affirmations = relationship(
        "AffirmationCategory", back_populates="category", cascade="all, delete-orphan"
    )
    user = relationship("User", back_populates="categories")


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

    # Cascade delete ensures related AffirmationCategory rows are deleted when an Affirmation is deleted
    user = relationship("User", back_populates="affirmations")
    categories = relationship(
        "AffirmationCategory",
        back_populates="affirmation",
        cascade="all, delete-orphan",
    )
    daily_history = relationship("DailyMailHistory", back_populates="affirmation")
    saved_affirmations = relationship("SavedAffirmation", back_populates="affirmation")
    user_affirmations = relationship("UserAffirmation", back_populates="affirmation")


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
    success = Column(Boolean, default=False)
    error_message = Column(Text)

    user = relationship("User", back_populates="daily_mail_history")
    affirmation = relationship("Affirmation", back_populates="daily_history")


class SavedAffirmation(db.Model):
    __tablename__ = "saved_affirmations"

    saved_affirmation_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    affirmation_id = Column(
        Integer,
        ForeignKey("affirmations.affirmation_id", ondelete="CASCADE"),
        nullable=False,
    )

    user = relationship("User", back_populates="saved_affirmations")
    affirmation = relationship("Affirmation", back_populates="saved_affirmations")


class UserAffirmation(db.Model):
    __tablename__ = "user_affirmations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    affirmation_id = Column(
        Integer,
        ForeignKey("affirmations.affirmation_id", ondelete="CASCADE"),
        nullable=False,
    )
    action_type = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    __table_args__ = (
        UniqueConstraint("user_id", "affirmation_id", name="user_affirmation_uc"),
    )

    user = relationship("User", back_populates="user_affirmations")
    affirmation = relationship("Affirmation", back_populates="user_affirmations")
