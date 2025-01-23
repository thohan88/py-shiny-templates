# FastAPI Users Template

A template integrating FastAPI, FastAPI-Users, and Shiny for Python to provide robust user authentication and registration functionality. The template offers some minimal email/password and Google OAuth2 login options.

## Disclaimer
This template is provided as-is for illustrative purposes. It has not been thoroughly tested for production use. Use at your own risk. The authors assume no responsibility for any issues that may arise from its use.

## Features

- **User Authentication & Registration**
  - Email/password authentication
  - Google OAuth2 integration
  - JWT-based authentication with cookies
  - Protected routes and middleware
  - Modular login/registration forms

- **Backend Architecture**
  - FastAPI REST endpoints
  - SQLite database (configurable)
  - Async database operations
  - Secure cookie handling
  - Configurable authentication strategies

## Project Structure

```
fastapi_users/
├── README.md
├── app.py             # Main application entry point
├── auth.py            # Authentication middleware
├── config.py          # Configuration settings
├── fastapi/           # Backend components
│   ├── app.py
│   ├── auth/          # Authentication logic
│   ├── core/          # Core functionality
│   └── user/          # User management
└── shiny/             # Frontend components
    ├── app.py
    ├── client.py
    └── modules/       # Reusable UI components
```

## Quick Start

1. Create `.env` file from `.env.example`:
```bash
DB_URL="sqlite+aiosqlite:///demo.db"
JWT_SECRET="your-secure-secret-key"
# Optional Google OAuth2 settings
GOOGLE_CLIENT_ID=""
GOOGLE_CLIENT_SECRET=""
GOOGLE_REDIRECT_URI=""
```

2. Run the application:
```bash
shiny run apps.fastapi_users.app:app
```

3. Access the application at `http://localhost:8000/fastapi_users/`

## Google OAuth2 Setup

To enable Google authentication:

1. Create a project in the [Google Cloud Console](https://console.cloud.google.com/)
2. Enable the People API
3. Configure OAuth2 credentials:
   - Set authorized redirect URI to `/api/auth/google/callback`
   - Example local development URI: `http://localhost:8000/api/auth/google/callback`
4. Add credentials to your `.env` file

## Deployment Options
[Previous sections remain the same...]

## Understanding URL Resolution Challenges
While deploying standard Shiny applications with single endpoints is generally straightforward, this template presents some challenges due to its multi-endpoint architecture (`/app`, `/api`, and `/`). These challenges become particularly significant in two scenarios:

1. Deployment behind a reverse proxy (such as shinyapps.io)
2. Hosting as a sub-application within a larger application context

Common URL resolution approaches have limitations in this context:

- `uvicorn` and `fastapi` both support `root_url` configuration, but this option cannot be specified in certain hosting environments (e.g., shinyapps.io's entrypoint configuration)
- FastAPI's `root_path` decorator (`FastAPI(root_path=...)`) does not propagate to the underlying ASGI scope, leaving `scope[root_path]` unchanged

To address these limitations, this template implements a custom URL resolution strategy using two configuration parameters:

```python
path_proxy: Optional[str] = "/proxy_path"        # For reverse proxy scenarios
path_nested_mount: Optional[str] = "app_name"    # For sub-application mounting
```

### Standard Deployment

For basic deployment with the app served at root (`shiny run app`):

```python
# config.py
path_proxy: Optional[str] = ""
path_nested_mount: Optional[str] = ""
```

### Nested App Deployment

For serving the app as a nested Starlette app (`shiny run apps.fastapi_users.app`):

```python
# config.py
path_proxy: Optional[str] = ""
path_nested_mount: Optional[str] = "fastapi_users"
```

### Reverse Proxy Deployment

For deployment behind a reverse proxy (e.g., shinyapps.io) (`shiny run apps.fastapi_users.app`):

```python
# config.py
path_proxy: Optional[str] = "/your-proxy-path"
path_nested_mount: Optional[str] = "fastapi_users"  # If nested
```

### Deployment to shinyapps.io
1. Discard deletion of demo.db in repo if you have ran the app locally first. *(Running locally automatically creates/destroys the database on startup/shutdown. Shinyapps.io does not support this, so we need to make sure an empty database is present on startup.)*
2. Add your app name (e.g. `/{app_name}`) to `proxy_path` in apps/fastapi_users/config.py
3. Update `GOOGLE_REDIRECT_URI` in .env to `https://{user}.shinyapps.io/{app_name}/fastapi_users/api/auth/google/callback`

```bash
rsconnect deploy shiny . \
    --entrypoint "app:app" \
    --override-python-version 3.12.1
```

## Development Setup

### Debugging URL Resolution

For testing URL resolution with Traefik:

1. Create `traefik.toml`:
```toml
[entryPoints]
  [entryPoints.http]
    address = ":9998"

[providers]
  [providers.file]
    filename = "routes.toml"
  
[log]
  level = "DEBUG"
```

2. Create `routes.toml`:
```toml
[http]
  [http.middlewares]
    [http.middlewares.api-stripprefix.stripPrefix]
      prefixes = ["/your-proxy-path"]

  [http.routers]
    [http.routers.app-http]
      entryPoints = ["http"]
      service = "app"
      rule = "PathPrefix(`/your-proxy-path`)"
      middlewares = ["api-stripprefix"]

  [http.services]
    [http.services.app]
      [http.services.app.loadBalancer]
        [[http.services.app.loadBalancer.servers]]
          url = "http://localhost:8000"
```

3. Start Traefik:
```bash
traefik --configFile=traefik.toml
```

4. Access your app at `http://localhost:9998/your-proxy-path`

