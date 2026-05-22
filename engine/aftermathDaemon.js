import cron from 'node-cron';
import Database from 'better-sqlite3';
import path from 'path';
import { fileURLToPath } from 'url';
import dotenv from 'dotenv';
import logger from './logger.js';
import { getMatchResult } from './sportsDataClient.js';
import { generateAftermath } from './writer.js';
import { marked } from 'marked';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
dotenv.config({ path: path.join(__dirname, '..', '.env') });

const DB_PATH = process.env.DB_PATH || path.join(__dirname, '..', 'db', 'oracle_sports.db');
const CRON_INTERVAL = process.env.AFTERMATH_INTERVAL || '*/30 * * * *';

/**
 * Check resolved matches and generate aftermath sections
 */
async function checkResolved() {
  const db = new Database(DB_PATH);
  db.pragma('journal_mode = WAL');

  logger.info('Aftermath Daemon: checking for resolved matches...');

  try {
    // Find unresolved articles where match date has passed
    const unresolved = db.prepare(`
      SELECT * FROM articles
      WHERE resolved = 0 AND match_date < datetime('now')
      ORDER BY match_date ASC
      LIMIT 10
    `).all();

    if (unresolved.length === 0) {
      logger.info('Aftermath: No unresolved matches found');
      return;
    }

    logger.info(`Aftermath: Found ${unresolved.length} unresolved matches`);

    const resolveStmt = db.prepare(`
      UPDATE articles
      SET resolved = 1, prediction_correct = ?, aftermath_html = ?, match_resolved_at = datetime('now')
      WHERE id = ?
    `);

    for (const article of unresolved) {
      try {
        // Check ESPN for actual result
        const result = await getMatchResult(article.sport, article.team_home, article.team_away);

        if (!result) {
          logger.info(`  No result yet for: ${article.team_home} vs ${article.team_away}`);
          continue;
        }

        // Determine if prediction was correct
        const predictionCorrect = result.winner?.toLowerCase() === article.prediction_winner?.toLowerCase() ? 1 : 0;

        // Generate aftermath text
        logger.info(`  Generating aftermath for: ${article.headline}`);
        const aftermathMd = await generateAftermath(
          article.headline,
          article.prediction_winner,
          article.confidence_pct,
          result
        );

        const aftermathHtml = await marked(aftermathMd || '');

        // Update article
        resolveStmt.run(predictionCorrect, aftermathHtml, article.id);

        const correctStr = predictionCorrect ? 'CORRECT ✓' : 'INCORRECT ✗';
        logger.info(`  → Resolved: ${article.headline} — Oracle was ${correctStr}`);

      } catch (err) {
        logger.error(`  Aftermath error for article ${article.id}: ${err.message}`);
      }
    }

    // Log Oracle record
    const record = db.prepare(`
      SELECT
        COUNT(*) as total,
        SUM(CASE WHEN prediction_correct = 1 THEN 1 ELSE 0 END) as correct
      FROM articles WHERE resolved = 1
    `).get();

    if (record.total > 0) {
      const pct = Math.round((record.correct / record.total) * 100);
      logger.info(`Oracle Record: ${pct}% (${record.correct}/${record.total})`);
    }

  } finally {
    db.close();
  }
}

// ─────────────────────────────────────
// Start aftermath daemon
// ─────────────────────────────────────
logger.info(`Aftermath Daemon starting with schedule: ${CRON_INTERVAL}`);

// Run immediately on startup
checkResolved().catch(err => {
  logger.error(`Initial aftermath check failed: ${err.message}`);
});

// Schedule recurring runs
cron.schedule(CRON_INTERVAL, () => {
  logger.info('Aftermath cron trigger');
  checkResolved().catch(err => {
    logger.error(`Scheduled aftermath check failed: ${err.message}`);
  });
});

process.on('SIGINT', () => {
  logger.info('Aftermath Daemon shutting down...');
  process.exit(0);
});

process.on('uncaughtException', (err) => {
  logger.error(`Uncaught exception: ${err.message}`);
});

process.on('unhandledRejection', (reason) => {
  logger.error(`Unhandled rejection: ${reason}`);
});
