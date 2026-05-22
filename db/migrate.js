import Database from 'better-sqlite3';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const DB_PATH = process.env.DB_PATH || path.join(__dirname, 'oracle_sports.db');

console.log(`\n═══════════════════════════════════════`);
console.log(`  ORACLE SPORTS — Database Migration`);
console.log(`═══════════════════════════════════════\n`);
console.log(`Database path: ${DB_PATH}\n`);

const db = new Database(DB_PATH);

// Enable WAL mode for concurrent reads during daemon writes
db.pragma('journal_mode = WAL');
db.pragma('foreign_keys = ON');

// ─────────────────────────────────────
// TABLE: articles
// ─────────────────────────────────────
db.exec(`
  CREATE TABLE IF NOT EXISTS articles (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    sport               TEXT NOT NULL,
    team_home           TEXT NOT NULL,
    team_away           TEXT NOT NULL,
    match_date          TEXT NOT NULL,
    headline            TEXT NOT NULL,
    headline_alt1       TEXT,
    headline_alt2       TEXT,
    subheadline         TEXT,
    body_html           TEXT NOT NULL,
    prediction_winner   TEXT,
    prediction_bet      TEXT,
    confidence_pct      INTEGER,
    odds_home           REAL,
    odds_away           REAL,
    odds_draw           REAL,
    edge_summary        TEXT,
    hero_image_url      TEXT,
    hero_image_local    TEXT,
    image_source        TEXT,
    audio_path          TEXT,
    source_urls         TEXT DEFAULT '[]',
    source_domains      TEXT DEFAULT '[]',
    status              TEXT DEFAULT 'published',
    resolved            INTEGER DEFAULT 0,
    prediction_correct  INTEGER,
    aftermath_html      TEXT,
    published_at        TEXT DEFAULT (datetime('now')),
    match_resolved_at   TEXT,
    reading_time_mins   INTEGER,
    tags                TEXT DEFAULT '[]',
    views               INTEGER DEFAULT 0
  );
`);

console.log('✓ Created table: articles');

// ─────────────────────────────────────
// TABLE: raw_articles
// ─────────────────────────────────────
db.exec(`
  CREATE TABLE IF NOT EXISTS raw_articles (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    sport               TEXT,
    source_url          TEXT UNIQUE,
    source_domain       TEXT,
    title               TEXT,
    summary             TEXT,
    full_text           TEXT,
    og_image            TEXT,
    pub_date            TEXT,
    matched_article_id  INTEGER,
    fetched_at          TEXT DEFAULT (datetime('now')),
    processed           INTEGER DEFAULT 0
  );
`);

console.log('✓ Created table: raw_articles');

// ─────────────────────────────────────
// TABLE: matches_queue
// ─────────────────────────────────────
db.exec(`
  CREATE TABLE IF NOT EXISTS matches_queue (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    sport               TEXT,
    team_home           TEXT,
    team_away           TEXT,
    match_date          TEXT,
    league              TEXT,
    odds_home           REAL,
    odds_away           REAL,
    odds_draw           REAL,
    status              TEXT DEFAULT 'pending',
    article_id          INTEGER,
    prediction_winner   TEXT,
    confidence_pct      INTEGER,
    prediction_bet      TEXT,
    edge_summary        TEXT,
    queued_at           TEXT DEFAULT (datetime('now'))
  );
`);

console.log('✓ Created table: matches_queue');

// ─────────────────────────────────────
// INDEXES for query performance
// ─────────────────────────────────────
db.exec(`
  CREATE INDEX IF NOT EXISTS idx_articles_sport ON articles(sport);
  CREATE INDEX IF NOT EXISTS idx_articles_status ON articles(status);
  CREATE INDEX IF NOT EXISTS idx_articles_resolved ON articles(resolved);
  CREATE INDEX IF NOT EXISTS idx_articles_published ON articles(published_at);
  CREATE INDEX IF NOT EXISTS idx_articles_confidence ON articles(confidence_pct DESC);
  CREATE INDEX IF NOT EXISTS idx_raw_articles_processed ON raw_articles(processed);
  CREATE INDEX IF NOT EXISTS idx_raw_articles_source ON raw_articles(source_url);
  CREATE INDEX IF NOT EXISTS idx_matches_status ON matches_queue(status);
  CREATE INDEX IF NOT EXISTS idx_matches_date ON matches_queue(match_date);
`);

console.log('✓ Created indexes');

db.close();

console.log(`\n═══════════════════════════════════════`);
console.log(`  Migration complete.`);
console.log(`═══════════════════════════════════════\n`);
