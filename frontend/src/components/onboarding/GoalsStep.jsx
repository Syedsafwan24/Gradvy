'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { ArrowRight, Search, Plus, X } from 'lucide-react';

const LEARNING_GOALS = [
  {
    id: 'web_dev',
    title: 'Web Development',
    description: 'HTML, CSS, JavaScript, React, Node.js',
    icon: '💻',
    popular: true
  },
  {
    id: 'mobile_dev', 
    title: 'Mobile Development',
    description: 'React Native, Flutter, iOS, Android',
    icon: '📱',
    popular: false
  },
  {
    id: 'ai_ml',
    title: 'AI & Machine Learning',
    description: 'Python, TensorFlow, PyTorch, Data Science',
    icon: '🤖',
    popular: true
  },
  {
    id: 'data_science',
    title: 'Data Science',
    description: 'Statistics, Python, R, Visualization',
    icon: '📊',
    popular: true
  },
  {
    id: 'devops',
    title: 'DevOps & Cloud',
    description: 'AWS, Docker, Kubernetes, CI/CD',
    icon: '☁️',
    popular: false
  },
  {
    id: 'design',
    title: 'UI/UX Design',
    description: 'Figma, Adobe XD, User Research',
    icon: '🎨',
    popular: false
  },
  {
    id: 'business',
    title: 'Business Skills',
    description: 'Management, Strategy, Leadership',
    icon: '💼',
    popular: false
  },
  {
    id: 'marketing',
    title: 'Digital Marketing',
    description: 'SEO, Social Media, Analytics',
    icon: '📈',
    popular: false
  },
  {
    id: 'finance',
    title: 'Finance & Accounting',
    description: 'Financial Analysis, Budgeting, Excel',
    icon: '💰',
    popular: false
  },
  {
    id: 'languages',
    title: 'Programming Languages',
    description: 'Python, Java, C++, Go, Rust',
    icon: '⚡',
    popular: true
  }
];

export default function GoalsStep({ data, onDataChange, onNext }) {
  const [selectedGoals, setSelectedGoals] = useState(data.learning_goals || []);
  const [searchTerm, setSearchTerm] = useState('');
  const [customGoal, setCustomGoal] = useState('');
  const [showCustomInput, setShowCustomInput] = useState(false);

  // Filter goals based on search
  const filteredGoals = LEARNING_GOALS.filter(goal =>
    goal.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    goal.description.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Handle goal selection
  const toggleGoal = (goalId) => {
    const newSelectedGoals = selectedGoals.includes(goalId)
      ? selectedGoals.filter(id => id !== goalId)
      : [...selectedGoals, goalId];
    
    setSelectedGoals(newSelectedGoals);
    onDataChange({ learning_goals: newSelectedGoals });
  };

  // Add custom goal
  const addCustomGoal = () => {
    if (customGoal.trim() && !selectedGoals.includes(customGoal.trim())) {
      const newSelectedGoals = [...selectedGoals, customGoal.trim()];
      setSelectedGoals(newSelectedGoals);
      onDataChange({ learning_goals: newSelectedGoals });
      setCustomGoal('');
      setShowCustomInput(false);
    }
  };

  // Remove custom goal
  const removeCustomGoal = (goal) => {
    const newSelectedGoals = selectedGoals.filter(g => g !== goal);
    setSelectedGoals(newSelectedGoals);
    onDataChange({ learning_goals: newSelectedGoals });
  };

  const canProceed = selectedGoals.length > 0;

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.1 }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: { y: 0, opacity: 1 }
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-6"
    >
      {/* Header */}
      <motion.div variants={itemVariants} className="text-center space-y-3">
        <h2 className="text-2xl font-bold text-gray-900">
          What do you want to learn?
        </h2>
        <p className="text-gray-600">
          Select all areas that interest you. We'll use this to personalize your learning path.
        </p>
      </motion.div>

      {/* Search */}
      <motion.div variants={itemVariants} className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
        <Input
          placeholder="Search learning areas..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="pl-10"
        />
      </motion.div>

      {/* Selected goals summary */}
      {selectedGoals.length > 0 && (
        <motion.div variants={itemVariants} className="bg-blue-50 p-4 rounded-lg">
          <h3 className="font-medium text-gray-900 mb-2">
            Selected ({selectedGoals.length}):
          </h3>
          <div className="flex flex-wrap gap-2">
            {selectedGoals.map((goal) => {
              const goalInfo = LEARNING_GOALS.find(g => g.id === goal);
              const isCustom = !goalInfo;
              
              return (
                <Badge
                  key={goal}
                  variant="secondary"
                  className="bg-blue-100 text-blue-800 hover:bg-blue-200"
                >
                  {isCustom ? goal : `${goalInfo.icon} ${goalInfo.title}`}
                  {isCustom && (
                    <button
                      onClick={() => removeCustomGoal(goal)}
                      className="ml-1 hover:text-red-600"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  )}
                </Badge>
              );
            })}
          </div>
        </motion.div>
      )}

      {/* Goals grid */}
      <motion.div
        variants={containerVariants}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
      >
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
                onClick={() => toggleGoal(goal.id)}
                className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                  isSelected
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300 bg-white'
                }`}
              >
                <div className="flex items-start space-x-3">
                  <span className="text-2xl">{goal.icon}</span>
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <h3 className="font-medium text-gray-900">{goal.title}</h3>
                      {goal.popular && (
                        <Badge variant="outline" className="text-xs">
                          Popular
                        </Badge>
                      )}
                    </div>
                    <p className="text-sm text-gray-600 mt-1">{goal.description}</p>
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
      </motion.div>

      {/* Custom goal input */}
      <motion.div variants={itemVariants} className="space-y-3">
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
              onKeyPress={(e) => e.key === 'Enter' && addCustomGoal()}
              className="flex-1"
              autoFocus
            />
            <Button onClick={addCustomGoal} disabled={!customGoal.trim()}>
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
      </motion.div>

      {/* Navigation */}
      <motion.div variants={itemVariants} className="flex justify-between pt-6">
        <div></div> {/* Spacer */}
        <Button
          onClick={onNext}
          disabled={!canProceed}
          size="lg"
          className="bg-blue-600 hover:bg-blue-700"
        >
          Continue
          <ArrowRight className="ml-2 h-5 w-5" />
        </Button>
      </motion.div>

      {!canProceed && (
        <motion.p
          variants={itemVariants}
          className="text-center text-sm text-gray-500"
        >
          Please select at least one learning goal to continue
        </motion.p>
      )}
    </motion.div>
  );
}