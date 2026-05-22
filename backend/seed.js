import Database from 'better-sqlite3';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const DB_PATH = process.env.DB_PATH || path.join(__dirname, '..', 'db', 'oracle_sports.db');

const db = new Database(DB_PATH);

console.log(`Seeding database at ${DB_PATH}...`);

const articles = [
  {
    sport: 'football',
    team_home: 'Arsenal',
    team_away: 'Manchester City',
    match_date: new Date(Date.now() + 86400000 * 2).toISOString(),
    headline: "Inside Arsenal's Quiet Revolution — And Why This Weekend Tests It",
    subheadline: "Mikel Arteta has built the Premier League's most robust defensive unit. But against Pep Guardiola's City, defensive solidity is only half the battle.",
    body_html: `
      <h2>Setting the Scene</h2>
      <p>There is a stillness around the Emirates these days. The chaotic energy of previous seasons has been replaced by a cold, methodical precision. Mikel Arteta has built something substantial here, a machine that grinds opponents down rather than blowing them away.</p>
      <p>But Manchester City brings a different kind of test. Pep Guardiola’s side arrives not just with tactical superiority, but with the psychological weight of champions. When these two meet, it’s rarely just a football match—it’s a referendum on Arsenal’s progress.</p>
      <h2>By the Numbers</h2>
      <p>Arsenal’s defensive metrics are staggering. They concede just 0.65 xG per game at home, a structural dominance that forces teams out wide and smothers crosses. But City is the one team that doesn't rely on crossing. They penetrate through the half-spaces.</p>
      <blockquote>"Arsenal’s 72% possession at home sounds dominant until you realize City have scored 68% of their away goals by overloading the central zones."</blockquote>
      <h2>Players to Watch</h2>
      <p><strong>Declan Rice</strong>: He is the metronome. Everything Arsenal does well flows through his ability to recover the ball and immediately break lines.</p>
      <p><strong>Phil Foden</strong>: Floating between the lines, Foden is the exact type of player designed to break Arteta’s mid-block. His spatial awareness will dictate the tempo.</p>
      <h2>Our Prediction</h2>
      <p>This will be tight, tactical, and likely decided by a single mistake. While Arsenal's defense is elite, City's ability to manipulate space in the final third gives them a slight edge. The numbers lean toward a narrow away win, driven by City's midfield superiority.</p>
      <h2>Final Thought</h2>
      <p>If Arsenal want to truly announce their arrival as equals, this is the moment. But history, and the underlying data, suggests City still holds the psychological high ground.</p>
    `,
    prediction_winner: 'Manchester City',
    confidence_pct: 62,
    edge_summary: 'City\'s central overloads directly counter Arsenal\'s defensive block.',
    hero_image_url: 'https://images.unsplash.com/photo-1522778119026-d647f0596c20?q=80&w=1200&auto=format&fit=crop',
    published_at: new Date().toISOString(),
    reading_time_mins: 4,
    tags: JSON.stringify(['PremierLeague', 'Arsenal', 'ManCity'])
  },
  {
    sport: 'basketball',
    team_home: 'Lakers',
    team_away: 'Nuggets',
    match_date: new Date(Date.now() + 86400000 * 3).toISOString(),
    headline: "The Jokic Problem: Why the Lakers Still Haven't Found the Answer",
    subheadline: "Denver's offense remains a puzzle Los Angeles cannot solve. Ahead of their next matchup, the numbers suggest the gap is only widening.",
    body_html: `
      <h2>Setting the Scene</h2>
      <p>Crypto.com Arena will be loud, but there's an underlying anxiety when the Nuggets come to town. Nikola Jokic has become a psychological hurdle for the Lakers—a player who doesn't just beat them, but dismantles their defensive philosophy in real-time.</p>
      <h2>By the Numbers</h2>
      <p>The Lakers' pick-and-roll defense ranks in the top 10 against 28 teams. Against Denver, it falls to the bottom 5. Why? Because Jokic’s passing angles break traditional defensive rotations. When Anthony Davis commits to the roller, Jokic finds the corner shooter with a cross-court whip that defies physics.</p>
      <h2>Players to Watch</h2>
      <p><strong>Anthony Davis</strong>: He has to be superhuman. If Davis isn't scoring 30+ and altering every shot at the rim, the Lakers simply don't have the math to keep up.</p>
      <p><strong>Jamal Murray</strong>: The closer. When games get tight, Murray's two-man game with Jokic becomes the most unstoppable play in basketball.</p>
      <h2>Our Prediction</h2>
      <p>The Lakers will keep it close for three quarters on pure adrenaline and home-court advantage. But in the final six minutes, execution wins. Denver's half-court offense is simply too clinical.</p>
      <h2>Final Thought</h2>
      <p>We are watching a generational offensive engine in Denver. Until the Lakers find a structural answer to the Jokic-Murray pick-and-roll, the outcome remains predictable.</p>
    `,
    prediction_winner: 'Nuggets',
    confidence_pct: 71,
    edge_summary: 'Denver\'s late-game execution and Jokic\'s elite passing vs AD.',
    hero_image_url: 'https://images.unsplash.com/photo-1504450758481-7338eba7524a?q=80&w=1200&auto=format&fit=crop',
    published_at: new Date(Date.now() - 3600000).toISOString(),
    reading_time_mins: 5,
    tags: JSON.stringify(['NBA', 'Lakers', 'Nuggets'])
  },
  {
    sport: 'f1',
    team_home: 'Ferrari',
    team_away: 'Red Bull',
    match_date: new Date(Date.now() + 86400000 * 5).toISOString(),
    headline: "The Aero Arms Race: How Ferrari Closed the Gap in the Corners",
    subheadline: "Red Bull's straight-line dominance is unquestioned, but Ferrari's recent floor upgrades have turned the slow corners into a battleground.",
    body_html: `
      <h2>Setting the Scene</h2>
      <p>The paddock whispers have turned into a roar. For two years, Red Bull has operated in a different aerodynamic reality. But as the circus rolls into this weekend, there's a genuine belief in the Ferrari garage that their latest upgrade package has fundamentally altered the equation.</p>
      <h2>By the Numbers</h2>
      <p>Telemetry from the last race showed something fascinating. While Red Bull still holds a 3-4 km/h advantage on the straights, Ferrari is carrying significantly more minimum speed through medium and slow-speed corners. Their tire degradation—long the Achilles heel of the Scuderia—has stabilized.</p>
      <h2>Players to Watch</h2>
      <p><strong>Charles Leclerc</strong>: The ultimate qualifier. If he can put the Ferrari on the front row, his ability to manage the tires in dirty air will be the defining factor of the race.</p>
      <p><strong>Max Verstappen</strong>: Relentless. Even when the car isn't perfectly hooked up, Verstappen extracts lap time that simply shouldn't exist in the data.</p>
      <h2>Our Prediction</h2>
      <p>Qualifying will be incredibly tight, but race pace is a different story. Red Bull's tire management over a full stint still gives them the edge. We predict a Verstappen win, but by the narrowest margin we've seen all season.</p>
      <h2>Final Thought</h2>
      <p>The era of total Red Bull dominance might be ending, replaced by a nuanced, highly technical battle for marginal gains.</p>
    `,
    prediction_winner: 'Red Bull',
    confidence_pct: 58,
    edge_summary: 'Superior race pace and tire management over a full stint.',
    hero_image_url: 'https://images.unsplash.com/photo-1532906561084-5f40344d5678?q=80&w=1200&auto=format&fit=crop',
    published_at: new Date(Date.now() - 7200000).toISOString(),
    reading_time_mins: 3,
    tags: JSON.stringify(['F1', 'Ferrari', 'RedBull'])
  },
  {
    sport: 'tennis',
    team_home: 'Alcaraz',
    team_away: 'Sinner',
    match_date: new Date(Date.now() + 86400000 * 1).toISOString(),
    headline: "The New Rivalry: Alcaraz, Sinner, and the Evolution of Power",
    subheadline: "Forget the Big Three. The sport now belongs to two young stars who are redefining what baseline tennis looks like.",
    body_html: `
      <h2>Setting the Scene</h2>
      <p>When Carlos Alcaraz and Jannik Sinner step onto the court, the sound of the ball is different. It’s a violent, heavy thud that reverberates through the stadium. This isn't just a match; it's a showcase of the sport's future—a baseline arms race where spin and pace are pushed to their absolute physical limits.</p>
      <h2>By the Numbers</h2>
      <p>Sinner’s average forehand speed is up 4mph this season, a terrifying development for the rest of the tour. But Alcaraz counters with variety. The Spaniard uses the drop shot 12% more often than Sinner, creating a dynamic vertical game that constantly disrupts Sinner's baseline rhythm.</p>
      <h2>Players to Watch</h2>
      <p><strong>Carlos Alcaraz</strong>: Creativity incarnate. His ability to hit winners from defensive positions scrambles the opponent's tactical plan.</p>
      <p><strong>Jannik Sinner</strong>: Clinical efficiency. His backhand down the line is currently the most devastating single shot in men's tennis.</p>
      <h2>Our Prediction</h2>
      <p>Sinner's recent consistency on hard courts gives him a slight mathematical edge. While Alcaraz's peak is arguably higher, Sinner's base level rarely drops. We expect Sinner to grind out a victory in a tight, multi-set battle.</p>
      <h2>Final Thought</h2>
      <p>Enjoy this. We are witnessing the foundation of a rivalry that will define the next decade of the sport.</p>
    `,
    prediction_winner: 'Sinner',
    confidence_pct: 55,
    edge_summary: 'Sinner\'s baseline consistency and devastating down-the-line backhand.',
    hero_image_url: 'https://images.unsplash.com/photo-1595435934249-5df7ed86e1c0?q=80&w=1200&auto=format&fit=crop',
    published_at: new Date(Date.now() - 86400000).toISOString(),
    reading_time_mins: 4,
    tags: JSON.stringify(['Tennis', 'ATP', 'Alcaraz', 'Sinner'])
  },
  {
    sport: 'cricket',
    team_home: 'India',
    team_away: 'Australia',
    match_date: new Date(Date.now() + 86400000 * 4).toISOString(),
    headline: "The Border-Gavaskar Tension: How Spin Will Decide the Series",
    subheadline: "Australia brings fiery pace, but India's slow, turning pitches demand a completely different kind of mastery.",
    body_html: `
      <h2>Setting the Scene</h2>
      <p>The heat is oppressive, the crowd is deafening, and the pitch is already showing cracks on Day 1. This is Test cricket in India. Australia arrives with a point to prove, but the ghosts of previous tours linger in the dressing room.</p>
      <h2>By the Numbers</h2>
      <p>Australian batsmen average just 24.5 against finger spin in the subcontinent over the last five years. India’s spinners, meanwhile, strike every 42 balls at home. The math is stark: if Australia cannot find a way to rotate the strike against the turning ball, the pressure will inevitably force false shots.</p>
      <h2>Players to Watch</h2>
      <p><strong>Ravichandran Ashwin</strong>: The grandmaster. He doesn't just bowl; he sets traps. His subtle variations in pace and release point make him unplayable on wearing pitches.</p>
      <p><strong>Steve Smith</strong>: The anomaly. Smith's eccentric technique allows him to smother the spin better than any of his contemporaries. If Australia is to win, he must bat long.</p>
      <h2>Our Prediction</h2>
      <p>The conditions heavily favor the home side. India’s mastery of their own conditions, combined with Australia's historical fragility against high-quality spin, points in one direction. India to win comfortably.</p>
      <h2>Final Thought</h2>
      <p>Test cricket remains the ultimate examination of technique and character. This series will expose every flaw and reward ultimate patience.</p>
    `,
    prediction_winner: 'India',
    confidence_pct: 78,
    edge_summary: 'India\'s dominant home record and superior spin attack.',
    hero_image_url: 'https://images.unsplash.com/photo-1531415074968-036ba1b575da?q=80&w=1200&auto=format&fit=crop',
    published_at: new Date(Date.now() - 172800000).toISOString(),
    reading_time_mins: 5,
    tags: JSON.stringify(['Cricket', 'TestMatch', 'IndvAus'])
  }
];

const insert = db.prepare(`
  INSERT INTO articles (
    sport, team_home, team_away, match_date, headline, subheadline, 
    body_html, prediction_winner, confidence_pct, edge_summary, 
    hero_image_url, published_at, reading_time_mins, tags, status
  ) VALUES (
    @sport, @team_home, @team_away, @match_date, @headline, @subheadline,
    @body_html, @prediction_winner, @confidence_pct, @edge_summary,
    @hero_image_url, @published_at, @reading_time_mins, @tags, 'published'
  )
`);

db.transaction(() => {
  for (const article of articles) {
    insert.run(article);
  }
})();

console.log('✓ Successfully seeded 5 articles!');
db.close();
