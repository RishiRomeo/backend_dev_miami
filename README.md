Run instrusctions: 
Prerequisites (for running on UV)
- git installed on machine
- uv installation (instructions -> https://docs.astral.sh/uv/getting-started/installation/)
- python 3.11

1. Clone repository into local directory
2. cd into local directory
3. run command $uv run main.py

You can also run this using python3 main.py
If running this way, please make sure you have the following libraries (included in pyproject.toml) 

dependencies = [
    "aiohttp>=3.12.14",
    "requests>=2.32.4",
]
