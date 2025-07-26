CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    username VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    is_email_opt_in BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE roles (
    role_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE user_roles (
    user_id INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    role_id INT NOT NULL REFERENCES roles(role_id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, role_id)
);

CREATE TABLE categories (
    category_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    user_id INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    is_admin_set BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE affirmations (
    affirmation_id SERIAL PRIMARY KEY,
    affirmation_text TEXT NOT NULL,
    user_id INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    is_admin_set BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE affirmations_categories (
    affirmation_id INT NOT NULL REFERENCES affirmations(affirmation_id) ON DELETE CASCADE,
    category_id INT NOT NULL REFERENCES categories(category_id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (affirmation_id, category_id)
);

CREATE TABLE daily_mail_history (
    daily_mail_history_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    affirmation_id INT NOT NULL REFERENCES affirmations(affirmation_id) ON DELETE CASCADE,
    sent_email_at TIMESTAMP,
    scheduled_for TIMESTAMP
);

CREATE TABLE saved_affirmations (
    saved_affirmation_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    affirmation_id INT NOT NULL REFERENCES affirmations(affirmation_id) ON DELETE CASCADE
);

CREATE TABLE user_affirmations (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    affirmation_id INT NOT NULL REFERENCES affirmations(affirmation_id) ON DELETE CASCADE,
    action_type TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT user_affirmation_uc UNIQUE(user_id, affirmation_id)
);


ALTER TABLE daily_mail_history DROP COLUMN scheduled_for;
ALTER TABLE daily_mail_history ADD COLUMN success BOOLEAN DEFAULT FALSE;
ALTER TABLE daily_mail_history ADD COLUMN error_message TEXT;
