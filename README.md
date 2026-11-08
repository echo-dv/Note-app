# Notes App

A Dockerized note-taking web application built with Django and
PostgreSQL. It supports private note management, public note sharing,
user interactions, and basic abuse protection through rate limiting.

## Features

-   Custom user model with profile information.
-   User registration, authentication, and session management.
-   Create, update, delete, and view personal notes.
-   Public feed for shared notes.
-   Public note details with comments and likes.
-   User profiles with activity statistics.
-   Endpoint-level rate limiting using a token bucket algorithm.
-   PostgreSQL as the primary database.
-   Nginx as a reverse proxy, TLS termination layer, and static-file
    server.
-   HTTP-to-HTTPS redirection.
-   HTTP Basic Authentication for the Django admin panel.
-   Application health checks.
-   Dockerized deployment using Docker Compose.

## Tech Stack

  Component            Technology
  -------------------- ------------------------
  Backend              Python
  Web framework        Django
  Database             PostgreSQL
  Database driver      Psycopg 3
  Application server   Gunicorn
  Reverse proxy        Nginx
  Containerization     Docker
  Orchestration        Docker Compose
  Rate limiting        django-smart-ratelimit

## Architecture

The application consists of three services:

  -----------------------------------------------------------------------
  Service                             Responsibility
  ----------------------------------- -----------------------------------
  `web`                               Django application served through
                                      Gunicorn.

  `db`                                PostgreSQL database.

  `nginx`                             Reverse proxy, TLS termination,
                                      static-file server, and HTTP Basic
                                      Authentication for the admin panel.
  -----------------------------------------------------------------------

### Request Flow

``` text
Internet
   |
   v
+------------------+
| Nginx            |
| :80 / :443       |
+------------------+
   |
   v
+------------------+
| Gunicorn         |
| :8000            |
+------------------+
   |
   v
+------------------+
| Django           |
+------------------+
   |
   v
+------------------+
| PostgreSQL       |
| :5432            |
+------------------+
```

Nginx handles incoming HTTP and HTTPS traffic and forwards application
requests to Gunicorn.

The Django application communicates with PostgreSQL through the internal
Docker network.

The application port is published only on the host's loopback interface.

## Project Structure

``` text
.
├── accounts/
│   ├── admin.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── common/
│   ├── health/
│   │   ├── urls.py
│   │   └── views.py
│   └── ratelimit_key.py
│
├── core/
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── landing/
│   ├── admin.py
│   ├── models.py
│   ├── tests.py
│   └── views.py
│
├── nginx/
│   ├── certs/
│   ├── nginx.conf
│   └── nginx.conf.template
│
├── notes/
│   ├── admin.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── templates/
├── static/
│
├── .dockerignore
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── entrypoint.sh
├── manage.py
└── requirements.txt
```

## Requirements

The following software and resources are required:

-   Docker Engine.
-   Docker Compose v2.
-   A domain name pointing to the deployment server.
-   A TLS certificate and private key for the domain.
-   An `htpasswd` credentials file for protecting the admin panel. See
    [Admin Panel Protection](#admin-panel-protection).
-   The `htpasswd` utility:
    -   `apache2-utils` on Debian/Ubuntu.
    -   `httpd-tools` on RHEL/Fedora.
    -   `httpd` on macOS.

Before starting the services, make sure these files exist on the host:

``` text
nginx/htpasswd
nginx/certs/<TLS_CERT_NAME>
nginx/certs/<TLS_CERT_KEY>
```

## Configuration

The application uses environment variables for configuration.

Create the environment file:

``` bash
cp .env.example .env
```

> **Note:** `DEBUG` is intentionally empty in `.env.example`. An empty
> value is treated as `0` (debug mode disabled). Set `DEBUG=1` only for
> local development.

### Environment Variables

#### Django

  -----------------------------------------------------------------------
  Variable                            Description
  ----------------------------------- -----------------------------------
  `DEBUG`                             Enables or disables Django debug
                                      mode (`0` or `1`).

  `SECRET_KEY`                        Django secret key.

  `ALLOWED_HOSTS`                     Comma-separated list of allowed
                                      hostnames.

  `CSRF_TRUSTED_ORIGINS`              Comma-separated list of trusted
                                      origins, including the scheme.
  -----------------------------------------------------------------------

#### Nginx

  Variable              Description
  --------------------- -------------------------------------------------
  `NGINX_SERVER_NAME`   Domain name handled by Nginx.
  `TLS_CERT_NAME`       TLS certificate filename inside `nginx/certs/`.
  `TLS_CERT_KEY`        TLS private-key filename inside `nginx/certs/`.

#### PostgreSQL

  Variable              Description
  --------------------- --------------------
  `POSTGRES_DB`         Database name.
  `POSTGRES_USER`       Database username.
  `POSTGRES_PASSWORD`   Database password.
  `POSTGRES_HOST`       Database hostname.
  `POSTGRES_PORT`       Database port.

### Example Configuration

``` env
DEBUG=0
SECRET_KEY=your-secret-key

ALLOWED_HOSTS=example.com
CSRF_TRUSTED_ORIGINS=https://example.com

NGINX_SERVER_NAME=example.com
TLS_CERT_NAME=fullchain.pem
TLS_CERT_KEY=privkey.pem

POSTGRES_DB=notes_db
POSTGRES_USER=notes_user
POSTGRES_PASSWORD=your-database-password
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

Replace all example values with the actual deployment domain and
credentials.

### TLS Configuration

Place the TLS certificate and private key inside:

``` text
nginx/certs/
```

Configure their filenames through:

-   `TLS_CERT_NAME`
-   `TLS_CERT_KEY`

The certificate directory is mounted read-only inside the Nginx
container.

Certificate provisioning and renewal are not handled by this project.

### Admin Panel Protection

The Django admin panel is protected by Nginx HTTP Basic Authentication.

The credentials file must be available at:

``` text
nginx/htpasswd
```

The file is mounted read-only into the Nginx container.

Requests to `/admin/` must pass Nginx authentication before reaching
Django. Django's own authentication and permission checks remain
enabled.

#### Creating the `htpasswd` File

Install the `htpasswd` utility:

``` bash
# Debian / Ubuntu
sudo apt install apache2-utils

# RHEL / Fedora
sudo dnf install httpd-tools

# macOS
brew install httpd
```

Create the file with the first user. The `-c` flag creates a new file
and prompts for a password:

``` bash
htpasswd -c nginx/htpasswd admin
```

Add more users later. Omit `-c` so the existing file is not overwritten:

``` bash
htpasswd nginx/htpasswd alice
```

The file is listed in `.gitignore` and will not be committed to the
repository.

## Deployment

### Build and Start Services

``` bash
docker compose up -d --build
```

Docker Compose starts PostgreSQL, Django, and Nginx.

The Django service waits for PostgreSQL to become healthy before
starting.

### Application Initialization

The application container automatically performs the following
operations through `entrypoint.sh`:

1.  Applies database migrations.
2.  Collects static files.
3.  Starts the configured application process.

No separate migration or static-file collection command is required
during the normal single-instance startup process.

### Access

After successful deployment, the application is available at:

  Resource       URL
  -------------- -------------------------------------
  Application    `https://example.com/`
  Accounts       `https://example.com/accounts/`
  Public notes   `https://example.com/notes/public/`
  Admin panel    `https://example.com/admin/`

The application is also published on the host loopback interface at:

``` text
http://127.0.0.1:8000
```

## Health Checks

Two health endpoints are provided.

  -----------------------------------------------------------------------
  Endpoint                            Purpose
  ----------------------------------- -----------------------------------
  `/health/liveness/`                 Checks whether the Django
                                      application is responding.

  `/health/readiness/`                Checks whether the application can
                                      communicate with PostgreSQL.
  -----------------------------------------------------------------------

### Liveness

``` http
GET /health/liveness/
```

Returns HTTP `200` when the application process responds.

### Readiness

``` http
GET /health/readiness/
```

Executes a database query to verify PostgreSQL connectivity.

-   Returns HTTP `200` when the database is accessible.
-   Returns HTTP `503` when a database connection error occurs.

Docker Compose uses the readiness endpoint as the web service health
check. Nginx waits for the web service to become healthy before
starting.

## Rate Limiting

The application uses `django-smart-ratelimit` with the token bucket
algorithm.

Rate limiting is applied to authentication, note operations, comments,
likes, and other application endpoints.

The rate-limit key is generated centrally in:

``` text
common/ratelimit_key.py
```

-   Authenticated requests are identified using the user ID.
-   Anonymous requests are identified using the client's IP address and
    User-Agent.

Rate limits and bucket configurations are defined alongside the
corresponding views.

Nginx also applies request and connection limits at the reverse-proxy
layer.

## Static Files

Django's static files are collected into:

``` text
/app/staticfiles/
```

A named Docker volume is used to persist the collected static files:

``` text
staticfiles
```

Nginx mounts this volume in read-only mode and serves files directly
through the `/static/` location.

Static responses include a 14-day cache policy with the `immutable`
directive.

## Persistent Data

Docker Compose defines two named volumes:

  Volume            Purpose
  ----------------- ----------------------------------
  `postgres_data`   PostgreSQL database persistence.
  `staticfiles`     Collected Django static files.

The PostgreSQL data volume survives container recreation.

Removing containers does not automatically remove named volumes.
Removing volumes, however, can permanently destroy the associated data.

## Security Considerations

-   Django debug mode is disabled by default.
-   The Django secret key and database credentials are provided through
    environment variables.
-   The PostgreSQL service does not publish its port to the host.
-   The Django application port is bound to `127.0.0.1`.
-   TLS is terminated at Nginx.
-   HTTP traffic is redirected to HTTPS.
-   The Nginx admin location requires HTTP Basic Authentication.
-   TLS certificates and the Nginx credentials file are mounted
    read-only.
-   Nginx applies request and connection limits.
-   Django applies application-level rate limiting.
-   Database readiness is checked before the application is considered
    healthy.

## Warnings and Deployment Limitations

### 1. Nginx Host Networking

Nginx uses `network_mode: host` intentionally.

This allows Nginx to obtain the real client IP address through
`$remote_addr` and forward it using the `X-Real-IP` header.

With this configuration, Nginx accesses the host network directly
instead of relying on Docker bridge networking and its
address-translation behavior.

### 2. Single-Instance Deployment

This Docker Compose configuration is designed for a single application
instance. It is not a multi-replica deployment configuration.

In particular, `entrypoint.sh` runs database migrations whenever the
application container starts.

Running migrations independently from multiple application replicas can
introduce race conditions and deployment problems.

For multi-replica deployments, migrations should be executed as a
separate, coordinated deployment step rather than by every application
instance.

### 3. Anonymous Rate-Limit Identification

The anonymous rate-limit key includes both the client IP address and
User-Agent.

This is intended to reduce false rate-limit collisions between different
users sharing the same public IP address, such as users behind NAT or
CGNAT.

Using only the IP address could cause multiple independent users behind
the same NAT gateway to consume the same rate-limit bucket.

### 4. Proxy Chain Limitation

The current client IP identification strategy is designed for the
specified deployment topology and is not safe for arbitrary proxy
chains.

The application trusts `X-Real-IP` as provided by Nginx.

If additional reverse proxies or load balancers are introduced, the
trusted-proxy configuration and client IP extraction strategy must be
reviewed.

Blindly trusting forwarded IP headers in a proxy chain can allow clients
to spoof their IP addresses and bypass IP-based rate limiting.

The current configuration must not be considered secure for arbitrary
multi-proxy deployments without additional proxy trust and header
validation.

