# Contributing to the ESS Backend

Thank you for your interest in contributing to the project! To ensure a smooth and collaborative development process, please follow these guidelines.

## Code Style

*   **PEP 8:** All Python code should adhere to the [PEP 8 style guide](https://www.python.org/dev/peps/pep-0008/).
*   **Linting:** Before committing, please run a linter to check for style issues. We recommend using `ruff`.
    ```bash
    # Install ruff (if you haven't already)
    pip install ruff

    # Run the linter
    ruff check .
    ```
*   **Imports:** Imports should be grouped in the following order: standard library, third-party libraries, and then local application imports.

## Commit Messages

We follow the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification. This helps in creating an explicit commit history and makes it easier to automate changelogs.

The commit message format is:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

*   **Types:** `feat` (new feature), `fix` (bug fix), `docs` (documentation), `style` (formatting), `refactor`, `test`, `chore` (build tasks, package manager configs, etc.).

*   **Examples:**
    *   `feat: Add user profile update endpoint`
    *   `fix: Correct validation error in LoginSerializer`
    *   `docs: Update README with setup instructions`

## Branching Strategy

The project uses a Gitflow-like branching model with three long-lived branches:

- `main`: Contains production-ready code. Direct commits to `main` are forbidden.
- `develop`: The primary development branch. All feature branches are merged into `develop`.
- `production`: Represents the code currently deployed in the production environment.

**Workflow:**

1.  Always create a new branch from the `develop` branch for any new feature or bug fix.
2.  Name your branch descriptively using the `type/description` convention. For example:
    *   `feature/user-password-reset`
    *   `fix/admin-login-styling`
3.  Once your work is complete and tested, open a pull request to merge your branch back into `develop`.

## Database Migrations

*   If you make any changes to the models in `models.py`, you **must** create a new database migration.
    ```bash
    python core/manage.py makemigrations
    ```
*   Run the migrations to apply the changes to your local database.
    ```bash
    python core/manage.py migrate
    ```
*   Always commit the generated migration files with your model changes.

## API Documentation

For any new set of API endpoints you create, you must add a corresponding `.md` documentation file in the same directory as the `urls.py` file that defines them.

The documentation for each endpoint should be detailed and follow a consistent structure. Please use the `api_documentation_template.md` in the root directory as a reference for the required format and sections.