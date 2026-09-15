const { AccessToken } = require('livekit-server-sdk');

module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  const apiKey = process.env.LIVEKIT_API_KEY;
  const apiSecret = process.env.LIVEKIT_API_SECRET;
  const livekitUrl = process.env.LIVEKIT_URL;

  if (!apiKey || !apiSecret) {
    console.error('Missing LiveKit environment variables:', {
      hasKey: !!apiKey,
      hasSecret: !!apiSecret
    });
    return res.status(500).json({ 
      error: 'LiveKit credentials missing on Vercel environment variables' 
    });
  }

  try {
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
      url: livekitUrl,
    });
  } catch (err) {
    console.error('Failed generating token:', err);
    return res.status(500).json({ error: err.message });
  }
};
