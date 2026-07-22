import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import { MatchesProvider } from './context/MatchesContext';
import Home from './pages/Home';
import Standings from './pages/Standings';
import MatchDetail from './pages/MatchDetail';

function App() {
  return (
    <MatchesProvider>
      <BrowserRouter>
        <nav style={{ display: 'flex', gap: '16px', padding: '16px' }}>
          <Link to="/">Fixtures</Link>
          <Link to="/standings">Standings</Link>
        </nav>

        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/standings" element={<Standings />} />
          <Route path="/match/:matchId" element={<MatchDetail />} />
        </Routes>
      </BrowserRouter>
    </MatchesProvider>
  );
}

export default App;