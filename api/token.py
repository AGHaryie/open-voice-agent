import os
import json
from http.server import BaseHTTPRequestHandler
from livekit import api

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        livekit_api_key = os.environ.get("LIVEKIT_API_KEY", "")
        livekit_api_secret = os.environ.get("LIVEKIT_API_SECRET", "")
        
        token = api.AccessToken(livekit_api_key, livekit_api_secret) \
            .with_identity("web-user") \
            .with_name("Web User") \
            .with_grants(api.VideoGrants(
                room_join=True,
                room="my-room",
                can_publish=True,
                can_subscribe=True,
            ))

        jwt_token = token.to_jwt()

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({"token": jwt_token}).encode('utf-8'))
