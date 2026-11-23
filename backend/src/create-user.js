import { PrismaClient } from '@prisma/client';
import bcrypt from 'bcrypt';

const [, , inputUsername, role] = process.argv;
const username = inputUsername?.trim();
const password = process.env.HIDJI_NEW_USER_PASSWORD;

if (!username || username.length > 64 || !['barista', 'gm'].includes(role) ||
    !password || password.length < 12 || Buffer.byteLength(password, 'utf8') > 72) {
  console.error('Gunakan npm run db:create-user -- <username> <barista|gm> dan isi HIDJI_NEW_USER_PASSWORD dengan 12 karakter hingga 72 byte.');
  process.exit(1);
}

const prisma = new PrismaClient();
try {
  const passwordHash = await bcrypt.hash(password, 12);
  const user = await prisma.user.create({
    data: { username, role, passwordHash },
    select: { username: true, role: true },
  });
  console.log(`Akun ${user.username} (${user.role}) dibuat.`);
} catch (err) {
  console.error(err.code === 'P2002' ? 'Username sudah dipakai.' : 'Gagal membuat akun. Periksa koneksi dan migrasi database.');
  process.exitCode = 1;
} finally {
  await prisma.$disconnect();
}
