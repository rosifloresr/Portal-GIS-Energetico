import { Navigate, Route, Routes } from 'react-router-dom';
import { Header } from './components/Header';
import { ProtectedRoute } from './components/ProtectedRoute';
import { Home } from './pages/Home';
import { Login } from './pages/Login';
import { MapPage } from './pages/MapPage';
import { Register } from './pages/Register';

export default function App() {
  return (
    <div className="apple-container">
      <Header />
      <main>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/registro" element={<Register />} />
          <Route element={<ProtectedRoute />}>
            <Route path="/mapa" element={<MapPage />} />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
      <footer className="site-footer">Portal GIS Energético · Proyecto de ciberseguridad y GIS</footer>
    </div>
  );
}
