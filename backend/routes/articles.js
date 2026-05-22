import { Router } from 'express';
import Fuse from 'fuse.js';
import { stmts } from '../db.js';

const router = Router();

// ─────────────────────────────────────
// GET /api/articles — Paginated article list
// ─────────────────────────────────────
router.get('/', (req, res) => {
  try {
    const page = Math.max(1, parseInt(req.query.page) || 1);
    const limit = Math.min(50, Math.max(1, parseInt(req.query.limit) || 12));
    const offset = (page - 1) * limit;
    const sport = req.query.sport;

    let articles, total;

    if (sport) {
      articles = stmts.getArticlesBySport.all(sport, limit, offset);
      total = stmts.countArticlesBySport.get(sport).total;
    } else {
      articles = stmts.getArticles.all(limit, offset);
      total = stmts.countArticles.get().total;
    }

    // Parse JSON fields
    articles = articles.map(a => ({
      ...a,
      tags: safeJsonParse(a.tags, []),
      source_urls: undefined,
      source_domains: undefined,
    }));

    res.json({
      articles,
      total,
      page,
      limit,
      totalPages: Math.ceil(total / limit),
    });
  } catch (err) {
    console.error('Error fetching articles:', err);
    res.status(500).json({ error: 'Failed to fetch articles' });
  }
});

// ─────────────────────────────────────
// GET /api/articles/news — Aggregated RSS News
// ─────────────────────────────────────
router.get('/news', (req, res) => {
  try {
    const page = Math.max(1, parseInt(req.query.page) || 1);
    const limit = Math.min(100, Math.max(1, parseInt(req.query.limit) || 20));
    const offset = (page - 1) * limit;
    const sport = req.query.sport;

    let news = [];
    if (sport) {
      news = stmts.getRecentRawArticlesBySport.all(sport, limit, offset);
    } else {
      news = stmts.getRecentRawArticles.all(limit, offset);
    }
    
    // De-duplicate by title/URL just in case
    const uniqueNews = [];
    const seen = new Set();
    for (const item of news) {
      if (!seen.has(item.source_url) && !seen.has(item.title)) {
        seen.add(item.source_url);
        seen.add(item.title);
        uniqueNews.push(item);
      }
    }

    res.json({ news: uniqueNews });
  } catch (err) {
    console.error('Error fetching news wire:', err);
    res.status(500).json({ error: 'Failed to fetch news' });
  }
});

// ─────────────────────────────────────
// GET /api/articles/search?q= — Fuzzy search
// ─────────────────────────────────────
router.get('/search', (req, res) => {
  try {
    const query = req.query.q;
    if (!query || query.length < 2) {
      return res.json({ results: [] });
    }

    const allArticles = stmts.getAllArticlesForSearch.all();

    const fuse = new Fuse(allArticles, {
      keys: [
        { name: 'headline', weight: 0.4 },
        { name: 'team_home', weight: 0.25 },
        { name: 'team_away', weight: 0.25 },
        { name: 'sport', weight: 0.1 },
      ],
      threshold: 0.4,
      includeScore: true,
    });

    const results = fuse.search(query, { limit: 20 }).map(r => ({
      ...r.item,
      tags: safeJsonParse(r.item.tags, []),
      score: r.score,
    }));

    res.json({ results });
  } catch (err) {
    console.error('Error searching articles:', err);
    res.status(500).json({ error: 'Search failed' });
  }
});

// ─────────────────────────────────────
// GET /api/articles/sport/:sport — Articles by sport
// ─────────────────────────────────────
router.get('/sport/:sport', (req, res) => {
  try {
    const { sport } = req.params;
    const page = Math.max(1, parseInt(req.query.page) || 1);
    const limit = Math.min(50, Math.max(1, parseInt(req.query.limit) || 12));
    const offset = (page - 1) * limit;
    const filter = req.query.filter; // 'upcoming', 'resolved', 'all'

    let articles = stmts.getArticlesBySport.all(sport, limit, offset);
    const total = stmts.countArticlesBySport.get(sport).total;

    // Apply resolution filter
    if (filter === 'upcoming') {
      articles = articles.filter(a => a.resolved === 0);
    } else if (filter === 'resolved') {
      articles = articles.filter(a => a.resolved === 1);
    }

    articles = articles.map(a => ({
      ...a,
      tags: safeJsonParse(a.tags, []),
    }));

    res.json({
      articles,
      total,
      page,
      limit,
      sport,
      totalPages: Math.ceil(total / limit),
    });
  } catch (err) {
    console.error('Error fetching sport articles:', err);
    res.status(500).json({ error: 'Failed to fetch sport articles' });
  }
});

// ─────────────────────────────────────
// GET /api/articles/:id — Single article
// ─────────────────────────────────────
router.get('/:id', (req, res) => {
  try {
    const id = parseInt(req.params.id);
    if (isNaN(id)) {
      return res.status(400).json({ error: 'Invalid article ID' });
    }

    const article = stmts.getArticleById.get(id);
    if (!article) {
      return res.status(404).json({ error: 'Article not found' });
    }

    // Increment view count
    stmts.incrementViews.run(id);

    // Parse JSON fields
    article.tags = safeJsonParse(article.tags, []);
    article.source_urls = safeJsonParse(article.source_urls, []);
    article.source_domains = safeJsonParse(article.source_domains, []);

    // Get related articles
    const related = stmts.getRelatedArticles.all(id, article.sport).map(a => ({
      ...a,
      tags: safeJsonParse(a.tags, []),
    }));

    res.json({ article, related });
  } catch (err) {
    console.error('Error fetching article:', err);
    res.status(500).json({ error: 'Failed to fetch article' });
  }
});

// ─────────────────────────────────────
// GET /api/leaderboard — Top predictions
// ─────────────────────────────────────
router.get('/meta/leaderboard', (req, res) => {
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

// ─────────────────────────────────────
// Helper: Safe JSON parse
// ─────────────────────────────────────
function safeJsonParse(str, fallback) {
  if (!str) return fallback;
  try {
    return JSON.parse(str);
  } catch {
    return fallback;
  }
}

export default router;
