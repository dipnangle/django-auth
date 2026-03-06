curl -s -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"dipnangle@gmail.com","password":"Dipnangle@908"}' | python3 -m json.tool


curl -s -X POST http://localhost:8000/api/v1/2fa/verify/email/ \
  -H "Content-Type: application/json" \
  -d '{
    "code": "116030",
    "partial_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiMmZhX3BlbmRpbmciLCJ1c2VyX2lkIjoiMTc4NGY4ZmQtNzg3MS00NWRhLThkMjAtNzM5OGZlNmZlNzU3IiwianRpIjoiMmRhYmM3MzItNDM4Yi00MzZhLTgwNDItN2Y2ODViMDc3YzdjIiwiaWF0IjoxNzcyODAxNjA3LCJleHAiOjE3NzI4MDE5MDcsImlzcyI6InBsYXRmb3JtIiwiYXVkIjoicGxhdGZvcm0tYXBpIn0.m4xCy1uNnF0dT4ova_wGr7WzFaGcJt-wkoj5YiHTVv0"
  }' | python3 -m json.tool



  {
    "requires_2fa": false,
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwidXNlcl9pZCI6IjE3ODRmOGZkLTc4NzEtNDVkYS04ZDIwLTczOThmZTZmZTc1NyIsImVtYWlsIjoiZGlwbmFuZ2xlQGdtYWlsLmNvbSIsImp0aSI6IjE5ODAwYzQ2LWJhNzctNGFhOS1iOTAwLThkMjA3MzhlYzI5NCIsImlhdCI6MTc3MjcwMjYwMSwiZXhwIjoxNzcyNzAzNTAxLCJpc3MiOiJwbGF0Zm9ybSIsImF1ZCI6InBsYXRmb3JtLWFwaSIsInJvbGUiOiJST09UIiwicm9sZV9sZXZlbCI6MH0.ie39swd29QLYGmYAySSrzab936dlJmBpnDcQByidkJQ",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsInVzZXJfaWQiOiIxNzg0ZjhmZC03ODcxLTQ1ZGEtOGQyMC03Mzk4ZmU2ZmU3NTciLCJqdGkiOiIxYTY1MmFlZS1iYTM0LTRiZGMtYjg1Ny00OWEyZDcyMTJkNTkiLCJpYXQiOjE3NzI3MDI2MDEsImV4cCI6MTc3MzMwNzQwMSwiaXNzIjoicGxhdGZvcm0iLCJhdWQiOiJwbGF0Zm9ybS1hcGkifQ.UWGo6gbh9ldHsSUoY7fbSXB1_QZ7DlddU4W8vSh3KPQ",
    "token_type": "Bearer",
    "expires_in": 900,
    "refresh_jti": "1a652aee-ba34-4bdc-b857-49a2d7212d59",
    "user_id": "1784f8fd-7871-45da-8d20-7398fe6fe757",
    "email": "dipnangle@gmail.com"
}

# List all users
curl -s http://localhost:8000/api/v1/users/ \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# Get your own profile
curl -s http://localhost:8000/api/v1/users/me/ \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwidXNlcl9pZCI6IjE3ODRmOGZkLTc4NzEtNDVkYS04ZDIwLTczOThmZTZmZTc1NyIsImVtYWlsIjoiZGlwbmFuZ2xlQGdtYWlsLmNvbSIsImp0aSI6IjE5ODAwYzQ2LWJhNzctNGFhOS1iOTAwLThkMjA3MzhlYzI5NCIsImlhdCI6MTc3MjcwMjYwMSwiZXhwIjoxNzcyNzAzNTAxLCJpc3MiOiJwbGF0Zm9ybSIsImF1ZCI6InBsYXRmb3JtLWFwaSIsInJvbGUiOiJST09UIiwicm9sZV9sZXZlbCI6MH0.ie39swd29QLYGmYAySSrzab936dlJmBpnDcQByidkJQ"

# Create SUPERADMIN user using role_id
curl -s -X POST http://localhost:8000/api/v1/users/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "dipesh@virtualizor.com",
    "password": "SecurePass123!",
    "first_name": "end",
    "last_name": "user",
    "role_id": "f54866ce-588e-4c06-95e3-9b70128055db"
  }' | python3 -m json.tool



curl -s http://localhost:8000/api/v1/roles/ \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

[
    {
        "id": "bbfe9870-418b-479d-8d64-acdcdafbd729",
        "name": "SUPERADMIN",
        "level": 10
    },
    {
        "id": "e00d5e6e-ab58-432c-b93c-2fca7fb696c9",
        "name": "ADMIN_PLUS",
        "level": 20
    },
    {
        "id": "e54f7d38-0fb1-423b-8fe2-946e518b2673",
        "name": "ADMIN",
        "level": 30
    },
    {
        "id": "f54866ce-588e-4c06-95e3-9b70128055db",
        "name": "END_USER",
        "level": 40
    }
]


python3 -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from apps.users.models import User
from apps.roles.models import Role

# Fix dipnanggle -> SUPERADMIN
superadmin_role = Role.objects.get(name='SUPERADMIN')
enduser_role = Role.objects.get(name='END_USER')

u1 = User.objects.all_including_deleted().get(email='dipnangle31@gmail.com')
u1.global_role = superadmin_role
u1.save(update_fields=['global_role'])
print(f'✅ {u1.email} -> {u1.global_role}')

u2 = User.objects.all_including_deleted().get(email='dipesh@virtualizor.com')
u2.global_role = enduser_role
u2.save(update_fields=['global_role'])
print(f'✅ {u2.email} -> {u2.global_role}')
"


curl -s -X POST http://localhost:8000/api/v1/users/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newadmin_plus@test.com",
    "password": "AdminPLus123!",
    "first_name": "admin",
    "last_name": "Plus",
    "role_id": "e00d5e6e-ab58-432c-b93c-2fca7fb696c9"
  }' | python3 -m json.tool
  

# admin plus login
curl -s -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"newadmin_plus@test.com","password":"AdminPLus123!"}' | python3 -m json.tool
  
# super admin login
curl -s -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"dipnangle31@gmail.com","password":"SuperAdmin@123"}' | python3 -m json.tool
  
# end user login
curl -s -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"dipesh@virtualizor.com","password":"EndUser@123"}' | python3 -m json.tool
  
  
# Check user
python3 -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from apps.users.models import User
try:
    u = User.objects.all_including_deleted().get(email='newadmin_plus@test.com')
    print(f'Email: {u.email}')
    print(f'Active: {u.is_active}')
    print(f'Email verified: {u.is_email_verified}')
    print(f'Deleted: {u.is_deleted}')
    print(f'Global role: {u.global_role}')
    print(f'Password usable: {u.has_usable_password()}')
except User.DoesNotExist:
    print('User not found - listing all users:')
    for u in User.objects.all_including_deleted():
        print(f'  {u.email} | verified: {u.is_email_verified} | role: {u.global_role}')
"
  
  
  python3 -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from apps.users.models import User

u = User.objects.all_including_deleted().get(email='dipesh@virtualizor.com')
u.set_password('EndUser@123')
u.save(update_fields=['password'])
print(f'✅ Password reset for: {u.email}')
"


# new user creation
curl -s -X POST http://localhost:8000/api/v1/users/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "nangledip@gmail.com",
    "password": "SecurePass123!",
    "first_name": "Test",
    "last_name": "User",
    "role_id": "f54866ce-588e-4c06-95e3-9b70128055db"
  }' | python3 -m json.tool

# delete all user other than root
python3 -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from apps.users.models import User
from apps.roles.models import Role

root_role = Role.objects.get(name='ROOT')
deleted = User.objects.all_including_deleted().exclude(global_role=root_role).delete()
print(f'✅ Deleted: {deleted}')
"
  
  
http://10.0.0.20:3000/verify-email?token=gnME5odyHHd3U4a5PeB_iDNydJo6QoYJSos6xmuKQEhWAXkfnVhZqduQjnFeWF0n

curl -s -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"dipesh@virtualizor.com","password":"SecurePass123!"}' | python3 -m json.tool
  
  
# verify the email
curl -s -X POST http://10.0.0.20:8000/api/v1/auth/verify-email/ \
  -H "Content-Type: application/json" \
  -d '{"token": "tdMzOotDAR3vga04yZI-Gk3eY0jfPBckVASHhrSYS2n36d6MFiNrFOLUvleLppcw"}' | python3 -m json.tool
  

# Step 1 — Request reset link (sends email)
curl -s -X POST http://10.0.0.20:8000/api/v1/auth/password/reset/ \
  -H "Content-Type: application/json" \
  -d '{"email": "dipesh@virtualizor.com"}' | python3 -m json.tool
  
http://10.0.0.20:8000/reset-password?token=_JOtbPx4TJ96fD4OpEbqbwia_aJYJrWDlcRpNYpOALAe2entENXD3EnNgbyFvQto
  
http://10.0.0.20:8000/password/reset/confirm/?token=zy4N2Ef3Tc7FbdKnEIZzFDbQeEdOcuHVnU7ZJTd_udVh0oTkWHLLxwg-fJQN4tNV

# Step 2 — Extract token from email link and confirm
curl -s -X POST http://10.0.0.20:8000/api/v1/auth/password/reset/confirm/ \
  -H "Content-Type: application/json" \
  -d '{
    "token": "_JOtbPx4TJ96fD4OpEbqbwia_aJYJrWDlcRpNYpOALAe2entENXD3EnNgbyFvQto",
    "new_password": "NewPassword123!"
  }' | python3 -m json.tool 
  
  
curl -s -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"dipesh@virtualizor.com","password":"NewPassword123!"}' | python3 -m json.tool


# 1 — Redis
redis-cli ping
redis-cli info server | grep "redis_version\|uptime"

# 2 — Check Redis connection from Django
cd /home/django/repo/backend
python3 -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from django.core.cache import cache
cache.set('test_key', 'test_value', 30)
result = cache.get('test_key')
print('✅ Redis cache working:', result)
"

# 3 — Check rate limiter specifically
python3 -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from apps.authentication.rate_limit import get_login_limiter
limiter = get_login_limiter('test_ip')
print('✅ Rate limiter working:', limiter)
"

# 4 — Check Celery (email tasks queue)
python3 -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from django.conf import settings
print('Celery broker:', settings.CELERY_BROKER_URL)
"

# 5 — Check overall health endpoint
curl -s http://10.0.0.20:8000/api/health/ | python3 -m json.tool


# fixes
python3 -c "
content = open('/home/django/repo/backend/config/celery.py').read()
if 'broker_connection_retry_on_startup' not in content:
    content = content.replace(
        'app.conf.update(',
        'app.conf.update(\n    broker_connection_retry_on_startup=True,'
    )
    open('/home/django/repo/backend/config/celery.py', 'w').write(content)
    print('Fixed')
else:
    print('Already present')
"

# checking the logout
# Login first to get tokens
curl -s -X POST http://10.0.0.20:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"dipnangle@gmail.com","password":"Dipnangle@908"}' | python3 -m json.tool
  
  
# confirm login
curl -s -X POST http://localhost:8000/api/v1/2fa/verify/email/ \
  -H "Content-Type: application/json" \
  -d '{
    "code": "382033",
    "partial_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiMmZhX3BlbmRpbmciLCJ1c2VyX2lkIjoiMTc4NGY4ZmQtNzg3MS00NWRhLThkMjAtNzM5OGZlNmZlNzU3IiwianRpIjoiYThiOTNmZDAtMjg3OS00M2M1LWJiMzMtM2VhMGY1NmE2ZWM1IiwiaWF0IjoxNzcyNzI1MzQzLCJleHAiOjE3NzI3MjU2NDMsImlzcyI6InBsYXRmb3JtIiwiYXVkIjoicGxhdGZvcm0tYXBpIn0.o6DXn4aVej82pj5_-KlwNgglqCxGk7y9JePyALJXVmA"
  }' | python3 -m json.tool
  
  
ACCESS_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwidXNlcl9pZCI6IjE3ODRmOGZkLTc4NzEtNDVkYS04ZDIwLTczOThmZTZmZTc1NyIsImVtYWlsIjoiZGlwbmFuZ2xlQGdtYWlsLmNvbSIsImp0aSI6IjBjMjEyYWNlLTY2MjQtNGVjYy05YmQyLWRiYjZhNDliNTM0YyIsImlhdCI6MTc3MjcyMzY4NiwiZXhwIjoxNzcyNzI0NTg2LCJpc3MiOiJwbGF0Zm9ybSIsImF1ZCI6InBsYXRmb3JtLWFwaSIsInJvbGUiOiJST09UIiwicm9sZV9sZXZlbCI6MH0.NEs3p77M6NmVG7qhnGTeyPQqT3aKzCqBlN2N3NqRa_w"
# logout
curl -s -X POST http://10.0.0.20:8000/api/v1/auth/logout/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsInVzZXJfaWQiOiIxNzg0ZjhmZC03ODcxLTQ1ZGEtOGQyMC03Mzk4ZmU2ZmU3NTciLCJqdGkiOiI2ZGU0NjUzNS1kMTA3LTRkYjItYWY1Yi1kNTNhOWU1ZWFkY2IiLCJpYXQiOjE3NzI3MjM2ODYsImV4cCI6MTc3MzMyODQ4NiwiaXNzIjoicGxhdGZvcm0iLCJhdWQiOiJwbGF0Zm9ybS1hcGkifQ.9tZynGOpP2n6lPqrx_3UqsVXzTA46q5W74kmXHRzIqw"}' | python3 -m json.tool
  
curl -s -X POST http://10.0.0.20:8000/api/v1/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsInVzZXJfaWQiOiIxNzg0ZjhmZC03ODcxLTQ1ZGEtOGQyMC03Mzk4ZmU2ZmU3NTciLCJqdGkiOiI2ZGU0NjUzNS1kMTA3LTRkYjItYWY1Yi1kNTNhOWU1ZWFkY2IiLCJpYXQiOjE3NzI3MjM2ODYsImV4cCI6MTc3MzMyODQ4NiwiaXNzIjoicGxhdGZvcm0iLCJhdWQiOiJwbGF0Zm9ybS1hcGkifQ.9tZynGOpP2n6lPqrx_3UqsVXzTA46q5W74kmXHRzIqw"}' | python3 -m json.tool
  
curl -s -X DELETE http://10.0.0.20:8000/api/v1/sessions/dbaec805-950f-4312-9cf6-cfce2f91c505/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" | python3 -m json.tool
  
  
  
# List audit logs
curl -s http://10.0.0.20:8000/api/v1/audit/ \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
  

# verify email first
cd /home/django/repo/backend
python3 -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from apps.users.models import User
emails = ['test_admin@test.com', 'test_enduser@test.com']
for email in emails:
    try:
        u = User.objects.get(email=email)
        u.is_email_verified = True
        u.save(update_fields=['is_email_verified', 'updated_at'])
        print(f'✅ {u.email} verified | role: {u.global_role}')
    except User.DoesNotExist:
        print(f'❌ {email} not found')
"


# disable 2fa

python3 -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from apps.users.models import User
emails = ['test_admin@test.com', 'test_enduser@test.com']
for email in emails:
    try:
        u = User.objects.get(email=email)
        u.is_2fa_enabled = False
        u.is_2fa_enforced = False
        u.save(update_fields=['is_2fa_enabled', 'is_2fa_enforced', 'updated_at'])
        print(f'✅ {u.email} 2FA disabled')
    except User.DoesNotExist:
        print(f'❌ {email} not found')
"


# check the users with heirarchy and thier ids
cd /home/django/repo/backend
python3 -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from apps.users.models import User
for u in User.objects.all():
    print(f'{u.email} | ID: {u.id} | Role: {u.global_role}')
"


# ADMIN token
ADMIN_TOKEN=$(curl -s -X POST http://10.0.0.20:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test_admin@test.com","password":"Admin123!"}' | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('access_token',''))")
echo "ADMIN TOKEN: $ADMIN_TOKEN"


# ❌ END_USER tries to delete ADMIN — should fail
curl -s -X DELETE http://10.0.0.20:8000/api/v1/users/331b0755-d9e9-47b2-8aaf-16230fe1aee2/ \
  -H "Authorization: Bearer $ENDUSER_TOKEN" | python3 -m json.tool

# ❌ ADMIN tries to delete SUPERADMIN — should fail
curl -s -X DELETE http://10.0.0.20:8000/api/v1/users/1784f8fd-7871-45da-8d20-7398fe6fe757/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python3 -m json.tool

# ✅ ROOT deletes END_USER — should work
curl -s -X DELETE http://10.0.0.20:8000/api/v1/users/854a07ee-0231-49ee-a896-3ace25ea069d/ \
  -H "Authorization: Bearer $ROOT_TOKEN" | python3 -m json.tool
  
# check the all code for organisation
python manage.py show_urls 2>/dev/null | grep "organ"

# create organization
curl -s -X POST http://10.0.0.20:8000/api/v1/organizations/ \
  -H "Authorization: Bearer $ROOT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Company",
    "slug": "test-company",
    "deployment_mode": "cloud"
  }' | python3 -m json.tool
  
  
# check orgnization
curl -s http://10.0.0.20:8000/api/v1/organizations/ \
  -H "Authorization: Bearer $ROOT_TOKEN" | python3 -m json.tool

# check users with satff role
# Create a staff SUPERADMIN and test
cd /home/django/repo/backend
python3 -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from apps.users.models import User
from apps.roles.models import Role

# Check existing users and their global_role
for u in User.objects.all():
    print(f'{u.email} | global_role: {u.global_role} | is_staff: {u.global_role.level if u.global_role else \"org-level\"}')
"

# create superadmin
cd /home/django/repo/backend

# Create staff SUPERADMIN (global_role = SUPERADMIN, no org) with no verification and skip the 2fa
python3 -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from apps.users.services import create_user
from apps.roles.models import Role

role = Role.objects.get(name='SUPERADMIN')
user = create_user(
    email='staff_superadmin@test.com',
    password='StaffAdmin123!',
    first_name='Staff',
    last_name='SuperAdmin',
    role=role,
    send_verification=False,
    is_email_verified=True,
)
user.is_2fa_enabled = False
user.is_2fa_enforced = False
user.save(update_fields=['is_2fa_enabled', 'is_2fa_enforced'])
print(f'✅ Created: {user.email} | global_role: {user.global_role}')
"

# Step 1 — Create user WITHOUT global role first
cd /home/django/repo/backend

python3 -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from apps.users.models import User

# Create bare user with no global role
user = User.objects.create_user(
    email='org_superadmin@test.com',
    password='OrgAdmin123!',
    first_name='Org',
    last_name='SuperAdmin',
    is_email_verified=True,
    is_active=True,
    is_2fa_enabled=False,
    is_2fa_enforced=False,
)
print(f'✅ Created: {user.email} | global_role: {user.global_role}')
"

# add the superadmin in orgnization
# Step 2 — Add this user to Test Company org with SUPERADMIN role
python3 -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from apps.organizations.models import Organization
from apps.organizations.services import add_member_to_organization
from apps.users.models import User
from apps.roles.models import Role

org = Organization.objects.get(slug='test-company')
user = User.objects.get(email='org_superadmin@test.com')
role = Role.objects.get(name='SUPERADMIN')

add_member_to_organization(organization=org, user=user, role=role, added_by=user)
print(f'✅ {user.email} added to {org.name} as SUPERADMIN')
print(f'global_role: {user.global_role}')
"

# Step 3 — Login and check what orgs they see
ORG_ADMIN_TOKEN=$(curl -s -X POST http://10.0.0.20:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"org_superadmin@test.com","password":"OrgAdmin123!"}' | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('access_token',''))")
echo "Token: $ORG_ADMIN_TOKEN"

# Should only see Test Company
curl -s http://10.0.0.20:8000/api/v1/organizations/ \
  -H "Authorization: Bearer $ORG_ADMIN_TOKEN" | python3 -m json.tool
  
  
# create plan for orgnization
python3 -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from apps.plans.models import Plan, License
from apps.organizations.models import Organization
from apps.users.models import User
from django.utils import timezone

plan, created = Plan.objects.get_or_create(
    tier='basic',
    defaults={
        'name': 'Basic',
        'max_superadmins': 5,
        'max_admin_plus': 5,
        'max_admins': 10,
        'max_end_users': 50,
        'features_json': {},
        'is_active': True,
        'price_monthly_usd': 0,
        'price_yearly_usd': 0,
    }
)
print(f'✅ Plan: {plan.name} (created: {created})')

org = Organization.objects.get(slug='test-company')
root = User.objects.get(email='dipnangle@gmail.com')
license, created = License.objects.get_or_create(
    organization=org,
    defaults={
        'plan': plan,
        'is_active': True,
        'valid_from': timezone.now(),
        'valid_until': timezone.now() + timezone.timedelta(days=365),
        'created_by': root,
    }
)
print(f'✅ License: created={created} | org={org.name} | plan={plan.name}')
"


# invitation creation

curl -s -X POST http://10.0.0.20:8000/api/v1/invitations/ \
  -H "Authorization: Bearer $ROOT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@invitaion.com",
    "role_id": "e54f7d38-0fb1-423b-8fe2-946e518b2673",
    "organization_id": "4b546ec7-acab-40cd-97e9-3087a3ae8654"
  }' | python3 -m json.tool