import { useState, type FormEvent } from 'react';
import { Link, Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

const DESTINO_POR_DEFECTO = '/mapa';

// ProtectedRoute guarda la ruta pedida; se valida igual porque una que empiece con
// "//" o sea un URL absoluto mandaría a la persona a otro sitio tras iniciar sesión.
function rutaSegura(ruta: string | undefined): string {
  return ruta?.startsWith('/') && !ruta.startsWith('//') ? ruta : DESTINO_POR_DEFECTO;
}

export function Login() {
  const { user, login } = useAuth();
  const destino = rutaSegura((useLocation().state as { from?: string } | null)?.from);
  const [identificador, setIdentificador] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [cargando, setCargando] = useState(false);

  // Una sola redirección: al iniciar sesión `user` cambia y este Navigate lleva
  // a la ruta pedida. Sumar un navigate() después de login() las haría competir.
  if (user) return <Navigate to={destino} replace />;

  const enviar = async (evento: FormEvent) => {
    evento.preventDefault();
    setError(null);
    setCargando(true);
    try {
      await login(identificador, password);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error inesperado.');
    } finally {
      setCargando(false);
    }
  };

  return (
    <form className="apple-card auth-card" onSubmit={enviar}>
      <h1>Iniciar sesión</h1>
      <label htmlFor="identificador">Usuario o email</label>
      <input
        id="identificador"
        className="apple-input"
        autoComplete="username"
        required
        value={identificador}
        onChange={(e) => setIdentificador(e.target.value)}
      />
      <label htmlFor="password">Contraseña</label>
      <input
        id="password"
        type="password"
        className="apple-input"
        autoComplete="current-password"
        required
        maxLength={72}
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      {error && <p className="error-message" role="alert">{error}</p>}
      <button className="apple-button" disabled={cargando}>{cargando ? 'Ingresando…' : 'Ingresar'}</button>
      <p className="auth-alt">¿No tenés cuenta? <Link to="/registro">Registrate</Link></p>
    </form>
  );
}
