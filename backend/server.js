import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import path from 'path';
import { fileURLToPath } from 'url';
import dotenv from 'dotenv';

import articlesRouter from './routes/articles.js';
import scoresRouter from './routes/scores.js';
import adminRouter from './routes/admin.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

dotenv.config({ path: path.join(__dirname, '..', '.env') });

const app = express();
const PORT = process.env.PORT || 4000;

// ─────────────────────────────────────
// Middleware
// ─────────────────────────────────────
app.use(helmet({
  crossOriginResourcePolicy: { policy: 'cross-origin' },
  contentSecurityPolicy: false,
}));

app.use(cors({
  origin: [`http://localhost:${process.env.FRONTEND_PORT || 3000}`, 'http://localhost:3000'],
  credentials: true,
}));

app.use(express.json());

// ─────────────────────────────────────
// Static Files
// ─────────────────────────────────────

// Serve TTS audio files
app.use('/audio', express.static(path.join(__dirname, 'public', 'audio'), {
  maxAge: '7d',
  setHeaders: (res) => {
    res.set('Cache-Control', 'public, max-age=604800');
  },
}));

// Serve cached hero images
app.use('/media', express.static(path.join(__dirname, '..', 'imageCache'), {
  maxAge: '7d',
  setHeaders: (res) => {
    res.set('Cache-Control', 'public, max-age=604800');
  },
}));

// ─────────────────────────────────────
// API Routes
// ─────────────────────────────────────
app.use('/api/articles', articlesRouter);
app.use('/api/scores', scoresRouter);
app.use('/api/admin', adminRouter);
app.use('/api', adminRouter);

// ─────────────────────────────────────
// Health Check
// ─────────────────────────────────────
app.get('/api/health', async (req, res) => {
  const health = {
    status: 'operational',
    timestamp: new Date().toISOString(),
    services: {
      backend: 'running',
      database: 'unknown',
      ollama: 'unknown',
      chromadb: 'unknown',
      kokoro: 'unknown',
    },
  };

  // Check database
  try {
    const { db } = await import('./db.js');
    db.prepare('SELECT 1').get();
    health.services.database = 'connected';
  } catch {
    health.services.database = 'disconnected';
  }

  // Check Ollama
  try {
    const ollamaUrl = process.env.OLLAMA_BASE_URL || 'http://localhost:11434/v1';
    const baseUrl = ollamaUrl.replace('/v1', '');
    const resp = await fetch(`${baseUrl}/api/tags`, { signal: AbortSignal.timeout(3000) });
    health.services.ollama = resp.ok ? 'running' : 'error';
  } catch {
    health.services.ollama = 'disconnected';
  }

  // Check ChromaDB
  try {
    const chromaUrl = process.env.CHROMADB_URL || 'http://localhost:8000';
    const resp = await fetch(`${chromaUrl}/api/v1/heartbeat`, { signal: AbortSignal.timeout(3000) });
    health.services.chromadb = resp.ok ? 'running' : 'error';
  } catch {
    health.services.chromadb = 'disconnected';
  }

  // Check Kokoro TTS
  try {
    const kokoroUrl = process.env.KOKORO_URL || 'http://localhost:8880';
    const resp = await fetch(`${kokoroUrl}/docs`, { signal: AbortSignal.timeout(3000) });
    health.services.kokoro = resp.ok ? 'running' : 'error';
  } catch {
    health.services.kokoro = 'disconnected';
  }

  const allHealthy = Object.values(health.services).every(s => s === 'running' || s === 'connected');
  health.status = allHealthy ? 'all_systems_operational' : 'degraded';

  res.json(health);
});

// ─────────────────────────────────────
// 404 Handler
// ─────────────────────────────────────
app.use((req, res) => {
  res.status(404).json({ error: 'Not found', path: req.path });
});

// ─────────────────────────────────────
// Error Handler
// ─────────────────────────────────────
app.use((err, req, res, next) => {
  console.error('Server error:', err);
  res.status(500).json({ error: 'Internal server error' });
});

// ─────────────────────────────────────
// Start Server
// ─────────────────────────────────────
app.listen(PORT, () => {
  console.log(`\n═══════════════════════════════════════`);
  console.log(`  ORACLE SPORTS — Backend API`);
  console.log(`  Port: ${PORT}`);
  console.log(`  Time: ${new Date().toISOString()}`);
  console.log(`═══════════════════════════════════════\n`);
});

export default app;
