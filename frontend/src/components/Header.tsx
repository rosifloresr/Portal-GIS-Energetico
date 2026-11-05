import { useState } from 'react';
import { Link, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

export function Header() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [errorSalida, setErrorSalida] = useState(false);

  const salir = async () => {
    setErrorSalida(false);
    try {
      await logout();
      navigate('/', { replace: true });
    } catch {
      // La sesión sigue abierta en el servidor: hay que avisarlo en vez de simular que se cerró.
      setErrorSalida(true);
    }
  };

  return (
    <header className="site-header">
      <Link to="/" className="brand">⚡ Portal GIS Energético</Link>
      <nav aria-label="Principal">
        <NavLink to="/">Inicio</NavLink>
        {user && <NavLink to="/mapa">Mapa</NavLink>}
        {user ? (
          <>
            <span className="user-chip">{user.username} · {user.role}</span>
            <button className="apple-button apple-button--ghost" onClick={salir}>Cerrar sesión</button>
          </>
        ) : (
          <>
            <NavLink to="/login">Iniciar sesión</NavLink>
            <Link to="/registro" className="apple-button">Registrarse</Link>
          </>
        )}
      </nav>
      {errorSalida && (
        <p className="error-message header-error" role="alert">
          No se pudo cerrar la sesión. Revisá tu conexión e intentá de nuevo.
        </p>
      )}
    </header>
  );
}
