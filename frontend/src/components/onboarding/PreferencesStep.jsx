'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { ArrowRight, Clock, Zap, Users, User, Building, TrendingUp, Plus } from 'lucide-react';

const LEARNING_STYLES = [
  {
    id: 'visual',
    title: 'Visual Learning',
    description: 'Charts, diagrams, and infographics',
    icon: '👁️',
    color: 'bg-purple-100 text-purple-800'
  },
  {
    id: 'hands_on',
    title: 'Hands-on Practice',
    description: 'Projects, labs, and interactive exercises',
    icon: '🛠️',
    color: 'bg-blue-100 text-blue-800'
  },
  {
    id: 'reading',
    title: 'Reading & Articles',
    description: 'Documentation, blogs, and written content',
    icon: '📚',
    color: 'bg-green-100 text-green-800'
  },
  {
    id: 'videos',
    title: 'Video Lectures',
    description: 'Structured video courses and tutorials',
    icon: '🎥',
    color: 'bg-red-100 text-red-800'
  },
  {
    id: 'interactive',
    title: 'Interactive Content',
    description: 'Quizzes, simulations, and gamified learning',
    icon: '🎮',
    color: 'bg-orange-100 text-orange-800'
  },
  {
    id: 'other_style',
    title: 'Other Learning Style',
    description: 'I prefer a different learning approach',
    icon: '➕',
    color: 'bg-gray-100 text-gray-800'
  }
];

const LEARNING_PACE = [
  {
    id: 'slow',
    title: 'Take It Slow',
    description: 'I prefer to thoroughly understand each concept',
    icon: Clock,
    details: 'Deep understanding, lots of practice'
  },
  {
    id: 'medium',
    title: 'Steady Progress',
    description: 'Balanced approach with regular learning',
    icon: TrendingUp,
    details: 'Consistent progress, balanced pace'
  },
  {
    id: 'fast',
    title: 'Fast Track',
    description: 'I want to learn quickly and efficiently',
    icon: Zap,
    details: 'Quick overview, efficient learning'
  }
];

const CAREER_STAGES = [
  {
    id: 'student',
    title: 'Student',
    description: 'Currently studying or in school',
    icon: User,
    color: 'from-green-500 to-emerald-600'
  },
  {
    id: 'career_change',
    title: 'Career Change',
    description: 'Looking to switch to a new field',
    icon: Users,
    color: 'from-blue-500 to-cyan-600'
  },
  {
    id: 'skill_upgrade',
    title: 'Skill Upgrade',
    description: 'Enhancing current skills',
    icon: TrendingUp,
    color: 'from-purple-500 to-violet-600'
  },
  {
    id: 'professional',
    title: 'Professional Growth',
    description: 'Advancing in my current career',
    icon: Building,
    color: 'from-orange-500 to-red-600'
  },
  {
    id: 'other_career',
    title: 'Other',
    description: 'My situation is different',
    icon: Users,
    color: 'from-gray-500 to-gray-600'
  }
];

const TARGET_TIMELINE = [
  {
    id: '3months',
    title: '3 Months',
    description: 'I need results quickly'
  },
  {
    id: '6months',
    title: '6 Months',
    description: 'Moderate timeline'
  },
  {
    id: '1year',
    title: '1 Year',
    description: 'I can take my time'
  },
  {
    id: 'flexible',
    title: 'Flexible',
    description: 'No specific deadline'
  }
];

export default function PreferencesStep({ data, onDataChange, onNext }) {
  const [selectedStyles, setSelectedStyles] = useState(data.learning_style || []);
  const [selectedPace, setSelectedPace] = useState(data.preferred_pace || '');
  const [selectedCareer, setSelectedCareer] = useState(data.career_stage || '');
  const [selectedTimeline, setSelectedTimeline] = useState(data.target_timeline || '');
  
  // Custom inputs for "Other" options
  const [customLearningStyle, setCustomLearningStyle] = useState(data.custom_learning_style || '');
  const [customCareerStage, setCustomCareerStage] = useState(data.custom_career_stage || '');
  const [showStyleInput, setShowStyleInput] = useState(selectedStyles.includes('other_style'));
  const [showCareerInput, setShowCareerInput] = useState(selectedCareer === 'other_career');

  const toggleStyle = (styleId) => {
    const newStyles = selectedStyles.includes(styleId)
      ? selectedStyles.filter(id => id !== styleId)
      : [...selectedStyles, styleId];
    
    setSelectedStyles(newStyles);
    setShowStyleInput(newStyles.includes('other_style'));
    
    if (!newStyles.includes('other_style')) {
      setCustomLearningStyle('');
      onDataChange({ learning_style: newStyles, custom_learning_style: '' });
    } else {
      onDataChange({ learning_style: newStyles, custom_learning_style: customLearningStyle });
    }
  };

  const handlePaceSelect = (paceId) => {
    setSelectedPace(paceId);
    onDataChange({ preferred_pace: paceId });
  };

  const handleCareerSelect = (careerId) => {
    setSelectedCareer(careerId);
    setShowCareerInput(careerId === 'other_career');
    
    if (careerId === 'other_career') {
      onDataChange({ career_stage: careerId, custom_career_stage: customCareerStage });
    } else {
      setCustomCareerStage('');
      onDataChange({ career_stage: careerId, custom_career_stage: '' });
    }
  };

  // Handlers for custom input changes
  const handleCustomStyleChange = (value) => {
    setCustomLearningStyle(value);
    onDataChange({ learning_style: selectedStyles, custom_learning_style: value });
  };

  const handleCustomCareerChange = (value) => {
    setCustomCareerStage(value);
    onDataChange({ career_stage: 'other_career', custom_career_stage: value });
  };

  const handleTimelineSelect = (timelineId) => {
    setSelectedTimeline(timelineId);
    onDataChange({ target_timeline: timelineId });
  };

  const canProceed = selectedStyles.length > 0 && selectedPace && selectedCareer && selectedTimeline;

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
      className="space-y-8"
    >
      {/* Header */}
      <motion.div variants={itemVariants} className="text-center space-y-3">
        <h2 className="text-2xl font-bold text-gray-900">
          How do you prefer to learn?
        </h2>
        <p className="text-gray-600">
          Tell us about your learning preferences to get personalized content recommendations.
        </p>
      </motion.div>

      {/* Learning Styles */}
      <motion.div variants={itemVariants} className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">Learning Styles (Select all that apply)</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {LEARNING_STYLES.map((style) => {
            const isSelected = selectedStyles.includes(style.id);
            
            return (
              <motion.div
                key={style.id}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <Card
                  onClick={() => toggleStyle(style.id)}
                  className={`p-4 cursor-pointer transition-all duration-200 border-2 ${
                    isSelected
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300 bg-white'
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <span className="text-2xl">{style.icon}</span>
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-900">{style.title}</h4>
                      <p className="text-sm text-gray-600">{style.description}</p>
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
      </motion.div>

      {/* Learning Pace */}
      <motion.div variants={itemVariants} className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">Learning Pace</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {LEARNING_PACE.map((pace) => {
            const Icon = pace.icon;
            const isSelected = selectedPace === pace.id;
            
            return (
              <motion.div
                key={pace.id}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <Card
                  onClick={() => handlePaceSelect(pace.id)}
                  className={`p-4 cursor-pointer transition-all duration-200 border-2 ${
                    isSelected
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300 bg-white'
                  }`}
                >
                  <div className="space-y-3">
                    <div className="flex items-center space-x-3">
                      <Icon className="h-6 w-6 text-blue-600" />
                      <div>
                        <h4 className="font-medium text-gray-900">{pace.title}</h4>
                        <p className="text-sm text-gray-600">{pace.description}</p>
                      </div>
                    </div>
                    <p className="text-xs text-gray-500">{pace.details}</p>
                  </div>
                </Card>
              </motion.div>
            );
          })}
        </div>
      </motion.div>

      {/* Career Stage */}
      <motion.div variants={itemVariants} className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">Career Stage</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {CAREER_STAGES.map((career) => {
            const Icon = career.icon;
            const isSelected = selectedCareer === career.id;
            
            return (
              <motion.div
                key={career.id}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <Card
                  onClick={() => handleCareerSelect(career.id)}
                  className={`p-4 cursor-pointer transition-all duration-200 border-2 ${
                    isSelected
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300 bg-white'
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${career.color} flex items-center justify-center`}>
                      <Icon className="h-5 w-5 text-white" />
                    </div>
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-900">{career.title}</h4>
                      <p className="text-sm text-gray-600">{career.description}</p>
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
      </motion.div>

      {/* Target Timeline */}
      <motion.div variants={itemVariants} className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">Target Timeline</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {TARGET_TIMELINE.map((timeline) => {
            const isSelected = selectedTimeline === timeline.id;
            
            return (
              <motion.div
                key={timeline.id}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <Card
                  onClick={() => handleTimelineSelect(timeline.id)}
                  className={`p-3 cursor-pointer transition-all duration-200 border-2 text-center ${
                    isSelected
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300 bg-white'
                  }`}
                >
                  <h4 className="font-medium text-gray-900 text-sm">{timeline.title}</h4>
                  <p className="text-xs text-gray-600 mt-1">{timeline.description}</p>
                </Card>
              </motion.div>
            );
          })}
        </div>
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
          Please complete all sections to continue
        </motion.p>
      )}
    </motion.div>
  );
}