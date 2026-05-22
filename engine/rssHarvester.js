import RssParser from 'rss-parser';
import Fuse from 'fuse.js';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import Database from 'better-sqlite3';
import dotenv from 'dotenv';
import logger from './logger.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
dotenv.config({ path: path.join(__dirname, '..', '.env') });

const DB_PATH = process.env.DB_PATH || path.join(__dirname, '..', 'db', 'oracle_sports.db');
const FEEDS_PATH = path.join(__dirname, '..', 'config', 'feeds.json');

const parser = new RssParser({
  timeout: 15000,
  headers: {
    'User-Agent': 'Mozilla/5.0 (compatible; OracleSportsBot/1.0; +https://oraclesports.ai)',
    'Accept': 'application/rss+xml, application/xml, text/xml',
  },
});

/**
 * Harvest all RSS feeds and match items to queued matches
 */
async function harvestFeeds() {
  const db = new Database(DB_PATH);
  db.pragma('journal_mode = WAL');

  try {
    // Load feed configuration
    const feedsConfig = JSON.parse(fs.readFileSync(FEEDS_PATH, 'utf-8'));

    // Load pending matches from queue
    const pendingMatches = db.prepare(
      `SELECT * FROM matches_queue WHERE status IN ('pending', 'harvesting') ORDER BY match_date ASC`
    ).all();

    if (pendingMatches.length === 0) {
      logger.info('RSS Harvester: No pending matches in queue, but will fetch for News Wire.');
    }

    // Build Fuse.js index for fuzzy team matching
    const matchIndex = new Fuse(pendingMatches, {
      keys: ['team_home', 'team_away'],
      threshold: 0.4,
      includeScore: true,
    });

    const insertStmt = db.prepare(`
      INSERT OR IGNORE INTO raw_articles (sport, source_url, source_domain, title, summary, og_image, pub_date, matched_article_id)
      VALUES (@sport, @source_url, @source_domain, @title, @summary, @og_image, @pub_date, @matched_article_id)
    `);

    let totalFetched = 0;
    let totalMatched = 0;

    // Iterate each sport's feeds
    for (const [sport, feeds] of Object.entries(feedsConfig)) {
      for (const feed of feeds) {
        try {
          logger.info(`RSS: Fetching ${feed.source} (${sport})`);
          const rss = await parser.parseURL(feed.url);

          for (const item of rss.items || []) {
            totalFetched++;

            // Skip items without titles
            if (!item.title) continue;

            // Match against pending matches
            const titleToMatch = item.title;
            const matches = matchIndex.search(titleToMatch);

            // Take best match if score is good enough (< 0.6 = good match)
            const bestMatch = matches.find(m => m.score < 0.6);

            if (bestMatch) {
              const match = bestMatch.item;
              try {
                insertStmt.run({
                  sport,
                  source_url: item.link || '',
                  source_domain: feed.source,
                  title: item.title,
                  summary: item.contentSnippet || item.content || '',
                  og_image: item.enclosure?.url || null,
                  pub_date: item.pubDate || item.isoDate || null,
                  matched_article_id: match.id,
                });
                totalMatched++;
                logger.info(`RSS matched: "${item.title}" → ${match.team_home} vs ${match.team_away}`);
              } catch (insertErr) {
                if (!insertErr.message.includes('UNIQUE')) {
                  logger.warn(`RSS insert error: ${insertErr.message}`);
                }
              }
            } else {
              // Insert anyway for the News Wire, just without a matched match
              try {
                insertStmt.run({
                  sport,
                  source_url: item.link || '',
                  source_domain: feed.source,
                  title: item.title,
                  summary: item.contentSnippet || item.content || '',
                  og_image: item.enclosure?.url || null,
                  pub_date: item.pubDate || item.isoDate || null,
                  matched_article_id: null,
                });
              } catch (insertErr) {
                // Ignore UNIQUE constraint errors silently
              }
            }
          }
        } catch (feedErr) {
          logger.warn(`RSS feed error (${feed.source}): ${feedErr.message}`);
        }
      }
    }

    logger.info(`RSS Harvest complete: ${totalFetched} items fetched, ${totalMatched} matched`);
    return { fetched: totalFetched, matched: totalMatched };
  } finally {
    db.close();
  }
}

export { harvestFeeds };
