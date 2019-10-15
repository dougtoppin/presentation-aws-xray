#!/bin/sh

# run the x-ray agent in the background and in local mode ( -o  ) to prevent
# the getting container instance metadata error
/usr/bin/xray -t 0.0.0.0:2000 -b 0.0.0.0:2000 -o --config /cfg.yaml &

# run the demo app in the foreground
exec /app.py
