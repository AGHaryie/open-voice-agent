const crypto = require('crypto');

function base64UrlEncode(str) {
  return Buffer.from(str)
    .toString('base64')
    .replace(/=/g, '')
    .replace(/\+/g, '-')
    .replace(/\//g, '_');
}

function sendResponse(res, statusCode, data) {
  if (typeof res.status === 'function' && typeof res.json === 'function') {
    return res.status(statusCode).json(data);
  }
  res.writeHead(statusCode, { 'Content-Type': 'application/json' });
  return res.end(JSON.stringify(data));
}

module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS');

  if (req.method === 'OPTIONS') {
    if (typeof res.status === 'function') return res.status(200).end();
    res.writeHead(200);
    return res.end();
  }

  const apiKey = process.env.LIVEKIT_API_KEY || "APIog2ZEydoX7Aw";
  const apiSecret = process.env.LIVEKIT_API_SECRET || "9U3CmxVTSAHeogAlFUtNNBVYfyaf8N8SiTKrfEuRNePE";
  const livekitUrl = process.env.LIVEKIT_URL || "wss://open-voice-agent-mbfh49s1.livekit.cloud";

  if (!apiKey || !apiSecret) {
    return sendResponse(res, 500, { error: 'LIVEKIT_API_KEY or LIVEKIT_API_SECRET missing.' });
  }

  const now = Math.floor(Date.now() / 1000);
  const header = { alg: 'HS256', typ: 'JWT' };

  const payload = {
    sub: `user-${Math.random().toString(36).substring(7)}`,
    iss: apiKey,
    nbf: now - 5,
    exp: now + 3600,
    video: {
      room: 'my-room',
      roomJoin: true,
      canPublish: true,
      canSubscribe: true
    }
  };

  const headerB64 = base64UrlEncode(JSON.stringify(header));
  const payloadB64 = base64UrlEncode(JSON.stringify(payload));
  const signInput = `${headerB64}.${payloadB64}`;

  const signature = crypto
    .createHmac('sha256', apiSecret)
    .update(signInput)
    .digest('base64')
    .replace(/=/g, '')
    .replace(/\+/g, '-')
    .replace(/\//g, '_');

  const token = `${signInput}.${signature}`;

  return sendResponse(res, 200, {
    token,
    url: livekitUrl
  });
};
