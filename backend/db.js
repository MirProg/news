import Database from 'better-sqlite3';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const DB_PATH = process.env.DB_PATH || path.join(__dirname, '..', 'db', 'oracle_sports.db');

const db = new Database(DB_PATH);
db.pragma('journal_mode = WAL');
db.pragma('foreign_keys = ON');

// ─────────────────────────────────────
// Prepared Statements — Articles
// ─────────────────────────────────────

const stmts = {
  getArticles: db.prepare(`
    SELECT id, sport, team_home, team_away, match_date, headline, subheadline,
           prediction_winner, confidence_pct, odds_home, odds_away, odds_draw,
           hero_image_url, hero_image_local, status, resolved, prediction_correct,
           published_at, reading_time_mins, tags, views
    FROM articles
    WHERE status = 'published'
    ORDER BY published_at DESC
    LIMIT ? OFFSET ?
  `),

  getArticlesBySport: db.prepare(`
    SELECT id, sport, team_home, team_away, match_date, headline, subheadline,
           prediction_winner, confidence_pct, odds_home, odds_away, odds_draw,
           hero_image_url, hero_image_local, status, resolved, prediction_correct,
           published_at, reading_time_mins, tags, views
    FROM articles
    WHERE status = 'published' AND sport = ?
    ORDER BY published_at DESC
    LIMIT ? OFFSET ?
  `),

  getArticleById: db.prepare(`
    SELECT * FROM articles WHERE id = ?
  `),

  countArticles: db.prepare(`
    SELECT COUNT(*) as total FROM articles WHERE status = 'published'
  `),

  countArticlesBySport: db.prepare(`
    SELECT COUNT(*) as total FROM articles WHERE status = 'published' AND sport = ?
  `),

  searchArticles: db.prepare(`
    SELECT id, sport, team_home, team_away, match_date, headline, subheadline,
           prediction_winner, confidence_pct, hero_image_url, hero_image_local,
           published_at, reading_time_mins, tags
    FROM articles
    WHERE status = 'published'
    ORDER BY published_at DESC
    LIMIT 100
  `),

  getLeaderboard: db.prepare(`
    SELECT id, sport, team_home, team_away, headline, confidence_pct,
           prediction_winner, resolved, prediction_correct
    FROM articles
    WHERE status = 'published' AND confidence_pct IS NOT NULL
    ORDER BY confidence_pct DESC
    LIMIT 5
  `),

  getOracleRecord: db.prepare(`
    SELECT
      COUNT(*) as total,
      SUM(CASE WHEN prediction_correct = 1 THEN 1 ELSE 0 END) as correct
    FROM articles
    WHERE resolved = 1
  `),

  getRelatedArticles: db.prepare(`
    SELECT id, sport, team_home, team_away, headline, subheadline,
           confidence_pct, hero_image_url, hero_image_local, published_at,
           reading_time_mins
    FROM articles
    WHERE status = 'published' AND id != ? AND sport = ?
    ORDER BY published_at DESC
    LIMIT 3
  `),

  incrementViews: db.prepare(`
    UPDATE articles SET views = views + 1 WHERE id = ?
  `),

  // ── Matches Queue ──
  getPendingMatches: db.prepare(`
    SELECT * FROM matches_queue WHERE status = 'pending' ORDER BY match_date ASC
  `),

  getUnresolvedArticles: db.prepare(`
    SELECT * FROM articles
    WHERE resolved = 0 AND match_date < datetime('now')
    ORDER BY match_date ASC
  `),

  insertArticle: db.prepare(`
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
  `),

  insertMatch: db.prepare(`
    INSERT OR IGNORE INTO matches_queue (sport, team_home, team_away, match_date, league, odds_home, odds_away, odds_draw)
    VALUES (@sport, @team_home, @team_away, @match_date, @league, @odds_home, @odds_away, @odds_draw)
  `),

  updateMatchStatus: db.prepare(`
    UPDATE matches_queue SET status = ?, article_id = ? WHERE id = ?
  `),

  insertRawArticle: db.prepare(`
    INSERT OR IGNORE INTO raw_articles (sport, source_url, source_domain, title, summary, og_image, pub_date, matched_article_id)
    VALUES (@sport, @source_url, @source_domain, @title, @summary, @og_image, @pub_date, @matched_article_id)
  `),

  getRawArticlesForMatch: db.prepare(`
    SELECT * FROM raw_articles WHERE matched_article_id = ? AND processed = 0
  `),

  markRawProcessed: db.prepare(`
    UPDATE raw_articles SET processed = 1, full_text = ? WHERE id = ?
  `),

  resolveArticle: db.prepare(`
    UPDATE articles
    SET resolved = 1, prediction_correct = ?, aftermath_html = ?, match_resolved_at = datetime('now')
    WHERE id = ?
  `),

  getMatchByTeams: db.prepare(`
    SELECT * FROM matches_queue
    WHERE team_home = ? AND team_away = ? AND match_date = ?
  `),

  getAllArticlesForSearch: db.prepare(`
    SELECT id, sport, team_home, team_away, headline, subheadline, tags
    FROM articles WHERE status = 'published'
    ORDER BY published_at DESC
  `),

  getRecentRawArticles: db.prepare(`
    SELECT id, sport, source_url, source_domain, title, summary, og_image, pub_date
    FROM raw_articles
    ORDER BY fetched_at DESC
    LIMIT ? OFFSET ?
  `),

  getRecentRawArticlesBySport: db.prepare(`
    SELECT id, sport, source_url, source_domain, title, summary, og_image, pub_date
    FROM raw_articles
    WHERE sport = ?
    ORDER BY fetched_at DESC
    LIMIT ? OFFSET ?
  `),
};

export { db, stmts };
export default db;
