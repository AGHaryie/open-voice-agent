import http.server
import socketserver
import json
import asyncio
import os
from livekit import api

PORT = 3005

LIVEKIT_URL = os.environ.get("LIVEKIT_URL", "wss://open-voice-agent-mbfh49s1.livekit.cloud")
LIVEKIT_API_KEY = os.environ.get("LIVEKIT_API_KEY", "APIog2ZEydoX7Aw")
LIVEKIT_API_SECRET = os.environ.get("LIVEKIT_API_SECRET", "9U3CmxVTSAHeogAlFUtNNBVYfyaf8N8SiTKrfEuRNePE")

# Convert wss:// to https:// for the REST API client
HTTP_URL = LIVEKIT_URL.replace("wss://", "https://")

async def create_agent_dispatch(room_name: str, agent_name: str):
    lk_api = api.LiveKitAPI(HTTP_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
    try:
        req = api.CreateAgentDispatchRequest(
            room=room_name,
            agent_name=agent_name
        )
        await lk_api.agent_dispatch.create_dispatch(req)
        print(f"--> [Cloud] Dispatched {agent_name} to room {room_name}")
    except Exception as e:
        print(f"Cloud dispatch error: {e}")
    finally:
        await lk_api.aclose()

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/token":
            try:
                room_name = "my-room"
                asyncio.run(create_agent_dispatch(room_name, "voice-agent"))

                grant = api.VideoGrants(
                    room_join=True,
                    room=room_name,
                    can_publish=True,
                    can_subscribe=True,
                )
                token = (
                    api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
                    .with_identity("web-user")
                    .with_name("Web User")
                    .with_grants(grant)
                    .to_jwt()
                )
                body = json.dumps({"token": token, "url": LIVEKIT_URL}).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode())
        else:
            super().do_GET()

socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Web server running at http://localhost:{PORT}")
    httpd.serve_forever()
