import { Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

const CARACTERISTICAS = [
  {
    icono: '🗺️',
    titulo: 'Mapa interactivo',
    texto: 'Ubicá subestaciones, transformadores y postes sobre el mapa y filtrá los activos por estado.',
  },
  {
    icono: '🚦',
    titulo: 'Estado de la red',
    texto: 'Identificá de un vistazo qué activos están operativos, en revisión o en falla.',
  },
  {
    icono: '🔐',
    titulo: 'Acceso con cuenta',
    texto: 'Cada persona entra con su cuenta y un rol (lector, operador o administrador) que define qué puede hacer.',
  },
];

const PASOS = [
  'Creá tu cuenta o iniciá sesión.',
  'Abrí el mapa de activos.',
  'Filtrá por estado y tocá un punto para ver su detalle.',
];

export function Home() {
  const { user } = useAuth();

  return (
    <>
      <section className="hero">
        <h1>Monitoreo geoespacial de la red eléctrica</h1>
        <p className="apple-subtitle">
          Un portal GIS para consultar la ubicación y el estado de la infraestructura energética:
          subestaciones, transformadores y postes, en un solo lugar y con acceso controlado.
        </p>
        <div className="hero-actions">
          {user ? (
            <Link to="/mapa" className="apple-button">Abrir el mapa</Link>
          ) : (
            <>
              <Link to="/registro" className="apple-button">Crear cuenta</Link>
              <Link to="/login" className="apple-button apple-button--ghost">Ya tengo cuenta</Link>
            </>
          )}
        </div>
      </section>

      <section className="features" aria-label="Características">
        {CARACTERISTICAS.map((c) => (
          <article key={c.titulo} className="apple-card">
            <div className="feature-icon" aria-hidden>{c.icono}</div>
            <h2>{c.titulo}</h2>
            <p>{c.texto}</p>
          </article>
        ))}
      </section>

      <section className="apple-card how-to" aria-label="Cómo empezar">
        <h2>Cómo empezar</h2>
        <ol className="steps">
          {PASOS.map((paso) => (
            <li key={paso}>{paso}</li>
          ))}
        </ol>
      </section>
    </>
  );
}
