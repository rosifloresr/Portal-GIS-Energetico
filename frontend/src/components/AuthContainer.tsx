import React, { useState } from 'react';

interface AuthContainerProps {
  onLoginSuccess: (token: string) => void;
}

export const AuthContainer: React.FC<AuthContainerProps> = ({ onLoginSuccess }) => {
  const [isRegistering, setIsRegistering] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [mensaje, setMensaje] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setMensaje(null);

    const endpoint = isRegistering ? 'http://localhost:8000/api/v1/auth/register' : 'http://localhost:8000/token';
    
    try {
      if (isRegistering) {
        const res = await fetch(endpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username, password }),
        });
        if (!res.ok) throw new Error('Error en el registro.');
        setMensaje('¡Registro exitoso! Ahora puedes iniciar sesión.');
        setIsRegistering(false);
      } else {
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        const res = await fetch(endpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: formData,
        });
        if (!res.ok) throw new Error('Credenciales incorrectas.');
        
        const data = await res.json();
        onLoginSuccess(data.access_token);
      }
    } catch (err: any) {
      setError(err.message || 'Ocurrió un error.');
    }
  };

  return (
    <div className="apple-card auth-card" style={{ maxWidth: '400px', margin: '40px auto', textAlign: 'center' }}>
      <h2>{isRegistering ? 'Crear Cuenta' : 'Acceso Operadores GIS'}</h2>
      {error && <p style={{ color: '#ff3b30', fontSize: '14px' }}>{error}</p>}
      {mensaje && <p style={{ color: '#34c759', fontSize: '14px' }}>{mensaje}</p>}
      
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '15px', marginTop: '20px' }}>
        <input
          type="text"
          placeholder="Usuario"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          className="apple-select"
          required
        />
        <input
          type="password"
          placeholder="Contraseña"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="apple-select"
          required
        />
        <button type="submit" className="apple-button">
          {isRegistering ? 'Registrarse' : 'Iniciar Sesión'}
        </button>
      </form>

      <p style={{ marginTop: '20px', fontSize: '14px', color: '#86868b', cursor: 'pointer' }} onClick={() => setIsRegistering(!isRegistering)}>
        {isRegistering ? '¿Ya tienes cuenta? Inicia sesión' : '¿No tienes cuenta? Regístrate aquí'}
      </p>
    </div>
  );
};