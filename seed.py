import bcrypt
from app.models import (
    db,
    User,
    Role,
    Category,
    Affirmation,
    AffirmationCategory,
    UserRole,
)


def seed_roles():
    db.create_all()

    roles = [
        {"name": "admin", "description": "Administrator with full access"},
        {"name": "user", "description": "Regular user"},
    ]
    for role_data in roles:
        role = Role.query.filter_by(name=role_data["name"]).first()
        if not role:
            role = Role(**role_data)
            db.session.add(role)
    db.session.commit()


def seed_users():
    users = [
        {
            "name": "Admin User",
            "username": "admin",
            "email": "admin@example.com",
            "password": "adminpass",
            "is_email_opt_in": False,
            "roles": ["admin"],
        },
        {
            "name": "Regular User",
            "username": "user1",
            "email": "user1@example.com",
            "password": "userpass",
            "is_email_opt_in": True,
            "roles": ["user"],
        },
        {
            "name": "Regular User",
            "username": "user2",
            "email": "user2@example.com",
            "password": "userpass",
            "is_email_opt_in": True,
            "roles": ["user"],
        },
        {
            "name": "Regular User",
            "username": "user3",
            "email": "user3@example.com",
            "password": "userpass",
            "is_email_opt_in": True,
            "roles": ["user"],
        },
        {
            "name": "Regular User",
            "username": "user4",
            "email": "user4@example.com",
            "password": "userpass",
            "is_email_opt_in": True,
            "roles": ["user"],
        },
        {
            "name": "Regular User",
            "username": "user5",
            "email": "user5@example.com",
            "password": "userpass",
            "is_email_opt_in": True,
            "roles": ["user"],
        },
    ]
    for user_data in users:
        user = User.query.filter_by(username=user_data["username"]).first()
        if not user:
            user = User(
                name=user_data["name"],
                username=user_data["username"],
                email=user_data["email"],
                password_hash=bcrypt.hashpw(
                    user_data["password"].encode("utf-8"), bcrypt.gensalt()
                ).decode("utf-8"),
                is_email_opt_in=user_data["is_email_opt_in"],
            )
            db.session.add(user)
            db.session.flush()
            for role_name in user_data["roles"]:
                role = Role.query.filter_by(name=role_name).first()
                if role:
                    user_role = UserRole(user_id=user.user_id, role_id=role.role_id)
                    db.session.add(user_role)
    db.session.commit()


def seed_categories():
    default_categories = [
        "Motivation",
        "Gratitude",
        "Health",
        "Career",
        "Finance",
        "Creativity",
        "Family",
        "Travel",
        "Sports",
        "Education",
    ]
    for cat_name in default_categories:
        exists = Category.query.filter_by(name=cat_name).first()
        admin_user = User.query.filter_by(username="admin").first()
        if not exists:
            cat = Category(name=cat_name, user_id=admin_user.user_id, is_admin_set=True)
            db.session.add(cat)
    db.session.commit()


def seed_affirmations():
    users = User.query.all()
    sample_affirmations = [
        # Motivation
        ("I am capable of achieving anything I set my mind to.", "Motivation"),
        ("Every challenge makes me stronger and wiser.", "Motivation"),
        ("I embrace each day with energy and determination.", "Motivation"),
        ("Success flows naturally to me.", "Motivation"),
        ("I turn obstacles into opportunities.", "Motivation"),
        # Gratitude
        ("I am thankful for all life's blessings.", "Gratitude"),
        ("Each moment brings new reasons to be grateful.", "Gratitude"),
        ("My heart is full of appreciation.", "Gratitude"),
        ("I find joy in simple pleasures.", "Gratitude"),
        ("Abundance surrounds me daily.", "Gratitude"),
        # Health
        ("My body is strong and healthy.", "Health"),
        ("I make choices that nourish my wellbeing.", "Health"),
        ("Vitality flows through me.", "Health"),
        ("I prioritize my health each day.", "Health"),
        ("My immune system is powerful.", "Health"),
        # Career
        ("I excel in my professional life.", "Career"),
        ("Success comes naturally to me.", "Career"),
        ("I attract amazing opportunities.", "Career"),
        ("My work brings me fulfillment.", "Career"),
        ("I am valued in my workplace.", "Career"),
        # Finance
        ("Money flows easily into my life.", "Finance"),
        ("I make wise financial decisions.", "Finance"),
        ("Abundance is my natural state.", "Finance"),
        ("I attract wealth and prosperity.", "Finance"),
        ("Financial success comes easily to me.", "Finance"),
        # Creativity
        ("My creativity knows no bounds.", "Creativity"),
        ("Ideas flow freely through me.", "Creativity"),
        ("I express myself authentically.", "Creativity"),
        ("My imagination is limitless.", "Creativity"),
        ("I am an endless source of inspiration.", "Creativity"),
        # Family
        ("Love fills our home.", "Family"),
        ("My family bonds grow stronger daily.", "Family"),
        ("I cherish family moments.", "Family"),
        ("Harmony exists in my household.", "Family"),
        ("My family supports each other.", "Family"),
        # Travel
        ("Adventures await me everywhere.", "Travel"),
        ("I explore the world fearlessly.", "Travel"),
        ("New experiences enrich my life.", "Travel"),
        ("I embrace different cultures.", "Travel"),
        ("Journey brings me wisdom.", "Travel"),
        # Sports
        ("My athletic abilities improve daily.", "Sports"),
        ("I push my physical limits.", "Sports"),
        ("Victory comes naturally to me.", "Sports"),
        ("I am strong and capable.", "Sports"),
        ("My endurance grows stronger.", "Sports"),
        # Education
        ("Knowledge empowers me.", "Education"),
        ("Learning comes easily to me.", "Education"),
        ("I absorb information naturally.", "Education"),
        ("My mind is sharp and focused.", "Education"),
        ("I embrace new learning opportunities.", "Education"),
    ]
    for user in users:
        for text, cat_name in sample_affirmations:
            affirmation = Affirmation.query.filter_by(
                user_id=user.user_id, affirmation_text=text
            ).first()
            if not affirmation:
                affirmation = Affirmation(
                    affirmation_text=text,
                    user_id=user.user_id,
                    is_admin_set=(user.is_admin()),
                )
                db.session.add(affirmation)
                db.session.flush()

                category = Category.query.filter_by(
                    user_id=user.user_id, name=cat_name
                ).first()
                if category:
                    ac = AffirmationCategory(
                        affirmation_id=affirmation.affirmation_id,
                        category_id=category.category_id,
                    )
                    db.session.add(ac)
    db.session.commit()


def run_all_seeds():
    seed_roles()
    seed_users()
    seed_categories()
    seed_affirmations()
    print("Database seeded successfully.")


if __name__ == "__main__":
    from app import create_app

    app = create_app()

    with app.app_context():
        run_all_seeds()
