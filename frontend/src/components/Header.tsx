import { useState } from 'react';
import { Link, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

export function Header() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [saliendo, setSaliendo] = useState(false);
  const [errorSalida, setErrorSalida] = useState(false);

  const salir = async () => {
    setErrorSalida(false);
    setSaliendo(true);
    // Se navega antes de cerrar la sesión: si fuera después, ProtectedRoute vería
    // "sin sesión" primero y llevaría al login en vez de a la portada.
    navigate('/', { replace: true });
    try {
      await logout();
    } catch {
      // La sesión sigue abierta en el servidor: hay que avisarlo en vez de simular que se cerró.
      setErrorSalida(true);
    } finally {
      setSaliendo(false);
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
            <button className="apple-button apple-button--ghost" onClick={salir} disabled={saliendo}>
              {saliendo ? 'Cerrando sesión…' : 'Cerrar sesión'}
            </button>
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
