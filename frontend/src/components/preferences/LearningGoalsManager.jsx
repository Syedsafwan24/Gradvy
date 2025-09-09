'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { 
  Target, 
  Plus, 
  X, 
  Search,
  Sparkles,
  TrendingUp,
  CheckCircle,
  AlertCircle
} from 'lucide-react';

const AVAILABLE_GOALS = [
  {
    id: 'web_dev',
    title: 'Web Development',
    description: 'HTML, CSS, JavaScript, React, Node.js',
    icon: '💻',
    category: 'Technical',
    difficulty: 'beginner',
    popular: true
  },
  {
    id: 'mobile_dev', 
    title: 'Mobile Development',
    description: 'React Native, Flutter, iOS, Android',
    icon: '📱',
    category: 'Technical',
    difficulty: 'intermediate',
    popular: false
  },
  {
    id: 'ai_ml',
    title: 'AI & Machine Learning',
    description: 'Python, TensorFlow, PyTorch, Data Science',
    icon: '🤖',
    category: 'Technical',
    difficulty: 'advanced',
    popular: true
  },
  {
    id: 'data_science',
    title: 'Data Science',
    description: 'Statistics, Python, R, Visualization',
    icon: '📊',
    category: 'Technical',
    difficulty: 'intermediate',
    popular: true
  },
  {
    id: 'devops',
    title: 'DevOps & Cloud',
    description: 'AWS, Docker, Kubernetes, CI/CD',
    icon: '☁️',
    category: 'Technical',
    difficulty: 'advanced',
    popular: false
  },
  {
    id: 'design',
    title: 'UI/UX Design',
    description: 'Figma, Adobe XD, User Research',
    icon: '🎨',
    category: 'Creative',
    difficulty: 'beginner',
    popular: false
  },
  {
    id: 'business',
    title: 'Business Skills',
    description: 'Management, Strategy, Leadership',
    icon: '💼',
    category: 'Business',
    difficulty: 'beginner',
    popular: false
  },
  {
    id: 'marketing',
    title: 'Digital Marketing',
    description: 'SEO, Social Media, Analytics',
    icon: '📈',
    category: 'Business',
    difficulty: 'beginner',
    popular: false
  },
  {
    id: 'finance',
    title: 'Finance & Accounting',
    description: 'Financial Analysis, Budgeting, Excel',
    icon: '💰',
    category: 'Business',
    difficulty: 'beginner',
    popular: false
  },
  {
    id: 'languages',
    title: 'Programming Languages',
    description: 'Python, Java, C++, Go, Rust',
    icon: '⚡',
    category: 'Technical',
    difficulty: 'intermediate',
    popular: true
  }
];

export default function LearningGoalsManager({ preferences, loading, validation, onPreferenceChange }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [customGoal, setCustomGoal] = useState('');
  const [showCustomInput, setShowCustomInput] = useState(false);
  const [filterCategory, setFilterCategory] = useState('all');

  const selectedGoals = preferences?.basic_info?.learning_goals || [];

  // Filter goals based on search and category
  const filteredGoals = AVAILABLE_GOALS.filter(goal => {
    const matchesSearch = goal.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         goal.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = filterCategory === 'all' || goal.category.toLowerCase() === filterCategory;
    return matchesSearch && matchesCategory;
  });

  const categories = ['all', 'technical', 'business', 'creative'];

  const handleGoalToggle = (goalId) => {
    const currentGoals = preferences?.basic_info?.learning_goals || [];
    const newGoals = currentGoals.includes(goalId)
      ? currentGoals.filter(id => id !== goalId)
      : [...currentGoals, goalId];
    
    // Call the parent component's preference change handler
    // This will automatically save via RTK Query
    onPreferenceChange('basic_info', { learning_goals: newGoals });
  };

  const handleAddCustomGoal = () => {
    const currentGoals = preferences?.basic_info?.learning_goals || [];
    if (customGoal.trim() && !currentGoals.includes(customGoal.trim())) {
      const newGoals = [...currentGoals, customGoal.trim()];
      onPreferenceChange('basic_info', { learning_goals: newGoals });
      setCustomGoal('');
      setShowCustomInput(false);
    }
  };

  const handleRemoveCustomGoal = (goal) => {
    const currentGoals = preferences?.basic_info?.learning_goals || [];
    const newGoals = currentGoals.filter(g => g !== goal);
    onPreferenceChange('basic_info', { learning_goals: newGoals });
  };

  const getGoalRecommendations = () => {
    const userExperience = preferences?.basic_info?.experience_level;
    
    if (!userExperience) return [];
    
    return AVAILABLE_GOALS.filter(goal => {
      // Don't recommend already selected goals
      if (selectedGoals.includes(goal.id)) return false;
      
      // Match difficulty to experience level
      if (userExperience === 'complete_beginner' && goal.difficulty === 'beginner') return true;
      if (userExperience === 'some_basics' && ['beginner', 'intermediate'].includes(goal.difficulty)) return true;
      if (userExperience === 'intermediate' && ['intermediate', 'advanced'].includes(goal.difficulty)) return true;
      if (userExperience === 'advanced') return true;
      
      return false;
    }).slice(0, 3);
  };

  const recommendations = getGoalRecommendations();

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.05 }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: { y: 0, opacity: 1 }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        {[1, 2].map((i) => (
          <Card key={i} className="animate-pulse">
            <CardHeader>
              <div className="h-4 bg-gray-200 rounded w-1/4"></div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-3 gap-3">
                {[1, 2, 3, 4, 5, 6].map((j) => (
                  <div key={j} className="h-20 bg-gray-200 rounded"></div>
                ))}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-6"
    >
      {/* Validation Feedback */}
      {validation && (
        <motion.div variants={itemVariants}>
          {validation.getFieldValidation('basic_info', 'learning_goals').hasErrors && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-start space-x-3">
              <AlertCircle className="h-5 w-5 text-red-500 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-red-700 font-medium">Learning Goals Required</p>
                <p className="text-red-600 text-sm mt-1">
                  {validation.getFieldValidation('basic_info', 'learning_goals').message}
                </p>
              </div>
            </div>
          )}
          {validation.suggestions
            .filter(s => s.field === 'learning_goals')
            .map((suggestion, index) => (
              <div key={index} className={`p-4 border rounded-lg flex items-start space-x-3 ${
                suggestion.type === 'error' ? 'bg-red-50 border-red-200' :
                suggestion.type === 'warning' ? 'bg-yellow-50 border-yellow-200' :
                'bg-blue-50 border-blue-200'
              }`}>
                <div className="flex-shrink-0 mt-0.5">
                  {suggestion.type === 'error' ? <AlertCircle className="h-5 w-5 text-red-500" /> :
                   suggestion.type === 'warning' ? <AlertCircle className="h-5 w-5 text-yellow-500" /> :
                   <Sparkles className="h-5 w-5 text-blue-500" />}
                </div>
                <div>
                  <p className={`font-medium ${
                    suggestion.type === 'error' ? 'text-red-700' :
                    suggestion.type === 'warning' ? 'text-yellow-700' :
                    'text-blue-700'
                  }`}>
                    {suggestion.message}
                  </p>
                  <p className={`text-sm mt-1 ${
                    suggestion.type === 'error' ? 'text-red-600' :
                    suggestion.type === 'warning' ? 'text-yellow-600' :
                    'text-blue-600'
                  }`}>
                    {suggestion.action}
                  </p>
                </div>
              </div>
            ))}
        </motion.div>
      )}

      {/* Current Goals Summary */}
      {selectedGoals.length > 0 && (
        <motion.div variants={itemVariants}>
          <Card className="bg-gradient-to-r from-blue-50 to-purple-50 border-blue-200">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <CheckCircle className="h-5 w-5 text-green-600" />
                <span>Your Learning Goals ({selectedGoals.length})</span>
                {validation && !validation.getFieldValidation('basic_info', 'learning_goals').hasErrors && (
                  <Badge variant="outline" className="text-green-600 border-green-200">
                    Valid
                  </Badge>
                )}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {selectedGoals.map((goal) => {
                  const goalInfo = AVAILABLE_GOALS.find(g => g.id === goal);
                  const isCustom = !goalInfo;
                  
                  return (
                    <Badge
                      key={goal}
                      variant="secondary"
                      className="bg-blue-100 text-blue-800 hover:bg-blue-200 flex items-center space-x-1"
                    >
                      {isCustom ? (
                        <>
                          <span>🎯 {goal}</span>
                          <button
                            onClick={() => handleRemoveCustomGoal(goal)}
                            className="ml-1 hover:text-red-600"
                          >
                            <X className="h-3 w-3" />
                          </button>
                        </>
                      ) : (
                        <>
                          <span>{goalInfo.icon} {goalInfo.title}</span>
                          <button
                            onClick={() => handleGoalToggle(goal)}
                            className="ml-1 hover:text-red-600"
                          >
                            <X className="h-3 w-3" />
                          </button>
                        </>
                      )}
                    </Badge>
                  );
                })}
              </div>
              
              {selectedGoals.length >= 5 && (
                <div className="mt-3 p-3 bg-green-50 rounded-lg">
                  <p className="text-sm text-green-700 flex items-center">
                    <CheckCircle className="h-4 w-4 mr-2" />
                    Great! You have a well-rounded set of learning goals.
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Smart Recommendations */}
      {recommendations.length > 0 && (
        <motion.div variants={itemVariants}>
          <Card className="border-purple-200 bg-purple-50">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Sparkles className="h-5 w-5 text-purple-600" />
                <span>Recommended for You</span>
              </CardTitle>
              <p className="text-sm text-gray-600">
                Based on your experience level: {preferences?.basic_info?.experience_level?.replace('_', ' ')}
              </p>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-3 gap-4">
                {recommendations.map((goal) => (
                  <motion.div
                    key={goal.id}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    className="p-4 bg-white rounded-lg border border-purple-200 cursor-pointer hover:border-purple-300 transition-colors"
                    onClick={() => handleGoalToggle(goal.id)}
                  >
                    <div className="flex items-start space-x-3">
                      <span className="text-2xl">{goal.icon}</span>
                      <div className="flex-1">
                        <h4 className="font-medium text-gray-900">{goal.title}</h4>
                        <p className="text-xs text-gray-600 mt-1">{goal.description}</p>
                        <div className="flex items-center space-x-2 mt-2">
                          <Badge variant="outline" className="text-xs">
                            {goal.category}
                          </Badge>
                          {goal.popular && (
                            <Badge variant="secondary" className="text-xs bg-orange-100 text-orange-700">
                              Popular
                            </Badge>
                          )}
                        </div>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Search and Filters */}
      <motion.div variants={itemVariants}>
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Target className="h-5 w-5 text-blue-600" />
              <span>Browse Learning Goals</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search learning areas..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>

            {/* Category Filters */}
            <div className="flex flex-wrap gap-2">
              {categories.map((category) => (
                <Button
                  key={category}
                  variant={filterCategory === category ? "default" : "outline"}
                  size="sm"
                  onClick={() => setFilterCategory(category)}
                  className="capitalize"
                >
                  {category}
                </Button>
              ))}
            </div>

            {/* Goals Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredGoals.map((goal) => {
                const isSelected = selectedGoals.includes(goal.id);
                
                return (
                  <motion.div
                    key={goal.id}
                    variants={itemVariants}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <div
                      onClick={() => handleGoalToggle(goal.id)}
                      className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                        isSelected
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300 bg-white'
                      }`}
                    >
                      <div className="flex items-start space-x-3">
                        <span className="text-2xl">{goal.icon}</span>
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-1">
                            <h3 className="font-medium text-gray-900">{goal.title}</h3>
                            {goal.popular && (
                              <Badge variant="outline" className="text-xs">
                                Popular
                              </Badge>
                            )}
                          </div>
                          <p className="text-sm text-gray-600 mb-2">{goal.description}</p>
                          <div className="flex items-center space-x-2">
                            <Badge variant="outline" className="text-xs">
                              {goal.category}
                            </Badge>
                            <Badge variant="outline" className="text-xs capitalize">
                              {goal.difficulty}
                            </Badge>
                          </div>
                        </div>
                        <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${
                          isSelected ? 'border-blue-500 bg-blue-500' : 'border-gray-300'
                        }`}>
                          {isSelected && <div className="w-2 h-2 bg-white rounded-full" />}
                        </div>
                      </div>
                    </div>
                  </motion.div>
                );
              })}
            </div>

            {filteredGoals.length === 0 && (
              <div className="text-center py-8">
                <AlertCircle className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                <p className="text-gray-500">No learning goals found matching your criteria.</p>
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>

      {/* Custom Goal Input */}
      <motion.div variants={itemVariants}>
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Plus className="h-5 w-5 text-green-600" />
              <span>Add Custom Goal</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {!showCustomInput ? (
              <Button
                variant="outline"
                onClick={() => setShowCustomInput(true)}
                className="w-full border-dashed border-2 border-gray-300 text-gray-600 hover:border-gray-400"
              >
                <Plus className="h-4 w-4 mr-2" />
                Add a custom learning goal
              </Button>
            ) : (
              <div className="flex space-x-2">
                <Input
                  placeholder="Enter your custom learning goal..."
                  value={customGoal}
                  onChange={(e) => setCustomGoal(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleAddCustomGoal()}
                  className="flex-1"
                  autoFocus
                />
                <Button onClick={handleAddCustomGoal} disabled={!customGoal.trim()}>
                  Add
                </Button>
                <Button
                  variant="outline"
                  onClick={() => {
                    setShowCustomInput(false);
                    setCustomGoal('');
                  }}
                >
                  Cancel
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>

      {/* Progress Tip */}
      {selectedGoals.length < 3 && (
        <motion.div variants={itemVariants}>
          <Card className="border-yellow-200 bg-yellow-50">
            <CardContent className="p-4">
              <div className="flex items-start space-x-3">
                <TrendingUp className="h-5 w-5 text-yellow-600 mt-0.5" />
                <div>
                  <h4 className="font-medium text-yellow-800">Enhance Your Learning Journey</h4>
                  <p className="text-sm text-yellow-700 mt-1">
                    Consider adding more learning goals (recommended: 3-5) to get diverse course recommendations 
                    and build a comprehensive skill set.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}
    </motion.div>
  );
}