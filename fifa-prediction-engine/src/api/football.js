const API_KEY = import.meta.env.VITE_FOOTBALL_API_KEY;
const BASE_URL = '/api/football'; // points through the Vite proxy


export async function getStandings(competitionCode) {
  const response = await fetch(`${BASE_URL}/competitions/${competitionCode}/standings`, {
    headers: {
      'X-Auth-Token': API_KEY,
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch standings: ${response.status}`);
  }

  const data = await response.json();
  return data.standings[0].table; // the main league table
}

export async function getFixtures(competitionCode) {
  const response = await fetch(`${BASE_URL}/competitions/${competitionCode}/matches?status=SCHEDULED`, {
    headers: {
      'X-Auth-Token': API_KEY,
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch fixtures: ${response.status}`);
  }

  const data = await response.json();
  return data.matches;
}