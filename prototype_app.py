"""Simple FastAPI prototype to serve fake Valorant data for Riot review.

Endpoints:
- GET /players -> list players
- GET /players/{ign}/{tag} -> player profile
- GET /players/{ign}/{tag}/matches -> recent matches

Run: uvicorn prototype_app:app --reload
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
from pathlib import Path

APP = FastAPI(title="ValoStats Prototype API")

APP.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = Path(__file__).parent / "fake_valo_db.json"

def load_db():
    with open(DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

@APP.get("/players")
def list_players():
    db = load_db()
    return db.get("players", [])

@APP.get("/players/{ign}/{tag}")
def get_player(ign: str, tag: str):
    db = load_db()
    for p in db.get("players", []):
        if p["ign"].lower() == ign.lower() and p["tag"] == tag:
            return p
    raise HTTPException(status_code=404, detail="Player not found")

@APP.get("/players/{ign}/{tag}/matches")
def get_matches(ign: str, tag: str):
    db = load_db()
    for p in db.get("players", []):
        if p["ign"].lower() == ign.lower() and p["tag"] == tag:
            return db.get("matches", {}).get(p["id"], [])
    raise HTTPException(status_code=404, detail="Player not found")
