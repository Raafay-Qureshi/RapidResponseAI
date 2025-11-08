import './App.css';
import MapView from './components/Map/MapView';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>HAM - The Heimdall Alert Module</h1>
        <p>Frontend Application</p>
      </header>
      <main style={{ height: 'calc(100vh - 120px)', width: '100%' }}>
        <MapView />
      </main>
    </div>
  );
}

export default App;
