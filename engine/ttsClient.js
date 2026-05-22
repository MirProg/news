import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import dotenv from 'dotenv';
import logger from './logger.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
dotenv.config({ path: path.join(__dirname, '..', '.env') });

const KOKORO_URL = process.env.KOKORO_URL || 'http://localhost:8880';
const AUDIO_DIR = process.env.AUDIO_DIR || path.join(__dirname, '..', 'backend', 'public', 'audio');

// Ensure audio directory exists
if (!fs.existsSync(AUDIO_DIR)) {
  fs.mkdirSync(AUDIO_DIR, { recursive: true });
}

/**
 * Strip HTML tags from article body to get plain text for TTS
 */
function stripHtml(html) {
  return html
    .replace(/<[^>]*>/g, '')
    .replace(/&nbsp;/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/\s+/g, ' ')
    .trim();
}

/**
 * Generate TTS audio for an article using Kokoro FastAPI
 */
async function generateAudio(articleId, bodyHtml) {
  const outputPath = path.join(AUDIO_DIR, `${articleId}.mp3`);

  // Check if already generated
  if (fs.existsSync(outputPath)) {
    logger.info(`Audio already exists: ${articleId}.mp3`);
    return `/audio/${articleId}.mp3`;
  }

  // Strip HTML to plain text
  const plainText = stripHtml(bodyHtml);

  if (plainText.length < 100) {
    logger.warn(`Article ${articleId} text too short for TTS (${plainText.length} chars)`);
    return null;
  }

  try {
    // Check if Kokoro is running
    const healthCheck = await fetch(`${KOKORO_URL}/docs`, {
      signal: AbortSignal.timeout(3000),
    });

    if (!healthCheck.ok) {
      logger.warn('Kokoro TTS not available');
      return null;
    }

    logger.info(`Generating TTS for article ${articleId} (${plainText.length} chars)`);

    const response = await fetch(`${KOKORO_URL}/v1/audio/speech`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: 'kokoro',
        input: plainText.slice(0, 10000), // Cap at 10k chars for TTS
        voice: 'am_michael',
        response_format: 'mp3',
        speed: 0.95,
      }),
      signal: AbortSignal.timeout(300000), // 5-minute timeout for long articles
    });

    if (!response.ok) {
      const errText = await response.text();
      throw new Error(`Kokoro error ${response.status}: ${errText}`);
    }

    const buffer = await response.arrayBuffer();
    fs.writeFileSync(outputPath, Buffer.from(buffer));

    const sizeMB = (Buffer.from(buffer).length / 1024 / 1024).toFixed(2);
    logger.info(`TTS audio saved: ${articleId}.mp3 (${sizeMB} MB)`);

    return `/audio/${articleId}.mp3`;
  } catch (err) {
    logger.error(`TTS generation failed for article ${articleId}: ${err.message}`);
    return null;
  }
}

export { generateAudio, stripHtml };
