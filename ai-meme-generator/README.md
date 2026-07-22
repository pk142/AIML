# AI Meme Generator

A React + Vite app that generates meme captions using Google Gemini's AI API. Built as Week 1 of a 4-week AI-powered React bootcamp, focused on JSX, components, props, state, and connecting to a real AI API.

## Features

- Type any topic and generate a funny, AI-written meme caption
- Live-updating UI with loading and error states
- Clean component structure (`App`, `MemeCard`) demonstrating props and one-way data flow
- Environment-based API key handling (never committed to source control)

## Tech Stack

- **React** (via Vite) — UI and component structure
- **Google Gemini API** (`gemini-flash-latest`) — AI caption generation
- Plain CSS for a subtle fade-in animation on new captions

## Setup

1. Clone the repo and install dependencies:
```bash
   npm install
```
2. Create a `.env` file in the project root:

Get a free key at [Google AI Studio](https://aistudio.google.com/apikey).
3. Run the dev server:
```bash
   npm run dev
```

## What I Learned

- JSX syntax and the "one parent element" rule
- Passing data between components via props
- Managing UI state with `useState` (input, loading, output all as separate state)
- Making async API calls from a React component with proper error handling
- Environment variable handling in Vite (`VITE_` prefix requirement)
- Reading real-world API docs and adapting to platform quirks (e.g. free-tier rate limits on image generation)

## Known Limitation

AI image generation (Gemini's `gemini-2.5-flash-image` / "Nano Banana" model) requires a billing-enabled Google Cloud project — the free tier currently has a 0 images-per-minute quota. The app currently uses a placeholder image service instead; enabling billing is a natural next step.

## Roadmap

This is Week 1 of a 4-week bootcamp:
- **Week 2:** FIFA Prediction Engine — routing, hooks, context
- **Week 3:** AI JIRA Storyboard — streaming AI responses, portals
- **Week 4:** AI Mental Health Counselor — animations, accessibility, deployment