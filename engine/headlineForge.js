import { callHeadline } from './ollamaClient.js';
import logger from './logger.js';

// Strong editorial words that score higher
const STRONG_WORDS = [
  'why', 'how', 'inside', 'truth', 'secret', 'rising', 'turning',
  'defining', 'moment', 'story', 'behind', 'making', 'breaking',
  'evolution', 'revolution', 'quiet', 'brilliant', 'remarkable',
  'fascinating', 'underrated', 'overlooked', 'problem', 'answer',
  'change', 'era', 'legacy', 'identity', 'resurgence',
];

/**
 * Generate 3 headline variants using phi3.5
 */
async function forgeHeadlines(teamHome, teamAway, sport, prediction, subheadline) {
  const systemPrompt = `You are a headline writer for Oracle Sports, a premium sports news site. You write headlines that are compelling, specific, and make readers want to click — like The Athletic, ESPN, or Grantland.

HEADLINE RULES:
- Each headline must be 8-14 words
- Use colons (:) or em dashes (—) for structure
- NEVER use "vs." or scores
- NEVER use the word "clash" as a noun
- NEVER start with a rhetorical question
- Focus on the STORY, not the prediction — the human drama, the tactical intrigue, the form crisis
- Reference specific teams, players, or situations
- Be vivid and specific, not generic

EXAMPLES OF GREAT HEADLINES:
"Inside Arsenal's Quiet Revolution — And Why This Weekend Tests It"
"The Saka Question: How One Player's Form Reshapes the Title Race"
"Why This Derby Feels Different: The Numbers Behind City's Slump"
"Arteta's Chess Match: The Tactical Battle That Could Define May"
"The Underrated Stat That Explains Liverpool's Home Dominance"

Output EXACTLY 3 headlines, one per line. No numbering, no quotes, no explanation.`;

  const userPrompt = `Generate 3 compelling headlines for:
Sport: ${sport}
Home: ${teamHome}
Away: ${teamAway}
Prediction: ${prediction.predicted_winner} to win (confidence: ${prediction.confidence_pct}%)
Context: ${subheadline || ''}`;

  try {
    const response = await callHeadline([
      { role: 'system', content: systemPrompt },
      { role: 'user', content: userPrompt },
    ]);

    const lines = response
      .split('\n')
      .map(l => l.replace(/^\d+[\.)\]]\s*/, '').replace(/^["']|["']$/g, '').trim())
      .filter(l => l.length > 10 && l.length < 150);

    while (lines.length < 3) {
      lines.push(`${teamHome} vs ${teamAway}: What the Numbers Tell Us About ${sport}`);
    }

    const scored = lines.slice(0, 3).map(h => ({
      headline: h,
      score: scoreHeadline(h),
    }));

    scored.sort((a, b) => b.score - a.score);

    const result = {
      best: scored[0].headline,
      alt1: scored[1]?.headline || scored[0].headline,
      alt2: scored[2]?.headline || scored[0].headline,
      scores: scored.map(s => ({ headline: s.headline, score: s.score })),
    };

    logger.info(`Headlines forged: "${result.best}" (score: ${scored[0].score})`);
    return result;
  } catch (err) {
    logger.error(`Headline generation failed: ${err.message}`);

    const fallback = `${teamHome} vs ${teamAway}: The Story Behind This ${sport} Showdown`;
    return {
      best: fallback,
      alt1: `Why ${teamHome}'s Form Makes This ${sport} Match Fascinating`,
      alt2: `Inside the Numbers: Our Take on ${teamHome} vs ${teamAway}`,
      scores: [],
    };
  }
}

/**
 * Score a headline for quality
 */
function scoreHeadline(headline) {
  let score = 50;

  const words = headline.split(/\s+/).length;
  if (words >= 8 && words <= 14) score += 20;
  else if (words >= 6 && words <= 16) score += 10;
  else score -= 10;

  const lower = headline.toLowerCase();
  for (const word of STRONG_WORDS) {
    if (lower.includes(word)) score += 5;
  }

  if (headline.includes('—') || headline.includes(':')) score += 10;

  // Penalize clichés
  if (lower.includes('clash')) score -= 30;
  if (lower.includes('vs.') || lower.includes('vs ')) score -= 20;
  if (lower.includes('?')) score -= 15;
  if (lower.includes('exciting') || lower.includes('must-watch')) score -= 25;
  if (lower.includes('oracle') || lower.includes('augury') || lower.includes('abyss')) score -= 20;

  return score;
}

export { forgeHeadlines, scoreHeadline };
