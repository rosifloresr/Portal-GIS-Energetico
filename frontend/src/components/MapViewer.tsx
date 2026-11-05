import { useEffect, useMemo, useState } from 'react';
import { CircleMarker, MapContainer, Popup, TileLayer, useMap } from 'react-leaflet';
// Sin estos estilos Leaflet no puede posicionar sus capas y el mapa se ve roto.
import 'leaflet/dist/leaflet.css';
import type { ActivoEnergetico, EstadoActivo, TipoActivo } from '../types/gis';

const COLOR_ESTADO: Record<EstadoActivo, string> = {
  Operativo: '#34c759',
  'En Revision': '#ff9500',
  'En Falla': '#ff3b30',
};
const ETIQUETA_ESTADO: Record<EstadoActivo, string> = {
  Operativo: 'Operativo',
  'En Revision': 'En revisión',
  'En Falla': 'En falla',
};
const RADIO_TIPO: Record<TipoActivo, number> = { Subestacion: 14, Transformador: 10, Poste: 7 };
const ETIQUETA_TIPO: Record<TipoActivo, string> = {
  Subestacion: 'Subestación',
  Transformador: 'Transformador',
  Poste: 'Poste',
};

const ESTADOS = Object.keys(COLOR_ESTADO) as EstadoActivo[];
const TIPOS = Object.keys(RADIO_TIPO) as TipoActivo[];

// Solo se usan cuando no hay activos que enmarcar: con datos, el mapa se ajusta a ellos.
const CENTRO_POR_DEFECTO: [number, number] = [-33.3, -66.3];
const ZOOM_POR_DEFECTO = 7;

type Filtro = 'TODOS' | EstadoActivo;

function AjustarVista({ activos }: { activos: ActivoEnergetico[] }) {
  const map = useMap();
  useEffect(() => {
    if (activos.length === 0) return;
    map.fitBounds(
      activos.map((a) => [a.latitud, a.longitud] as [number, number]),
      { padding: [40, 40], maxZoom: 15 }, // maxZoom evita un acercamiento extremo si hay un solo punto
    );
  }, [activos, map]);
  return null;
}

export function PopupActivo({ activo }: { activo: ActivoEnergetico }) {
  // React escapa todo el texto: un código con HTML se muestra como texto y no se ejecuta.
  return (
    <div className="popup-content">
      <h3>{activo.codigo}</h3>
      <p><strong>Tipo:</strong> {ETIQUETA_TIPO[activo.tipo]}</p>
      <p>
        <strong>Estado:</strong>{' '}
        <span className={`status-tag status-${activo.estado.replace(' ', '-').toLowerCase()}`}>
          {ETIQUETA_ESTADO[activo.estado]}
        </span>
      </p>
      <p><strong>Coordenadas:</strong> {activo.latitud.toFixed(4)}, {activo.longitud.toFixed(4)}</p>
    </div>
  );
}

export function MapViewer({ activos }: { activos: ActivoEnergetico[] }) {
  const [filtro, setFiltro] = useState<Filtro>('TODOS');

  const visibles = useMemo(
    () => activos.filter((a) => filtro === 'TODOS' || a.estado === filtro),
    [activos, filtro],
  );
  const conteo = useMemo(
    () => Object.fromEntries(ESTADOS.map((e) => [e, activos.filter((a) => a.estado === e).length])) as Record<EstadoActivo, number>,
    [activos],
  );

  return (
    <section aria-label="Mapa de activos">
      <div className="stats">
        {ESTADOS.map((estado) => (
          <div key={estado} className="apple-card stat">
            <span className="dot" style={{ background: COLOR_ESTADO[estado] }} aria-hidden />
            <strong>{conteo[estado]}</strong>
            <span>{ETIQUETA_ESTADO[estado]}</span>
          </div>
        ))}
      </div>

      <div className="apple-card controls-card">
        <label htmlFor="filtro-estado">Filtrar por estado</label>
        <select
          id="filtro-estado"
          className="apple-select"
          value={filtro}
          onChange={(e) => setFiltro(e.target.value as Filtro)}
        >
          <option value="TODOS">Todos los activos ({activos.length})</option>
          {ESTADOS.map((estado) => (
            <option key={estado} value={estado}>{ETIQUETA_ESTADO[estado]} ({conteo[estado]})</option>
          ))}
        </select>
      </div>

      <div className="apple-card map-card">
        {/* El contenedor necesita altura explícita (ver .map-box): sin ella Leaflet mide 0 px y no dibuja nada. */}
        <div className="map-box">
          <MapContainer center={CENTRO_POR_DEFECTO} zoom={ZOOM_POR_DEFECTO} scrollWheelZoom style={{ height: '100%', width: '100%' }}>
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            <AjustarVista activos={visibles} />
            {visibles.map((activo) => (
              // CircleMarker en vez de Marker: el ícono por defecto de Leaflet se rompe al empaquetar con Vite.
              <CircleMarker
                key={activo.id_activo}
                center={[activo.latitud, activo.longitud]}
                radius={RADIO_TIPO[activo.tipo]}
                pathOptions={{ color: '#fff', weight: 2, fillColor: COLOR_ESTADO[activo.estado], fillOpacity: 0.9 }}
              >
                <Popup>
                  <PopupActivo activo={activo} />
                </Popup>
              </CircleMarker>
            ))}
          </MapContainer>
        </div>
        <ul className="legend" aria-label="Leyenda">
          <li>El color indica el estado.</li>
          {TIPOS.map((tipo) => (
            <li key={tipo}>
              <span className="legend-dot" style={{ width: RADIO_TIPO[tipo] * 2, height: RADIO_TIPO[tipo] * 2 }} aria-hidden />
              {ETIQUETA_TIPO[tipo]}
            </li>
          ))}
        </ul>
      </div>

      {activos.length === 0 && <p className="center-note">Todavía no hay activos cargados.</p>}
      {activos.length > 0 && visibles.length === 0 && (
        <p className="center-note">Ningún activo coincide con el filtro seleccionado.</p>
      )}
    </section>
  );
}
