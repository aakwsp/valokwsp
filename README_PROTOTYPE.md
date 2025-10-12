valokwsp Prototype
====================

This is a small prototype FastAPI app that serves fake Valorant data for demonstration purposes. Use this to show Riot what your app will request and how you will present data.

Run locally (PowerShell):

```powershell
python -m pip install -r requirements.txt
uvicorn prototype_app:APP --reload
```

Endpoints:
- GET /players
- GET /players/{ign}/{tag}
- GET /players/{ign}/{tag}/matches

Example GET:
```powershell
curl http://127.0.0.1:8000/players
curl http://127.0.0.1:8000/players/Shadow/001
curl http://127.0.0.1:8000/players/Shadow/001/matches
```

Note: This is a mock service and does not call Riot's API. It is intended solely to demonstrate the product to Riot for requesting API access.
