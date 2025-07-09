from flask import Flask, redirect, request, session
import os
import json
import requests
from scraper import get_rematchtracker_rank

app = Flask(__name__)
app.secret_key = os.urandom(24)

NGROK_URL = "https://f96dc8fc15bd.ngrok-free.app"  # ✅ Make sure this is always your active ngrok URL

@app.route('/')
def home():
    return '<a href="/steam/login">Login with Steam</a>'

@app.route('/steam/login')
def steam_login():
    discord_id = request.args.get("discord_id")
    if not discord_id:
        return "❌ Discord ID not provided in the URL."

    session["discord_id"] = discord_id

    steam_openid_url = (
        "https://steamcommunity.com/openid/login"
        "?openid.ns=http://specs.openid.net/auth/2.0"
        "&openid.mode=checkid_setup"
        f"&openid.return_to={NGROK_URL}/steam/return"
        f"&openid.realm={NGROK_URL}/"
        "&openid.identity=http://specs.openid.net/auth/2.0/identifier_select"
        "&openid.claimed_id=http://specs.openid.net/auth/2.0/identifier_select"
    )
    return redirect(steam_openid_url)

@app.route('/steam/return')
def steam_return():
    from urllib.parse import urlencode

    # Validate Steam login
    params = request.args.to_dict()
    params['openid.mode'] = 'check_authentication'
    response = requests.post('https://steamcommunity.com/openid/login', data=params)

    if "is_valid:true" in response.text:
        claimed_id = request.args.get('openid.claimed_id')
        steam_id = claimed_id.split('/')[-1]

        discord_id = session.get("discord_id")
        if not discord_id:
            return "❌ Discord ID not found in session."

        # Scrape rank
        rank = get_rematchtracker_rank(steam_id)

        # Save locally
        try:
            with open("data.json", "r") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}

        data[str(discord_id)] = {
            "steam_id": steam_id,
            "rank": rank
        }

        with open("data.json", "w") as f:
            json.dump(data, f, indent=4)

        # ✅ AUTOMATED ROLE ASSIGNMENT
        # Replace this with your server's ID
        guild_id = 1376261610137456892

        assign_data = {
            "discord_id": discord_id,
            "rank": rank,
            "guild_id": guild_id
        }

        try:
            post_response = requests.post("http://localhost:8080/assignrole", json=assign_data)
            result = post_response.json()
        except Exception as e:
            result = {"success": False, "error": str(e)}

        if result.get("success"):
            return f"✅ Verified! Your Steam ID is: {steam_id}<br>Rank: {rank} — Role has been added in Discord!"
        else:
            return f"✅ Verified! Your Steam ID is: {steam_id}<br>Rank: {rank}<br>❌ Role assignment failed: {result.get('error', 'Unknown error')}"

    else:
        return "❌ Failed to verify Steam login."

if __name__ == '__main__':
    app.run(debug=True)