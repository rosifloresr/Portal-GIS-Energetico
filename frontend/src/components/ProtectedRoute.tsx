import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

/** Deja pasar solo a quien tiene sesión; al resto lo manda a iniciar sesión. */
export function ProtectedRoute() {
  const { user, cargando } = useAuth();
  const location = useLocation();

  // Mientras se consulta al servidor `user` es null aunque haya sesión: redirigir
  // ahora mandaría al login a alguien que ya está logueado.
  if (cargando) return <p className="center-note">Verificando sesión…</p>;

  // Se guarda la ruta pedida para volver a ella después de iniciar sesión.
  if (!user) return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  return <Outlet />;
}
