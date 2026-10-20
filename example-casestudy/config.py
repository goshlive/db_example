"""Read configuration from this example's .env, independent of the parent project."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Existing environment variables take precedence over this local .env file.
load_dotenv(Path(__file__).resolve().with_name('.env'), override=False)


def enabled(name):
    return os.getenv(name, 'false').strip().lower() in {'true', '1', 'yes'}


def database_config():
    required = ['DB_USER', 'DB_PASSWORD', 'DB_NAME']
    missing = [key for key in required if key not in os.environ]
    if missing:
        raise ValueError('Configure the local .env first. Missing: ' + ', '.join(missing))
    return {
        'host': os.getenv('DB_HOST', '127.0.0.1'),
        'port': int(os.getenv('DB_PORT', '3306')),
        'user': os.environ['DB_USER'],
        'password': os.environ['DB_PASSWORD'],
        'database': os.environ['DB_NAME'],
        'charset': 'utf8mb4',
    }
