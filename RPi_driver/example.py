#!/usr/bin/python3

import time, mcp9808


sensor = mcp9808.MCP9808()

while True:
    print(sensor.readTemp())
    time.sleep(1)
