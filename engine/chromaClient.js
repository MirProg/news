import { ChromaClient } from 'chromadb';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';
import { getEmbedding } from './ollamaClient.js';
import logger from './logger.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
dotenv.config({ path: path.join(__dirname, '..', '.env') });

const CHROMADB_URL = process.env.CHROMADB_URL || 'http://localhost:8000';
const COLLECTION_NAME = 'oracle_articles';

let client = null;
let collection = null;

/**
 * Initialize ChromaDB connection and collection
 */
async function initChroma() {
  if (collection) return collection;

  try {
    client = new ChromaClient({ path: CHROMADB_URL });
    collection = await client.getOrCreateCollection({
      name: COLLECTION_NAME,
      metadata: { 'hnsw:space': 'cosine' },
    });
    logger.info(`ChromaDB connected: collection "${COLLECTION_NAME}"`);
    return collection;
  } catch (err) {
    logger.warn(`ChromaDB connection failed: ${err.message}`);
    return null;
  }
}

/**
 * Embed article text and store in ChromaDB
 */
async function embedAndStore(articleId, text, metadata = {}) {
  try {
    const coll = await initChroma();
    if (!coll) {
      logger.warn('ChromaDB not available — skipping embed');
      return false;
    }

    // Get embedding from Ollama nomic-embed-text
    const embedding = await getEmbedding(text.slice(0, 6000));

    if (!embedding || embedding.length === 0) {
      logger.warn('Empty embedding returned — skipping store');
      return false;
    }

    await coll.add({
      ids: [`article_${articleId}`],
      embeddings: [embedding],
      documents: [text.slice(0, 2000)], // Store excerpt for retrieval
      metadatas: [{
        article_id: articleId,
        sport: metadata.sport || '',
        teams: metadata.teams || '',
        match_date: metadata.match_date || '',
      }],
    });

    logger.info(`ChromaDB stored: article_${articleId} (${metadata.sport})`);
    return true;
  } catch (err) {
    logger.error(`ChromaDB embed error: ${err.message}`);
    return false;
  }
}

/**
 * Query similar past articles for RAG context
 */
async function querySimilar(sport, teams, n = 3) {
  try {
    const coll = await initChroma();
    if (!coll) return [];

    const queryText = `${sport} ${teams}`;
    const embedding = await getEmbedding(queryText);

    if (!embedding || embedding.length === 0) return [];

    const results = await coll.query({
      queryEmbeddings: [embedding],
      nResults: n,
      where: { sport: sport },
    });

    const documents = results.documents?.[0] || [];
    logger.info(`ChromaDB query: found ${documents.length} similar articles for ${sport} ${teams}`);

    return documents;
  } catch (err) {
    logger.warn(`ChromaDB query error: ${err.message}`);
    return [];
  }
}

export { initChroma, embedAndStore, querySimilar };
