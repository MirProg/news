import { Router } from 'express';
import { stmts } from '../db.js';

const router = Router();

// ─────────────────────────────────────
// POST /api/admin/generate — Trigger article generation
// ─────────────────────────────────────
router.post('/admin/generate', async (req, res) => {
  try {
    const { sport, team_home, team_away, match_date, league } = req.body;

    if (!sport || !team_home || !team_away || !match_date) {
      return res.status(400).json({
        error: 'Missing required fields: sport, team_home, team_away, match_date',
      });
    }

    // Insert into matches_queue
    const result = stmts.insertMatch.run({
      sport,
      team_home,
      team_away,
      match_date,
      league: league || '',
      odds_home: req.body.odds_home || null,
      odds_away: req.body.odds_away || null,
      odds_draw: req.body.odds_draw || null,
    });

    res.json({
      message: 'Match queued for article generation',
      matchId: result.lastInsertRowid,
      note: 'The daemon will process this match on its next cycle, or you can restart the daemon to trigger immediate generation.',
    });
  } catch (err) {
    console.error('Error queueing match:', err);
    res.status(500).json({ error: 'Failed to queue match for generation' });
  }
});

// ─────────────────────────────────────
// POST /api/admin/resolve/:id — Mark match resolved
// ─────────────────────────────────────
router.post('/admin/resolve/:id', async (req, res) => {
  try {
    const id = parseInt(req.params.id);
    const { prediction_correct, aftermath_html } = req.body;

    if (isNaN(id)) {
      return res.status(400).json({ error: 'Invalid article ID' });
    }

    if (prediction_correct === undefined) {
      return res.status(400).json({ error: 'Missing prediction_correct (0 or 1)' });
    }

    stmts.resolveArticle.run(
      prediction_correct ? 1 : 0,
      aftermath_html || null,
      id
    );

    res.json({
      message: 'Article resolved',
      articleId: id,
      predictionCorrect: !!prediction_correct,
    });
  } catch (err) {
    console.error('Error resolving article:', err);
    res.status(500).json({ error: 'Failed to resolve article' });
  }
});

// ─────────────────────────────────────
// GET /api/health — System health check
// ─────────────────────────────────────
router.get('/health', async (req, res) => {
  const health = {
    status: 'operational',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    memory: process.memoryUsage(),
  };

  try {
    const articleCount = stmts.countArticles.get();
    health.articles = articleCount.total;

    const record = stmts.getOracleRecord.get();
    health.oracle_record = {
      total: record.total || 0,
      correct: record.correct || 0,
      pct: record.total > 0 ? Math.round((record.correct / record.total) * 100) : 0,
    };
  } catch {
    health.database = 'error';
  }

  res.json(health);
});

// ─────────────────────────────────────
// GET /api/leaderboard — Top confidence predictions
// ─────────────────────────────────────
router.get('/leaderboard', (req, res) => {
  try {
    const predictions = stmts.getLeaderboard.all();
    const record = stmts.getOracleRecord.get();

    res.json({
      predictions,
      record: {
        total: record.total || 0,
        correct: record.correct || 0,
        pct: record.total > 0 ? Math.round((record.correct / record.total) * 100) : 0,
      },
    });
  } catch (err) {
    console.error('Error fetching leaderboard:', err);
    res.status(500).json({ error: 'Failed to fetch leaderboard' });
  }
});

export default router;
