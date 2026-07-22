# FIFA Prediction Engine

A React app for browsing live Premier League fixtures and standings, with AI-powered match outcome predictions using Google Gemini.

Built as Week 2 of a 4-week AI-powered React bootcamp, focused on React Router, hooks, Context, live API data fetching, and connecting real data to an AI model.

## Features

- Live Premier League fixtures and league standings (real data, not mock)
- Multi-page navigation with React Router
- Shared app state via Context — data is fetched once, used everywhere
- AI-generated match predictions: winner, confidence %, and reasoning, based on real team standings
- Predictions persist across page refreshes via localStorage
- Jump from a match to the standings table with both teams highlighted

## Tech Stack

- **React** (via Vite) — UI and routing
- **React Router** — multi-page navigation, route params, query params
- **React Context** — shared fixtures/standings state across pages
- **football-data.org API** — live fixtures and standings data
- **Google Gemini API** (`gemini-flash-latest`) — structured JSON predictions grounded in real data
- **localStorage** — client-side prediction persistence

## Setup

1. Install dependencies:
   ```bash
   npm install
   ```
2. Create a `.env` file in the project root:
   ```
   VITE_FOOTBALL_API_KEY=your_football_data_org_key
   VITE_GEMINI_API_KEY=your_gemini_api_key
   ```
   - Get a free football-data.org key at [football-data.org/client/register](https://www.football-data.org/client/register)
   - Get a free Gemini key at [Google AI Studio](https://aistudio.google.com/apikey)
3. Run the dev server:
   ```bash
   npm run dev
   ```

## How Predictions Work

Clicking "Predict Outcome" on a match sends both teams' current standings (position, points, games played) to Gemini with a prompt that forces a strict JSON response:

```json
{ "winner": "home", "confidence": 65, "reasoning": "..." }
```

This makes the AI's output machine-readable rather than free-form text, so it can be rendered directly into the UI. Predictions are cached in localStorage per match, so re-visiting a match shows the saved result instead of calling the API again.

## What I Learned

- React Router: routes, route params (`:matchId`), query params, and `Link` vs `<a>`
- React Context for sharing fetched data across multiple pages without prop drilling
- Handling CORS in local development via Vite's dev proxy
- Designing a prompt that returns structured, parseable JSON from an LLM
- Client-side persistence with localStorage as a lightweight alternative to a backend
- Debugging real API issues: rate limits, CORS, and environment variable scoping across separate projects

## Known Limitations

- football-data.org's free tier provides delayed (not real-time) data
- The CORS-bypassing dev proxy only works in local development — a deployed version would need a serverless function to proxy requests
- Predictions are AI-reasoned over real data, not output from a trained statistical/ML model

## Roadmap

This is Week 2 of a 4-week bootcamp:
- **Week 1:** AI Meme Generator — JSX, components, props, state, AI API integration
- **Week 3:** AI JIRA Storyboard — streaming AI responses, portals, debouncing
- **Week 4:** AI Mental Health Counselor — animations, accessibility, deployment

See `FIFA-Prediction-Engine-Documentation.md` for full architecture details and flow diagrams.
