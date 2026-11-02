import React from 'react';

interface HeaderProps {
  isAuthenticated: boolean;
  onLogout?: () => void;
}

export const Header: React.FC<HeaderProps> = ({ isAuthenticated, onLogout }) => (
  <header className="apple-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
    <div>
      <h1 style={{ margin: 0, fontSize: '28px' }}>Portal de Infraestructura Energética</h1>
      <p className="apple-subtitle" style={{ margin: 0 }}>Monitoreo de Red Eléctrica & Incidencias GIS</p>
    </div>
    
    {/* El botón de logout solo se muestra si el usuario está autenticado */}
    {isAuthenticated && onLogout && (
      <button 
        onClick={onLogout}
        style={{
          background: '#ff3b30',
          color: 'white',
          border: 'none',
          padding: '8px 16px',
          borderRadius: '980px',
          cursor: 'pointer',
          fontSize: '14px',
          fontWeight: 500,
          transition: 'opacity 0.2s'
        }}
      >
        Cerrar Sesión
      </button>
    )}
  </header>
);