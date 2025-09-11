/*
 * File: frontend/src/components/career/CareerHero.jsx
 * Description: Hero section component for the public career page showcasing tech career pathways
 * Purpose: Inspire users to explore tech careers and guide them toward personalized learning paths
 * Relevant Files: components/career/CareerPathways.jsx, components/sections/Hero.jsx, app/career/page.jsx
 */

'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  TrendingUp,
  DollarSign,
  Users,
  ArrowRight,
  Sparkles,
  Briefcase,
  Target,
  Clock,
  Star,
  Code,
  Palette,
  Server,
  Smartphone,
  Database,
  Shield,
  BarChart3,
  Cloud
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import Link from 'next/link';

const CareerHero = ({ onExploreCareer }) => {
  const [selectedPath, setSelectedPath] = useState(0);
  
  const careerPaths = [
    {
      title: 'Frontend Developer',
      icon: Palette,
      salary: '$75k - $120k',
      growth: '+15%',
      demand: 'Very High',
      description: 'Build beautiful, interactive user interfaces',
      skills: ['React', 'JavaScript', 'CSS', 'TypeScript'],
      gradient: 'from-pink-500 to-rose-500'
    },
    {
      title: 'Backend Developer',
      icon: Server,
      salary: '$80k - $130k',
      growth: '+18%',
      demand: 'Very High',
      description: 'Create robust server-side applications',
      skills: ['Python', 'Node.js', 'Databases', 'APIs'],
      gradient: 'from-blue-500 to-cyan-500'
    },
    {
      title: 'DevOps Engineer',
      icon: Cloud,
      salary: '$90k - $150k',
      growth: '+25%',
      demand: 'Extreme',
      description: 'Automate and scale infrastructure',
      skills: ['Docker', 'AWS', 'Kubernetes', 'CI/CD'],
      gradient: 'from-green-500 to-teal-500'
    },
    {
      title: 'Data Scientist',
      icon: BarChart3,
      salary: '$85k - $140k',
      growth: '+22%',
      demand: 'High',
      description: 'Extract insights from data using AI',
      skills: ['Python', 'ML', 'Statistics', 'SQL'],
      gradient: 'from-purple-500 to-violet-500'
    }
  ];

  const stats = [
    { value: '3.2M', label: 'Tech Jobs Available', icon: Briefcase },
    { value: '94%', label: 'Employment Rate', icon: TrendingUp },
    { value: '$85k', label: 'Average Salary', icon: DollarSign },
    { value: '6-12mo', label: 'Time to Job Ready', icon: Clock }
  ];

  const successStories = [
    {
      name: 'Sarah Chen',
      role: 'Frontend Developer at Google',
      timeframe: '8 months',
      background: 'Marketing → Tech',
      image: '👩‍💻'
    },
    {
      name: 'Marcus Johnson',
      role: 'DevOps Engineer at Netflix',
      timeframe: '10 months',
      background: 'Finance → Tech',
      image: '👨‍💼'
    },
    {
      name: 'Priya Patel',
      role: 'Data Scientist at Meta',
      timeframe: '12 months',
      background: 'Biology → Tech',
      image: '👩‍🔬'
    }
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setSelectedPath((prev) => (prev + 1) % careerPaths.length);
    }, 3000);
    
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="relative min-h-[90vh] bg-gradient-to-br from-indigo-50 via-white to-cyan-50 overflow-hidden">
      {/* Background Elements */}
      <div className="absolute inset-0">
        <div className="absolute top-20 left-10 w-20 h-20 bg-indigo-200 rounded-full opacity-20 animate-pulse"></div>
        <div className="absolute top-40 right-20 w-32 h-32 bg-cyan-200 rounded-full opacity-20 animate-pulse delay-1000"></div>
        <div className="absolute bottom-20 left-20 w-24 h-24 bg-purple-200 rounded-full opacity-20 animate-pulse delay-2000"></div>
        <div className="absolute bottom-40 right-40 w-16 h-16 bg-pink-200 rounded-full opacity-20 animate-pulse delay-3000"></div>
      </div>

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 lg:py-20">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-16 items-center">
          
          {/* Left Content */}
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center lg:text-left"
          >
            {/* Badge */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="inline-flex items-center space-x-2 bg-white/80 backdrop-blur-sm border border-indigo-200 rounded-full px-4 py-2 mb-6"
            >
              <Sparkles className="h-4 w-4 text-indigo-600" />
              <span className="text-sm font-medium text-indigo-700">Launch Your Tech Career</span>
            </motion.div>

            {/* Main Heading */}
            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="text-4xl lg:text-6xl font-bold leading-tight"
            >
              <span className="bg-gradient-to-r from-indigo-600 via-purple-600 to-cyan-600 bg-clip-text text-transparent">
                Your Dream Tech
              </span>
              <br />
              <span className="text-gray-900">Career Awaits</span>
            </motion.h1>

            {/* Subtitle */}
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="text-lg lg:text-xl text-gray-600 mt-6 max-w-2xl"
            >
              Discover high-paying tech careers, get personalized learning paths, and land your dream job 
              in 6-12 months. No experience required.
            </motion.p>

            {/* Stats Grid */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="grid grid-cols-2 gap-4 mt-8 mb-8"
            >
              {stats.map((stat, index) => {
                const Icon = stat.icon;
                return (
                  <div key={index} className="bg-white/60 backdrop-blur-sm rounded-lg p-4 border border-gray-200 text-center">
                    <div className="flex items-center justify-center mb-2">
                      <Icon className="h-5 w-5 text-indigo-600 mr-2" />
                      <span className="text-2xl font-bold text-gray-900">{stat.value}</span>
                    </div>
                    <p className="text-sm text-gray-600">{stat.label}</p>
                  </div>
                );
              })}
            </motion.div>

            {/* CTA Buttons */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 }}
              className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start"
            >
              <Button 
                size="lg" 
                onClick={onExploreCareer}
                className="bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white px-8 py-4 text-lg font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 group"
              >
                <Target className="h-5 w-5 mr-2 group-hover:animate-pulse" />
                Explore Career Paths
                <ArrowRight className="h-5 w-5 ml-2 group-hover:translate-x-1 transition-transform" />
              </Button>
              
              <Link href="/register">
                <Button 
                  variant="outline" 
                  size="lg"
                  className="border-2 border-gray-300 hover:border-indigo-500 px-8 py-4 text-lg font-semibold rounded-xl transition-all duration-300 group"
                >
                  <Briefcase className="h-5 w-5 mr-2" />
                  Start Learning Free
                </Button>
              </Link>
            </motion.div>

            {/* Success Stories */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.8 }}
              className="mt-8"
            >
              <p className="text-sm text-gray-500 mb-3">Join successful career changers:</p>
              <div className="flex items-center justify-center lg:justify-start space-x-4 overflow-x-auto">
                {successStories.map((story, index) => (
                  <div key={index} className="flex items-center space-x-2 bg-white/60 backdrop-blur-sm rounded-lg p-3 border border-gray-200 min-w-fit">
                    <span className="text-2xl">{story.image}</span>
                    <div className="text-left">
                      <p className="text-sm font-medium text-gray-900">{story.name}</p>
                      <p className="text-xs text-gray-600">{story.background}</p>
                      <p className="text-xs text-indigo-600">Success in {story.timeframe}</p>
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>
          </motion.div>

          {/* Right Content - Career Path Showcase */}
          <motion.div
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.3 }}
            className="relative"
          >
            <div className="relative bg-white rounded-2xl shadow-2xl overflow-hidden">
              {/* Header */}
              <div className="bg-gradient-to-r from-indigo-600 to-purple-600 px-6 py-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-white font-semibold">Hot Career Paths 2024</h3>
                  <div className="flex space-x-1">
                    {careerPaths.map((_, index) => (
                      <div
                        key={index}
                        className={`w-2 h-2 rounded-full transition-all duration-300 ${
                          index === selectedPath ? 'bg-white' : 'bg-white/50'
                        }`}
                      />
                    ))}
                  </div>
                </div>
              </div>

              {/* Career Path Content */}
              <div className="p-6">
                <motion.div
                  key={selectedPath}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5 }}
                  className="space-y-4"
                >
                  <div className="flex items-center space-x-3">
                    <div className={`w-12 h-12 rounded-xl bg-gradient-to-r ${careerPaths[selectedPath].gradient} flex items-center justify-center`}>
                      {React.createElement(careerPaths[selectedPath].icon, { 
                        className: "h-6 w-6 text-white" 
                      })}
                    </div>
                    <div>
                      <h4 className="text-xl font-bold text-gray-900">
                        {careerPaths[selectedPath].title}
                      </h4>
                      <p className="text-gray-600">
                        {careerPaths[selectedPath].description}
                      </p>
                    </div>
                  </div>

                  {/* Metrics */}
                  <div className="grid grid-cols-3 gap-4">
                    <div className="text-center p-3 bg-gray-50 rounded-lg">
                      <DollarSign className="h-5 w-5 text-green-600 mx-auto mb-1" />
                      <p className="text-sm font-semibold text-gray-900">
                        {careerPaths[selectedPath].salary}
                      </p>
                      <p className="text-xs text-gray-600">Salary Range</p>
                    </div>
                    <div className="text-center p-3 bg-gray-50 rounded-lg">
                      <TrendingUp className="h-5 w-5 text-blue-600 mx-auto mb-1" />
                      <p className="text-sm font-semibold text-green-600">
                        {careerPaths[selectedPath].growth}
                      </p>
                      <p className="text-xs text-gray-600">Growth Rate</p>
                    </div>
                    <div className="text-center p-3 bg-gray-50 rounded-lg">
                      <Users className="h-5 w-5 text-purple-600 mx-auto mb-1" />
                      <p className="text-sm font-semibold text-purple-600">
                        {careerPaths[selectedPath].demand}
                      </p>
                      <p className="text-xs text-gray-600">Job Demand</p>
                    </div>
                  </div>

                  {/* Skills */}
                  <div>
                    <p className="text-sm font-medium text-gray-900 mb-2">Key Skills:</p>
                    <div className="flex flex-wrap gap-2">
                      {careerPaths[selectedPath].skills.map((skill, index) => (
                        <Badge key={index} className="bg-blue-100 text-blue-700">
                          {skill}
                        </Badge>
                      ))}
                    </div>
                  </div>

                  {/* Progress Indicator */}
                  <div className="bg-gray-50 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-gray-900">Learning Progress</span>
                      <span className="text-sm text-gray-600">0% Complete</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 h-2 rounded-full w-0 animate-pulse"></div>
                    </div>
                    <p className="text-xs text-gray-600 mt-2">Ready to start your journey?</p>
                  </div>
                </motion.div>
              </div>
            </div>

            {/* Floating Elements */}
            <motion.div
              animate={{ y: [0, -10, 0] }}
              transition={{ duration: 3, repeat: Infinity }}
              className="absolute -top-6 -right-6 bg-gradient-to-r from-green-500 to-teal-500 text-white p-3 rounded-full shadow-lg"
            >
              <Star className="h-6 w-6" />
            </motion.div>

            <motion.div
              animate={{ y: [0, 10, 0] }}
              transition={{ duration: 4, repeat: Infinity, delay: 1 }}
              className="absolute -bottom-6 -left-6 bg-gradient-to-r from-pink-500 to-rose-500 text-white p-3 rounded-full shadow-lg"
            >
              <Briefcase className="h-6 w-6" />
            </motion.div>
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default CareerHero;