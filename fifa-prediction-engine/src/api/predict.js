const API_KEY = import.meta.env.VITE_GEMINI_API_KEY;
const URL = `https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key=${API_KEY}`;

export async function predictMatch(homeTeam, awayTeam, standings) {
  const homeStats = standings.find((s) => s.team.name === homeTeam);
  const awayStats = standings.find((s) => s.team.name === awayTeam);

  const prompt = `You are a football analyst. Predict the outcome of this match using the standings data below.

Home team: ${homeTeam} — Position: ${homeStats?.position ?? 'unknown'}, Points: ${homeStats?.points ?? 'unknown'}, Played: ${homeStats?.playedGames ?? 'unknown'}
Away team: ${awayTeam} — Position: ${awayStats?.position ?? 'unknown'}, Points: ${awayStats?.points ?? 'unknown'}, Played: ${awayStats?.playedGames ?? 'unknown'}

Respond ONLY in this exact JSON format, no markdown, no extra text:
{"winner": "home" or "away" or "draw", "confidence": a number 0-100, "reasoning": "one short sentence explaining why"}`;

  const response = await fetch(URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      contents: [{ parts: [{ text: prompt }] }],
    }),
  });

  if (!response.ok) {
    if (response.status === 429) {
      throw new Error('Rate limit hit — wait a minute before trying again.');
    }
    throw new Error(`Prediction failed: ${response.status}`);
  }

  const data = await response.json();
  const rawText = data.candidates[0].content.parts[0].text.trim();

  // Gemini sometimes wraps JSON in markdown fences — strip those if present
  const cleanText = rawText.replace(/```json|```/g, '').trim();

  return JSON.parse(cleanText);
}