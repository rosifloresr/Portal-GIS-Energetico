// El contexto, el proveedor (AuthProvider.tsx) y el hook (hooks/useAuth.ts) están
// en archivos distintos porque Vite solo recarga en caliente los archivos que
// exportan únicamente componentes; mezclarlos reinicia el estado en cada edición.
import { createContext } from 'react';
import type { Usuario } from '../types/gis';

export interface AuthState {
  user: Usuario | null;
  /** `true` mientras se averigua si ya había una sesión abierta al cargar la app. */
  cargando: boolean;
  login: (identificador: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string) => Promise<void>;
  /** Si el servidor no responde, lanza el error y la sesión local no se cierra. */
  logout: () => Promise<void>;
}

export const AuthContext = createContext<AuthState | null>(null);