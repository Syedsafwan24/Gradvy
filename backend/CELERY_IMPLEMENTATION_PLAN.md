# Celery + django-celery-beat Implementation Plan

This plan outlines the steps to integrate Celery and `django-celery-beat` into your Django project, providing a robust solution for background task processing and periodic task scheduling. This setup is recommended for production environments.

**Assumptions:**
*   You have a working Django project.
*   You are familiar with basic Django development.
*   This plan uses Redis as the message broker and result backend.

---

## **Step 1: Install Required Packages**

First, you need to install Celery and `django-celery-beat`.

1.  **Update `requirements.txt`**: Add the following lines to your `requirements.txt` file:
    ```
    celery~=5.3.6
    django-celery-beat~=2.5.0
    redis~=5.0.1 # For Redis broker and result backend
    ```
2.  **Install packages**: Run the following command in your terminal to install them:
    ```bash
    pip install -r requirements.txt
    ```

---

## **Step 2: Configure Django Settings (`core/core/settings.py`)**

You need to integrate `django-celery-beat` into your Django applications and configure Celery's connection to the message broker and result backend.

1.  **Add to `INSTALLED_APPS`**:
    Open `core/core/settings.py` and add `'django_celery_beat'` to your `INSTALLED_APPS` list:
    ```python
    # core/core/settings.py

    INSTALLED_APPS = [
        # ... existing apps
        'django_celery_beat',
        # ... your project apps, e.g., 'core.modules.auth.accounts', 'core.modules.ESS'
    ]
    ```

2.  **Celery Configuration**:
    Add the following Celery-specific settings, preferably at the end of your `settings.py` file.

    *   **Broker URL**: This is where Celery sends and receives messages.
    *   **Result Backend**: This is where Celery stores task results.
    *   **Content Serialization**: Recommended settings for security and compatibility.
    *   **Timezone**: Must match your Django `TIME_ZONE`.
    *   **Beat Scheduler**: Tells Celery Beat to use the Django database for scheduling.

    ```python
    # core/core/settings.py

    # ... (other settings)

    # Celery Configuration
    # For production, use a robust broker like RabbitMQ or a dedicated Redis instance.
    # For local development, you can run Redis via Docker: docker run -p 6379:6379 --name my-redis-container -d redis
    CELERY_BROKER_URL = 'redis://localhost:6379/0' # Using Redis on default port, database 0
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0' # Same for result backend

    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_TIMEZONE = 'UTC' # Or your project's TIME_ZONE, e.g., 'America/New_York'
    CELERY_ENABLE_UTC = True # Recommended to work with UTC
    CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True # Added to ensure broker connection retries on startup

    # MFA Cleanup Settings
    UNCONFIRMED_TOTP_RETENTION_HOURS = 24 # Unconfirmed TOTP devices older than this will be deleted
    USED_BACKUP_CODE_RETENTION_DAYS = 90 # Used backup codes older than this will be deleted

    # django-celery-beat scheduler
    CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
    ```

---

## **Step 3: Create Celery App Instance (`core/core/celery.py`)**

You need to create a `celery.py` file that defines your Celery application instance. This file will be used by Celery to discover tasks.

1.  **Create `celery.py`**:
    Create a new file `core/core/celery.py` with the following content:
    ```python
    # core/core/celery.py

    import os
    from celery import Celery

    # Set the default Django settings module for the 'celery' program.
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

    app = Celery('core')

    # Using a string here means the worker doesn't have to serialize
    # the configuration object to child processes.
    # - namespace='CELERY' means all celery-related configuration keys
    #   should have a `CELERY_` prefix in your settings.py.
    app.config_from_object('django.conf:settings', namespace='CELERY')

    # Auto-discover tasks in all installed apps.
    app.autodiscover_tasks()

    @app.task(bind=True, ignore_result=True)
    def debug_task(self):
        print(f'Request: {self.request!r}')
    ```

---

## **Step 4: Integrate Celery App with Django (`core/core/__init__.py`)**

To ensure the Celery app is loaded when Django starts, you need to import it in your project's `__init__.py` file.

1.  **Update `__init__.py`**:
    Open `core/core/__init__.py` and add the following lines:
    ```python
    # core/core/__init__.py

    # This will make sure the app is always imported when Django starts
    # so that shared_task will use this app.
    from .celery import app as celery_app

    __all__ = ('celery_app',)
    ```

---

## **Step 5: Define Celery Tasks in Your Apps**

Now you can start defining tasks in your Django applications. It's conventional to create a `tasks.py` file within each app that needs to define Celery tasks.

1.  **Create `tasks.py`**:
    For example, in `core/modules/accounts/`, create a new file `tasks.py`:
    ```python
    # core/modules/accounts/tasks.py

    from celery import shared_task
    import time
    from django.conf import settings
    from django.utils import timezone
    from datetime import timedelta
    from modules.auth.accounts.models import User, AuthAuditLog, UserTOTPDevice, BackupCode

    @shared_task
    def send_welcome_email(user_email):
        """
        A sample task to simulate sending a welcome email.
        """
        print(f"Simulating sending welcome email to {user_email}...")
        time.sleep(5) # Simulate a long-running operation
        print(f"Welcome email sent to {user_email}!")
        return f"Email sent to {user_email}"

    @shared_task
    def process_user_data(user_id):
        """
        A sample task to process user data in the background.
        """
        print(f"Processing data for user ID: {user_id}...")
        time.sleep(10) # Simulate a more intensive operation
        print(f"Finished processing data for user ID: {user_id}.")
        return f"Data processed for user ID: {user_id}"

    @shared_task
    def clean_mfa_data():
        """
        Cleans up old unconfirmed TOTP devices and used backup codes.
        """
        unconfirmed_totp_retention_hours = getattr(settings, 'UNCONFIRMED_TOTP_RETENTION_HOURS', 24)
        totp_cutoff_time = timezone.now() - timedelta(hours=unconfirmed_totp_retention_hours)
        deleted_totp_count, _ = UserTOTPDevice.objects.filter(
            confirmed=False,
            created_at__lt=totp_cutoff_time
        ).delete()
        print(f"Cleaned up {deleted_totp_count} unconfirmed TOTP devices.")

        used_backup_code_retention_days = getattr(settings, 'USED_BACKUP_CODE_RETENTION_DAYS', 90)
        backup_code_cutoff_time = timezone.now() - timedelta(days=used_backup_code_retention_days)
        deleted_backup_count, _ = BackupCode.objects.filter(
            used=True,
            used_at__lt=backup_code_cutoff_time
        ).delete()
        print(f"Cleaned up {deleted_backup_count} used backup codes.")

        return f"MFA data cleanup complete. Deleted {deleted_totp_count} TOTP devices and {deleted_backup_count} backup codes."

    @shared_task
    def log_auth_event_task(user_id, event_type, ip_address, user_agent, device_info, success, details):
        """
        Celery task to log authentication events in the background.
        """
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            print(f"User with ID {user_id} not found for auth event logging.")
            return

        AuthAuditLog.objects.create(
            user=user,
            event_type=event_type,
            ip_address=ip_address,
            user_agent=user_agent,
            device_info=device_info,
            success=success,
            details=details or {}
        )
        print(f"Auth event logged for user {user.email}: {event_type} (Success: {success})")
    ```
    You can do the same for `core/modules/ESS/` if it needs background tasks.

---

## **Step 6: Run Database Migrations**

`django-celery-beat` requires its own database tables to store periodic task schedules.

1.  **Apply Migrations**:
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```
    This will create the necessary tables for `django_celery_beat`.

---

## **Step 7: Run Celery Worker and Beat Scheduler**

You'll need to run two separate processes: the Celery worker (to execute tasks) and the Celery Beat scheduler (to manage periodic tasks).

1.  **Start Redis (if not already running)**:
    If you're using Docker for Redis:
    ```bash
    docker run -p 6379:6379 --name my-redis-container -d redis
    ```

2.  **Start Celery Worker**:
    Open a new terminal window, navigate to your project's `backend` directory (`/home/mohammed-azaan-peshmam/Desktop/Coding Club/Projects/ESS/backend/`), and run:
    ```bash
    celery -A core.celery worker -l info
    ```
    *   `-A core`: Specifies your Django project's Celery app (defined in `core/core/celery.py`).
    *   `worker`: Starts the worker process.
    *   `-l info`: Sets the logging level to info, showing more details.

3.  **Start Celery Beat Scheduler**:
    Open *another* new terminal window, navigate to your project's `backend` directory, and run:
    ```bash
    celery -A core beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
    ```
    *   `beat`: Starts the beat scheduler.
    *   `--scheduler django_celery_beat.schedulers:DatabaseScheduler`: Tells Beat to use the database scheduler provided by `django-celery-beat`.

    **Note**: For production, you would typically use a process manager (like Supervisor, Systemd, or Docker Compose) to keep these processes running reliably.

---

## **Step 7.1: Asynchronous Authentication Logging**

To prevent authentication logging from blocking the request-response cycle, the creation of `AuthAuditLog` entries has been moved to a background Celery task.

*   **Modification**: The `log_auth_event` utility function in `core/modules/accounts/utils.py` now calls the `log_auth_event_task` asynchronously using `.delay()` instead of directly creating the `AuthAuditLog` object.

---

## **Step 7.2: Daily Database Cleanup (MFA Data)**

To maintain database hygiene and remove unnecessary data, a daily cleanup task has been implemented for MFA-related records.

*   **Task**: `modules.auth.accounts.tasks.clean_mfa_data`
*   **Purpose**: This task deletes:
    *   Unconfirmed `UserTOTPDevice` entries older than `UNCONFIRMED_TOTP_RETENTION_HOURS` (default: 24 hours).
    *   Used `BackupCode` entries older than `USED_BACKUP_CODE_RETENTION_DAYS` (default: 90 days).

*   **Scheduling**: To schedule this task, follow these steps:
    1.  **Access Django Admin**: Go to `http://localhost:8000/admin/`.
    2.  **Navigate to Periodic Tasks**: Under the "DJANGO CELERY BEAT" section, click on "Periodic tasks".
    3.  **Add a New Periodic Task**: Click "Add periodic task".
    4.  **Configure**: 
        *   **Name**: `Clean MFA Data Daily`
        *   **Task**: Select `modules.auth.accounts.tasks.clean_mfa_data`.
        *   **Schedule**: Choose a Crontab Schedule (e.g., daily at 03:00 AM UTC). Create a new one if needed.
        *   **Enabled**: Check this box.
    5.  **Save** the periodic task.

---

## **Step 8: Test and Verify**

Now that everything is set up, let's test it.

1.  **Manually Trigger a Task (from Django Shell)**:
    Open a new terminal and start the Django shell:
    ```bash
    python manage.py shell
    ```
    Inside the shell, import and call your task:
    ```python
    from core.modules.auth.accounts.tasks import send_welcome_email
    send_welcome_email.delay("test@example.com") # .delay() is a shortcut for .apply_async()
    # You should see output in your Celery worker terminal
    ```
    You can also use `send_welcome_email.apply_async(args=["test@example.com"], countdown=10)` to schedule it to run in 10 seconds.

2.  **Schedule a Periodic Task (via Django Admin)**:
    *   Ensure your Django development server is running: `python manage.py runserver`
    *   Access the Django admin interface (usually `http://127.0.0.1:8000/admin/`).
    *   Log in with a superuser account. If you don't have one, create it: `python manage.py createsuperuser`
    *   In the admin, you'll see a section for `DJANGO CELERY BEAT`.
    *   Go to `Periodic tasks` and click "Add periodic task".
    *   **Name**: `Send Daily Report` (or similar)
    *   **Task**: Select `accounts.tasks.send_welcome_email` (or your desired task).
    *   **Arguments (JSON)**: `["admin@yourdomain.com"]` (if your task takes arguments).
    *   **Interval**: Choose "Add new interval" and set it (e.g., every 1 day).
    *   **Enabled**: Check this box.
    *   Save the periodic task.
    *   The Celery Beat scheduler will pick up this task and schedule it to run at the specified interval. You should see it being executed in your Celery worker terminal.
