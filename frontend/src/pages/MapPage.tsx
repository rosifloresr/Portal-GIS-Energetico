import { useEffect, useState } from 'react';
import { api, ApiError } from '../api/client';
import { MapViewer } from '../components/MapViewer';
import { useAuth } from '../hooks/useAuth';
import type { ActivoEnergetico } from '../types/gis';

export function MapPage() {
  const { logout } = useAuth();
  const [activos, setActivos] = useState<ActivoEnergetico[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [cargando, setCargando] = useState(true);
  // Cambiar este número vuelve a ejecutar la carga (botón "Reintentar").
  const [intento, setIntento] = useState(0);

  useEffect(() => {
    // Si la persona sale de la página o reintenta antes de que responda el
    // servidor, la respuesta vieja se descarta.
    let vigente = true;
    api
      .activos()
      .then((datos) => {
        if (vigente) setActivos(datos);
      })
      .catch(async (err: unknown) => {
        if (err instanceof ApiError && err.status === 401) {
          // La sesión venció. Al cerrar la local, ProtectedRoute lleva al login.
          try {
            await logout();
            return;
          } catch {
            // Si tampoco se pudo cerrar, se muestra el error de abajo.
          }
        }
        if (vigente) setError(err instanceof Error ? err.message : 'No se pudieron cargar los activos.');
      })
      .finally(() => {
        if (vigente) setCargando(false);
      });
    return () => {
      vigente = false;
    };
  }, [intento, logout]);

  const reintentar = () => {
    setError(null);
    setCargando(true);
    setIntento((n) => n + 1);
  };

  return (
    <>
      <h1>Mapa de activos</h1>
      <p className="apple-subtitle">
        Cada punto es un activo de la red. El color indica su estado; tocá uno para ver el detalle.
      </p>
      {error && (
        <div className="error-message" role="alert">
          <p>{error}</p>
          <button className="apple-button apple-button--ghost" onClick={reintentar}>Reintentar</button>
        </div>
      )}
      {cargando ? <p className="center-note">Cargando activos…</p> : !error && <MapViewer activos={activos} />}
    </>
  );
}
