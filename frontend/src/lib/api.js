import axios from 'axios';

const API_BASE_URL =
	process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

const api = axios.create({
	baseURL: API_BASE_URL,
	headers: {
		'Content-Type': 'application/json',
	},
});

// Request interceptor
api.interceptors.request.use(
	(config) => {
		const token = localStorage.getItem('token');
		if (token) {
			config.headers.Authorization = `Bearer ${token}`;
		}
		return config;
	},
	(error) => Promise.reject(error)
);

// Response interceptor
api.interceptors.response.use(
	(response) => response,
	(error) => {
		if (error.response?.status === 401) {
			localStorage.removeItem('token');
			window.location.href = '/login';
		}
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
