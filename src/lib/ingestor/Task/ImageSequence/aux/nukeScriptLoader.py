import json
import sys

# compatibility with python 2/3
try:
    basestring
except NameError:
    basestring = str

# parsing options
options = {}
optionsArgIndex = sys.argv.index('--ingestor-options')
optionsFile = sys.argv[optionsArgIndex + 1]
with open(optionsFile) as jsonFile:
    options = json.load(jsonFile)

# getting the options converted from unicode to str
# (nuke does not have unicode support)
for optionName, optionValue in options.items():
    if isinstance(optionValue, basestring):
        options[optionName] = str(optionValue)

# making sure script is defined in the options
if 'script' not in options:
    raise Exception('Could not find "script" in the options!')

# executing script
exec(
    open(options['script']).read(),
    globals()
)
