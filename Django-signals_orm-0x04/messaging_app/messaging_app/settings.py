import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ... other settings ...

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# ... rest of settings ...