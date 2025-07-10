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

### Run the application

```bash
uv run main.py
```

## - Running with Docker

For easier deployment and environment consistency, you can run this application using Docker.

### Prerequisites for Docker

- **Docker Desktop**: Make sure you have Docker Desktop installed on your system. You can download it from https://www.docker.com/products/docker-desktop/ or https://docs.docker.com/engine/install/ for linux.
- **Docker Files**: Ensure that Dockerfile and docker-compose.yml are present in the root directory of this project.

### Using Docker Compose

<ol>
  <li>
    <b>Build and Run the Application:</b><br>Open your terminal in the project's root directory (where docker-compose.yml is located) and run:<br><pre>docker compose up --build -d</pre>
    <ul>
      <li><code>docker compose up</code>: Builds (if necessary) and starts the services defined in <code>docker-compose.yml</code>.</li>
      <li><code>--build</code>: Ensures the Docker image is rebuilt, picking up any changes in your <code>Dockerfile</code> or source code.</li>
      <li><code>-d</code>: Runs the containers in detached mode (in the background).</li>
    </ul>
  </li>
  <li>
    <b>Access the Application:</b><br>Your Flask application should now be running and accessible at <code>http://localhost:8000</code> in your web browser.
  </li>
  <li>
    <b>Stop the Application:</b><br>To stop and remove the containers, networks, and volumes created by <code>docker compose up</code>, run:
    <pre>docker compose down</pre>
  </li>
</ol>

## Project Structure

```
indigo-class/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── controllers/
│   │   ├── root.py          # Root blueprint and routes
│   │   └── auth.py          # Authentication
│   ├── static/              # Static files (CSS, JS, images)
│   └── templates/           # HTML templates
│       ├── base.html        # Base template
│       ├── _header.html     # Base template's header
│       ├── _footer.html     # Base template's footer
│       ├── home/
│       │   ├── index.html             # Home page template
│       │   ├── dashboard.html         # User dashboard template
│       │   └── admin_dashboard.html   # Admin dashboard template:w
│       └── auth/
│           ├── register.html   # Account registration template
│           ├── login.html      # Login template 
│           └── profile.html    # User profile template
├── main.py                  # Application entry point
├── pyproject.toml           # Project configuration
└── README.md                # This file
```
