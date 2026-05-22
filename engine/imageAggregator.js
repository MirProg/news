import axios from 'axios';
import sharp from 'sharp';
import fs from 'fs';
import path from 'path';
import crypto from 'crypto';
import { fileURLToPath } from 'url';
import dotenv from 'dotenv';
import logger from './logger.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
dotenv.config({ path: path.join(__dirname, '..', '.env') });

const CACHE_DIR = process.env.IMAGE_CACHE_DIR || path.join(__dirname, '..', 'imageCache');
const SD_API_URL = process.env.SD_API_URL || 'http://localhost:7860';
const TARGET_WIDTH = 1200;
const TARGET_HEIGHT = 630;

// Ensure cache directory exists
if (!fs.existsSync(CACHE_DIR)) {
  fs.mkdirSync(CACHE_DIR, { recursive: true });
}

/**
 * Download and resize an image to standard hero dimensions
 */
async function downloadAndResize(imageUrl, filename = null) {
  try {
    const hash = filename || crypto.createHash('md5').update(imageUrl).digest('hex');
    const outputPath = path.join(CACHE_DIR, `${hash}.jpg`);

    // Check if already cached
    if (fs.existsSync(outputPath)) {
      logger.info(`Image cached: ${hash}.jpg`);
      return outputPath;
    }

    const response = await axios.get(imageUrl, {
      responseType: 'arraybuffer',
      timeout: 15000,
      headers: {
        'User-Agent': 'Mozilla/5.0 (compatible; OracleSportsBot/1.0)',
      },
      maxRedirects: 5,
    });

    // Resize to standard hero dimensions
    await sharp(Buffer.from(response.data))
      .resize(TARGET_WIDTH, TARGET_HEIGHT, {
        fit: 'cover',
        position: 'center',
      })
      .jpeg({ quality: 85 })
      .toFile(outputPath);

    logger.info(`Image saved: ${hash}.jpg (${TARGET_WIDTH}x${TARGET_HEIGHT})`);
    return outputPath;
  } catch (err) {
    logger.warn(`Image download failed for ${imageUrl}: ${err.message}`);
    return null;
  }
}

/**
 * Search Wikimedia Commons for a relevant image
 */
async function searchWikimedia(query) {
  try {
    const { data } = await axios.get('https://commons.wikimedia.org/w/api.php', {
      params: {
        action: 'query',
        list: 'search',
        srsearch: query,
        srnamespace: 6,
        format: 'json',
        srlimit: 5,
      },
      timeout: 8000,
    });

    const results = data?.query?.search || [];
    if (results.length === 0) return null;

    // Get image URL for first result
    const title = results[0].title;
    const imageInfoResp = await axios.get('https://commons.wikimedia.org/w/api.php', {
      params: {
        action: 'query',
        titles: title,
        prop: 'imageinfo',
        iiprop: 'url',
        format: 'json',
      },
      timeout: 8000,
    });

    const pages = imageInfoResp.data?.query?.pages || {};
    const page = Object.values(pages)[0];
    return page?.imageinfo?.[0]?.url || null;
  } catch (err) {
    logger.warn(`Wikimedia search failed: ${err.message}`);
    return null;
  }
}

/**
 * Generate image with AUTOMATIC1111 Stable Diffusion (if running)
 */
async function generateWithSD(teamHome, teamAway, sport) {
  try {
    // Check if A1111 is running
    await axios.get(`${SD_API_URL}/sdapi/v1/sd-models`, { timeout: 3000 });

    const prompt = `${teamHome} vs ${teamAway} ${sport} stadium atmosphere, dramatic cinematic lighting, fog, dark, photorealistic, 8k`;
    const negativePrompt = 'text, watermark, cartoon, low quality, blurry';

    const { data } = await axios.post(`${SD_API_URL}/sdapi/v1/txt2img`, {
      prompt,
      negative_prompt: negativePrompt,
      steps: 20,
      cfg_scale: 7,
      width: TARGET_WIDTH,
      height: TARGET_HEIGHT,
      sampler_name: 'DPM++ 2M Karras',
    }, { timeout: 120000 });

    if (data.images?.[0]) {
      const hash = crypto.createHash('md5').update(prompt).digest('hex');
      const outputPath = path.join(CACHE_DIR, `sd_${hash}.jpg`);
      const buffer = Buffer.from(data.images[0], 'base64');
      fs.writeFileSync(outputPath, buffer);
      logger.info(`SD image generated: sd_${hash}.jpg`);
      return outputPath;
    }
    return null;
  } catch {
    logger.info('Stable Diffusion not available, skipping');
    return null;
  }
}

/**
 * Build Unsplash fallback URL
 */
function getUnsplashUrl(sport, teamHome) {
  const keywords = `${sport},stadium,atmosphere,night`;
  return `https://source.unsplash.com/1200x630/?${encodeURIComponent(keywords)}`;
}

/**
 * Main image acquisition pipeline with priority chain:
 * 1. Scraped og:image
 * 2. Wikimedia Commons
 * 3. AUTOMATIC1111 SD
 * 4. Unsplash fallback
 */
async function acquireImage(options = {}) {
  const { scrapedImages = [], teamHome, teamAway, sport } = options;

  // 1. Try scraped og:images
  for (const imgUrl of scrapedImages) {
    if (!imgUrl || !imgUrl.startsWith('http')) continue;
    const localPath = await downloadAndResize(imgUrl);
    if (localPath) {
      return { path: localPath, source: 'scraped', url: imgUrl };
    }
  }

  // 2. Try Wikimedia Commons
  const wikiQuery = `${teamHome} ${sport} stadium`;
  const wikiUrl = await searchWikimedia(wikiQuery);
  if (wikiUrl) {
    const localPath = await downloadAndResize(wikiUrl);
    if (localPath) {
      return { path: localPath, source: 'wikimedia', url: wikiUrl };
    }
  }

  // 3. Try AUTOMATIC1111 Stable Diffusion
  const sdPath = await generateWithSD(teamHome, teamAway, sport);
  if (sdPath) {
    return { path: sdPath, source: 'stable-diffusion', url: null };
  }

  // 4. Unsplash fallback
  const unsplashUrl = getUnsplashUrl(sport, teamHome);
  const localPath = await downloadAndResize(unsplashUrl);
  if (localPath) {
    return { path: localPath, source: 'unsplash', url: unsplashUrl };
  }

  logger.warn(`Image acquisition failed for ${teamHome} vs ${teamAway}`);
  return { path: null, source: null, url: null };
}

export { acquireImage, downloadAndResize };
