# Notes App (Django)

A simple note-taking web application built with Django. Users can create private notes, share them publicly, and interact through comments and likes.

## Features

- Custom user model with bio field
- User authentication (register, login, logout)
- Create, update, delete notes
- Public notes feed
- Comment system on public notes
- Like/unlike functionality
- Rate limiting on key endpoints
- PostgreSQL database
- Dockerized setup

## Tech Stack

- Django
- PostgreSQL
- Docker & Docker Compose

## Project Structure

core/              # Django project settings
accounts/          # Authentication & user logic
notes/             # Notes, comments, likes
templates/         # HTML templates

## Environment Variables

This project uses environment variables for configuration.

Instead of defining them manually, copy the example file:

cp .env.example .env

Then edit the ".env" file and set your own values.

### Run with Docker

Make sure Docker and Docker Compose are installed.

### Build and run

docker-compose up -d --build

### Apply migrations

docker-compose exec web python manage.py migrate

### Create superuser

docker-compose exec web python manage.py createsuperuser

## Access the App

- Application: http://localhost:8000/accounts/
- Admin panel: http://localhost:8000/admin

## Rate Limiting

The project uses "django_smart_ratelimit" to protect endpoints such as:

- Authentication (login, register)
- Notes (create, update, delete)
- Interactions (likes, comments)

A token bucket algorithm is used with different limits depending on the endpoint.

## Security Notes

- Set "DEBUG=0" in production
- Use a strong "SECRET_KEY"
- Configure "ALLOWED_HOSTS" properly
- Do not expose database credentials
- Use HTTPS in production (recommended)

### License

This project is intended for educational purposes.
