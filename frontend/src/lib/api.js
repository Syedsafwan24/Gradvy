import axios from 'axios';
import { getCSRFToken } from './cookieUtils';

const API_BASE_URL =
	process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

const api = axios.create({
	baseURL: API_BASE_URL,
	headers: {
		'Content-Type': 'application/json',
	},
	withCredentials: true, // Include cookies in requests
});

// Request interceptor - now uses Redux store for tokens and cookies for CSRF
api.interceptors.request.use(
	(config) => {
		// Note: Access tokens are now handled by Redux/RTK Query, not localStorage
		// CSRF token from cookies for state-changing requests
		const csrfToken = getCSRFToken();
		if (csrfToken && ['post', 'put', 'patch', 'delete'].includes(config.method)) {
			config.headers['X-CSRFToken'] = csrfToken;
		}
		return config;
	},
	(error) => Promise.reject(error)
);

// Response interceptor - simplified since token refresh is handled by RTK Query
api.interceptors.response.use(
	(response) => response,
	(error) => {
		// 401 errors are now handled by RTK Query's baseQueryWithReauth
		// Just pass through the error
		return Promise.reject(error);
	}
);

export const apiService = {
	// Auth
	login: (credentials) => api.post('/auth/login/', credentials),
	register: (userData) => api.post('/auth/register/', userData),
	logout: () => api.post('/auth/logout/'),

	// Courses
	getCourses: (params) => api.get('/courses/', { params }),
	getCourse: (id) => api.get(`/courses/${id}/`),

	// Learning Paths
	getPaths: () => api.get('/paths/'),
	createPath: (pathData) => api.post('/paths/', pathData),
	getPath: (id) => api.get(`/paths/${id}/`),

	// User Profile
	getProfile: () => api.get('/profile/'),
	updateProfile: (profileData) => api.put('/profile/', profileData),

	// Assessment
	submitQuiz: (quizData) => api.post('/assessment/quiz/', quizData),
	generatePath: (assessmentData) =>
		api.post('/assessment/generate-path/', assessmentData),
};

export default api;
