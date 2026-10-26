import React, { useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import type { ActivoEnergetico } from '../types/gis';

interface MapViewerProps {
  activos: ActivoEnergetico[];
}

export const MapViewer: React.FC<MapViewerProps> = ({ activos }) => {
  const [filtroEstado, setFiltroEstado] = useState<string>('TODOS');

  const activosFiltrados = activos.filter((item) =>
    filtroEstado === 'TODOS' ? true : item.estado === filtroEstado
  );

  return (
    <div>
      <div className="apple-card controls-card">
        <span className="badge-connected">● Sesión Segura Activa</span>
        <div className="filter-group">
          <label>Filtrar Estado: </label>
          <select
            className="apple-select"
            value={filtroEstado}
            onChange={(e) => setFiltroEstado(e.target.value)}
          >
            <option value="TODOS">Todos los activos</option>
            <option value="Operativo">Operativos</option>
            <option value="En Revision">En Revisión</option>
            <option value="En Falla">En Falla</option>
          </select>
        </div>
      </div>

      <div className="apple-card map-card">
        {/* Contenedor explícito con altura fija para prevenir pantallas en blanco en Leaflet */}
        <div style={{ height: '480px', width: '100%', borderRadius: '12px', overflow: 'hidden' }}>
          <MapContainer
            center={[-33.3011, -65.3412]}
            zoom={13}
            style={{ height: '100%', width: '100%' }}
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            {activosFiltrados.map((activo) => (
              <Marker
                key={activo.id_activo}
                position={[activo.latitud, activo.longitud]}
              >
                <Popup className="apple-popup">
                  <div className="popup-content">
                    <h3>{activo.codigo}</h3>
                    <p><strong>Tipo:</strong> {activo.tipo}</p>
                    <p>
                      <strong>Estado:</strong>{' '}
                      <span className={`status-tag status-${activo.estado.replace(' ', '-').toLowerCase()}`}>
                        {activo.estado}
                      </span>
                    </p>
                  </div>
                </Popup>
              </Marker>
            ))}
          </MapContainer>
        </div>
      </div>
    </div>
  );
};