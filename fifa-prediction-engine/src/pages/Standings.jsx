import { useSearchParams } from 'react-router-dom';
import { useMatches } from '../context/MatchesContext';

function Standings() {
  const [searchParams] = useSearchParams();
  const { standings, isLoading, error } = useMatches();

  const homeTeam = searchParams.get('home');
  const awayTeam = searchParams.get('away');

  if (isLoading) return <p>Loading standings...</p>;
  if (error) return <p>Error: {error}</p>;

  return (
    <div>
      <h2>Premier League Standings</h2>
      <table style={{ borderCollapse: 'collapse', width: '100%' }}>
        <thead>
          <tr>
            <th style={{ textAlign: 'left' }}>Pos</th>
            <th style={{ textAlign: 'left' }}>Team</th>
            <th>Played</th>
            <th>Points</th>
          </tr>
        </thead>
        <tbody>
          {standings.map((team) => {
            const isHighlighted =
              team.team.name === homeTeam || team.team.name === awayTeam;

            return (
              <tr
                key={team.team.id}
                style={{
                  backgroundColor: isHighlighted ? '#2a4d3a' : 'transparent',
                  fontWeight: isHighlighted ? 'bold' : 'normal',
                }}
              >
                <td>{team.position}</td>
                <td>{team.team.name}</td>
                <td style={{ textAlign: 'center' }}>{team.playedGames}</td>
                <td style={{ textAlign: 'center' }}>{team.points}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

export default Standings;