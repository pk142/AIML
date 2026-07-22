const STORAGE_KEY = 'fifa_predictions';

export function getSavedPredictions() {
  const raw = localStorage.getItem(STORAGE_KEY);
  return raw ? JSON.parse(raw) : {};
}

export function savePrediction(matchId, prediction) {
  const all = getSavedPredictions();
  all[matchId] = prediction;
  localStorage.setItem(STORAGE_KEY, JSON.stringify(all));
}

export function getPrediction(matchId) {
  const all = getSavedPredictions();
  return all[matchId] || null;
}