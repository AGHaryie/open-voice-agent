import { AccessToken } from 'livekit-server-sdk';

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Credentials', true);
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS');

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  const apiKey = process.env.LIVEKIT_API_KEY;
  const apiSecret = process.env.LIVEKIT_API_SECRET;

  if (!apiKey || !apiSecret) {
    return res.status(500).json({ error: 'LiveKit credentials missing in environment variables' });
  }

  const roomName = 'my-room';
  const participantIdentity = `user-${Math.random().toString(36).substring(7)}`;

  const at = new AccessToken(apiKey, apiSecret, {
    identity: participantIdentity,
    name: 'Web User',
  });

  at.addGrant({
    roomJoin: true,
    room: roomName,
    canPublish: true,
    canSubscribe: true,
  });

  const token = await at.toJwt();

  return res.status(200).json({
    token,
    url: process.env.LIVEKIT_URL,
  });
}
