import OpenAI from 'openai';
import PQueue from 'p-queue';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';
import logger from './logger.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
dotenv.config({ path: path.join(__dirname, '..', '.env') });

const OLLAMA_BASE_URL = process.env.OLLAMA_BASE_URL || 'http://localhost:11434/v1';

// OpenAI-compatible client pointing at Ollama
const client = new OpenAI({
  baseURL: OLLAMA_BASE_URL,
  apiKey: 'ollama',
});

// ─────────────────────────────────────
// CRITICAL: Single-concurrency queue for RTX 3070 (8GB VRAM)
// Cannot run two model inferences simultaneously
// ─────────────────────────────────────
const queue = new PQueue({ concurrency: 1 });

let lastModel = null;
const MODEL_SWITCH_COOLDOWN = 2000; // 2 seconds

/**
 * Call any Ollama model through the queue with auto-cooldown on model switch.
 */
async function callModel(model, messages, options = {}) {
  return queue.add(async () => {
    // Cooldown when switching models (Ollama needs to unload/reload weights)
    if (lastModel && lastModel !== model) {
      logger.info(`Model switch: ${lastModel} → ${model} (${MODEL_SWITCH_COOLDOWN}ms cooldown)`);
      await new Promise(r => setTimeout(r, MODEL_SWITCH_COOLDOWN));
    }
    lastModel = model;

    const startTime = Date.now();
    logger.info(`Ollama call: model=${model}, tokens=${options.max_tokens || 'default'}`);

    try {
      const response = await client.chat.completions.create({
        model,
        messages,
        temperature: options.temperature ?? 0.7,
        max_tokens: options.max_tokens,
        ...(options.response_format ? { response_format: options.response_format } : {}),
      });

      const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
      const content = response.choices?.[0]?.message?.content || '';
      logger.info(`Ollama response: model=${model}, ${content.length} chars, ${elapsed}s`);

      return content;
    } catch (err) {
      const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
      logger.error(`Ollama error: model=${model}, ${elapsed}s — ${err.message}`);
      throw err;
    }
  });
}

/**
 * Writer model — mistral-nemo, high creativity
 */
async function callWriter(messages) {
  const model = process.env.WRITER_MODEL || 'mistral-nemo';
  return callModel(model, messages, {
    temperature: 0.85,
    max_tokens: 2800,
  });
}

/**
 * Predictor model — qwen2.5:7b-instruct, low temp, JSON output
 */
async function callPredictor(messages) {
  const model = process.env.PREDICTOR_MODEL || 'qwen2.5:7b-instruct';
  return callModel(model, messages, {
    temperature: 0.2,
    max_tokens: 500,
    response_format: { type: 'json_object' },
  });
}

/**
 * Headline model — phi3.5, maximum creativity
 */
async function callHeadline(messages) {
  const model = process.env.HEADLINE_MODEL || 'phi3.5';
  return callModel(model, messages, {
    temperature: 0.95,
    max_tokens: 150,
  });
}

/**
 * Embedding via nomic-embed-text
 */
async function getEmbedding(text) {
  return queue.add(async () => {
    const model = process.env.EMBEDDING_MODEL || 'nomic-embed-text';

    if (lastModel && lastModel !== model) {
      await new Promise(r => setTimeout(r, MODEL_SWITCH_COOLDOWN));
    }
    lastModel = model;

    try {
      const response = await client.embeddings.create({
        model,
        input: text.slice(0, 8000), // Limit input length
      });
      return response.data?.[0]?.embedding || [];
    } catch (err) {
      logger.error(`Embedding error: ${err.message}`);
      throw err;
    }
  });
}

/**
 * Writer with fallback chain: mistral-nemo → llama3.1:8b → qwen2.5:7b-instruct
 */
async function callWriterWithFallback(messages) {
  const fallbackChain = [
    process.env.WRITER_MODEL || 'mistral-nemo',
    'llama3.1:8b',
    process.env.PREDICTOR_MODEL || 'qwen2.5:7b-instruct',
  ];

  for (const model of fallbackChain) {
    try {
      logger.info(`Attempting writer with model: ${model}`);
      const result = await callModel(model, messages, {
        temperature: 0.85,
        max_tokens: 2800,
      });
      return { content: result, model };
    } catch (err) {
      logger.warn(`Writer model ${model} failed: ${err.message}`);
      if (model === fallbackChain[fallbackChain.length - 1]) {
        throw new Error(`All writer models failed. Last error: ${err.message}`);
      }
    }
  }
}

export {
  client,
  queue,
  callModel,
  callWriter,
  callPredictor,
  callHeadline,
  getEmbedding,
  callWriterWithFallback,
};
