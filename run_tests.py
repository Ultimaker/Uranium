import pytest
from pathlib import Path

# Small helper script to run the coverage of main code & all plugins

path = Path("plugins")
args = []
for p in path.glob('**/*'):
	if p.is_dir():
		if p.name in ["__pycache__", "tests"]:
			continue
		args.append(str(p))

args.append(".")
print(pytest.main(args))

