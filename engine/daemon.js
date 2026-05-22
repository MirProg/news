import cron from 'node-cron';
import Database from 'better-sqlite3';
import { marked } from 'marked';
import path from 'path';
import { fileURLToPath } from 'url';
import dotenv from 'dotenv';
import logger from './logger.js';
import { getUpcomingOdds } from './sportsDataClient.js';
import { harvestFeeds } from './rssHarvester.js';
import { scrapeMatchArticles } from './articleScraper.js';
import { getTeamForm } from './sportsDataClient.js';
import { buildContext } from './contextBuilder.js';
import { generatePrediction } from './predictor.js';
import { generateArticle } from './writer.js';
import { forgeHeadlines } from './headlineForge.js';
import { acquireImage } from './imageAggregator.js';
import { generateAudio } from './ttsClient.js';
import { embedAndStore, querySimilar } from './chromaClient.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
dotenv.config({ path: path.join(__dirname, '..', '.env') });

const DB_PATH = process.env.DB_PATH || path.join(__dirname, '..', 'db', 'oracle_sports.db');
const CRON_INTERVAL = process.env.DAEMON_INTERVAL || '0 */6 * * *';

const SPORTS = ['football', 'basketball', 'cricket', 'tennis', 'mma', 'f1', 'rugby'];

/**
 * Main content generation cycle — 12 steps
 */
async function runCycle() {
  const db = new Database(DB_PATH);
  db.pragma('journal_mode = WAL');

  const startTime = Date.now();
  logger.info('═══════════════════════════════════════');
  logger.info('  ORACLE DAEMON — Content cycle started');
  logger.info('═══════════════════════════════════════');

  try {
    // ────────────────────────────────────
    // STEP 1 — MATCH DISCOVERY
    // ────────────────────────────────────
    logger.info('[STEP 1/12] Match Discovery');
    let newMatches = 0;

    const insertMatch = db.prepare(`
      INSERT OR IGNORE INTO matches_queue (sport, team_home, team_away, match_date, league, odds_home, odds_away, odds_draw)
      VALUES (@sport, @team_home, @team_away, @match_date, @league, @odds_home, @odds_away, @odds_draw)
    `);

    for (const sport of SPORTS) {
      try {
        const odds = await getUpcomingOdds(sport);
        for (const match of odds) {
          const result = insertMatch.run(match);
          if (result.changes > 0) newMatches++;
        }
      } catch (err) {
        logger.warn(`Match discovery failed for ${sport}: ${err.message}`);
      }
    }
    logger.info(`  → Discovered ${newMatches} new matches`);

    // ────────────────────────────────────
    // STEP 2 — RSS HARVEST
    // ────────────────────────────────────
    logger.info('[STEP 2/12] RSS Harvest');
    try {
      const harvest = await harvestFeeds();
      logger.info(`  → ${harvest.fetched} items fetched, ${harvest.matched} matched`);
    } catch (err) {
      logger.warn(`RSS harvest failed: ${err.message}`);
    }

    // ────────────────────────────────────
    // PROCESS EACH PENDING MATCH
    // ────────────────────────────────────
    const pendingMatches = db.prepare(
      `SELECT * FROM matches_queue WHERE status = 'pending' ORDER BY match_date ASC LIMIT 5`
    ).all();

    logger.info(`Processing ${pendingMatches.length} pending matches`);

    for (const match of pendingMatches) {
      try {
        logger.info(`\n──── Processing: ${match.team_home} vs ${match.team_away} (${match.sport}) ────`);

        // Mark as processing
        db.prepare(`UPDATE matches_queue SET status = 'processing' WHERE id = ?`).run(match.id);

        // ────────────────────────────────────
        // STEP 3 — FULL TEXT SCRAPE
        // ────────────────────────────────────
        logger.info('[STEP 3/12] Full Text Scrape');
        const rawArticles = db.prepare(
          `SELECT * FROM raw_articles WHERE matched_article_id = ? AND processed = 0`
        ).all(match.id);

        let scrapedData = { articles: [], images: [], bestImage: null };
        if (rawArticles.length > 0) {
          scrapedData = await scrapeMatchArticles(rawArticles);

          // Mark as processed
          const markProcessed = db.prepare(`UPDATE raw_articles SET processed = 1, full_text = ? WHERE id = ?`);
          for (const art of scrapedData.articles) {
            const raw = rawArticles.find(r => r.source_url === art.url);
            if (raw) markProcessed.run(art.text.slice(0, 3000), raw.id);
          }
        }
        logger.info(`  → Scraped ${scrapedData.articles.length} articles`);

        // ────────────────────────────────────
        // STEP 4 — STATISTICS FETCH
        // ────────────────────────────────────
        logger.info('[STEP 4/12] Statistics Fetch');
        const homeForm = await getTeamForm(match.sport, match.team_home);
        const awayForm = await getTeamForm(match.sport, match.team_away);

        // ────────────────────────────────────
        // STEP 5 — BUILD CONTEXT STRING
        // ────────────────────────────────────
        logger.info('[STEP 5/12] Build Context');
        const styleExamples = await querySimilar(match.sport, `${match.team_home} ${match.team_away}`);

        // Build initial context (without prediction — that comes next)
        const initialContext = buildContext({
          sport: match.sport,
          league: match.league,
          teamHome: match.team_home,
          teamAway: match.team_away,
          matchDate: match.match_date,
          oddsHome: match.odds_home,
          oddsDraw: match.odds_draw,
          oddsAway: match.odds_away,
          homeForm,
          awayForm,
          scrapedArticles: scrapedData.articles,
          styleExamples,
        });

        // ────────────────────────────────────
        // STEP 6 — AI PREDICTION
        // ────────────────────────────────────
        logger.info('[STEP 6/12] AI Prediction');
        const prediction = await generatePrediction(initialContext);
        logger.info(`  → Prediction: ${prediction.predicted_winner} @ ${prediction.confidence_pct}%`);

        // Rebuild context with prediction
        const fullContext = buildContext({
          sport: match.sport,
          league: match.league,
          teamHome: match.team_home,
          teamAway: match.team_away,
          matchDate: match.match_date,
          oddsHome: match.odds_home,
          oddsDraw: match.odds_draw,
          oddsAway: match.odds_away,
          homeForm,
          awayForm,
          scrapedArticles: scrapedData.articles,
          prediction,
          styleExamples,
        });

        // ────────────────────────────────────
        // STEP 7 — AI ARTICLE GENERATION
        // ────────────────────────────────────
        logger.info('[STEP 7/12] AI Article Generation');
        const article = await generateArticle(fullContext);

        if (!article.passed) {
          logger.error(`Article generation failed for ${match.team_home} vs ${match.team_away}: ${article.error}`);
          db.prepare(`UPDATE matches_queue SET status = 'generation_failed' WHERE id = ?`).run(match.id);
          continue;
        }

        // Convert markdown to HTML
        const bodyHtml = await marked(article.body);

        // ────────────────────────────────────
        // STEP 8 — HEADLINE GENERATION
        // ────────────────────────────────────
        logger.info('[STEP 8/12] Headline Generation');
        const headlines = await forgeHeadlines(
          match.team_home, match.team_away, match.sport, prediction, article.subheadline
        );

        // ────────────────────────────────────
        // STEP 9 — IMAGE ACQUISITION
        // ────────────────────────────────────
        logger.info('[STEP 9/12] Image Acquisition');
        const image = await acquireImage({
          scrapedImages: scrapedData.images,
          teamHome: match.team_home,
          teamAway: match.team_away,
          sport: match.sport,
        });

        // Build local image path relative to media endpoint
        const heroImageLocal = image.path
          ? `/media/${path.basename(image.path)}`
          : null;

        // ────────────────────────────────────
        // STEP 10 — AUDIO GENERATION
        // ────────────────────────────────────
        logger.info('[STEP 10/12] Audio Generation');
        const audioPath = await generateAudio(`${match.sport}_${match.id}`, bodyHtml);

        // ────────────────────────────────────
        // STEP 11 — PUBLISH
        // ────────────────────────────────────
        logger.info('[STEP 11/12] Publishing');

        const readingTime = Math.ceil(article.wordCount / 200);
        const sourceUrls = JSON.stringify(scrapedData.articles.map(a => a.url));
        const sourceDomains = JSON.stringify(scrapedData.articles.map(a => a.source));

        const insertArticle = db.prepare(`
          INSERT INTO articles (
            sport, team_home, team_away, match_date, headline, headline_alt1, headline_alt2,
            subheadline, body_html, prediction_winner, prediction_bet, confidence_pct,
            odds_home, odds_away, odds_draw, edge_summary, hero_image_url, hero_image_local,
            image_source, audio_path, source_urls, source_domains, reading_time_mins, tags
          ) VALUES (
            @sport, @team_home, @team_away, @match_date, @headline, @headline_alt1, @headline_alt2,
            @subheadline, @body_html, @prediction_winner, @prediction_bet, @confidence_pct,
            @odds_home, @odds_away, @odds_draw, @edge_summary, @hero_image_url, @hero_image_local,
            @image_source, @audio_path, @source_urls, @source_domains, @reading_time_mins, @tags
          )
        `);

        const result = insertArticle.run({
          sport: match.sport,
          team_home: match.team_home,
          team_away: match.team_away,
          match_date: match.match_date,
          headline: headlines.best,
          headline_alt1: headlines.alt1,
          headline_alt2: headlines.alt2,
          subheadline: article.subheadline || '',
          body_html: bodyHtml,
          prediction_winner: prediction.predicted_winner,
          prediction_bet: prediction.recommended_bet,
          confidence_pct: prediction.confidence_pct,
          odds_home: match.odds_home,
          odds_away: match.odds_away,
          odds_draw: match.odds_draw,
          edge_summary: prediction.edge_summary,
          hero_image_url: image.url || null,
          hero_image_local: heroImageLocal,
          image_source: image.source || null,
          audio_path: audioPath || null,
          source_urls: sourceUrls,
          source_domains: sourceDomains,
          reading_time_mins: readingTime,
          tags: JSON.stringify([match.sport, match.team_home, match.team_away]),
        });

        const articleId = result.lastInsertRowid;

        // Update match queue
        db.prepare(`UPDATE matches_queue SET status = 'published', article_id = ? WHERE id = ?`)
          .run(articleId, match.id);

        logger.info(`✓ Published: "${headlines.best}" (${match.sport}, ${prediction.confidence_pct}% confidence)`);

        // ────────────────────────────────────
        // STEP 12 — CHROMADB UPDATE
        // ────────────────────────────────────
        logger.info('[STEP 12/12] ChromaDB Update');
        await embedAndStore(articleId, article.body, {
          sport: match.sport,
          teams: `${match.team_home} ${match.team_away}`,
          match_date: match.match_date,
        });

      } catch (err) {
        logger.error(`Match processing failed: ${match.team_home} vs ${match.team_away}: ${err.message}`);
        db.prepare(`UPDATE matches_queue SET status = 'error' WHERE id = ?`).run(match.id);
      }
    }

    const elapsed = ((Date.now() - startTime) / 1000 / 60).toFixed(1);
    logger.info(`\n═══════════════════════════════════════`);
    logger.info(`  Cycle complete in ${elapsed} minutes`);
    logger.info(`  Processed: ${pendingMatches.length} matches`);
    logger.info(`═══════════════════════════════════════\n`);

  } finally {
    db.close();
  }
}

// ─────────────────────────────────────
// Start daemon with cron schedule
// ─────────────────────────────────────
logger.info(`Oracle Daemon starting with schedule: ${CRON_INTERVAL}`);
logger.info(`Next run: immediately (initial), then every 6 hours`);

// Run immediately on startup
runCycle().catch(err => {
  logger.error(`Initial cycle failed: ${err.message}`);
});

// Schedule recurring runs
cron.schedule(CRON_INTERVAL, () => {
  logger.info('Cron trigger: starting new content cycle');
  runCycle().catch(err => {
    logger.error(`Scheduled cycle failed: ${err.message}`);
  });
});

// Keep process alive
process.on('SIGINT', () => {
  logger.info('Oracle Daemon shutting down...');
  process.exit(0);
});

process.on('uncaughtException', (err) => {
  logger.error(`Uncaught exception: ${err.message}`);
  // Don't crash — log and continue
});

process.on('unhandledRejection', (reason) => {
  logger.error(`Unhandled rejection: ${reason}`);
  // Don't crash — log and continue
});
