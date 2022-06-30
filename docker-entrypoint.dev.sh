#!/bin/sh

/usr/share/python3/venv/bin/python -m market.db upgrade head

export IS_DEBUG=TRUE
/usr/share/python3/venv/bin/python -m market --app-host=0.0.0.0
