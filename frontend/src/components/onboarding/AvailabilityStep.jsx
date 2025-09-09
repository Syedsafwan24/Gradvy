'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ArrowRight, Clock, Youtube, BookOpen, Play, FileText, Headphones, Globe } from 'lucide-react';

const TIME_AVAILABILITY = [
  {
    id: '1-2hrs',
    title: '1-2 hours per week',
    description: 'Light learning schedule',
    icon: Clock,
    color: 'from-green-500 to-emerald-600',
    recommendation: 'Perfect for short courses and bite-sized content'
  },
  {
    id: '3-5hrs',
    title: '3-5 hours per week',
    description: 'Moderate learning schedule',
    icon: Clock,
    color: 'from-blue-500 to-cyan-600',
    recommendation: 'Great for structured courses and regular progress'
  },
  {
    id: '5+hrs',
    title: '5+ hours per week',
    description: 'Intensive learning schedule',
    icon: Clock,
    color: 'from-purple-500 to-violet-600',
    recommendation: 'Ideal for comprehensive courses and fast progress'
  }
];

const PREFERRED_PLATFORMS = [
  {
    id: 'udemy',
    title: 'Udemy',
    description: 'Comprehensive courses with lifetime access',
    icon: '🎓',
    color: 'bg-purple-100 text-purple-800'
  },
  {
    id: 'coursera',
    title: 'Coursera',
    description: 'University-level courses and specializations',
    icon: '🏛️',
    color: 'bg-blue-100 text-blue-800'
  },
  {
    id: 'youtube',
    title: 'YouTube',
    description: 'Free tutorials and educational videos',
    icon: '📺',
    color: 'bg-red-100 text-red-800'
  },
  {
    id: 'edx',
    title: 'edX',
    description: 'Courses from top universities',
    icon: '🎯',
    color: 'bg-green-100 text-green-800'
  },
  {
    id: 'pluralsight',
    title: 'Pluralsight',
    description: 'Technology and creative skills',
    icon: '💡',
    color: 'bg-orange-100 text-orange-800'
  },
  {
    id: 'linkedin_learning',
    title: 'LinkedIn Learning',
    description: 'Professional development courses',
    icon: '💼',
    color: 'bg-cyan-100 text-cyan-800'
  }
];

const CONTENT_TYPES = [
  {
    id: 'video',
    title: 'Video Courses',
    description: 'Structured video lessons',
    icon: Play,
    color: 'bg-red-100 text-red-800'
  },
  {
    id: 'article',
    title: 'Articles & Blogs',
    description: 'Written tutorials and guides',
    icon: FileText,
    color: 'bg-blue-100 text-blue-800'
  },
  {
    id: 'interactive',
    title: 'Interactive Content',
    description: 'Hands-on labs and coding exercises',
    icon: BookOpen,
    color: 'bg-green-100 text-green-800'
  },
  {
    id: 'podcast',
    title: 'Podcasts',
    description: 'Audio content for learning on-the-go',
    icon: Headphones,
    color: 'bg-purple-100 text-purple-800'
  },
  {
    id: 'book',
    title: 'Books & eBooks',
    description: 'Comprehensive written materials',
    icon: BookOpen,
    color: 'bg-orange-100 text-orange-800'
  },
  {
    id: 'quiz',
    title: 'Quizzes & Tests',
    description: 'Practice tests and assessments',
    icon: FileText,
    color: 'bg-yellow-100 text-yellow-800'
  }
];

const LANGUAGES = [
  {
    id: 'english',
    title: 'English',
    flag: '🇺🇸'
  },
  {
    id: 'spanish',
    title: 'Spanish',
    flag: '🇪🇸'
  },
  {
    id: 'french',
    title: 'French',
    flag: '🇫🇷'
  },
  {
    id: 'german',
    title: 'German',
    flag: '🇩🇪'
  },
  {
    id: 'portuguese',
    title: 'Portuguese',
    flag: '🇵🇹'
  },
  {
    id: 'mandarin',
    title: 'Mandarin',
    flag: '🇨🇳'
  }
];

export default function AvailabilityStep({ data, onDataChange, onNext }) {
  const [selectedTime, setSelectedTime] = useState(data.time_availability || '');
  const [selectedPlatforms, setSelectedPlatforms] = useState(data.preferred_platforms || []);
  const [selectedContentTypes, setSelectedContentTypes] = useState(data.content_types || []);
  const [selectedLanguages, setSelectedLanguages] = useState(data.language_preference || ['english']);

  const handleTimeSelect = (timeId) => {
    setSelectedTime(timeId);
    onDataChange({ time_availability: timeId });
  };

  const togglePlatform = (platformId) => {
    const newPlatforms = selectedPlatforms.includes(platformId)
      ? selectedPlatforms.filter(id => id !== platformId)
      : [...selectedPlatforms, platformId];
    
    setSelectedPlatforms(newPlatforms);
    onDataChange({ preferred_platforms: newPlatforms });
  };

  const toggleContentType = (typeId) => {
    const newTypes = selectedContentTypes.includes(typeId)
      ? selectedContentTypes.filter(id => id !== typeId)
      : [...selectedContentTypes, typeId];
    
    setSelectedContentTypes(newTypes);
    onDataChange({ content_types: newTypes });
  };

  const toggleLanguage = (langId) => {
    const newLanguages = selectedLanguages.includes(langId)
      ? selectedLanguages.filter(id => id !== langId)
      : [...selectedLanguages, langId];
    
    setSelectedLanguages(newLanguages);
    onDataChange({ language_preference: newLanguages });
  };

  const canProceed = selectedTime && selectedPlatforms.length > 0 && selectedContentTypes.length > 0 && selectedLanguages.length > 0;

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
          Tell us about your schedule
        </h2>
        <p className="text-gray-600">
          Help us recommend the right amount and type of content for your learning goals.
        </p>
      </motion.div>

      {/* Time Availability */}
      <motion.div variants={itemVariants} className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">How much time can you dedicate to learning?</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {TIME_AVAILABILITY.map((time) => {
            const Icon = time.icon;
            const isSelected = selectedTime === time.id;
            
            return (
              <motion.div
                key={time.id}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <Card
                  onClick={() => handleTimeSelect(time.id)}
                  className={`p-4 cursor-pointer transition-all duration-200 border-2 ${
                    isSelected
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300 bg-white'
                  }`}
                >
                  <div className="space-y-3">
                    <div className="flex items-center space-x-3">
                      <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${time.color} flex items-center justify-center`}>
                        <Icon className="h-5 w-5 text-white" />
                      </div>
                      <div>
                        <h4 className="font-medium text-gray-900">{time.title}</h4>
                        <p className="text-sm text-gray-600">{time.description}</p>
                      </div>
                    </div>
                    <p className="text-xs text-gray-500">{time.recommendation}</p>
                  </div>
                </Card>
              </motion.div>
            );
          })}
        </div>
      </motion.div>

      {/* Preferred Platforms */}
      <motion.div variants={itemVariants} className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">Which platforms do you prefer? (Select all that apply)</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {PREFERRED_PLATFORMS.map((platform) => {
            const isSelected = selectedPlatforms.includes(platform.id);
            
            return (
              <motion.div
                key={platform.id}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <Card
                  onClick={() => togglePlatform(platform.id)}
                  className={`p-3 cursor-pointer transition-all duration-200 border-2 ${
                    isSelected
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300 bg-white'
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <span className="text-xl">{platform.icon}</span>
                    <div className="flex-1 min-w-0">
                      <h4 className="font-medium text-gray-900 text-sm truncate">{platform.title}</h4>
                      <p className="text-xs text-gray-600 truncate">{platform.description}</p>
                    </div>
                    <div className={`w-4 h-4 rounded-full border-2 flex items-center justify-center flex-shrink-0 ${
                      isSelected ? 'border-blue-500 bg-blue-500' : 'border-gray-300'
                    }`}>
                      {isSelected && <div className="w-1.5 h-1.5 bg-white rounded-full" />}
                    </div>
                  </div>
                </Card>
              </motion.div>
            );
          })}
        </div>
      </motion.div>

      {/* Content Types */}
      <motion.div variants={itemVariants} className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">What types of content do you enjoy? (Select all that apply)</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {CONTENT_TYPES.map((type) => {
            const Icon = type.icon;
            const isSelected = selectedContentTypes.includes(type.id);
            
            return (
              <motion.div
                key={type.id}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <Card
                  onClick={() => toggleContentType(type.id)}
                  className={`p-3 cursor-pointer transition-all duration-200 border-2 ${
                    isSelected
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300 bg-white'
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <Icon className="h-5 w-5 text-blue-600 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <h4 className="font-medium text-gray-900 text-sm truncate">{type.title}</h4>
                      <p className="text-xs text-gray-600 truncate">{type.description}</p>
                    </div>
                    <div className={`w-4 h-4 rounded-full border-2 flex items-center justify-center flex-shrink-0 ${
                      isSelected ? 'border-blue-500 bg-blue-500' : 'border-gray-300'
                    }`}>
                      {isSelected && <div className="w-1.5 h-1.5 bg-white rounded-full" />}
                    </div>
                  </div>
                </Card>
              </motion.div>
            );
          })}
        </div>
      </motion.div>

      {/* Language Preferences */}
      <motion.div variants={itemVariants} className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">Language Preferences (Select all that apply)</h3>
        <div className="grid grid-cols-3 md:grid-cols-6 gap-3">
          {LANGUAGES.map((language) => {
            const isSelected = selectedLanguages.includes(language.id);
            
            return (
              <motion.div
                key={language.id}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <Card
                  onClick={() => toggleLanguage(language.id)}
                  className={`p-3 cursor-pointer transition-all duration-200 border-2 text-center ${
                    isSelected
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300 bg-white'
                  }`}
                >
                  <div className="space-y-1">
                    <span className="text-2xl block">{language.flag}</span>
                    <h4 className="font-medium text-gray-900 text-xs">{language.title}</h4>
                  </div>
                </Card>
              </motion.div>
            );
          })}
        </div>
      </motion.div>

      {/* Selected summary */}
      {(selectedPlatforms.length > 0 || selectedContentTypes.length > 0) && (
        <motion.div variants={itemVariants} className="bg-blue-50 p-4 rounded-lg">
          <h4 className="font-medium text-gray-900 mb-3">Your Preferences Summary:</h4>
          <div className="space-y-2">
            {selectedPlatforms.length > 0 && (
              <div>
                <span className="text-sm text-gray-600">Platforms: </span>
                <div className="inline-flex flex-wrap gap-1 mt-1">
                  {selectedPlatforms.map(platformId => {
                    const platform = PREFERRED_PLATFORMS.find(p => p.id === platformId);
                    return (
                      <Badge key={platformId} variant="secondary" className="text-xs">
                        {platform?.title}
                      </Badge>
                    );
                  })}
                </div>
              </div>
            )}
            {selectedContentTypes.length > 0 && (
              <div>
                <span className="text-sm text-gray-600">Content Types: </span>
                <div className="inline-flex flex-wrap gap-1 mt-1">
                  {selectedContentTypes.map(typeId => {
                    const type = CONTENT_TYPES.find(t => t.id === typeId);
                    return (
                      <Badge key={typeId} variant="secondary" className="text-xs">
                        {type?.title}
                      </Badge>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        </motion.div>
      )}

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