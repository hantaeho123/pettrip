/**
 * components/Auth/AuthModal.jsx
 * 로그인 / 회원가입 모달.
 * 탭으로 두 모드를 전환하며, 성공 시 AuthContext에 유저를 저장한다.
 */
import { useState } from "react";
import { useAuth } from "../../context/AuthContext";
import { login, register } from "../../api";
import "./AuthModal.css";

export default function AuthModal({ onClose }) {
  const { loginUser } = useAuth();
  const [mode, setMode] = useState("login"); // 'login' | 'register'
  const [form, setForm] = useState({ nickname: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const set = (k, v) => setForm({ ...form, [k]: v });

  const handleSubmit = async () => {
    setError(""); setLoading(true);
    try {
      if (mode === "register") {
        await register(form);
        // 가입 후 자동 로그인
        const res = await login({ email: form.email, password: form.password });
        loginUser(res.user);
      } else {
        const res = await login({ email: form.email, password: form.password });
        loginUser(res.user);
      }
      onClose();
    } catch (e) {
      setError(e.response?.data?.detail || "오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-overlay" onClick={onClose}>
      <div className="auth-modal" onClick={(e) => e.stopPropagation()}>
        <button className="auth-close" onClick={onClose}>✕</button>

        <div className="auth-logo">🐾 PetTrip</div>
        <div className="auth-tabs">
          <button className={mode === "login" ? "active" : ""} onClick={() => setMode("login")}>로그인</button>
          <button className={mode === "register" ? "active" : ""} onClick={() => setMode("register")}>회원가입</button>
        </div>

        <div className="auth-form">
          {mode === "register" && (
            <input placeholder="닉네임" value={form.nickname}
              onChange={(e) => set("nickname", e.target.value)} />
          )}
          <input placeholder="이메일" type="email" value={form.email}
            onChange={(e) => set("email", e.target.value)} />
          <input placeholder="비밀번호" type="password" value={form.password}
            onChange={(e) => set("password", e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSubmit()} />

          {error && <p className="auth-error">{error}</p>}

          <button className="auth-submit" onClick={handleSubmit} disabled={loading}>
            {loading ? "처리 중..." : mode === "login" ? "로그인" : "가입하기"}
          </button>
        </div>

        <p className="auth-demo">
          데모 계정: petlover1@pettrip.com / password123
        </p>
      </div>
    </div>
  );
}
