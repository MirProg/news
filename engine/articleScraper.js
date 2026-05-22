import axios from 'axios';
import * as cheerio from 'cheerio';
import { JSDOM } from 'jsdom';
import { Readability } from '@mozilla/readability';
import logger from './logger.js';

const USER_AGENT = 'Mozilla/5.0 (compatible; OracleSportsBot/1.0; +https://oraclesports.ai)';
const MAX_TEXT_LENGTH = 3000;

/**
 * Scrape a single article URL for full text and og:image
 */
async function scrapeArticle(url) {
  try {
    const { data } = await axios.get(url, {
      headers: {
        'User-Agent': USER_AGENT,
        'Accept': 'text/html,application/xhtml+xml',
        'Accept-Language': 'en-GB,en;q=0.9',
      },
      timeout: 10000,
      maxRedirects: 5,
    });

    // Extract og:image and og:title with cheerio
    const $ = cheerio.load(data);
    const ogImage = $('meta[property="og:image"]').attr('content')
      || $('meta[name="og:image"]').attr('content')
      || $('meta[property="twitter:image"]').attr('content')
      || null;

    const ogTitle = $('meta[property="og:title"]').attr('content')
      || $('meta[name="og:title"]').attr('content')
      || $('title').text()
      || null;

    // Extract full readable text with Readability
    const dom = new JSDOM(data, { url });
    const reader = new Readability(dom.window.document);
    const parsed = reader.parse();

    const fullText = parsed?.textContent?.slice(0, MAX_TEXT_LENGTH) || '';

    return {
      title: ogTitle || parsed?.title || '',
      text: fullText,
      image: ogImage,
      source: new URL(url).hostname.replace('www.', ''),
      url,
      success: true,
    };
  } catch (err) {
    logger.warn(`Scrape failed for ${url}: ${err.message}`);
    return {
      title: '',
      text: '',
      image: null,
      source: '',
      url,
      success: false,
    };
  }
}

/**
 * Scrape multiple articles for a match context
 */
async function scrapeMatchArticles(rawArticles) {
  const results = [];
  const images = [];

  for (const raw of rawArticles.slice(0, 5)) {
    if (!raw.source_url) continue;

    const scraped = await scrapeArticle(raw.source_url);
    if (scraped.success) {
      results.push(scraped);
      if (scraped.image) {
        images.push(scraped.image);
      }
    }

    // Polite delay between requests
    await new Promise(r => setTimeout(r, 1000));
  }

  logger.info(`Scraped ${results.length}/${rawArticles.length} articles, found ${images.length} images`);

  return {
    articles: results,
    images,
    bestImage: images[0] || null,
  };
}

export { scrapeArticle, scrapeMatchArticles };
