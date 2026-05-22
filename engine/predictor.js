import { callPredictor } from './ollamaClient.js';
import logger from './logger.js';

/**
 * Generate prediction JSON using qwen2.5:7b-instruct
 */
async function generatePrediction(contextString) {
  const systemPrompt = `You are a sports prediction AI. Analyze the match context provided and produce a JSON prediction.

You MUST output valid JSON with exactly these fields:
{
  "predicted_winner": "team name or DRAW",
  "confidence_pct": <number 40-95>,
  "recommended_bet": "Home Win / Away Win / Draw / Over 2.5 / BTTS",
  "edge_summary": "2-3 sentence plain analysis of the key edge",
  "key_factors": ["factor1", "factor2", "factor3"]
}

Rules:
- confidence_pct must be between 40 and 95. Anything outside this range is unreliable.
- predicted_winner must be exactly one of: the home team name, the away team name, or "DRAW"
- edge_summary should explain WHY this prediction has value — what structural advantage exists
- key_factors should list the 3 most important factors driving the prediction
- Be analytical, not hype-driven. Focus on data patterns, form, and matchup dynamics.`;

  const userPrompt = `Analyze this match and produce your prediction JSON:\n\n${contextString}`;

  try {
    const response = await callPredictor([
      { role: 'system', content: systemPrompt },
      { role: 'user', content: userPrompt },
    ]);

    // Parse JSON from response
    let prediction;
    try {
      // Try direct parse
      prediction = JSON.parse(response);
    } catch {
      // Try to extract JSON from response text
      const jsonMatch = response.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        prediction = JSON.parse(jsonMatch[0]);
      } else {
        throw new Error('No valid JSON found in predictor response');
      }
    }

    // Validate prediction
    if (!prediction.predicted_winner) {
      throw new Error('Missing predicted_winner');
    }

    // Clamp confidence to valid range
    if (prediction.confidence_pct < 40) prediction.confidence_pct = 40;
    if (prediction.confidence_pct > 95) prediction.confidence_pct = 95;

    // Ensure key_factors is an array
    if (!Array.isArray(prediction.key_factors)) {
      prediction.key_factors = [];
    }

    logger.info(`Prediction: ${prediction.predicted_winner} @ ${prediction.confidence_pct}% confidence`);
    return prediction;
  } catch (err) {
    logger.error(`Prediction generation failed: ${err.message}`);

    // Return default prediction on failure
    return {
      predicted_winner: 'DRAW',
      confidence_pct: 45,
      recommended_bet: 'Draw',
      edge_summary: 'Insufficient data for a confident prediction. The match appears evenly balanced.',
      key_factors: ['Limited data available', 'Even matchup', 'No clear edge identified'],
    };
  }
}

export { generatePrediction };
