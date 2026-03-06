curl -s -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"dipnangle@gmail.com","password":"Dipnangle@908"}' | python3 -m json.tool


curl -s -X POST http://localhost:8000/api/v1/2fa/verify/email/ \
  -H "Content-Type: application/json" \
  -d '{
    "code": "185068",
    "partial_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiMmZhX3BlbmRpbmciLCJ1c2VyX2lkIjoiMTc4NGY4ZmQtNzg3MS00NWRhLThkMjAtNzM5OGZlNmZlNzU3IiwianRpIjoiMmMzMmY1ZTQtN2FmZS00ZWU0LThhYzYtNmIwNGY2NWQ5ZTM0IiwiaWF0IjoxNzcyNzE2MTg0LCJleHAiOjE3NzI3MTY0ODQsImlzcyI6InBsYXRmb3JtIiwiYXVkIjoicGxhdGZvcm0tYXBpIn0.TsZdjqyxbr1J0AI_Yh8bj5zZDdZcL5tZrklKoPLRT3E"
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