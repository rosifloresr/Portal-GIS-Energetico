// Contrato con la API: debe coincidir con backend/app/schemas y core/catalogs.py.

export type TipoActivo = 'Transformador' | 'Poste' | 'Subestacion';
export type EstadoActivo = 'Operativo' | 'En Revision' | 'En Falla';
export type Rol = 'lector' | 'operador' | 'admin';

export interface ActivoEnergetico {
  id_activo: number;
  codigo: string;
  tipo: TipoActivo;
  estado: EstadoActivo;
  latitud: number;
  longitud: number;
  fecha_creacion: string;
}

export interface Usuario {
  id: number;
  username: string;
  email: string;
  role: Rol;
  created_at: string;
}