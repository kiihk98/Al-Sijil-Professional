# AlSijil_Bot

Setup:

1. Copy `.env.example` to `.env` and set `DISCORD_TOKEN`.
2. Install dependencies: `pip install -r requirements.txt`.
3. Run `python main.py`.

Deployment on Render:
- Create a Python web service on Render and point to this repo.
- Render will use the Flask root `/` that exists in `main.py` to keep the service alive.
- Add environment variable `DISCORD_TOKEN` and `SECRET_TOKEN` in Render settings (do NOT commit `.env`).

Security note:
- Immediately rotate your bot token if it was exposed.
