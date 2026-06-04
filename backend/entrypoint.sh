#!/bin/sh
set -e

if [ "${HACKSCORE_RUN_MIGRATIONS:-true}" = "true" ]; then
  alembic upgrade head
fi

if [ "${HACKSCORE_AUTO_SEED:-false}" = "true" ]; then
  python -m app.seed_cli
fi

exec "$@"
