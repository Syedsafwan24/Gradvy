'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ArrowRight, Clock, Zap, BookOpen, TrendingUp, User } from 'lucide-react';
import { useSaveOnboardingProgressMutation } from '@/services/preferencesApi';

// Simplified, most popular learning goals for quick onboarding
const QUICK_LEARNING_GOALS = [
  {
    id: 'web_dev',
    title: 'Web Development',
    description: 'HTML, CSS, JavaScript, React',
    icon: '💻',
    popular: true
  },
  {
    id: 'ai_ml',
    title: 'AI & Machine Learning',
    description: 'Python, TensorFlow, Data Science',
    icon: '🤖',
    popular: true
  },
  {
    id: 'data_science',
    title: 'Data Science',
    description: 'Statistics, Python, Visualization',
    icon: '📊',
    popular: true
  },
  {
    id: 'languages',
    title: 'Programming Languages',
    description: 'Python, Java, C++, Go',
    icon: '⚡',
    popular: true
  }
];

// Simplified experience levels
const QUICK_EXPERIENCE_LEVELS = [
  {
    id: 'complete_beginner',
    title: 'Complete Beginner',
    description: 'Just starting out',
    icon: BookOpen,
    color: 'from-green-500 to-emerald-600'
  },
  {
    id: 'some_basics',
    title: 'Some Experience',
    description: 'Know the basics',
    icon: User,
    color: 'from-blue-500 to-cyan-600'
  },
  {
    id: 'intermediate',
    title: 'Experienced',
    description: 'Comfortable with fundamentals',
    icon: TrendingUp,
    color: 'from-purple-500 to-violet-600'
  }
];

// Simplified time availability
const QUICK_TIME_OPTIONS = [
  {
    id: '1-2hrs',
    title: '1-2 hours/week',
    description: 'Light learning schedule',
    icon: Clock
  },
  {
    id: '3-5hrs',
    title: '3-5 hours/week',
    description: 'Regular learning schedule',
    icon: Clock
  },
  {
    id: '5+hrs',
    title: '5+ hours/week',
    description: 'Intensive learning schedule',
    icon: Zap
  }
];

// Top learning styles for quick selection
const QUICK_LEARNING_STYLES = [
  {
    id: 'videos',
    title: 'Video Courses',
    description: 'Structured video lectures',
    icon: '🎥'
  },
  {
    id: 'hands_on',
    title: 'Hands-on Practice',
    description: 'Projects and exercises',
    icon: '🛠️'
  },
  {
    id: 'reading',
    title: 'Reading & Articles',
    description: 'Documentation and guides',
    icon: '📚'
  }
];

export default function QuickOnboardingStep({ 
  data = {}, 
  onDataChange, 
  onComplete, 
  onSkip,
  isLoading = false 
}) {
  const [selectedGoal, setSelectedGoal] = useState(data.primary_learning_goal || '');
  const [selectedExperience, setSelectedExperience] = useState(data.experience_level || '');
  const [selectedTime, setSelectedTime] = useState(data.time_availability || '');
  const [selectedStyle, setSelectedStyle] = useState(data.primary_learning_style || '');
  
  const [currentStep, setCurrentStep] = useState(0);
  const totalSteps = 4;
  
  // Progressive saving
  const [saveProgress, { isLoading: isSaving }] = useSaveOnboardingProgressMutation();

  // Update data when selections change
  const updateData = (field, value) => {
    const newData = {
      ...data,
      [field]: value
    };
    onDataChange(newData);
  };

  // Save progress after each step
  const saveStepProgress = async (stepData) => {
    try {
      await saveProgress({
        step: currentStep + 1,
        data: stepData,
        timestamp: new Date().toISOString(),
        type: 'quick_onboarding'
      });
    } catch (error) {
      console.warn('Failed to save progress:', error);
    }
  };

  const handleGoalSelect = async (goalId) => {
    setSelectedGoal(goalId);
    const newData = { ...data, primary_learning_goal: goalId };
    updateData('primary_learning_goal', goalId);
    await saveStepProgress(newData);
  };

  const handleExperienceSelect = async (experienceId) => {
    setSelectedExperience(experienceId);
    const newData = { ...data, experience_level: experienceId };
    updateData('experience_level', experienceId);
    await saveStepProgress(newData);
  };

  const handleTimeSelect = async (timeId) => {
    setSelectedTime(timeId);
    const newData = { ...data, time_availability: timeId };
    updateData('time_availability', timeId);
    await saveStepProgress(newData);
  };

  const handleStyleSelect = async (styleId) => {
    setSelectedStyle(styleId);
    const newData = { ...data, primary_learning_style: styleId };
    updateData('primary_learning_style', styleId);
    await saveStepProgress(newData);
  };

  const handleNext = () => {
    if (currentStep < totalSteps - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      onComplete();
    }
  };

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const canProceed = () => {
    switch (currentStep) {
      case 0: return selectedGoal !== '';
      case 1: return selectedExperience !== '';
      case 2: return selectedTime !== '';
      case 3: return selectedStyle !== '';
      default: return false;
    }
  };

  const getStepTitle = () => {
    switch (currentStep) {
      case 0: return "What do you want to learn?";
      case 1: return "What's your experience level?";
      case 2: return "How much time do you have?";
      case 3: return "How do you prefer to learn?";
      default: return "Quick Setup";
    }
  };

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
        <div className="flex items-center justify-center space-x-2 text-sm text-gray-500">
          <span>Quick Setup</span>
          <span>•</span>
          <span>Step {currentStep + 1} of {totalSteps}</span>
        </div>
        <h2 className="text-3xl font-bold text-gray-900">
          {getStepTitle()}
        </h2>
        <p className="text-gray-600">
          Help us personalize your learning experience
        </p>
        
        {/* Progress Bar */}
        <div className="w-full max-w-md mx-auto bg-gray-200 rounded-full h-2">
          <div
            className="bg-blue-500 h-2 rounded-full transition-all duration-300"
            style={{ width: `${((currentStep + 1) / totalSteps) * 100}%` }}
          />
        </div>
      </motion.div>

      {/* Step Content */}
      <motion.div variants={itemVariants} className="min-h-[500px]">
        {/* Step 1: Learning Goals */}
        {currentStep === 0 && (
          <div className="space-y-6">
            <div className="text-center">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">What would you like to learn?</h3>
              <p className="text-sm text-gray-600">Choose your primary area of interest</p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {QUICK_LEARNING_GOALS.map((goal) => {
                const isSelected = selectedGoal === goal.id;
                
                return (
                  <motion.div
                    key={goal.id}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <Card
                      onClick={() => handleGoalSelect(goal.id)}
                      className={`p-6 cursor-pointer transition-all duration-200 border-2 ${
                        isSelected
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300 bg-white'
                      }`}
                    >
                      <div className="flex items-center space-x-3">
                        <span className="text-2xl">{goal.icon}</span>
                        <div className="flex-1">
                          <h3 className="font-medium text-gray-900">{goal.title}</h3>
                          <p className="text-sm text-gray-600">{goal.description}</p>
                        </div>
                        <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${
                          isSelected ? 'border-blue-500 bg-blue-500' : 'border-gray-300'
                        }`}>
                          {isSelected && <div className="w-2 h-2 bg-white rounded-full" />}
                        </div>
                      </div>
                    </Card>
                  </motion.div>
                );
              })}
            </div>
          </div>
        )}

        {/* Step 2: Experience Level */}
        {currentStep === 1 && (
          <div className="space-y-6">
            <div className="text-center">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">What's your current level?</h3>
              <p className="text-sm text-gray-600">This helps us recommend the right difficulty</p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {QUICK_EXPERIENCE_LEVELS.map((level) => {
                const Icon = level.icon;
                const isSelected = selectedExperience === level.id;
                
                return (
                  <motion.div
                    key={level.id}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <Card
                      onClick={() => handleExperienceSelect(level.id)}
                      className={`p-6 cursor-pointer transition-all duration-300 border-2 ${
                        isSelected
                          ? 'border-blue-500 bg-blue-50 shadow-lg'
                          : 'border-gray-200 hover:border-gray-300 bg-white hover:shadow-md'
                      }`}
                    >
                      <div className="text-center space-y-3">
                        <div className={`w-12 h-12 mx-auto rounded-lg bg-gradient-to-br ${level.color} flex items-center justify-center`}>
                          <Icon className="h-6 w-6 text-white" />
                        </div>
                        <div>
                          <h3 className="font-semibold text-gray-900">{level.title}</h3>
                          <p className="text-sm text-gray-600">{level.description}</p>
                        </div>
                      </div>
                    </Card>
                  </motion.div>
                );
              })}
            </div>
          </div>
        )}

        {/* Step 3: Time Availability */}
        {currentStep === 2 && (
          <div className="space-y-6">
            <div className="text-center">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">How much time can you dedicate?</h3>
              <p className="text-sm text-gray-600">This helps us find courses that fit your schedule</p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {QUICK_TIME_OPTIONS.map((timeOption) => {
                const Icon = timeOption.icon;
                const isSelected = selectedTime === timeOption.id;
                
                return (
                  <motion.div
                    key={timeOption.id}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <Card
                      onClick={() => handleTimeSelect(timeOption.id)}
                      className={`p-6 cursor-pointer transition-all duration-300 border-2 ${
                        isSelected
                          ? 'border-blue-500 bg-blue-50 shadow-lg'
                          : 'border-gray-200 hover:border-gray-300 bg-white hover:shadow-md'
                      }`}
                    >
                      <div className="text-center space-y-3">
                        <div className="w-12 h-12 mx-auto bg-blue-100 rounded-lg flex items-center justify-center">
                          <Icon className="h-6 w-6 text-blue-600" />
                        </div>
                        <div>
                          <h3 className="font-semibold text-gray-900">{timeOption.title}</h3>
                          <p className="text-sm text-gray-600">{timeOption.description}</p>
                        </div>
                      </div>
                    </Card>
                  </motion.div>
                );
              })}
            </div>
          </div>
        )}

        {/* Step 4: Learning Style */}
        {currentStep === 3 && (
          <div className="space-y-6">
            <div className="text-center">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">How do you learn best?</h3>
              <p className="text-sm text-gray-600">Choose your preferred learning style</p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {QUICK_LEARNING_STYLES.map((style) => {
                const isSelected = selectedStyle === style.id;
                
                return (
                  <motion.div
                    key={style.id}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale:0.98 }}
                  >
                    <Card
                      onClick={() => handleStyleSelect(style.id)}
                      className={`p-6 cursor-pointer transition-all duration-300 border-2 ${
                        isSelected
                          ? 'border-blue-500 bg-blue-50 shadow-lg'
                          : 'border-gray-200 hover:border-gray-300 bg-white hover:shadow-md'
                      }`}
                    >
                      <div className="text-center space-y-3">
                        <span className="text-3xl">{style.icon}</span>
                        <div>
                          <h3 className="font-semibold text-gray-900">{style.title}</h3>
                          <p className="text-sm text-gray-600">{style.description}</p>
                        </div>
                      </div>
                    </Card>
                  </motion.div>
                );
              })}
            </div>
          </div>
        )}
      </motion.div>

      {/* Navigation */}
      <motion.div variants={itemVariants} className="flex justify-between items-center pt-6">
        <div className="flex space-x-3">
          {currentStep > 0 && (
            <Button
              variant="outline"
              onClick={handleBack}
              disabled={isLoading}
            >
              Back
            </Button>
          )}
          
          {onSkip && (
            <Button
              variant="ghost"
              onClick={onSkip}
              disabled={isLoading}
              className="text-gray-500 hover:text-gray-700"
            >
              Skip for now
            </Button>
          )}
        </div>

        <div className="flex items-center space-x-3">
          {isSaving && (
            <div className="text-sm text-gray-500 flex items-center">
              <span className="animate-spin mr-2">💾</span>
              Saving progress...
            </div>
          )}
          
          <Button
            onClick={handleNext}
            disabled={!canProceed() || isLoading}
            className="bg-blue-600 hover:bg-blue-700"
          >
            {currentStep === totalSteps - 1 ? (
              isLoading ? (
                <>
                  <span className="animate-spin mr-2">⏳</span>
                  Completing...
                </>
              ) : (
                <>
                  Complete Setup
                  <ArrowRight className="ml-2 h-4 w-4" />
                </>
              )
            ) : (
              <>
                Continue
                <ArrowRight className="ml-2 h-4 w-4" />
              </>
            )}
          </Button>
        </div>
      </motion.div>

      {/* Progress Summary */}
      {currentStep === totalSteps - 1 && (
        <motion.div 
          variants={itemVariants}
          className="bg-blue-50 p-4 rounded-lg"
        >
          <h3 className="font-medium text-gray-900 mb-2">Your Quick Profile:</h3>
          <div className="flex flex-wrap gap-2">
            {selectedGoal && (
              <Badge variant="secondary" className="bg-blue-100 text-blue-800">
                {QUICK_LEARNING_GOALS.find(g => g.id === selectedGoal)?.title}
              </Badge>
            )}
            {selectedExperience && (
              <Badge variant="secondary" className="bg-green-100 text-green-800">
                {QUICK_EXPERIENCE_LEVELS.find(e => e.id === selectedExperience)?.title}
              </Badge>
            )}
            {selectedTime && (
              <Badge variant="secondary" className="bg-purple-100 text-purple-800">
                {QUICK_TIME_OPTIONS.find(t => t.id === selectedTime)?.title}
              </Badge>
            )}
            {selectedStyle && (
              <Badge variant="secondary" className="bg-orange-100 text-orange-800">
                {QUICK_LEARNING_STYLES.find(s => s.id === selectedStyle)?.title}
              </Badge>
            )}
          </div>
        </motion.div>
      )}
    </motion.div>
  );
}