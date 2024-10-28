import logo from './logo.svg';
import './App.css';
import MainDashboard from './components/MainDashboard';
import { BrowserRouter } from 'react-router-dom'; // Import BrowserRouter

function App() {
  return (
    <BrowserRouter>
      <MainDashboard />
    </BrowserRouter>
  );
}

export default App;
