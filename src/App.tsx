import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

interface AppProps {}

function App({}: AppProps) {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<Home />} />
        </Routes>
      </div>
    </Router>
  );
}

const Home: React.FC = () => {
  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold">Maven Dependency Analyzer</h1>
      <p className="mt-4">Upload your Maven dependency tree JSON or analysis TXT files to get started.</p>
    </div>
  );
};

export default App;