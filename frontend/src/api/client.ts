import type { ActivoEnergetico, Usuario } from '../types/gis';

// Ruta relativa: en desarrollo el proxy de Vite la reenvía al backend, y así
// el navegador habla con un solo origen. VITE_API_URL permite apuntar a otro servidor.
const BASE = import.meta.env.VITE_API_URL ?? '/api/v1';

export class ApiError extends Error {
  status: number; // 0 si ni siquiera hubo respuesta (servidor caído, sin red)

  constructor(message: string, status: number) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

interface DetalleValidacion {
  loc: (string | number)[];
  msg: string;
  type: string;
  ctx?: { min_length?: number; max_length?: number };
}

const NOMBRE_CAMPO: Record<string, string> = {
  username: 'usuario',
  identificador: 'usuario',
  email: 'email',
  password: 'contraseña',
  codigo: 'código',
  tipo: 'tipo',
  estado: 'estado',
  latitud: 'latitud',
  longitud: 'longitud',
};

const PREFIJO_VALIDADOR_PROPIO = 'Value error, ';

// FastAPI devuelve los errores de validación (422) en inglés. Se traducen los
// más comunes; los validadores propios del backend ya vienen en español.
function mensajeDeValidacion(d: DetalleValidacion): string {
  const campo = `El campo ${NOMBRE_CAMPO[String(d.loc[d.loc.length - 1])] ?? 'ingresado'}`;
  switch (d.type) {
    case 'string_too_short':
      return `${campo} debe tener al menos ${d.ctx?.min_length} caracteres.`;
    case 'string_too_long':
      return `${campo} debe tener como máximo ${d.ctx?.max_length} caracteres.`;
    case 'missing':
      return `${campo} es obligatorio.`;
    case 'value_error':
      return d.msg.startsWith(PREFIJO_VALIDADOR_PROPIO)
        ? d.msg.slice(PREFIJO_VALIDADOR_PROPIO.length)
        : `${campo} no es válido.`;
    default:
      return `${campo} no es válido.`;
  }
}

function mensajeDeError(body: unknown, status: number): string {
  const detail = (body as { detail?: unknown } | null)?.detail;
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) return detail.map(mensajeDeValidacion).join(' ');
  // Sin cuerpo JSON (por ejemplo, una página de error del proxy): se infiere por el código.
  return status >= 500 ? 'El servidor tuvo un problema. Probá de nuevo en unos minutos.' : 'Error inesperado.';
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  // Solo se declara el tipo de contenido cuando hay cuerpo: evita pedidos
  // de preflight innecesarios en los GET si la API está en otro origen.
  const headers: Record<string, string> = init.body ? { 'Content-Type': 'application/json' } : {};

  let res: Response;
  try {
    // `include` envía la cookie de sesión también si la API está en otro origen.
    res = await fetch(`${BASE}${path}`, { credentials: 'include', ...init, headers });
  } catch {
    throw new ApiError('No se pudo conectar con el servidor.', 0);
  }

  if (res.status === 204) return undefined as T;
  const body: unknown = await res.json().catch(() => null);
  if (!res.ok) throw new ApiError(mensajeDeError(body, res.status), res.status);
  return body as T;
}

export const api = {
  me: () => request<Usuario>('/auth/me'),
  login: (identificador: string, password: string) =>
    request<Usuario>('/auth/login', { method: 'POST', body: JSON.stringify({ identificador, password }) }),
  register: (username: string, email: string, password: string) =>
    request<Usuario>('/auth/register', { method: 'POST', body: JSON.stringify({ username, email, password }) }),
  logout: () => request<void>('/auth/logout', { method: 'POST' }),
  activos: () => request<ActivoEnergetico[]>('/activos'),
};