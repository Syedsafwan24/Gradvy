'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/badge';
import { CheckCircle, Sparkles, ArrowRight, Target, BookOpen, Clock, TrendingUp, Loader2, Award, Trophy, Star, Zap } from 'lucide-react';

export default function CompletionStep({ data, onComplete, isLoading, currentStep, totalSteps }) {
  const [showSummary, setShowSummary] = useState(false);

  useEffect(() => {
    // Show summary after a brief delay for better UX
    const timer = setTimeout(() => setShowSummary(true), 500);
    return () => clearTimeout(timer);
  }, []);

  const handleComplete = () => {
    onComplete();
  };

  // Create preference summary from collected data
  const getPreferenceSummary = () => {
    const summary = {
      goals: data.learning_goals || [],
      experience: data.experience_level || '',
      pace: data.preferred_pace || '',
      styles: data.learning_style || [],
      career: data.career_stage || '',
      timeline: data.target_timeline || '',
      time: data.time_availability || '',
      platforms: data.preferred_platforms || [],
      contentTypes: data.content_types || [],
      languages: data.language_preference || []
    };
    return summary;
  };

  const summary = getPreferenceSummary();

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.2 }
    }
  };

  const itemVariants = {
    hidden: { y: 30, opacity: 0 },
    visible: { 
      y: 0, 
      opacity: 1,
      transition: { duration: 0.6, ease: "easeOut" }
    }
  };

  const iconVariants = {
    hidden: { scale: 0, rotate: -180 },
    visible: { 
      scale: 1, 
      rotate: 0,
      transition: { duration: 0.8, ease: "easeOut" }
    }
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-8"
    >
      {/* Success Icon & Header */}
      <motion.div variants={itemVariants} className="text-center space-y-6">
        <motion.div
          variants={iconVariants}
          className="flex justify-center"
        >
          <div className="w-24 h-24 bg-gradient-to-br from-green-500 to-emerald-600 rounded-full flex items-center justify-center">
            <CheckCircle className="h-12 w-12 text-white" />
          </div>
        </motion.div>
        
        <div className="space-y-3">
          <h2 className="text-3xl font-bold text-gray-900">
            You're all set! 🎉
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            We've created your personalized learning profile. Get ready to discover 
            courses perfectly tailored to your goals and preferences.
          </p>
        </div>
      </motion.div>

      {/* Achievement Badges */}
      <motion.div
        variants={itemVariants}
        className="space-y-6"
      >
        <div className="text-center">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">Achievements Unlocked! 🏆</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <motion.div
              initial={{ scale: 0, rotate: -180 }}
              animate={{ scale: 1, rotate: 0 }}
              transition={{ duration: 0.6, delay: 0.5 }}
              className="bg-gradient-to-br from-blue-500 to-blue-600 text-white p-4 rounded-xl text-center"
            >
              <Trophy className="h-8 w-8 mx-auto mb-2" />
              <h4 className="font-semibold text-sm">Profile Pioneer</h4>
              <p className="text-xs opacity-90">Completed full onboarding</p>
            </motion.div>

            <motion.div
              initial={{ scale: 0, rotate: -180 }}
              animate={{ scale: 1, rotate: 0 }}
              transition={{ duration: 0.6, delay: 0.7 }}
              className="bg-gradient-to-br from-purple-500 to-purple-600 text-white p-4 rounded-xl text-center"
            >
              <Target className="h-8 w-8 mx-auto mb-2" />
              <h4 className="font-semibold text-sm">Goal Setter</h4>
              <p className="text-xs opacity-90">Defined learning goals</p>
            </motion.div>

            <motion.div
              initial={{ scale: 0, rotate: -180 }}
              animate={{ scale: 1, rotate: 0 }}
              transition={{ duration: 0.6, delay: 0.9 }}
              className="bg-gradient-to-br from-green-500 to-green-600 text-white p-4 rounded-xl text-center"
            >
              <Star className="h-8 w-8 mx-auto mb-2" />
              <h4 className="font-semibold text-sm">Preference Pro</h4>
              <p className="text-xs opacity-90">Set learning preferences</p>
            </motion.div>

            <motion.div
              initial={{ scale: 0, rotate: -180 }}
              animate={{ scale: 1, rotate: 0 }}
              transition={{ duration: 0.6, delay: 1.1 }}
              className="bg-gradient-to-br from-orange-500 to-orange-600 text-white p-4 rounded-xl text-center"
            >
              <Zap className="h-8 w-8 mx-auto mb-2" />
              <h4 className="font-semibold text-sm">Ready to Learn</h4>
              <p className="text-xs opacity-90">All set for personalization</p>
            </motion.div>
          </div>
        </div>
      </motion.div>

      {/* Preference Summary */}
      {showSummary && (
        <motion.div
          variants={itemVariants}
          className="space-y-6"
        >
          <div className="text-center">
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Your Learning Profile</h3>
            <p className="text-gray-600">Here's what we learned about you:</p>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            {/* Goals & Experience */}
            <Card className="p-6 space-y-4">
              <div className="flex items-center space-x-3">
                <Target className="h-6 w-6 text-blue-600" />
                <h4 className="font-semibold text-gray-900">Goals & Experience</h4>
              </div>
              
              <div className="space-y-3">
                <div>
                  <span className="text-sm font-medium text-gray-700">Learning Goals:</span>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {summary.goals.slice(0, 3).map((goal, index) => (
                      <Badge key={index} variant="secondary" className="text-xs">
                        {goal}
                      </Badge>
                    ))}
                    {summary.goals.length > 3 && (
                      <Badge variant="outline" className="text-xs">
                        +{summary.goals.length - 3} more
                      </Badge>
                    )}
                  </div>
                </div>
                
                {summary.experience && (
                  <div>
                    <span className="text-sm font-medium text-gray-700">Experience Level:</span>
                    <p className="text-sm text-gray-600 capitalize">
                      {summary.experience.replace('_', ' ')}
                    </p>
                  </div>
                )}
                
                {summary.career && (
                  <div>
                    <span className="text-sm font-medium text-gray-700">Career Stage:</span>
                    <p className="text-sm text-gray-600 capitalize">
                      {summary.career.replace('_', ' ')}
                    </p>
                  </div>
                )}
              </div>
            </Card>

            {/* Learning Preferences */}
            <Card className="p-6 space-y-4">
              <div className="flex items-center space-x-3">
                <BookOpen className="h-6 w-6 text-green-600" />
                <h4 className="font-semibold text-gray-900">Learning Preferences</h4>
              </div>
              
              <div className="space-y-3">
                {summary.pace && (
                  <div>
                    <span className="text-sm font-medium text-gray-700">Learning Pace:</span>
                    <p className="text-sm text-gray-600 capitalize">{summary.pace}</p>
                  </div>
                )}
                
                <div>
                  <span className="text-sm font-medium text-gray-700">Learning Styles:</span>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {summary.styles.map((style, index) => (
                      <Badge key={index} variant="secondary" className="text-xs">
                        {style.replace('_', ' ')}
                      </Badge>
                    ))}
                  </div>
                </div>
                
                {summary.timeline && (
                  <div>
                    <span className="text-sm font-medium text-gray-700">Target Timeline:</span>
                    <p className="text-sm text-gray-600">{summary.timeline}</p>
                  </div>
                )}
              </div>
            </Card>

            {/* Time & Platforms */}
            <Card className="p-6 space-y-4">
              <div className="flex items-center space-x-3">
                <Clock className="h-6 w-6 text-purple-600" />
                <h4 className="font-semibold text-gray-900">Schedule & Platforms</h4>
              </div>
              
              <div className="space-y-3">
                {summary.time && (
                  <div>
                    <span className="text-sm font-medium text-gray-700">Weekly Time:</span>
                    <p className="text-sm text-gray-600">{summary.time}</p>
                  </div>
                )}
                
                <div>
                  <span className="text-sm font-medium text-gray-700">Preferred Platforms:</span>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {summary.platforms.slice(0, 3).map((platform, index) => (
                      <Badge key={index} variant="secondary" className="text-xs capitalize">
                        {platform.replace('_', ' ')}
                      </Badge>
                    ))}
                    {summary.platforms.length > 3 && (
                      <Badge variant="outline" className="text-xs">
                        +{summary.platforms.length - 3} more
                      </Badge>
                    )}
                  </div>
                </div>
              </div>
            </Card>

            {/* Content & Languages */}
            <Card className="p-6 space-y-4">
              <div className="flex items-center space-x-3">
                <TrendingUp className="h-6 w-6 text-orange-600" />
                <h4 className="font-semibold text-gray-900">Content & Languages</h4>
              </div>
              
              <div className="space-y-3">
                <div>
                  <span className="text-sm font-medium text-gray-700">Content Types:</span>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {summary.contentTypes.slice(0, 3).map((type, index) => (
                      <Badge key={index} variant="secondary" className="text-xs">
                        {type}
                      </Badge>
                    ))}
                    {summary.contentTypes.length > 3 && (
                      <Badge variant="outline" className="text-xs">
                        +{summary.contentTypes.length - 3} more
                      </Badge>
                    )}
                  </div>
                </div>
                
                <div>
                  <span className="text-sm font-medium text-gray-700">Languages:</span>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {summary.languages.map((lang, index) => (
                      <Badge key={index} variant="secondary" className="text-xs capitalize">
                        {lang}
                      </Badge>
                    ))}
                  </div>
                </div>
              </div>
            </Card>
          </div>
        </motion.div>
      )}

      {/* What's Next */}
      <motion.div variants={itemVariants} className="bg-gradient-to-br from-blue-50 to-purple-50 p-6 rounded-xl">
        <div className="text-center space-y-4">
          <div className="flex justify-center">
            <Sparkles className="h-8 w-8 text-blue-600" />
          </div>
          <h3 className="text-xl font-semibold text-gray-900">What happens next?</h3>
          <div className="grid md:grid-cols-3 gap-4 text-sm">
            <div className="flex flex-col items-center space-y-2">
              <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                <span className="text-blue-600 font-bold">1</span>
              </div>
              <p className="text-gray-700 text-center">
                We'll analyze your preferences and generate personalized recommendations
              </p>
            </div>
            <div className="flex flex-col items-center space-y-2">
              <div className="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center">
                <span className="text-purple-600 font-bold">2</span>
              </div>
              <p className="text-gray-700 text-center">
                Discover curated courses from your favorite platforms
              </p>
            </div>
            <div className="flex flex-col items-center space-y-2">
              <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                <span className="text-green-600 font-bold">3</span>
              </div>
              <p className="text-gray-700 text-center">
                Start learning with content perfectly matched to your goals
              </p>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Complete Button */}
      <motion.div variants={itemVariants} className="text-center pt-6">
        <Button
          onClick={handleComplete}
          disabled={isLoading}
          size="lg"
          className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-8 py-3 text-lg"
        >
          {isLoading ? (
            <>
              <Loader2 className="mr-2 h-5 w-5 animate-spin" />
              Setting up your profile...
            </>
          ) : (
            <>
              Start Learning
              <ArrowRight className="ml-2 h-5 w-5" />
            </>
          )}
        </Button>
        
        <p className="text-sm text-gray-500 mt-4">
          You can update these preferences anytime in your settings
        </p>
      </motion.div>
    </motion.div>
  );
}