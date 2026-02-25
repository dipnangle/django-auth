"""Auto-select settings based on DJANGO_ENV environment variable."""

import os

env = os.environ.get("DJANGO_ENV", "development")

if env == "production":
    from .production import *  # noqa
elif env == "staging":
    from .staging import *  # noqa
elif env == "test":
    from .test import *  # noqa
else:
    from .development import *  # noqa
