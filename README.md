# MeetSpotX — Intelligent Meeting Point Finder for Every Group 🗺️

[![Releases](https://img.shields.io/badge/Releases-Download-blue.svg)](https://github.com/pholaa99/MeetSpotX/releases)

Download the release asset from https://github.com/pholaa99/MeetSpotX/releases and run the provided executable.

<div align="center">
  <img src="docs/logo.png" alt="MeetSpotX Logo" width="220"/>
</div>

Badges
- [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
- [![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
- [![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
- [![Build Status](https://github.com/pholaa99/MeetSpotX/actions/workflows/ci.yml/badge.svg)](https://github.com/pholaa99/MeetSpotX/actions)

Table of contents
- Features
- Screenshots
- Quick demo
- Installation
- Usage
  - Web UI
  - API
- Configuration
- Architecture
- Data model & algorithms
- Tests & CI
- Contributing
- License
- Releases

Features
- Compute optimal meetups. Balance travel time, venue ratings, and user preferences.
- Support for multi-origin groups. Accept addresses, coordinates, or POIs for each user.
- Rank venues by combined score. Use distance, ETA, and venue quality in one metric.
- Filter by categories. Restaurants, cafes, parks, coworking spaces, gyms.
- Time-aware routing. Use traffic estimates and public transit windows.
- Heuristic and ML modes. Use rule-based scoring or a trained model for preference weighting.
- FastAPI backend. Lightweight, async, and scalable.
- Static web UI. Responsive map, multi-select, and result export.

Screenshots
<div align="center">
  <img src="docs/show1.png" alt="Main Interface" width="800"/>
  <p>Main interface: enter participant locations and preferences.</p>
  <img src="docs/show2.png" alt="Multi-Venue Selection" width="800"/>
  <p>Pick multiple candidate venues to refine recommendations.</p>
  <img src="docs/show3.png" alt="Recommendation Results" width="800"/>
  <p>Sorted list with scores, travel times, and map markers.</p>
</div>

Quick demo
- Start backend and open the web UI.
- Add three participants with different start points.
- Set a desired time and transport mode.
- MeetSpotX returns a ranked list of meeting points with travel estimates and route links.

Installation

Prerequisites
- Python 3.11 or newer
- system packages: libgeos, libproj (for some spatial ops)
- pip

Install from source
1. Clone the repo
   git clone https://github.com/pholaa99/MeetSpotX.git
2. Create virtual env
   python -m venv .venv
   source .venv/bin/activate
3. Install
   pip install -r requirements.txt
4. Run the service
   uvicorn meetspotx.main:app --reload

Install a release (recommended)
- Download the release asset from https://github.com/pholaa99/MeetSpotX/releases and run the provided executable or wheel. This page lists packaged binaries and installable wheels for stable versions.

Usage

Web UI
- Open http://localhost:8000 in a browser.
- Add participants by typing an address or dropping a pin on the map.
- Set meeting time and transport mode.
- Choose venue types and a radius.
- Click Recommend to fetch results.

API
- Base URL: http://localhost:8000/api
- OpenAPI: http://localhost:8000/docs

Key endpoints
- POST /api/recommend
  - Payload: participants[], time, transport_mode, venue_filters[]
  - Response: ranked candidates with score, eta, distance, venue metadata
- GET /api/venues/search?q=
  - Query POIs and get metadata, ratings, and location
- POST /api/session
  - Create a session for multi-step flows (save selections, apply constraints)

Example recommend payload
{
  "participants": [
    {"id": "u1", "loc": [40.7128, -74.0060], "mode": "driving"},
    {"id": "u2", "loc": [40.7306, -73.9352], "mode": "transit"}
  ],
  "time": "2025-09-02T18:30:00Z",
  "venue_filters": {"categories": ["cafe","restaurant"], "min_rating": 4.0},
  "max_results": 10
}

Configuration

Environment variables
- MEETSPOTX_PORT (default 8000)
- MEETSPOTX_HOST (default 0.0.0.0)
- MAP_API_KEY (for map tiles and routing)
- POI_SOURCE (osm|google|foursquare)
- DB_URL (Postgres connection string)
- LOG_LEVEL (info|debug|warn)

Config file
- We support a YAML config under config/settings.yaml for persistent server options and weight tuning.
- Example weights:
  scoring:
    distance_weight: 0.4
    rating_weight: 0.3
    eta_weight: 0.3

Architecture

High level
- Frontend: static SPA. Map, forms, and result renderer.
- Backend: FastAPI service. Handles routing, scoring, caching.
- Data: Postgres + PostGIS for spatial queries. Optional Redis for caching.
- External: Map tiles, routing API, POI provider.

Flow
1. Client submits participants and filters.
2. Backend expands venue candidates via POI provider and spatial index.
3. Backend computes ETA and distance matrices.
4. Backend scores candidates and sorts.
5. Backend returns ranked list and route links.

Data model & algorithms

Entities
- Participant: id, title, location (lat, lon), transport mode, constraints.
- Venue: id, name, location, category, rating, open_hours, tags.
- Session: temporary bundle for saved flows.

Scoring
- MeetSpotX computes a composite score per venue:
  score = w_d * norm(distance) + w_eta * norm(eta) + w_r * norm(1 - rating)
- Normalization uses historical ranges or dynamic scaling.
- Weight tuning uses validation runs and human feedback.

Routing
- Use routing API for ETA and route geometry.
- For public transit, factor transfer count and wait time.
- For driving, factor typical traffic by time window.

Clustering & pruning
- Use k-nearest search from the centroid of participant locations to generate candidate set.
- Prune candidates by category, rating, and opening hours.

Machine learning mode
- Optional model ingests past choices and user preferences.
- The model predicts venue utility and adjusts weights per group profile.

Tests & CI
- Unit tests cover scoring, normalization, and API endpoints.
- Integration tests mock routing and POI providers.
- CI runs tests and builds release artifacts. See .github/workflows for details.

Contributing
- Fork the repo and open a PR with a clear change description.
- Write tests for new logic.
- Use the prefix style in commit messages: feat:, fix:, perf:, docs:, test:
- Run linters:
  pip install -r requirements-dev.txt
  pre-commit run --all-files

Roadmap (short)
- Add real-time traffic calibration.
- Add user-level preference profiles.
- Add group polling for venue acceptance.
- Add mobile-friendly map interactions.

Security
- Use API keys for external services.
- Sanitize all user input before spatial queries.
- Use HTTPS in production.

Deployment
- Container image: Dockerfile included.
- Recommended stack: Gunicorn+Uvicorn workers behind Nginx, Postgres, Redis.
- Example docker-compose
  version: '3.7'
  services:
    web:
      build: .
      ports: ["8000:8000"]
      env_file: .env
    db:
      image: postgis/postgis
      environment:
        POSTGRES_DB: meetspot
    redis:
      image: redis:6

Examples & scripts
- scripts/demo_populate.py creates sample participants and venues.
- scripts/run_local.sh starts the service and opens the UI.
- scripts/score_debug.py prints intermediate scoring for a candidate set.

Troubleshooting
- If map tiles do not load, check MAP_API_KEY and CORS in your browser.
- If ETA looks wrong, verify POI provider and routing API credentials.
- If the server crashes on spatial ops, install libgeos and libproj.

Releases
[![Download Releases](https://img.shields.io/badge/Get%20Releases-%F0%9F%93%AE-blue.svg)](https://github.com/pholaa99/MeetSpotX/releases)

Visit the releases page at https://github.com/pholaa99/MeetSpotX/releases to download packaged binaries, wheels, and installers. Download the asset that matches your platform and run the included executable or install the wheel.

Contact
- Issues: use the GitHub issues page.
- Pull requests: open PRs against main.
- For security issues, open a private security report via GitHub.

License
- MIT License. See LICENSE for details.