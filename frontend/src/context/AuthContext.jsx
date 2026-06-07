/**
 * context/AuthContext.jsx
 * 로그인 상태를 앱 전체에서 공유하기 위한 React Context.
 *
 * - user: 현재 로그인한 유저 정보 ({user_id, nickname, email})
 * - 로그인하면 메모리에 보관 (새로고침 시 풀리지만 과제 프로토타입엔 충분)
 * - 실제 서비스라면 JWT 토큰을 안전한 저장소에 보관
 */
import { createContext, useContext, useState } from "react";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);

  const loginUser  = (userData) => setUser(userData);
  const logoutUser = () => setUser(null);

  return (
    <AuthContext.Provider value={{ user, loginUser, logoutUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
