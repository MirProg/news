import { callWriterWithFallback } from './ollamaClient.js';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import logger from './logger.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Load banned phrases
const BANNED_PATH = path.join(__dirname, '..', 'config', 'banned_phrases.json');
let bannedPhrases = [];
try {
  bannedPhrases = JSON.parse(fs.readFileSync(BANNED_PATH, 'utf-8'));
} catch {
  logger.warn('Could not load banned_phrases.json');
}

const MIN_WORDS = parseInt(process.env.MIN_ARTICLE_WORDS) || 900;
const MAX_RETRIES = 2;

/**
 * Oracle Sports editorial voice — warm, insightful sports journalism
 */
const ORACLE_SYSTEM_PROMPT = `You are a senior sports journalist at Oracle Sports, an AI-powered sports news publication known for exceptional storytelling and smart analysis. Your writing style blends the narrative depth of Grantland, the tactical insight of The Athletic, and the cultural awareness of modern sports journalism.

YOUR VOICE:
- Warm, vivid, and engaging — the reader should feel like they're sitting with a brilliant friend who happens to know everything about this sport
- Paint scenes: the atmosphere of the stadium, the body language of a player in their warm-up, the tension in a rivalry
- Use metaphors from cinema, music, literature, history — but keep them natural, never forced
- Stats are important but they serve the narrative. A number without context is noise. A number with a story is revelation
- Show genuine passion for the sport. This is not cold analysis — it's journalism that cares
- Be specific. Name actual plays, real patterns, concrete moments from recent matches
- Have a point of view. Don't hedge everything. Be willing to say something bold and explain why

ARTICLE STRUCTURE — follow this closely:

## Setting the Scene
(~200 words) Open with atmosphere and narrative. What makes this particular matchup fascinating right now? Connect recent form to a human story — a manager under pressure, a striker finding their rhythm, a team's identity shift. Use real facts from the context.

## By the Numbers
(~300 words) The statistical picture, but told as a story. Don't just list xG and possession — explain what those numbers actually mean in the context of how these teams play. Compare styles, identify mismatches, highlight the stat that tells a story no one is talking about. Example: "Arsenal's 72% possession at home sounds dominant until you realize Aston Villa have scored 68% of their away goals on the counter this season."

## Players to Watch
(~250 words) 2-3 player spotlights as character portraits. What makes this player interesting right now? Recent form, personal narrative, tactical role. The reader should understand not just what they do, but who they are in this moment.

## Our Prediction
(~200 words) State the prediction clearly and explain the reasoning. Be honest about confidence level — don't oversell it. Include the key insight: the one factor that tips the balance. Use language like: "We think..." / "The numbers lean toward..." / "Here's what tips the balance..." This should feel like expert analysis from someone you trust, not a gambling tip.

## Final Thought
(~100 words) A closing observation that zooms out. Connect this match to a bigger picture — a title race, a player's legacy, a tactical trend reshaping the sport. End with a sentence that makes the reader think.

RULES:
- Write minimum 900 words, maximum 1400 words
- Use at least 4 section headings with ## markers
- Include at least one blockquote pull quote (> format)
- Name specific players with character-study detail
- NEVER use: "must-watch", "both teams", "exciting match", "fans are in for", "everything to play for", "bounce back", "hit the ground running", "at the end of the day", "clash" as a noun, "six-pointer", "crucial encounter"
- NEVER start with a rhetorical question
- NEVER write bullet-point summaries
- Every sentence must earn its place — no filler
- The tone is smart, warm, and confident — never cold, never pretentious, never like a betting preview`;

/**
 * Generate a full Oracle article from match context
 */
async function generateArticle(contextString) {
  const userPrompt = `Using the match context below, write a complete Oracle Sports article following the exact structure specified. Write the full article now.\n\n${contextString}`;

  let lastError = null;

  for (let attempt = 0; attempt <= MAX_RETRIES; attempt++) {
    try {
      if (attempt > 0) {
        logger.info(`Writer retry ${attempt}/${MAX_RETRIES}`);
      }

      const result = await callWriterWithFallback([
        { role: 'system', content: ORACLE_SYSTEM_PROMPT },
        { role: 'user', content: userPrompt },
      ]);

      const content = result.content;
      const model = result.model;

      // Run quality gates
      const quality = checkQuality(content);

      if (quality.passed) {
        logger.info(`Article generated: ${quality.wordCount} words via ${model}`);

        // Extract subheadline (first non-heading paragraph)
        const lines = content.split('\n').filter(l => l.trim());
        const subheadline = lines.find(l => !l.startsWith('#') && l.length > 30)?.trim() || '';

        return {
          body: content,
          subheadline: subheadline.slice(0, 200),
          wordCount: quality.wordCount,
          model,
          passed: true,
        };
      } else {
        logger.warn(`Quality gate failed (attempt ${attempt + 1}): ${quality.failures.join(', ')}`);
        lastError = `Quality: ${quality.failures.join(', ')}`;
      }
    } catch (err) {
      lastError = err.message;
      logger.error(`Writer attempt ${attempt + 1} failed: ${err.message}`);
    }
  }

  logger.error(`Article generation failed after ${MAX_RETRIES + 1} attempts: ${lastError}`);
  return {
    body: null,
    subheadline: null,
    wordCount: 0,
    model: null,
    passed: false,
    error: lastError,
  };
}

/**
 * Quality gate checks
 */
function checkQuality(content) {
  const failures = [];

  // Word count
  const plainText = content.replace(/[#*_>\[\]()]/g, '').trim();
  const wordCount = plainText.split(/\s+/).length;
  if (wordCount < MIN_WORDS) {
    failures.push(`Word count ${wordCount} < ${MIN_WORDS}`);
  }

  // Section headings (## markers)
  const headings = (content.match(/^##\s/gm) || []).length;
  if (headings < 4) {
    failures.push(`Only ${headings} section headings (need 4+)`);
  }

  // Banned phrases
  const lowerContent = content.toLowerCase();
  for (const phrase of bannedPhrases) {
    if (lowerContent.includes(phrase.toLowerCase())) {
      failures.push(`Banned phrase: "${phrase}"`);
    }
  }

  return {
    passed: failures.length === 0,
    failures,
    wordCount,
    headingCount: headings,
  };
}

/**
 * Generate aftermath text for a resolved match
 */
async function generateAftermath(headline, predictionWinner, confidencePct, actualResult) {
  const wasCorrect = actualResult.winner?.toLowerCase() === predictionWinner?.toLowerCase();

  const systemPrompt = `${ORACLE_SYSTEM_PROMPT}

You are now writing a post-match follow-up section called "After the Final Whistle."
Write approximately 250 words in the same warm, insightful journalism style.
${wasCorrect
    ? 'Our prediction was correct. Explain what played out as expected and what the result means going forward. Be gracious, not smug.'
    : 'Our prediction was wrong. Be honest about what we missed. What surprised us? What can we learn from getting this one wrong? Sports is humbling — show that humility.'
  }`;

  const userPrompt = `ORIGINAL HEADLINE: ${headline}
OUR PREDICTION: ${predictionWinner} (Confidence: ${confidencePct}%)
ACTUAL RESULT: ${actualResult.home_team} ${actualResult.home_score} - ${actualResult.away_score} ${actualResult.away_team}
WINNER: ${actualResult.winner}

Write the follow-up section now.`;

  try {
    const result = await callWriterWithFallback([
      { role: 'system', content: systemPrompt },
      { role: 'user', content: userPrompt },
    ]);

    return result.content;
  } catch (err) {
    logger.error(`Aftermath generation failed: ${err.message}`);
    return wasCorrect
      ? '<p>Our analysis played out as expected. The key factors we identified proved decisive.</p>'
      : '<p>This one didn\'t go as we predicted. Sports has a way of reminding us that no model captures everything. We\'ll learn from this.</p>';
  }
}

export { generateArticle, generateAftermath, checkQuality };
