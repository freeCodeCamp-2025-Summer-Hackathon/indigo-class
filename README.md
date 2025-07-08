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
