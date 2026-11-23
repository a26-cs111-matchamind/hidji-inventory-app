import bcrypt from 'bcrypt';
import cors from 'cors';
import express from 'express';
import { rateLimit } from 'express-rate-limit';
import jwt from 'jsonwebtoken';

const dummyHash = await bcrypt.hash('hidji-invalid-login', 12);

function sendError(res, status, code, message) {
  return res.status(status).json({ status: 'error', error: { code, message, details: [] } });
}

export function createApp({ users, jwtSecret, frontendOrigin }) {
  const app = express();
  app.disable('x-powered-by');
  app.use(cors({ origin: frontendOrigin }));

  const loginLimit = rateLimit({
    windowMs: 60_000,
    limit: 20,
    standardHeaders: 'draft-8',
    legacyHeaders: false,
    skipSuccessfulRequests: true,
    handler: (_req, res) =>
      sendError(res, 429, 'RATE_LIMIT_EXCEEDED', 'Terlalu banyak percobaan login. Coba lagi nanti.'),
  });

  app.post('/api/v1/auth/login', loginLimit, express.json({ limit: '16kb' }), async (req, res) => {
    const { username, password } = req.body ?? {};
    if (username === undefined || password === undefined) {
      return sendError(res, 400, 'BAD_REQUEST', 'Username dan password wajib diisi.');
    }

    if (
      typeof username !== 'string' || !username.trim() || username.trim().length > 64 ||
      typeof password !== 'string' || !password || Buffer.byteLength(password, 'utf8') > 72
    ) {
      return sendError(res, 422, 'VALIDATION_ERROR', 'Username atau password tidak valid.');
    }

    const user = await users.findUnique({
      where: { username: username.trim() },
      select: { id: true, role: true, passwordHash: true },
    });
    const matches = await bcrypt.compare(password, user?.passwordHash ?? dummyHash);
    if (!user || !matches) {
      return sendError(res, 401, 'UNAUTHORIZED', 'Username atau password salah.');
    }

    const token = jwt.sign({ role: user.role }, jwtSecret, {
      algorithm: 'HS256',
      subject: user.id,
      issuer: 'hidji-backend',
      expiresIn: '1h',
    });
    return res.set('Cache-Control', 'no-store').json({ token, role: user.role });
  });

  app.use((_req, res) => sendError(res, 404, 'NOT_FOUND', 'Endpoint tidak ditemukan.'));
  app.use((err, _req, res, next) => {
    if (res.headersSent) return next(err);
    if (err.type === 'entity.parse.failed') {
      return sendError(res, 400, 'BAD_REQUEST', 'Format JSON tidak valid.');
    }
    if (err.type === 'entity.too.large') {
      return sendError(res, 413, 'PAYLOAD_TOO_LARGE', 'Ukuran request terlalu besar.');
    }

    console.error('API request failed', err.name, err.code);
    return sendError(res, 500, 'INTERNAL_ERROR', 'Terjadi kesalahan pada server.');
  });

  return app;
}
