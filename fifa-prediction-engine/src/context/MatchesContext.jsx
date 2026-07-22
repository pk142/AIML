import { createContext, useContext, useState, useEffect } from 'react';
import { getFixtures, getStandings } from '../api/football';

const MatchesContext = createContext();

export function MatchesProvider({ children }) {
  const [matches, setMatches] = useState([]);
  const [standings, setStandings] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadData() {
      try {
        const [matchesData, standingsData] = await Promise.all([
          getFixtures('PL'),
          getStandings('PL'),
        ]);
        setMatches(matchesData.slice(0, 10));
        setStandings(standingsData);
      } catch (err) {
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    }

    loadData();
  }, []);

  return (
    <MatchesContext.Provider value={{ matches, standings, isLoading, error }}>
      {children}
    </MatchesContext.Provider>
  );
}

export function useMatches() {
  return useContext(MatchesContext);
}