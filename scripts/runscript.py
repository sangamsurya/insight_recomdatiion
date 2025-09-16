import subprocess
import sys

# You could also use a single script that imports and runs functions from both.
subprocess.run([sys.executable, "hunter_fetch.py"])
subprocess.run([sys.executable, "groq_leads.py"])