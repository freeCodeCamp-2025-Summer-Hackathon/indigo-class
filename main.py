import os

from app import create_app
from dotenv import load_dotenv

load_dotenv()


if not os.environ.get("DATABASE_URL"):
    raise ValueError("DATABASE_URL is not set")


def main():
    """Main function to run the flask application."""
    app = create_app()

    host = os.environ.get("FLASK_HOST", "0.0.0.0")
    port = int(os.environ.get("FLASK_PORT", 8000))
    debug = os.environ.get("FLASK_DEBUG", "False").lower() == "true"

    print(f"starting on http://{host}:{port}")

    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    main()
