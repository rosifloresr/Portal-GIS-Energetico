import React, { useState } from 'react';

interface AuthPanelProps {
  onLoginSuccess: (token: string) => void;
}

export const AuthPanel: React.FC<AuthPanelProps> = ({ onLoginSuccess }) => {
  const [cargando, setCargando] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const autenticar = async () => {
    setCargando(true);
    setError(null);
    try {
      const formData = new URLSearchParams();
      formData.append('username', 'operador_gis');
      formData.append('password', 'admin123');

      const res = await fetch('http://localhost:8000/token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData,
      });

      if (!res.ok) throw new Error('Credenciales inválidas o servidor inactivo.');

      const data = await res.json();
      onLoginSuccess(data.access_token);
    } catch (err: any) {
      setError(err.message || 'Error de conexión con el servidor.');
    } finally {
      setCargando(false);
    }
  };

  return (
    <div className="apple-card auth-card">
      <p>Inicie sesión para acceder a la capa geoespacial restringida.</p>
      {error && <p className="error-message">{error}</p>}
      <button className="apple-button" onClick={autenticar} disabled={cargando}>
        {cargando ? 'Conectando...' : 'Iniciar Sesión (Operador GIS)'}
      </button>
    </div>
  );
};