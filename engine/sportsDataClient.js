import axios from 'axios';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';
import logger from './logger.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
dotenv.config({ path: path.join(__dirname, '..', '.env') });

const ODDS_API_KEY = process.env.THE_ODDS_API_KEY || '';
const ODDS_API_BASE = 'https://api.the-odds-api.com/v4';

// ─────────────────────────────────────
// Sport key mapping for The Odds API
// ─────────────────────────────────────
const ODDS_SPORT_KEYS = {
  football: 'soccer_epl',
  basketball: 'basketball_nba',
  cricket: 'cricket_ipl',
  tennis: 'tennis_atp_french_open',
  mma: 'mma_mixed_martial_arts',
  f1: 'motorsport_formula_one',
  nfl: 'americanfootball_nfl',
  rugby: 'rugbyleague_nrl',
  nhl: 'icehockey_nhl',
  mlb: 'baseball_mlb',
};

// ─────────────────────────────────────
// ESPN API sport/league mapping
// ─────────────────────────────────────
const ESPN_MAP = {
  football: { sport: 'soccer', league: 'eng.1' },
  basketball: { sport: 'basketball', league: 'nba' },
  cricket: { sport: 'cricket', league: '' },
  tennis: { sport: 'tennis', league: '' },
  mma: { sport: 'mma', league: '' },
  f1: { sport: 'racing', league: 'f1' },
  rugby: { sport: 'rugby', league: '' },
  nfl: { sport: 'football', league: 'nfl' },
  nhl: { sport: 'hockey', league: 'nhl' },
  mlb: { sport: 'baseball', league: 'mlb' },
};

/**
 * Fetch upcoming match odds from The Odds API
 */
async function getUpcomingOdds(sport = 'football') {
  const sportKey = ODDS_SPORT_KEYS[sport] || ODDS_SPORT_KEYS.football;

  if (!ODDS_API_KEY || ODDS_API_KEY === 'your_free_key_here') {
    logger.warn('The Odds API key not configured — skipping odds fetch');
    return [];
  }

  try {
    const { data } = await axios.get(`${ODDS_API_BASE}/sports/${sportKey}/odds`, {
      params: {
        apiKey: ODDS_API_KEY,
        regions: 'uk,eu',
        markets: 'h2h',
        oddsFormat: 'decimal',
      },
      timeout: 10000,
    });

    return data.map(event => ({
      sport,
      team_home: event.home_team,
      team_away: event.away_team,
      match_date: event.commence_time,
      league: event.sport_title || '',
      odds_home: extractOdds(event.bookmakers, event.home_team),
      odds_away: extractOdds(event.bookmakers, event.away_team),
      odds_draw: extractOdds(event.bookmakers, 'Draw'),
    }));
  } catch (err) {
    logger.error(`Odds API error for ${sport}: ${err.message}`);
    return [];
  }
}

/**
 * Extract best odds from bookmakers array
 */
function extractOdds(bookmakers, outcome) {
  if (!bookmakers || !bookmakers.length) return null;

  for (const bm of bookmakers) {
    const market = bm.markets?.find(m => m.key === 'h2h');
    if (!market) continue;
    const o = market.outcomes?.find(out => out.name === outcome);
    if (o) return o.price;
  }
  return null;
}

/**
 * Get live scores from ESPN public API
 */
async function getLiveScores(sport = 'football') {
  const config = ESPN_MAP[sport];
  if (!config) return [];

  try {
    const leaguePath = config.league ? `/${config.league}` : '';
    const url = `https://site.api.espn.com/apis/site/v2/sports/${config.sport}${leaguePath}/scoreboard`;

    const { data } = await axios.get(url, { timeout: 8000 });

    if (!data.events) return [];

    return data.events.map(event => {
      const comp = event.competitions?.[0];
      const teams = comp?.competitors || [];
      const home = teams.find(t => t.homeAway === 'home');
      const away = teams.find(t => t.homeAway === 'away');

      return {
        sport,
        home_team: home?.team?.displayName || '',
        away_team: away?.team?.displayName || '',
        home_score: home?.score || '0',
        away_score: away?.score || '0',
        status: event.status?.type?.shortDetail || 'Scheduled',
        state: event.status?.type?.state || 'pre',
        clock: event.status?.displayClock || '',
        start_time: event.date,
        venue: comp?.venue?.fullName || '',
        winner: event.status?.type?.state === 'post'
          ? (parseInt(home?.score) > parseInt(away?.score) ? home?.team?.displayName
            : parseInt(away?.score) > parseInt(home?.score) ? away?.team?.displayName
            : 'DRAW')
          : null,
      };
    });
  } catch (err) {
    logger.error(`ESPN scores error for ${sport}: ${err.message}`);
    return [];
  }
}

/**
 * Get team recent form from ESPN (last 5 results)
 */
async function getTeamForm(sport = 'football', teamName = '') {
  try {
    const config = ESPN_MAP[sport];
    if (!config || !config.league) return { form: 'N/A', results: [] };

    const teamsUrl = `https://site.api.espn.com/apis/site/v2/sports/${config.sport}/${config.league}/teams`;
    const { data } = await axios.get(teamsUrl, { timeout: 8000 });

    // Find team by name
    const team = data.sports?.[0]?.leagues?.[0]?.teams?.find(t =>
      t.team?.displayName?.toLowerCase().includes(teamName.toLowerCase()) ||
      t.team?.shortDisplayName?.toLowerCase().includes(teamName.toLowerCase())
    );

    if (!team) return { form: 'N/A', results: [] };

    const record = team.team?.record?.items?.[0];
    return {
      form: record?.summary || 'N/A',
      wins: record?.stats?.find(s => s.name === 'wins')?.value || 0,
      losses: record?.stats?.find(s => s.name === 'losses')?.value || 0,
      draws: record?.stats?.find(s => s.name === 'ties')?.value || 0,
    };
  } catch (err) {
    logger.warn(`Team form fetch failed for ${teamName}: ${err.message}`);
    return { form: 'N/A', results: [] };
  }
}

/**
 * Fetch upcoming matches across all sports (next 48 hours)
 */
async function getUpcomingMatches() {
  const allMatches = [];

  for (const [sport, sportKey] of Object.entries(ODDS_SPORT_KEYS)) {
    try {
      const matches = await getUpcomingOdds(sport);
      allMatches.push(...matches);
    } catch (err) {
      logger.warn(`Failed to fetch upcoming for ${sport}: ${err.message}`);
    }
  }

  // Filter to next 48 hours
  const now = new Date();
  const cutoff = new Date(now.getTime() + 48 * 60 * 60 * 1000);

  return allMatches.filter(m => {
    const matchDate = new Date(m.match_date);
    return matchDate > now && matchDate < cutoff;
  });
}

/**
 * Check match result from ESPN
 */
async function getMatchResult(sport, teamHome, teamAway) {
  try {
    const scores = await getLiveScores(sport);
    const match = scores.find(s =>
      s.state === 'post' &&
      (s.home_team.toLowerCase().includes(teamHome.toLowerCase()) ||
       s.away_team.toLowerCase().includes(teamHome.toLowerCase()))
    );

    if (!match) return null;

    return {
      home_team: match.home_team,
      away_team: match.away_team,
      home_score: match.home_score,
      away_score: match.away_score,
      winner: match.winner,
      status: 'completed',
    };
  } catch (err) {
    logger.error(`Match result check failed: ${err.message}`);
    return null;
  }
}

export {
  getUpcomingOdds,
  getLiveScores,
  getTeamForm,
  getUpcomingMatches,
  getMatchResult,
};
