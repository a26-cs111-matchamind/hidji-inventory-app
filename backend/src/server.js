import { PrismaClient } from '@prisma/client';
import { createApp } from './app.js';

const { DATABASE_URL, JWT_SECRET, PORT = '5000', FRONTEND_ORIGIN = 'http://localhost:5173' } = process.env;

if (!DATABASE_URL || !JWT_SECRET || Buffer.byteLength(JWT_SECRET, 'utf8') < 32 ||
    JWT_SECRET === 'super-secret-jwt-key-replace-in-production') {
  throw new Error('Isi DATABASE_URL dan JWT_SECRET acak minimal 32 byte di environment backend.');
}

const prisma = new PrismaClient();
const app = createApp({ users: prisma.user, jwtSecret: JWT_SECRET, frontendOrigin });

app.listen(Number(PORT), () => {
  console.log(`HIDJI API berjalan di port ${PORT}`);
});
