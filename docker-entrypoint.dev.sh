#!/bin/bash

/usr/share/python3/venv/bin/python -m market.db upgrade head

/usr/share/python3/venv/bin/python -m market --app-host=0.0.0.0
