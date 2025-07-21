from app.models import (
    db,
    User,
    Role,
    Category,
    Affirmation,
    AffirmationCategory,
    UserRole,
)
from werkzeug.security import generate_password_hash


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
                password_hash=generate_password_hash(user_data["password"]),
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
    users = User.query.all()
    default_categories = [
        "Motivation",
        "Gratitude",
        "Self-Love",
        "Health",
        "Relationships",
        "Career",
        "Finance",
        "Personal Growth",
        "Spirituality",
        "Creativity",
        "Fun",
        "Family",
        "Friends",
        "Romance",
        "Travel",
        "Entertainment",
        "Technology",
    ]
    for user in users:
        for cat_name in default_categories:
            exists = Category.query.filter_by(
                user_id=user.user_id, name=cat_name
            ).first()
            if not exists:
                cat = Category(
                    name=cat_name, user_id=user.user_id, is_admin_set=(user.is_admin())
                )
                db.session.add(cat)
    db.session.commit()


def seed_affirmations():
    users = User.query.all()
    sample_affirmations = [
        ("Strength flows through every challenge I face.", "Motivation"),
        ("Gratitude fills my heart for the little moments.", "Gratitude"),
        ("Self-acceptance brings me peace and confidence.", "Self-Love"),
        ("Healthy choices nourish my body and mind.", "Health"),
        ("Love and support surround my relationships.", "Relationships"),
        ("Opportunities for growth appear in my career.", "Career"),
        ("Abundance and security are present in my finances.", "Finance"),
        ("Every day is a chance to learn something new.", "Personal Growth"),
        ("A sense of connection guides my spirit.", "Spirituality"),
        ("Creative ideas flow freely and inspire me.", "Creativity"),
        ("Joy and laughter brighten my experiences.", "Fun"),
        ("Family time creates lasting memories.", "Family"),
        ("Friendships bring warmth and understanding.", "Friends"),
        ("Romance is nurtured with kindness and care.", "Romance"),
        ("Adventure awaits in every new destination.", "Travel"),
        ("Entertainment brings relaxation and delight.", "Entertainment"),
        ("Technology empowers me to achieve my goals.", "Technology"),
        ("Nutritious meals energize my body.", "Health"),
        ("Mindfulness supports my mental well-being.", "Mental Health"),
        ("Movement and rest keep my body strong.", "Physical Health"),
        ("Emotions are valid and guide me wisely.", "Emotional Health"),
        ("Spiritual practices bring me clarity and calm.", "Spiritual Health"),
        ("Meaningful connections enrich my social life.", "Social Health"),
        ("Caring for the environment makes a difference.", "Environmental Health"),
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
