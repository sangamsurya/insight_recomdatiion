import subprocess
import sys


subprocess.run([sys.executable, "hunter_fetch.py"])
subprocess.run([sys.executable, "groq_leads.py"])