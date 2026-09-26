import sys
import json

with open("/home/azureuser/AGY-MASTER/POLICIES/hook_experiment/live_hook.log", "a") as f:
    f.write("LIVE HOOK INVOKED\n")

print(json.dumps({"decision": "allow"}))
