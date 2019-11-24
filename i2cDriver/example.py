import mcp9808
import time


sensor = mcp9808.MCP9808(0x18)

while True:
    print(sensor.readTemp())
    time.sleep(0.5)
