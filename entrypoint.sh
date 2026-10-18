#!/bin/sh
set -e

# WARNING: Running migrations from container entrypoint
# is not safe for multi-replica deployments.

python manage.py migrate
python manage.py collectstatic --noinput

exec "$@"