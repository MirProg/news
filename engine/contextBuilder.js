import logger from './logger.js';

/**
 * Build the full match context string from all data sources.
 * This is the structured prompt sent to the AI writer model.
 */
function buildContext(options = {}) {
  const {
    sport = '',
    league = '',
    teamHome = '',
    teamAway = '',
    matchDate = '',
    venue = '',
    oddsHome = null,
    oddsDraw = null,
    oddsAway = null,
    homeForm = null,
    awayForm = null,
    headToHead = [],
    homeStats = {},
    awayStats = {},
    keyPlayers = [],
    injuries = [],
    scrapedArticles = [],
    prediction = {},
    styleExamples = [],
  } = options;

  // Calculate implied probabilities from odds
  const impliedHome = oddsHome ? ((1 / oddsHome) * 100).toFixed(1) : 'N/A';
  const impliedAway = oddsAway ? ((1 / oddsAway) * 100).toFixed(1) : 'N/A';
  const impliedDraw = oddsDraw ? ((1 / oddsDraw) * 100).toFixed(1) : 'N/A';

  let ctx = '';

  ctx += `══════════════════════════════════════\n`;
  ctx += `MATCH CONTEXT FOR ORACLE ARTICLE\n`;
  ctx += `══════════════════════════════════════\n\n`;

  ctx += `SPORT: ${sport}\n`;
  ctx += `COMPETITION: ${league}\n`;
  ctx += `HOME TEAM: ${teamHome}\n`;
  ctx += `AWAY TEAM: ${teamAway}\n`;
  ctx += `MATCH DATE: ${matchDate}\n`;
  if (venue) ctx += `VENUE: ${venue}\n`;

  ctx += `\nODDS:\n`;
  ctx += `Home Win: ${oddsHome || 'N/A'} | Draw: ${oddsDraw || 'N/A'} | Away Win: ${oddsAway || 'N/A'}\n`;
  ctx += `Implied probabilities — Home: ${impliedHome}% | Draw: ${impliedDraw}% | Away: ${impliedAway}%\n`;

  // Recent form
  ctx += `\nRECENT FORM:\n`;
  if (homeForm) {
    ctx += `${teamHome}: ${homeForm.form || 'N/A'}`;
    if (homeForm.wins !== undefined) ctx += ` (W${homeForm.wins} D${homeForm.draws || 0} L${homeForm.losses || 0})`;
    ctx += `\n`;
  } else {
    ctx += `${teamHome}: Form data unavailable\n`;
  }
  if (awayForm) {
    ctx += `${teamAway}: ${awayForm.form || 'N/A'}`;
    if (awayForm.wins !== undefined) ctx += ` (W${awayForm.wins} D${awayForm.draws || 0} L${awayForm.losses || 0})`;
    ctx += `\n`;
  } else {
    ctx += `${teamAway}: Form data unavailable\n`;
  }

  // Head to head
  if (headToHead.length > 0) {
    ctx += `\nHEAD TO HEAD (recent meetings):\n`;
    for (const h2h of headToHead.slice(0, 5)) {
      ctx += `${h2h.date || 'Date unknown'}: ${h2h.result || 'Unknown'}\n`;
    }
  }

  // Key statistics
  ctx += `\nKEY STATISTICS:\n`;
  ctx += `${teamHome} — `;
  ctx += Object.entries(homeStats).map(([k, v]) => `${k}: ${v}`).join(' | ') || 'Stats unavailable';
  ctx += `\n`;
  ctx += `${teamAway} — `;
  ctx += Object.entries(awayStats).map(([k, v]) => `${k}: ${v}`).join(' | ') || 'Stats unavailable';
  ctx += `\n`;

  // Key players
  if (keyPlayers.length > 0) {
    ctx += `\nKEY PLAYERS TO WATCH:\n`;
    for (const player of keyPlayers) {
      ctx += `${player.name}: ${player.role || 'Player'}, ${player.form || 'Form unknown'}`;
      if (player.injury) ctx += ` [${player.injury}]`;
      ctx += `\n`;
    }
  }

  // Injuries
  if (injuries.length > 0) {
    ctx += `\nINJURY / SUSPENSION NEWS:\n`;
    for (const inj of injuries) {
      ctx += `${inj.team}: ${inj.player} — ${inj.status}\n`;
    }
  }

  // Scraped news summaries
  if (scrapedArticles.length > 0) {
    ctx += `\nSCRAPED NEWS SUMMARIES (use as factual skeleton — do not copy verbatim):\n`;
    for (let i = 0; i < scrapedArticles.length; i++) {
      const art = scrapedArticles[i];
      ctx += `\nSOURCE ${i + 1} (${art.source || 'Unknown'}):\n`;
      ctx += `${art.text?.slice(0, 600) || 'No text extracted'}\n`;
    }
  }

  // Prediction from AI predictor
  if (prediction.predicted_winner) {
    ctx += `\nORACLE PREDICTION (from predictor model):\n`;
    ctx += `Winner: ${prediction.predicted_winner}\n`;
    ctx += `Confidence: ${prediction.confidence_pct}%\n`;
    ctx += `Recommended bet: ${prediction.recommended_bet || 'N/A'}\n`;
    ctx += `Edge: ${prediction.edge_summary || 'N/A'}\n`;
  }

  // ChromaDB style examples
  if (styleExamples.length > 0) {
    ctx += `\nSTYLE EXAMPLES FROM PRIOR ORACLE ARTICLES:\n`;
    ctx += `Match the voice, tone, and structure of these examples exactly:\n`;
    for (let i = 0; i < styleExamples.length; i++) {
      ctx += `\n--- Example ${i + 1} ---\n`;
      ctx += `${styleExamples[i].slice(0, 500)}\n`;
    }
  }

  ctx += `\n══════════════════════════════════════\n`;

  logger.info(`Context built: ${ctx.length} chars for ${teamHome} vs ${teamAway}`);
  return ctx;
}

export { buildContext };
