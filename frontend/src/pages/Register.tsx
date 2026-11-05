import { useState, type FormEvent } from 'react';
import { Link, Navigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

export function Register() {
  const { user, register } = useAuth();
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmar, setConfirmar] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [cargando, setCargando] = useState(false);

  // Tras registrarse, `user` cambia y este Navigate lleva al mapa.
  if (user) return <Navigate to="/mapa" replace />;

  const enviar = async (evento: FormEvent) => {
    evento.preventDefault();
    setError(null);
    if (password !== confirmar) {
      setError('Las contraseñas no coinciden.');
      return;
    }
    setCargando(true);
    try {
      await register(username, email, password);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error inesperado.');
    } finally {
      setCargando(false);
    }
  };

  return (
    <form className="apple-card auth-card" onSubmit={enviar}>
      <h1>Crear cuenta</h1>
      <label htmlFor="username">Usuario <small>(se guarda en minúsculas)</small></label>
      <input
        id="username"
        className="apple-input"
        autoComplete="username"
        required
        minLength={3}
        maxLength={30}
        pattern="[A-Za-z0-9_.\-]+"
        title="Letras, números, punto, guion y guion bajo"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
      />
      <label htmlFor="email">Email</label>
      <input
        id="email"
        type="email"
        className="apple-input"
        autoComplete="email"
        required
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      <label htmlFor="password">Contraseña <small>(mínimo 8, con letras y números)</small></label>
      <input
        id="password"
        type="password"
        className="apple-input"
        autoComplete="new-password"
        required
        minLength={8}
        maxLength={72}
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      <label htmlFor="confirmar">Repetir contraseña</label>
      <input
        id="confirmar"
        type="password"
        className="apple-input"
        autoComplete="new-password"
        required
        value={confirmar}
        onChange={(e) => setConfirmar(e.target.value)}
      />
      {error && <p className="error-message" role="alert">{error}</p>}
      <button className="apple-button" disabled={cargando}>{cargando ? 'Creando…' : 'Registrarme'}</button>
      <p className="auth-alt">¿Ya tenés cuenta? <Link to="/login">Iniciá sesión</Link></p>
    </form>
  );
}
