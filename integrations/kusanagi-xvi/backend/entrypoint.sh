#!/bin/sh
# Same-container API / SQLite probe worker / observer.
set -eu
exec python -m backend.supervisor
