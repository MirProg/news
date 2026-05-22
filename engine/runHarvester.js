import { harvestFeeds } from './rssHarvester.js';
import logger from './logger.js';

async function main() {
  logger.info('Manual Harvester Run Started...');
  try {
    const result = await harvestFeeds();
    logger.info(`Done! Fetched: ${result.fetched}, Matched to games: ${result.matched}`);
    process.exit(0);
  } catch (err) {
    logger.error('Error:', err);
    process.exit(1);
  }
}

main();
