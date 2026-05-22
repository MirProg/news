import { Router } from 'express';

const router = Router();

// ESPN API base URLs by sport
const ESPN_SPORTS = {
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

// ─────────────────────────────────────
// GET /api/scores/live — Live scores
// ─────────────────────────────────────
router.get('/live', async (req, res) => {
  try {
    const sport = req.query.sport;
    const scores = [];

    const sportsToFetch = sport
      ? { [sport]: ESPN_SPORTS[sport] }
      : ESPN_SPORTS;

    for (const [key, config] of Object.entries(sportsToFetch)) {
      if (!config) continue;

      try {
        const leaguePath = config.league ? `/${config.league}` : '';
        const url = `https://site.api.espn.com/apis/site/v2/sports/${config.sport}${leaguePath}/scoreboard`;

        const resp = await fetch(url, {
          signal: AbortSignal.timeout(5000),
          headers: { 'Accept': 'application/json' },
        });

        if (!resp.ok) continue;

        const data = await resp.json();

        if (data.events) {
          for (const event of data.events.slice(0, 5)) {
            const competition = event.competitions?.[0];
            if (!competition) continue;

            const teams = competition.competitors || [];
            const homeTeam = teams.find(t => t.homeAway === 'home');
            const awayTeam = teams.find(t => t.homeAway === 'away');

            if (!homeTeam || !awayTeam) continue;

            scores.push({
              sport: key,
              home: homeTeam.team?.abbreviation || homeTeam.team?.shortDisplayName || 'HOME',
              away: awayTeam.team?.abbreviation || awayTeam.team?.shortDisplayName || 'AWAY',
              homeScore: homeTeam.score || '0',
              awayScore: awayTeam.score || '0',
              status: event.status?.type?.shortDetail || 'Scheduled',
              state: event.status?.type?.state || 'pre',
              clock: event.status?.displayClock || '',
              period: event.status?.period || 0,
              startTime: event.date,
            });
          }
        }
      } catch {
        // Skip failed sport fetches silently
      }
    }

    res.json({ scores });
  } catch (err) {
    console.error('Error fetching live scores:', err);
    res.status(500).json({ error: 'Failed to fetch live scores', scores: [] });
  }
});

// ─────────────────────────────────────
// GET /api/scores/upcoming — Upcoming matches (48h)
// ─────────────────────────────────────
router.get('/upcoming', async (req, res) => {
  try {
    const matches = [];

    for (const [key, config] of Object.entries(ESPN_SPORTS)) {
      try {
        const leaguePath = config.league ? `/${config.league}` : '';
        const url = `https://site.api.espn.com/apis/site/v2/sports/${config.sport}${leaguePath}/scoreboard`;

        const resp = await fetch(url, {
          signal: AbortSignal.timeout(5000),
          headers: { 'Accept': 'application/json' },
        });

        if (!resp.ok) continue;

        const data = await resp.json();

        if (data.events) {
          for (const event of data.events) {
            const status = event.status?.type?.state;
            if (status !== 'pre') continue;

            const competition = event.competitions?.[0];
            if (!competition) continue;

            const teams = competition.competitors || [];
            const homeTeam = teams.find(t => t.homeAway === 'home');
            const awayTeam = teams.find(t => t.homeAway === 'away');

            if (!homeTeam || !awayTeam) continue;

            const matchDate = new Date(event.date);
            const now = new Date();
            const hoursAway = (matchDate - now) / (1000 * 60 * 60);

            if (hoursAway > 0 && hoursAway <= 48) {
              matches.push({
                sport: key,
                home: homeTeam.team?.displayName || 'Home',
                away: awayTeam.team?.displayName || 'Away',
                homeAbbr: homeTeam.team?.abbreviation || '',
                awayAbbr: awayTeam.team?.abbreviation || '',
                startTime: event.date,
                venue: competition.venue?.fullName || '',
                league: event.season?.type?.name || '',
              });
            }
          }
        }
      } catch {
        // Skip failed sport fetches
      }
    }

    // Sort by start time
    matches.sort((a, b) => new Date(a.startTime) - new Date(b.startTime));

    res.json({ matches });
  } catch (err) {
    console.error('Error fetching upcoming matches:', err);
    res.status(500).json({ error: 'Failed to fetch upcoming matches', matches: [] });
  }
});

export default router;
