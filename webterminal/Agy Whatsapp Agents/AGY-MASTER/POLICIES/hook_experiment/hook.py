import sys
import json

with open("/home/azureuser/AGY-MASTER/POLICIES/hook_experiment/hook_invoked.log", "a") as f:
    f.write("HOOK INVOKED\n")

# Return allow
print(json.dumps({"decision": "allow"}))
