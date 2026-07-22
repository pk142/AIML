import { Link } from 'react-router-dom';
import { useMatches } from '../context/MatchesContext';
import { getPrediction } from '../api/predictionStorage';

function Home() {
  const { matches, isLoading, error } = useMatches();

  if (isLoading) return <p>Loading fixtures...</p>;
  if (error) return <p>Error: {error}</p>;

  return (
    <div>
      <h2>Upcoming Fixtures</h2>
      <ul>
        {matches.map((match) => {
          const predicted = getPrediction(match.id);
          return (
            <li key={match.id} style={{ marginBottom: '8px' }}>
              <Link to={`/match/${match.id}`}>
                {match.homeTeam.name} vs {match.awayTeam.name}
              </Link>
              {' — '}
              {new Date(match.utcDate).toLocaleDateString()}
              {predicted && (
                <span style={{ marginLeft: '8px', fontSize: '0.85em', color: '#8f8' }}>
                  ✓ Predicted: {predicted.winner} ({predicted.confidence}%)
                </span>
              )}
            </li>
          );
        })}
      </ul>
    </div>
  );
}

export default Home;