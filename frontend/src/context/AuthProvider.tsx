import { useCallback, useEffect, useMemo, useState, type ReactNode } from 'react';
import { api } from '../api/client';
import type { Usuario } from '../types/gis';
import { AuthContext } from './authContext';

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<Usuario | null>(null);
  const [cargando, setCargando] = useState(true);

  // La cookie de sesión es httpOnly: JavaScript no puede verla, así que la
  // única forma de saber si ya hay una sesión abierta es preguntárselo al servidor.
  useEffect(() => {
    // En desarrollo React monta el componente dos veces; la bandera evita
    // aplicar la respuesta de la primera consulta, que ya quedó descartada.
    let vigente = true;
    api
      .me()
      .then((usuario) => {
        if (vigente) setUser(usuario);
      })
      .catch(() => {
        // 401 u otro error: no hay sesión válida, se sigue como visitante.
      })
      .finally(() => {
        if (vigente) setCargando(false);
      });
    return () => {
      vigente = false;
    };
  }, []);

  const login = useCallback(async (identificador: string, password: string) => {
    setUser(await api.login(identificador, password));
  }, []);

  const register = useCallback(async (username: string, email: string, password: string) => {
    setUser(await api.register(username, email, password));
  }, []);

  const logout = useCallback(async () => {
    // No se usa `finally`: si la petición falla, la cookie sigue activa en el
    // navegador y mostrar "sesión cerrada" sería engañoso.
    await api.logout();
    setUser(null);
  }, []);

  const value = useMemo(() => ({ user, cargando, login, register, logout }), [user, cargando, login, register, logout]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
