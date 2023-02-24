# Planning Poker

Simple FastAPI websockets server to vote on tickets like scrum poker

![Screenshot](screenshot.png?raw=true "Screenshot")

# Setup
Tested with Python 3.10
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

# Start
Simple uvicorn server on port 8888

`./start.sh`

# Dev
Auto reloading server for development work

`./dev.sh`

# Test
Selenium tests that require the server to be running

`./test.sh`
