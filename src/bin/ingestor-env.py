import json
import os
import sys
import subprocess

env = dict(os.environ)
envArg = sys.argv.index('-env')
envFile = sys.argv[envArg + 1]
with open(envFile) as jsonFile:
	env = json.load(jsonFile)

p = subprocess.Popen(
    ' '.join(sys.argv[envArg + 2:]),
    shell=True,
    env=env
)

p.wait()
sys.exit(p.returncode)
