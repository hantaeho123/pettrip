/**
 * api/index.js
 * 백엔드(FastAPI)와 통신하는 모든 함수를 모아둔 모듈.
 * 컴포넌트에서는 여기 함수만 import해서 사용한다.
 */
import axios from "axios";

const BASE = process.env.REACT_APP_API_BASE_URL || "http://localhost:8000";

const api = axios.create({ baseURL: BASE });

// 업로드 이미지의 절대 경로를 만들어주는 헬퍼
export const mediaUrl = (path) => (path ? `${BASE}${path}` : null);

// ── 인증 ────────────────────────────────────────────────
export const register = (data) => api.post("/api/auth/register", data).then((r) => r.data);
export const login    = (data) => api.post("/api/auth/login", data).then((r) => r.data);
export const deleteAccount = (userId) => api.delete(`/api/auth/users/${userId}`).then((r) => r.data);

// ── 장소 ────────────────────────────────────────────────
export const getPlaces = (params) => api.get("/api/places/", { params }).then((r) => r.data);
export const getPlaceDetail = (id) => api.get(`/api/places/${id}`).then((r) => r.data);
export const recommendForPet = (petId, category) =>
  api.get(`/api/places/recommend/for-pet/${petId}`, { params: { category } }).then((r) => r.data);

// ── 리뷰 ────────────────────────────────────────────────
export const getPlaceReviews = (placeId) =>
  api.get(`/api/reviews/place/${placeId}`).then((r) => r.data);

export const createReview = (formData) =>
  api.post("/api/reviews/", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  }).then((r) => r.data);

export const deleteReview = (reviewId, userId) =>
  api.delete(`/api/reviews/${reviewId}`, { params: { user_id: userId } }).then((r) => r.data);

export const getCommunityFeed = (limit = 30) =>
  api.get("/api/reviews/feed", { params: { limit } }).then((r) => r.data);

// ── 반려동물 ────────────────────────────────────────────
export const getUserPets = (userId) => api.get(`/api/pets/user/${userId}`).then((r) => r.data);
export const createPet = (data, userId) =>
  api.post("/api/pets/", data, { params: { user_id: userId } }).then((r) => r.data);
export const addCoOwner = (petId, userId) =>
  api.post(`/api/pets/${petId}/co-owner/${userId}`).then((r) => r.data);
export const getBreedRanking = (breed) =>
  api.get(`/api/pets/ranking/${encodeURIComponent(breed)}`).then((r) => r.data);
export const getPetDiary = (petId) => api.get(`/api/pets/diary/${petId}`).then((r) => r.data);
export const getBreedList = () => api.get("/api/pets/breeds/list").then((r) => r.data);

// ── 통계 ────────────────────────────────────────────────
export const getRollup  = () => api.get("/api/stats/rollup").then((r) => r.data);
export const getSummary = () => api.get("/api/stats/summary").then((r) => r.data);

export default api;
