# Directory Restructure Plan

## Current Analysis

### Current Structure Issues

The current project structure is organized around an ESS (Employee Self-Service) specific system with a `modules/` directory approach. This creates unnecessary complexity for a general-purpose backend and couples the architecture to a specific business domain.

**Current Structure:**

```
core-backend/
├── core/
│   ├── manage.py
│   ├── core/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── celery.py
│   │   └── ...
│   └── modules/                    # ❌ Unnecessary nesting
│       ├── accounts/               # ✅ Good auth app
│       └── ESS/                    # ❌ Business-specific, not needed
│           └── ess/
└── demo_frontend/                  # ✅ Keep separate
```

### Current Dependencies & Features

- **Django 5.1.3** with DRF
- **Custom User Model** with employee-specific fields
- **JWT Authentication** with SimpleJWT
- **Two-Factor Authentication (2FA)**
- **Celery** for background tasks
- **Module-based access control** (needs refactoring)
- **Security features** (django-axes, Argon2 hashing)

## Proposed New Structure

### Target Structure

```
core-backend/
├── core/
│   ├── manage.py
│   ├── core/                       # Django project settings
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   ├── asgi.py
│   │   └── celery.py
│   ├── apps/                       # ✅ New: All Django apps here
│   │   └── accounts/               # ✅ Moved from modules/accounts/
│   │       ├── __init__.py
│   │       ├── admin.py
│   │       ├── apps.py
│   │       ├── models.py
│   │       ├── serializers.py
│   │       ├── views.py
│   │       ├── urls.py
│   │       ├── managers.py
│   │       ├── signals.py
│   │       ├── tasks.py
│   │       ├── utils.py
│   │       ├── tests.py
│   │       ├── migrations/
│   │       └── migrations_otp_totp/
│   ├── templates/                  # ✅ Keep templates
│   │   └── two_factor/
│   ├── static/                     # ✅ Add static files directory
│   ├── media/                      # ✅ Add media files directory
│   └── requirements.txt            # ✅ Move requirements to core/
└── frontend/                       # ✅ Rename demo_frontend
    └── ...
```

## Migration Steps

### Phase 1: Restructure Directories

1. **Create new `apps/` directory**

   ```bash
   mkdir core/apps
   echo "" > core/apps/__init__.py
   ```

2. **Move accounts app**

   ```bash
   # Move the entire accounts directory
   mv core/modules/accounts core/apps/accounts
   ```

3. **Remove ESS module** (not needed for general backend)

   ```bash
   rm -rf core/modules/ESS
   rm -rf core/modules
   ```

4. **Rename frontend directory**

   ```bash
   mv demo_frontend frontend
   ```

5. **Move requirements.txt**
   ```bash
   mv requirements.txt core/requirements.txt
   ```

### Phase 2: Update Configuration Files

#### 2.1 Update `core/core/settings.py`

**Changes needed:**

- Update `INSTALLED_APPS` to use new path
- Remove ESS-specific configurations
- Update Python path configuration
- Clean up module-specific settings

**Key changes:**

```python
# OLD
INSTALLED_APPS = [
    # ...
    'modules.accounts.apps.AccountsConfig',
    'modules.ESS.ess.apps.EssConfig',  # ❌ Remove
]

# NEW
INSTALLED_APPS = [
    # ...
    'apps.accounts.apps.AccountsConfig',  # ✅ Update path
]

# OLD
MIGRATION_MODULES = {
    'otp_totp': 'modules.accounts.migrations_otp_totp',  # ❌ Old path
}

# NEW
MIGRATION_MODULES = {
    'otp_totp': 'apps.accounts.migrations_otp_totp',     # ✅ New path
}

# OLD
sys.path.insert(0, os.path.join(BASE_DIR, 'modules'))  # ❌ Remove

# NEW
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))     # ✅ Add apps to path
```

#### 2.2 Update `core/core/urls.py`

```python
# OLD
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(tf_urls)),
    path('api/auth/', include('modules.accounts.urls')),      # ❌ Old path
    path('api/ess/', include('modules.ESS.ess.urls')),       # ❌ Remove ESS
]

# NEW
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(tf_urls)),
    path('api/auth/', include('apps.accounts.urls')),        # ✅ New path
    # Add new API endpoints as needed for future apps
]
```

#### 2.3 Update `apps/accounts/apps.py`

```python
# OLD
class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'modules.accounts'  # ❌ Old path

# NEW
class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.accounts'     # ✅ New path
```

### Phase 3: Clean Up Models and Business Logic

#### 3.1 Refactor User Model (`apps/accounts/models.py`)

**Current issues with User model:**

- Employee-specific fields (`employee_id`)
- ESS-specific module system
- Business domain coupling

**Proposed changes:**

```python
# Make employee_id optional for general use
employee_id = models.CharField(
    max_length=32,
    unique=True,
    null=True,
    blank=True,
    verbose_name="Employee ID"
)

# Rename Module to Permission/Role for general use
class Permission(models.Model):  # Renamed from Module
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    code = models.CharField(max_length=50, unique=True)  # Add code field

    def __str__(self):
        return self.name

# Update User model
class User(AbstractBaseUser, PermissionsMixin):
    # ... existing fields ...
    permissions = models.ManyToManyField(  # Renamed from modules
        'Permission',
        blank=True,
        related_name='users'
    )
```

#### 3.2 Update Documentation

- Create new API documentation
- Update README.md to reflect general-purpose backend
- Remove ESS-specific references

### Phase 4: Testing and Validation

1. **Run migrations** to ensure database schema is updated
2. **Test authentication endpoints** to ensure they work with new structure
3. **Verify static/media file serving**
4. **Test Celery task discovery** with new app structure
5. **Run existing tests** and update imports

## Benefits of New Structure

### ✅ Advantages

1. **Cleaner Architecture**: Standard Django project layout
2. **Domain Agnostic**: No business-specific coupling
3. **Scalable**: Easy to add new apps under `apps/`
4. **Standard**: Follows Django best practices
5. **Maintainable**: Simpler import paths and structure
6. **Flexible**: Can be used for any type of backend service

### 🔧 Technical Improvements

1. **Simplified imports**: `from apps.accounts` instead of `from modules.accounts`
2. **Better organization**: All apps in one place
3. **Easier testing**: Standard Django test discovery
4. **Clear separation**: Core Django config vs. application logic

## Implementation Timeline

| Phase     | Tasks                 | Estimated Time |
| --------- | --------------------- | -------------- |
| 1         | Directory restructure | 30 minutes     |
| 2         | Configuration updates | 1 hour         |
| 3         | Model/logic cleanup   | 2 hours        |
| 4         | Testing & validation  | 1 hour         |
| **Total** |                       | **4.5 hours**  |

## Risk Mitigation

1. **Backup**: Create git branch before starting
2. **Incremental**: Test each phase separately
3. **Rollback plan**: Keep original structure until fully validated
4. **Documentation**: Update all references and docs

## Next Steps After Restructure

1. **Add new apps** as needed (e.g., `apps/api/`, `apps/notifications/`)
2. **Implement proper API versioning**
3. **Add comprehensive logging**
4. **Set up proper CI/CD** with the new structure
5. **Create Docker configuration** for deployment

---

_This plan transforms the ESS-specific backend into a clean, general-purpose Django REST API backend that can be used for any project while maintaining all existing functionality._
