import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useMatches } from '../context/MatchesContext';
import { predictMatch } from '../api/predict';
import { getPrediction, savePrediction } from '../api/predictionStorage';

function MatchDetail() {
  const { matchId } = useParams();
  const { matches, standings, isLoading } = useMatches();
  const [prediction, setPrediction] = useState(null);
  const [isPredicting, setIsPredicting] = useState(false);
  const [predictError, setPredictError] = useState(null);

  const match = matches.find((m) => m.id === Number(matchId));

  // Load a cached prediction (if one exists) whenever the match changes
  useEffect(() => {
    if (match) {
      const cached = getPrediction(match.id);
      setPrediction(cached);
    }
  }, [match]);

  if (isLoading) return <p>Loading...</p>;
  if (!match) return <p>Match not found. <Link to="/">Back to fixtures</Link></p>;

  async function handlePredict() {
    setIsPredicting(true);
    setPredictError(null);
    try {
      const result = await predictMatch(match.homeTeam.name, match.awayTeam.name, standings);
      setPrediction(result);
      savePrediction(match.id, result);
    } catch (err) {
      setPredictError(err.message);
    } finally {
      setIsPredicting(false);
    }
  }

  return (
    <div>
      <h2>{match.homeTeam.name} vs {match.awayTeam.name}</h2>
      <p>Date: {new Date(match.utcDate).toLocaleString()}</p>
      <p>Competition: {match.competition.name}</p>

      <button onClick={handlePredict} disabled={isPredicting}>
        {isPredicting
          ? 'Analyzing...'
          : prediction
          ? 'Re-predict Outcome (AI)'
          : 'Predict Outcome (AI)'}
      </button>

      {predictError && <p style={{ color: 'salmon' }}>Error: {predictError}</p>}

      {prediction && (
        <div style={{ marginTop: '12px', padding: '12px', border: '1px solid #444' }}>
          <p><strong>Predicted winner:</strong> {prediction.winner}</p>
          <p><strong>Confidence:</strong> {prediction.confidence}%</p>
          <p><strong>Reasoning:</strong> {prediction.reasoning}</p>
        </div>
      )}

      <br />
      <Link to="/">← Back to fixtures</Link>
      {' | '}
      <Link to={`/standings?home=${encodeURIComponent(match.homeTeam.name)}&away=${encodeURIComponent(match.awayTeam.name)}`}>
        View these teams on Standings
      </Link>
    </div>
  );
}

export default MatchDetail;