import axios from 'axios';

const api = axios.create({
  baseURL: process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000',
});

// ── Places ──────────────────────────────────────────
export const getPlaces = (params) =>
  api.get('/api/places', { params }).then(r => r.data);

export const getPlaceDetail = (placeId) =>
  api.get(`/api/places/${placeId}`).then(r => r.data);

export const getRecommendedPlaces = (petWeight, minRating = 4.0) =>
  api.get('/api/places/recommend/by-pet-weight', {
    params: { pet_weight: petWeight, min_rating: minRating },
  }).then(r => r.data);

// ── Reviews ─────────────────────────────────────────
export const getReviews = (placeId) =>
  api.get(`/api/reviews/${placeId}`).then(r => r.data);

export const createReview = (data) =>
  api.post('/api/reviews', data).then(r => r.data);

// ── Pets ────────────────────────────────────────────
export const getPetsByUser = (userId) =>
  api.get(`/api/pets/user/${userId}`).then(r => r.data);

export const createPet = (data) =>
  api.post('/api/pets', data).then(r => r.data);

export const addPetOwner = (petId, userId) =>
  api.post(`/api/pets/${petId}/owner/${userId}`).then(r => r.data);

export const getRankingByBreed = (breed) =>
  api.get(`/api/pets/ranking/${encodeURIComponent(breed)}`).then(r => r.data);

// ── Users ────────────────────────────────────────────
export const createUser = (data) =>
  api.post('/api/users', data).then(r => r.data);

export const getUser = (userId) =>
  api.get(`/api/users/${userId}`).then(r => r.data);
