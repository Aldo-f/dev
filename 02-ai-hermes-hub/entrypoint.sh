#!/bin/sh
exec uvicorn hub:app --host 0.0.0.0 --port 8789