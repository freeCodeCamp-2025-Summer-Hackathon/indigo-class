# DailyDose

A platform for daily affirmations and positive self-talk.

## - Prerequisites

<details>
  <summary> Install <code><a href="https://docs.astral.sh/uv/">uv</a></code> package manager</summary>

### **Install with curl**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### **Install with wget**

```bash
wget -qO- https://astral.sh/uv/install.sh | sh
```

### **Install on Windows (PowerShell)**

Use `irm` to download the script and execute it with `iex`:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

> ⚠️ Changing the execution policy allows running a script from the internet.

</details>

## - Running the Application

### Configure environment variables

```bash
cp .env.example .env
```
 
### Install dependencies

> **uv** will automatically manage the required Python version for this project, so you don't have to worry about installing the correct Python version yourself.

```bash
uv sync
```

### Seed the database
> **Note:** This will add some sample data to the database.
```bash
uv run seed.py
```

### Run the application

```bash
uv run main.py
```

## - Running with Docker

For easier deployment and environment consistency, you can run this application using Docker.

### Configure environment variables

```bash
cp .env.example .env
```

Then, open the .env file and make sure the following variables are set correctly:

```
FLASK_DEBUG=True
POSTGRES_DB=dailydose_db
POSTGRES_USER=dailydose_user
POSTGRES_PASSWORD=dailydose_password
DATABASE_URL=postgresql://dailydose_user:dailydose_password@db:5432/dailydose_db
```

### Prerequisites for Docker

- **Docker Desktop**: Make sure you have Docker Desktop installed on your system. You can download it from https://www.docker.com/products/docker-desktop/ or https://docs.docker.com/engine/install/ for linux.
- **Docker Files**: Ensure that Dockerfile and docker-compose.yml are present in the root directory of this project.

### Using Docker Compose

1. **Build and Run the Application:**<br>Open your terminal in the project's root directory (where docker-compose.yml is located) and run:
    ```
    docker compose up --build -d
    ```
    - `docker compose up`: Builds (if necessary) and starts the services defined in `docker-compose.yml`.
    - `--build`: Ensures the Docker image is rebuilt, picking up any changes in your `Dockerfile` or source code.
    - `-d`: Runs the containers in detached mode (in the background).
1. **Access the Application:**<br>Your Flask application should now be running and accessible at `http://localhost:8000` in your web browser.
1. **Stop the Application:**<br>To stop and remove the containers, networks, and volumes created by `docker compose up`, run:
    ```
    docker compose down
    ```

## Project Structure

```
indigo-class/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── controllers/
│   │   ├── root.py          # Root blueprint and routes
│   │   ├── auth.py          # Authentication blueprint and routes
│   │   ├── affirmations.py  # Affirmation blueprint and routes
│   │   ├── categories.py    # Affirmation categories blueprint and routes
│   │   ├── user.py          # User blueprint and routes
│   │   └── admin/
│   │       ├── dashboard.py   # Admin dashboard blueprint and routes
│   │       └── user.html      # User management blueprint and routes
│   ├── static/              # Static files (CSS, JS, images)
│   └── templates/           # HTML templates
│       ├── base.html a      # Base template
│       ├── _header.html     # Base template's header partial
│       ├── _footer.html     # Base template's footer partial
│       ├── home/
│       │   ├── index.html             # Home page template
│       │   └── dashboard.html         # User dashboard template
│       ├── auth/
│       │   ├── register.html                 # Account registration template
│       │   ├── login.html                    # Login template
│       │   ├── reset_password_request.html   # Password reset request template
│       │   ├── new_password.html             # New password input template
│       │   └── user_settings.html            # User settings template
│       ├── affirmations/
│       │   ├── index.html   # Affirmation list template
│       │   ├── add.html     # Affirmation submission template
│       │   └── edit.html    # Affirmation edit template
│       ├── categories/
│       │   ├── list.html    # Affirmation categeries list template
│       │   ├── add.html     # Affirmation category submission template
│       │   └── edit.html    # Affirmation category edit template
│       └── admin/
│           ├── dashboard.html      # Admin dashboard template
│           ├── users.html          # Users management template
│           ├── affirmations.html   # Affirmation management template
│           ├── categories.html     # Categories management template
│           ├── analytics.html      # Analytics template
│           └── settings.html       # Admin settings template
├── main.py                  # Application entry point
├── pyproject.toml           # Project configuration
├── Dockerfile               # Instructions for building the Docker image
├── docker-compose.yml       # Requirements for building the Docker image
└── README.md                # This file
```
