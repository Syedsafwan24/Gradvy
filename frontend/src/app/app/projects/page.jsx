'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  FolderOpen, 
  Plus, 
  Search,
  Filter,
  ExternalLink,
  Github,
  Star,
  Eye,
  Calendar,
  Code,
  Globe,
  Share2,
  Edit,
  Trash2,
  Heart,
  Download,
  Play,
  Settings,
  Users,
  Award
} from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import ProtectedRoute from '@/components/auth/ProtectedRoute';

const ProjectsPage = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedStatus, setSelectedStatus] = useState('all');
  const [viewMode, setViewMode] = useState('grid');

  const categories = [
    { id: 'all', name: 'All Projects', count: 12 },
    { id: 'web-app', name: 'Web Applications', count: 5 },
    { id: 'mobile-app', name: 'Mobile Apps', count: 2 },
    { id: 'api', name: 'APIs & Backend', count: 3 },
    { id: 'data-science', name: 'Data Science', count: 2 },
    { id: 'open-source', name: 'Open Source', count: 4 }
  ];

  const projects = [
    {
      id: 1,
      title: 'E-commerce Platform',
      description: 'Full-stack e-commerce application with React, Node.js, and PostgreSQL. Features include user authentication, product catalog, shopping cart, and payment integration.',
      thumbnail: '/api/placeholder/400/300',
      category: 'web-app',
      status: 'completed',
      technologies: ['React', 'Node.js', 'PostgreSQL', 'Stripe', 'Tailwind CSS'],
      createdAt: '2024-01-15',
      updatedAt: '2024-02-01',
      githubUrl: 'https://github.com/user/ecommerce-platform',
      liveUrl: 'https://my-ecommerce-app.vercel.app',
      progress: 100,
      likes: 45,
      views: 1200,
      isPublic: true,
      isFeatured: true,
      collaborators: [
        { name: 'John Doe', avatar: '/api/placeholder/32/32' },
        { name: 'Jane Smith', avatar: '/api/placeholder/32/32' }
      ],
      achievements: ['Project of the Month', 'Community Choice'],
      images: [
        '/api/placeholder/600/400',
        '/api/placeholder/600/400',
        '/api/placeholder/600/400'
      ]
    },
    {
      id: 2,
      title: 'Task Management Mobile App',
      description: 'Cross-platform mobile app built with React Native for task and project management. Includes offline support and real-time synchronization.',
      thumbnail: '/api/placeholder/400/300',
      category: 'mobile-app',
      status: 'in_progress',
      technologies: ['React Native', 'Firebase', 'Redux', 'AsyncStorage'],
      createdAt: '2024-02-10',
      updatedAt: '2024-02-28',
      githubUrl: 'https://github.com/user/task-manager-app',
      liveUrl: null,
      progress: 75,
      likes: 28,
      views: 680,
      isPublic: true,
      isFeatured: false,
      collaborators: [],
      achievements: [],
      images: ['/api/placeholder/600/400']
    },
    {
      id: 3,
      title: 'Data Visualization Dashboard',
      description: 'Interactive dashboard for data visualization using D3.js and Python. Processes large datasets and provides real-time analytics insights.',
      thumbnail: '/api/placeholder/400/300',
      category: 'data-science',
      status: 'completed',
      technologies: ['Python', 'D3.js', 'Flask', 'Pandas', 'Chart.js'],
      createdAt: '2023-11-20',
      updatedAt: '2023-12-15',
      githubUrl: 'https://github.com/user/data-dashboard',
      liveUrl: 'https://data-dashboard-demo.herokuapp.com',
      progress: 100,
      likes: 67,
      views: 2100,
      isPublic: true,
      isFeatured: true,
      collaborators: [],
      achievements: ['Technical Excellence'],
      images: ['/api/placeholder/600/400', '/api/placeholder/600/400']
    },
    {
      id: 4,
      title: 'REST API for Social Media',
      description: 'Scalable REST API built with Node.js and Express for a social media platform. Includes authentication, post management, and real-time messaging.',
      thumbnail: '/api/placeholder/400/300',
      category: 'api',
      status: 'completed',
      technologies: ['Node.js', 'Express', 'MongoDB', 'Socket.io', 'JWT'],
      createdAt: '2023-10-01',
      updatedAt: '2023-11-10',
      githubUrl: 'https://github.com/user/social-api',
      liveUrl: 'https://social-api-docs.netlify.app',
      progress: 100,
      likes: 34,
      views: 950,
      isPublic: true,
      isFeatured: false,
      collaborators: [],
      achievements: [],
      images: ['/api/placeholder/600/400']
    },
    {
      id: 5,
      title: 'Machine Learning Model Trainer',
      description: 'Web application for training and deploying machine learning models without coding. Features drag-and-drop interface and automated model selection.',
      thumbnail: '/api/placeholder/400/300',
      category: 'data-science',
      status: 'in_progress',
      technologies: ['Python', 'Scikit-learn', 'TensorFlow', 'React', 'FastAPI'],
      createdAt: '2024-03-01',
      updatedAt: '2024-03-15',
      githubUrl: 'https://github.com/user/ml-trainer',
      liveUrl: null,
      progress: 40,
      likes: 19,
      views: 420,
      isPublic: false,
      isFeatured: false,
      collaborators: [
        { name: 'Alice Johnson', avatar: '/api/placeholder/32/32' }
      ],
      achievements: [],
      images: []
    },
    {
      id: 6,
      title: 'Open Source UI Component Library',
      description: 'Modern React component library with TypeScript support. Designed for accessibility and customization with extensive documentation.',
      thumbnail: '/api/placeholder/400/300',
      category: 'open-source',
      status: 'completed',
      technologies: ['React', 'TypeScript', 'Storybook', 'Rollup', 'CSS-in-JS'],
      createdAt: '2023-08-15',
      updatedAt: '2024-01-20',
      githubUrl: 'https://github.com/user/ui-components',
      liveUrl: 'https://ui-components-storybook.netlify.app',
      progress: 100,
      likes: 89,
      views: 3200,
      isPublic: true,
      isFeatured: true,
      collaborators: [
        { name: 'Bob Wilson', avatar: '/api/placeholder/32/32' },
        { name: 'Carol Brown', avatar: '/api/placeholder/32/32' },
        { name: 'David Chen', avatar: '/api/placeholder/32/32' }
      ],
      achievements: ['Open Source Star', 'Community Favorite'],
      images: ['/api/placeholder/600/400', '/api/placeholder/600/400']
    }
  ];

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-700';
      case 'in_progress': return 'bg-blue-100 text-blue-700';
      case 'paused': return 'bg-yellow-100 text-yellow-700';
      case 'planning': return 'bg-gray-100 text-gray-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  const getCategoryColor = (category) => {
    const colors = {
      'web-app': 'bg-blue-100 text-blue-700',
      'mobile-app': 'bg-green-100 text-green-700',
      'api': 'bg-purple-100 text-purple-700',
      'data-science': 'bg-orange-100 text-orange-700',
      'open-source': 'bg-pink-100 text-pink-700'
    };
    return colors[category] || 'bg-gray-100 text-gray-700';
  };

  const ProjectCard = ({ project }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -5 }}
      className="group"
    >
      <Card className="overflow-hidden hover:shadow-xl transition-all duration-300">
        <div className="relative">
          <div className="aspect-video bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
            <FolderOpen className="h-16 w-16 text-white opacity-50" />
          </div>
          
          {/* Project Status Badges */}
          <div className="absolute top-3 left-3 flex space-x-2">
            <Badge className={getStatusColor(project.status)}>
              {project.status.replace('_', ' ')}
            </Badge>
            {project.isFeatured && (
              <Badge className="bg-yellow-600 text-white">
                <Star className="h-3 w-3 mr-1" />
                Featured
              </Badge>
            )}
            {!project.isPublic && (
              <Badge variant="secondary">Private</Badge>
            )}
          </div>
          
          {/* Action Buttons */}
          <div className="absolute top-3 right-3 flex space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
            <Button
              variant="secondary"
              size="sm"
              className="h-8 w-8 p-0 bg-white/90"
            >
              <Heart className="h-4 w-4" />
            </Button>
            <Button
              variant="secondary"
              size="sm"
              className="h-8 w-8 p-0 bg-white/90"
            >
              <Share2 className="h-4 w-4" />
            </Button>
            <Button
              variant="secondary"
              size="sm"
              className="h-8 w-8 p-0 bg-white/90"
            >
              <Edit className="h-4 w-4" />
            </Button>
          </div>

          {/* Progress Bar */}
          {project.progress < 100 && (
            <div className="absolute bottom-0 left-0 right-0 bg-black/50 p-2">
              <div className="flex items-center justify-between text-white text-xs mb-1">
                <span>Progress</span>
                <span>{project.progress}%</span>
              </div>
              <Progress value={project.progress} className="h-1" />
            </div>
          )}
        </div>

        <div className="p-6">
          {/* Header */}
          <div className="flex items-start justify-between mb-3">
            <div className="flex-1">
              <div className="flex items-center space-x-2 mb-2">
                <Badge className={getCategoryColor(project.category)}>
                  {categories.find(c => c.id === project.category)?.name}
                </Badge>
              </div>
              <h3 className="font-semibold text-lg leading-tight group-hover:text-blue-600 transition-colors">
                {project.title}
              </h3>
            </div>
          </div>

          {/* Description */}
          <p className="text-gray-600 text-sm mb-4 line-clamp-3">
            {project.description}
          </p>

          {/* Technologies */}
          <div className="flex flex-wrap gap-1 mb-4">
            {project.technologies.slice(0, 3).map(tech => (
              <Badge key={tech} variant="outline" className="text-xs">
                {tech}
              </Badge>
            ))}
            {project.technologies.length > 3 && (
              <Badge variant="outline" className="text-xs">
                +{project.technologies.length - 3} more
              </Badge>
            )}
          </div>

          {/* Stats */}
          <div className="flex items-center space-x-4 text-xs text-gray-500 mb-4">
            <span className="flex items-center space-x-1">
              <Heart className="h-3 w-3" />
              <span>{project.likes}</span>
            </span>
            <span className="flex items-center space-x-1">
              <Eye className="h-3 w-3" />
              <span>{project.views}</span>
            </span>
            <span className="flex items-center space-x-1">
              <Calendar className="h-3 w-3" />
              <span>{new Date(project.updatedAt).toLocaleDateString()}</span>
            </span>
          </div>

          {/* Collaborators */}
          {project.collaborators.length > 0 && (
            <div className="flex items-center space-x-2 mb-4">
              <span className="text-xs text-gray-500">Collaborators:</span>
              <div className="flex -space-x-1">
                {project.collaborators.slice(0, 3).map((collaborator, index) => (
                  <div 
                    key={index}
                    className="w-6 h-6 bg-gray-200 rounded-full border-2 border-white flex items-center justify-center"
                    title={collaborator.name}
                  >
                    <span className="text-xs font-medium">{collaborator.name.charAt(0)}</span>
                  </div>
                ))}
                {project.collaborators.length > 3 && (
                  <div className="w-6 h-6 bg-gray-300 rounded-full border-2 border-white flex items-center justify-center">
                    <span className="text-xs">+{project.collaborators.length - 3}</span>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Achievements */}
          {project.achievements.length > 0 && (
            <div className="flex flex-wrap gap-1 mb-4">
              {project.achievements.map(achievement => (
                <Badge key={achievement} className="bg-yellow-100 text-yellow-700 text-xs">
                  <Award className="h-3 w-3 mr-1" />
                  {achievement}
                </Badge>
              ))}
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex items-center justify-between space-x-2">
            <div className="flex items-center space-x-2">
              {project.githubUrl && (
                <Button variant="outline" size="sm">
                  <Github className="h-3 w-3 mr-1" />
                  Code
                </Button>
              )}
              {project.liveUrl && (
                <Button variant="outline" size="sm">
                  <ExternalLink className="h-3 w-3 mr-1" />
                  Demo
                </Button>
              )}
            </div>
            <Button size="sm" className="bg-blue-600 hover:bg-blue-700">
              View Project
            </Button>
          </div>
        </div>
      </Card>
    </motion.div>
  );

  const filteredProjects = projects.filter(project => {
    const matchesSearch = project.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          project.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || project.category === selectedCategory;
    const matchesStatus = selectedStatus === 'all' || project.status === selectedStatus;
    
    return matchesSearch && matchesCategory && matchesStatus;
  });

  const projectStats = {
    total: projects.length,
    completed: projects.filter(p => p.status === 'completed').length,
    inProgress: projects.filter(p => p.status === 'in_progress').length,
    totalViews: projects.reduce((sum, p) => sum + p.views, 0),
    totalLikes: projects.reduce((sum, p) => sum + p.likes, 0)
  };

  return (
    <ProtectedRoute>
      <div className="space-y-6">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col lg:flex-row lg:items-center justify-between space-y-4 lg:space-y-0"
        >
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">My Projects</h1>
            <p className="text-gray-600">
              Showcase your work, track progress, and collaborate with others
            </p>
          </div>
          
          <div className="flex items-center space-x-3">
            <Button variant="outline">
              <Settings className="h-4 w-4 mr-2" />
              Portfolio Settings
            </Button>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              New Project
            </Button>
          </div>
        </motion.div>

        {/* Stats Overview */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="grid grid-cols-2 md:grid-cols-5 gap-4"
        >
          <Card className="p-4 text-center">
            <div className="text-2xl font-bold text-gray-900">{projectStats.total}</div>
            <div className="text-sm text-gray-600">Total Projects</div>
          </Card>
          <Card className="p-4 text-center">
            <div className="text-2xl font-bold text-green-600">{projectStats.completed}</div>
            <div className="text-sm text-gray-600">Completed</div>
          </Card>
          <Card className="p-4 text-center">
            <div className="text-2xl font-bold text-blue-600">{projectStats.inProgress}</div>
            <div className="text-sm text-gray-600">In Progress</div>
          </Card>
          <Card className="p-4 text-center">
            <div className="text-2xl font-bold text-purple-600">{projectStats.totalViews.toLocaleString()}</div>
            <div className="text-sm text-gray-600">Total Views</div>
          </Card>
          <Card className="p-4 text-center">
            <div className="text-2xl font-bold text-red-600">{projectStats.totalLikes}</div>
            <div className="text-sm text-gray-600">Total Likes</div>
          </Card>
        </motion.div>

        {/* Search and Filters */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="flex flex-col lg:flex-row gap-4"
        >
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              placeholder="Search projects..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
          
          <Select value={selectedCategory} onValueChange={setSelectedCategory}>
            <SelectTrigger className="lg:w-48">
              <SelectValue placeholder="Category" />
            </SelectTrigger>
            <SelectContent>
              {categories.map(category => (
                <SelectItem key={category.id} value={category.id}>
                  {category.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Select value={selectedStatus} onValueChange={setSelectedStatus}>
            <SelectTrigger className="lg:w-48">
              <SelectValue placeholder="Status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Status</SelectItem>
              <SelectItem value="completed">Completed</SelectItem>
              <SelectItem value="in_progress">In Progress</SelectItem>
              <SelectItem value="paused">Paused</SelectItem>
              <SelectItem value="planning">Planning</SelectItem>
            </SelectContent>
          </Select>

          <div className="flex items-center bg-gray-100 rounded-lg p-1">
            <Button
              variant={viewMode === 'grid' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => setViewMode('grid')}
            >
              Grid
            </Button>
            <Button
              variant={viewMode === 'list' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => setViewMode('list')}
            >
              List
            </Button>
          </div>
        </motion.div>

        {/* Projects Content */}
        <Tabs defaultValue="all-projects">
          <TabsList>
            <TabsTrigger value="all-projects">All Projects</TabsTrigger>
            <TabsTrigger value="featured">Featured</TabsTrigger>
            <TabsTrigger value="public">Public</TabsTrigger>
            <TabsTrigger value="private">Private</TabsTrigger>
          </TabsList>

          <TabsContent value="all-projects" className="mt-6">
            {filteredProjects.length === 0 ? (
              <Card className="p-12 text-center">
                <FolderOpen className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">No Projects Found</h3>
                <p className="text-gray-600 mb-6">
                  {searchTerm || selectedCategory !== 'all' || selectedStatus !== 'all'
                    ? "Try adjusting your search or filter criteria."
                    : "Start building your portfolio by creating your first project."
                  }
                </p>
                <Button>
                  <Plus className="h-4 w-4 mr-2" />
                  Create First Project
                </Button>
              </Card>
            ) : (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
              >
                {filteredProjects.map(project => (
                  <ProjectCard key={project.id} project={project} />
                ))}
              </motion.div>
            )}
          </TabsContent>

          <TabsContent value="featured" className="mt-6">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
            >
              {projects.filter(project => project.isFeatured).map(project => (
                <ProjectCard key={project.id} project={project} />
              ))}
            </motion.div>
          </TabsContent>

          <TabsContent value="public" className="mt-6">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
            >
              {projects.filter(project => project.isPublic).map(project => (
                <ProjectCard key={project.id} project={project} />
              ))}
            </motion.div>
          </TabsContent>

          <TabsContent value="private" className="mt-6">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
            >
              {projects.filter(project => !project.isPublic).map(project => (
                <ProjectCard key={project.id} project={project} />
              ))}
            </motion.div>
          </TabsContent>
        </Tabs>
      </div>
    </ProtectedRoute>
  );
};

export default ProjectsPage;