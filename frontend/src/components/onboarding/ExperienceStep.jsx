'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { ArrowRight, BookOpen, Code, GraduationCap, Trophy, Plus, X } from 'lucide-react';

const EXPERIENCE_LEVELS = [
  {
    id: 'complete_beginner',
    title: 'Complete Beginner',
    description: 'I\'m just starting my learning journey',
    icon: BookOpen,
    details: [
      'New to this field',
      'Looking for foundational courses',
      'Need step-by-step guidance'
    ],
    color: 'from-green-500 to-emerald-600'
  },
  {
    id: 'some_basics',
    title: 'Some Basics',
    description: 'I know a few things but want to learn more',
    icon: GraduationCap,
    details: [
      'Have basic knowledge',
      'Completed some tutorials',
      'Ready for intermediate content'
    ],
    color: 'from-blue-500 to-cyan-600'
  },
  {
    id: 'intermediate',
    title: 'Intermediate',
    description: 'I have solid knowledge and some experience',
    icon: Code,
    details: [
      'Comfortable with fundamentals',
      'Built some projects',
      'Looking to deepen expertise'
    ],
    color: 'from-purple-500 to-violet-600'
  },
  {
    id: 'advanced',
    title: 'Advanced',
    description: 'I\'m experienced and looking to master skills',
    icon: Trophy,
    details: [
      'Years of experience',
      'Looking for advanced topics',
      'Want to stay current with trends'
    ],
    color: 'from-orange-500 to-red-600'
  },
  {
    id: 'other',
    title: 'Other',
    description: 'My experience doesn\'t fit these categories',
    icon: Plus,
    details: [
      'Unique background or experience',
      'Mixed experience levels',
      'Prefer to specify manually'
    ],
    color: 'from-gray-500 to-gray-600'
  }
];

export default function ExperienceStep({ data, onDataChange, onNext }) {
  const [selectedLevel, setSelectedLevel] = useState(data.experience_level || '');
  const [customExperience, setCustomExperience] = useState(data.custom_experience || '');
  const [showCustomInput, setShowCustomInput] = useState(data.experience_level === 'other');

  const handleLevelSelect = (levelId) => {
    setSelectedLevel(levelId);
    setShowCustomInput(levelId === 'other');
    
    if (levelId === 'other') {
      onDataChange({ experience_level: levelId, custom_experience: customExperience });
    } else {
      onDataChange({ experience_level: levelId, custom_experience: '' });
      setCustomExperience('');
    }
  };

  const handleCustomExperienceChange = (value) => {
    setCustomExperience(value);
    onDataChange({ experience_level: 'other', custom_experience: value });
  };

  const canProceed = selectedLevel !== '' && (selectedLevel !== 'other' || customExperience.trim() !== '');

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
          What's your experience level?
        </h2>
        <p className="text-gray-600">
          This helps us recommend content that matches your current skill level.
        </p>
      </motion.div>

      {/* Experience levels grid */}
      <motion.div
        variants={containerVariants}
        className="grid grid-cols-1 md:grid-cols-2 gap-4"
      >
        {EXPERIENCE_LEVELS.map((level) => {
          const Icon = level.icon;
          const isSelected = selectedLevel === level.id;
          
          return (
            <motion.div
              key={level.id}
              variants={itemVariants}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <Card
                onClick={() => handleLevelSelect(level.id)}
                className={`p-6 cursor-pointer transition-all duration-300 border-2 ${
                  isSelected
                    ? 'border-blue-500 bg-blue-50 shadow-lg'
                    : 'border-gray-200 hover:border-gray-300 bg-white hover:shadow-md'
                }`}
              >
                <div className="space-y-4">
                  {/* Icon and title */}
                  <div className="flex items-center space-x-3">
                    <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${level.color} flex items-center justify-center`}>
                      <Icon className="h-6 w-6 text-white" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900">{level.title}</h3>
                      <p className="text-sm text-gray-600">{level.description}</p>
                    </div>
                    <div className={`ml-auto w-5 h-5 rounded-full border-2 flex items-center justify-center ${
                      isSelected ? 'border-blue-500 bg-blue-500' : 'border-gray-300'
                    }`}>
                      {isSelected && <div className="w-2 h-2 bg-white rounded-full" />}
                    </div>
                  </div>

                  {/* Details */}
                  <div className="space-y-2">
                    {level.details.map((detail, index) => (
                      <div key={index} className="flex items-center space-x-2">
                        <div className="w-1.5 h-1.5 bg-gray-400 rounded-full"></div>
                        <span className="text-sm text-gray-600">{detail}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </Card>
            </motion.div>
          );
        })}
      </motion.div>

      {/* Custom experience input */}
      {showCustomInput && (
        <motion.div
          variants={itemVariants}
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0 }}
          className="space-y-3"
        >
          <Card className="p-4 border-gray-300 border-dashed">
            <div className="space-y-3">
              <div className="flex items-center space-x-2">
                <Plus className="h-4 w-4 text-gray-600" />
                <h4 className="font-medium text-gray-900">Describe Your Experience</h4>
              </div>
              <Input
                placeholder="Tell us about your background and experience level..."
                value={customExperience}
                onChange={(e) => handleCustomExperienceChange(e.target.value)}
                className="w-full"
                autoFocus
              />
              <p className="text-xs text-gray-500">
                For example: "I have some coding experience but new to web development" or 
                "I'm switching careers from marketing to tech"
              </p>
            </div>
          </Card>
        </motion.div>
      )}

      {/* Help text */}
      <motion.div variants={itemVariants} className="bg-blue-50 p-4 rounded-lg">
        <div className="flex items-start space-x-3">
          <div className="w-5 h-5 bg-blue-500 rounded-full flex items-center justify-center mt-0.5">
            <span className="text-white text-xs font-bold">?</span>
          </div>
          <div>
            <h4 className="font-medium text-gray-900 mb-1">Not sure about your level?</h4>
            <p className="text-sm text-gray-600">
              Don't worry! You can always adjust this later in your settings. 
              We'll also adapt recommendations based on your learning progress.
            </p>
          </div>
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
          Please select your experience level to continue
        </motion.p>
      )}
    </motion.div>
  );
}