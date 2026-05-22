import Database from 'better-sqlite3';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const DB_PATH = process.env.DB_PATH || path.join(__dirname, '..', 'db', 'oracle_sports.db');

const db = new Database(DB_PATH);

console.log(`Seeding matches queue at ${DB_PATH}...`);

const matches = [
  { sport: 'football', team_home: 'Real Madrid', team_away: 'Barcelona', match_date: new Date(Date.now() + 86400000 * 1).toISOString(), league: 'La Liga' },
  { sport: 'basketball', team_home: 'Celtics', team_away: 'Heat', match_date: new Date(Date.now() + 86400000 * 2).toISOString(), league: 'NBA' },
  { sport: 'mma', team_home: 'Makhachev', team_away: 'Tsarukyan', match_date: new Date(Date.now() + 86400000 * 3).toISOString(), league: 'UFC' },
  { sport: 'nfl', team_home: 'Chiefs', team_away: '49ers', match_date: new Date(Date.now() + 86400000 * 4).toISOString(), league: 'NFL' },
  { sport: 'rugby', team_home: 'New Zealand', team_away: 'South Africa', match_date: new Date(Date.now() + 86400000 * 5).toISOString(), league: 'Rugby Championship' }
];

const insert = db.prepare(`
  INSERT INTO matches_queue (sport, team_home, team_away, match_date, league, status) 
  VALUES (@sport, @team_home, @team_away, @match_date, @league, 'pending')
`);

db.transaction(() => {
  for (const match of matches) {
    insert.run(match);
  }
})();

console.log('✓ Successfully seeded upcoming matches!');
db.close();
