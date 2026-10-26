// Interfaz que mapea estrictamente el contrato expuesto por el esquema Pydantic de la API
export interface ActivoEnergetico {
  id_activo: number;
  codigo: string;
  tipo: 'Transformador' | 'Poste' | 'Subestacion';
  estado: 'Operativo' | 'En Revision' | 'En Falla';
  latitud: number;
  longitud: number;
  fecha_creacion: string;
}