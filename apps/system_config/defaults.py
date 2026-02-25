"""System config defaults."""

DEFAULTS = {
    "lockout_max_attempts": 5,
    "lockout_duration_minutes": 30,
    "lockout_progressive": True,
    "password_min_length": 10,
    "password_expiry_days": 0,  # 0 = never expires
    "session_max_per_user": 10,
    "require_2fa_for_admins": True,
    "allow_self_registration": True,
    "invite_expiry_hours": 72,
    "maintenance_mode": False,
    "maintenance_message": "We're currently undergoing maintenance. Please check back soon.",
}
