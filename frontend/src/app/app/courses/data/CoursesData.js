// /home/mohammed-azaan-peshmam/Desktop/Gradvy/Project/Gradvy/frontend/src/app/app/courses/data/CoursesData.js
// Static data and utility functions for courses functionality
// Extracted from massive CoursesPage component for better maintainability
// RELEVANT FILES: CourseCard.jsx, CourseFilters.jsx, CourseGrid.jsx, CoursesPage.jsx

export const categories = [
  { id: 'all', name: 'All Courses', count: 234 },
  { id: 'programming', name: 'Programming', count: 52 },
  { id: 'web-development', name: 'Web Development', count: 38 },
  { id: 'data-science', name: 'Data Science', count: 35 },
  { id: 'ai-ml', name: 'AI & Machine Learning', count: 28 },
  { id: 'cloud-computing', name: 'Cloud Computing', count: 24 },
  { id: 'mobile-development', name: 'Mobile Development', count: 22 },
  { id: 'cybersecurity', name: 'Cybersecurity', count: 18 },
  { id: 'devops', name: 'DevOps', count: 15 },
  { id: 'product-management', name: 'Product Management', count: 14 },
  { id: 'design', name: 'Design', count: 12 },
  { id: 'blockchain', name: 'Blockchain & Web3', count: 8 }
];

export const courses = [
  {
    id: 1,
    title: 'Complete React Developer Course',
    instructor: 'Sarah Chen',
    instructorAvatar: '/api/placeholder/40/40',
    description: 'Master React from fundamentals to advanced concepts including hooks, context, and testing.',
    thumbnail: '/api/placeholder/300/200',
    category: 'web-development',
    level: 'intermediate',
    duration: '40 hours',
    lessons: 156,
    students: 12500,
    rating: 4.8,
    reviews: 2100,
    price: '$89.99',
    originalPrice: '$159.99',
    tags: ['React', 'JavaScript', 'Frontend'],
    isEnrolled: false,
    isFavorite: false,
    progress: 0,
    lastUpdated: '2024-01-15',
    certificateAvailable: true
  },
  {
    id: 2,
    title: 'Python for Data Science Masterclass',
    instructor: 'Dr. Michael Rodriguez',
    instructorAvatar: '/api/placeholder/40/40',
    description: 'Learn Python programming for data analysis, visualization, and machine learning.',
    thumbnail: '/api/placeholder/300/200',
    category: 'data-science',
    level: 'beginner',
    duration: '35 hours',
    lessons: 128,
    students: 8900,
    rating: 4.9,
    reviews: 1650,
    price: '$79.99',
    originalPrice: '$139.99',
    tags: ['Python', 'Data Science', 'Machine Learning'],
    isEnrolled: true,
    isFavorite: true,
    progress: 45,
    lastUpdated: '2024-01-20',
    certificateAvailable: true
  },
  {
    id: 3,
    title: 'Full Stack JavaScript Development',
    instructor: 'Alex Thompson',
    instructorAvatar: '/api/placeholder/40/40',
    description: 'Build complete web applications using Node.js, Express, MongoDB, and React.',
    thumbnail: '/api/placeholder/300/200',
    category: 'web-development',
    level: 'advanced',
    duration: '60 hours',
    lessons: 220,
    students: 15600,
    rating: 4.7,
    reviews: 2800,
    price: '$119.99',
    originalPrice: '$199.99',
    tags: ['JavaScript', 'Node.js', 'Full Stack'],
    isEnrolled: false,
    isFavorite: false,
    progress: 0,
    lastUpdated: '2024-01-10',
    certificateAvailable: true
  },
  {
    id: 4,
    title: 'Mobile App Development with React Native',
    instructor: 'Emma Wilson',
    instructorAvatar: '/api/placeholder/40/40',
    description: 'Create cross-platform mobile applications using React Native and modern tools.',
    thumbnail: '/api/placeholder/300/200',
    category: 'mobile-development',
    level: 'intermediate',
    duration: '45 hours',
    lessons: 180,
    students: 9800,
    rating: 4.6,
    reviews: 1450,
    price: '$99.99',
    originalPrice: '$179.99',
    tags: ['React Native', 'Mobile', 'JavaScript'],
    isEnrolled: true,
    isFavorite: false,
    progress: 25,
    lastUpdated: '2024-01-12',
    certificateAvailable: true
  },
  {
    id: 5,
    title: 'Machine Learning with Python',
    instructor: 'Prof. David Kim',
    instructorAvatar: '/api/placeholder/40/40',
    description: 'Deep dive into machine learning algorithms, neural networks, and AI applications.',
    thumbnail: '/api/placeholder/300/200',
    category: 'ai-ml',
    level: 'advanced',
    duration: '50 hours',
    lessons: 165,
    students: 7200,
    rating: 4.8,
    reviews: 1100,
    price: '$129.99',
    originalPrice: '$219.99',
    tags: ['Machine Learning', 'Python', 'AI'],
    isEnrolled: false,
    isFavorite: true,
    progress: 0,
    lastUpdated: '2024-01-18',
    certificateAvailable: true
  }
];

// Helper functions for course styling and categorization
export const getLevelColor = (level) => {
  switch (level) {
    case 'beginner': return 'bg-green-100 text-green-700';
    case 'intermediate': return 'bg-yellow-100 text-yellow-700';
    case 'advanced': return 'bg-red-100 text-red-700';
    default: return 'bg-gray-100 text-gray-700';
  }
};

export const getCategoryColor = (category) => {
  const colors = {
    'programming': 'bg-blue-100 text-blue-700',
    'web-development': 'bg-green-100 text-green-700',
    'data-science': 'bg-purple-100 text-purple-700',
    'ai-ml': 'bg-violet-100 text-violet-700',
    'cloud-computing': 'bg-sky-100 text-sky-700',
    'mobile-development': 'bg-orange-100 text-orange-700',
    'cybersecurity': 'bg-red-100 text-red-700',
    'devops': 'bg-indigo-100 text-indigo-700',
    'product-management': 'bg-emerald-100 text-emerald-700',
    'design': 'bg-pink-100 text-pink-700',
    'blockchain': 'bg-yellow-100 text-yellow-700'
  };
  return colors[category] || 'bg-gray-100 text-gray-700';
};

// Derived data helpers
export const getFeaturedCourses = () => courses.slice(0, 3);
export const getEnrolledCourses = () => courses.filter(course => course.isEnrolled);

// Filter course logic
export const filterCourses = (courses, { searchTerm, selectedCategory, selectedLevel }) => {
  return courses.filter(course => {
    const matchesSearch = course.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          course.instructor.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          course.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || course.category === selectedCategory;
    const matchesLevel = selectedLevel === 'all' || course.level === selectedLevel;
    
    return matchesSearch && matchesCategory && matchesLevel;
  });
};