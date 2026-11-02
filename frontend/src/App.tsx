import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { AuthContainer } from './components/AuthContainer';
import { MapViewer } from './components/MapViewer';
import type { ActivoEnergetico } from './types/gis';
import './AppleTheme.css';

export const App: React.FC = () => {
  const [token, setToken] = useState<string | null>(null);
  const [activos, setActivos] = useState<ActivoEnergetico[]>([]);

  const obtenerActivos = async (authToken: string) => {
    try {
      const res = await fetch('http://localhost:8000/api/v1/activos', {
        headers: { Authorization: `Bearer ${authToken}` },
      });
      if (!res.ok) throw new Error('Error al obtener activos');
      const data = await res.json();
      setActivos(data);
    } catch (err) {
      console.error('Error recuperando datos geográficos:', err);
    }
  };

  useEffect(() => {
    if (token) {
      obtenerActivos(token);
    }
  }, [token]);

  const handleLogout = () => {
    setToken(null);
    setActivos([]);
  };

  return (
    <div className="apple-container">
      {/* Pasamos el estado de autenticación y la función de logout al Header */}
      <Header isAuthenticated={!!token} onLogout={handleLogout} />

      {!token ? (
        <AuthContainer onLoginSuccess={(newToken) => setToken(newToken)} />
      ) : (
        <MapViewer activos={activos} />
      )}
    </div>
  );
};

export default App;