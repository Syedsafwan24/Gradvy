'use client';

import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { ArrowRight, BookOpen, Target, TrendingUp } from 'lucide-react';

export default function WelcomeStep({ onNext }) {
  const features = [
    {
      icon: Target,
      title: 'Personalized Learning Paths',
      description: 'AI-powered recommendations tailored to your goals and learning style'
    },
    {
      icon: BookOpen,
      title: 'Curated Content',
      description: 'Best courses from Udemy, Coursera, YouTube, and more in one place'
    },
    {
      icon: TrendingUp,
      title: 'Track Your Progress',
      description: 'Monitor your learning journey and celebrate your achievements'
    }
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2
      }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: { duration: 0.5 }
    }
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="text-center space-y-8"
    >
      {/* Hero section */}
      <motion.div variants={itemVariants} className="space-y-4">
        <div className="w-24 h-24 mx-auto bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center">
          <BookOpen className="h-12 w-12 text-white" />
        </div>
        
        <h2 className="text-3xl font-bold text-gray-900">
          Welcome to Your Learning Journey
        </h2>
        
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          Gradvy helps you discover the perfect learning path based on your goals, 
          experience, and preferences. Let's get started by learning more about you.
        </p>
      </motion.div>

      {/* Features */}
      <motion.div
        variants={itemVariants}
        className="grid md:grid-cols-3 gap-6 py-8"
      >
        {features.map((feature, index) => {
          const Icon = feature.icon;
          return (
            <motion.div
              key={index}
              variants={itemVariants}
              className="bg-white/50 p-6 rounded-xl border border-gray-100 hover:shadow-md transition-shadow"
            >
              <div className="w-12 h-12 mx-auto mb-4 bg-blue-100 rounded-lg flex items-center justify-center">
                <Icon className="h-6 w-6 text-blue-600" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">{feature.title}</h3>
              <p className="text-sm text-gray-600">{feature.description}</p>
            </motion.div>
          );
        })}
      </motion.div>

      {/* What to expect */}
      <motion.div variants={itemVariants} className="bg-blue-50 p-6 rounded-xl">
        <h3 className="font-semibold text-gray-900 mb-3">What to Expect</h3>
        <div className="grid md:grid-cols-2 gap-4 text-sm text-gray-600">
          <div className="flex items-start space-x-3">
            <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
            <span>5 quick questions about your learning goals</span>
          </div>
          <div className="flex items-start space-x-3">
            <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
            <span>Your experience level and preferences</span>
          </div>
          <div className="flex items-start space-x-3">
            <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
            <span>Time availability and learning style</span>
          </div>
          <div className="flex items-start space-x-3">
            <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
            <span>Personalized course recommendations</span>
          </div>
        </div>
      </motion.div>

      {/* CTA */}
      <motion.div variants={itemVariants} className="pt-6">
        <Button
          onClick={onNext}
          size="lg"
          className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-8 py-3 text-lg"
        >
          Let's Get Started
          <ArrowRight className="ml-2 h-5 w-5" />
        </Button>
        
        <p className="text-xs text-gray-500 mt-4">
          Takes about 2-3 minutes • You can change these settings later
        </p>
      </motion.div>
    </motion.div>
  );
}