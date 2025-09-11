/*
 * File: frontend/src/components/playground/PlaygroundHero.jsx
 * Description: Hero section component for the public playground page showcasing Gradvy's coding environment
 * Purpose: Attract users to try the interactive code playground and convert them to registered users
 * Relevant Files: components/sections/Hero.jsx, components/ui/Button.jsx, app/playground/page.jsx
 */

'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Play, 
  Code, 
  Zap, 
  Users, 
  GitBranch, 
  Globe, 
  ArrowRight,
  Sparkles,
  Terminal,
  FileCode
} from 'lucide-react';
import { Button } from '@/components/ui/Button';
import Link from 'next/link';

const PlaygroundHero = ({ onStartCoding }) => {
  const [currentExample, setCurrentExample] = useState(0);
  
  const codeExamples = [
    {
      language: 'JavaScript',
      icon: '🟨',
      code: `// Create interactive animations
function createParticles() {
  const particles = [];
  for (let i = 0; i < 50; i++) {
    particles.push({
      x: Math.random() * window.innerWidth,
      y: Math.random() * window.innerHeight,
      vx: (Math.random() - 0.5) * 2,
      vy: (Math.random() - 0.5) * 2
    });
  }
  return particles;
}`,
      description: 'Build interactive web applications'
    },
    {
      language: 'Python',
      icon: '🐍',
      code: `# AI-powered data analysis
import pandas as pd
import numpy as np

def analyze_trends(data):
    """Discover patterns in your data"""
    trends = data.groupby('category').agg({
        'value': ['mean', 'std', 'count']
    })
    return trends.round(2)

# Process real-world datasets
df = pd.read_csv('sales_data.csv')
insights = analyze_trends(df)`,
      description: 'Analyze data and build AI models'
    },
    {
      language: 'React',
      icon: '⚛️',
      code: `// Modern React components
import { useState, useEffect } from 'react';

export default function WeatherApp() {
  const [weather, setWeather] = useState(null);
  
  useEffect(() => {
    fetch('/api/weather')
      .then(res => res.json())
      .then(setWeather);
  }, []);
  
  return (
    <div className="weather-card">
      <h2>Today's Weather</h2>
      {weather && (
        <p>{weather.temp}°C - {weather.description}</p>
      )}
    </div>
  );
}`,
      description: 'Create modern user interfaces'
    }
  ];

  const features = [
    {
      icon: Zap,
      title: 'Instant Execution',
      description: 'Run your code instantly without setup',
      color: 'from-yellow-500 to-orange-500'
    },
    {
      icon: Users,
      title: 'Collaborative Coding',
      description: 'Code together in real-time with others',
      color: 'from-blue-500 to-purple-500'
    },
    {
      icon: GitBranch,
      title: 'Version Control',
      description: 'Track changes and collaborate safely',
      color: 'from-green-500 to-teal-500'
    },
    {
      icon: Globe,
      title: 'Share Anywhere',
      description: 'Share your creations with the world',
      color: 'from-pink-500 to-rose-500'
    }
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentExample((prev) => (prev + 1) % codeExamples.length);
    }, 4000);
    
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="relative min-h-[90vh] bg-gradient-to-br from-blue-50 via-white to-purple-50 overflow-hidden">
      {/* Background Elements */}
      <div className="absolute inset-0">
        <div className="absolute top-20 left-10 w-20 h-20 bg-blue-200 rounded-full opacity-20 animate-pulse"></div>
        <div className="absolute top-40 right-20 w-32 h-32 bg-purple-200 rounded-full opacity-20 animate-pulse delay-1000"></div>
        <div className="absolute bottom-20 left-20 w-24 h-24 bg-green-200 rounded-full opacity-20 animate-pulse delay-2000"></div>
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
              className="inline-flex items-center space-x-2 bg-white/80 backdrop-blur-sm border border-blue-200 rounded-full px-4 py-2 mb-6"
            >
              <Sparkles className="h-4 w-4 text-blue-600" />
              <span className="text-sm font-medium text-blue-700">AI-Powered Code Playground</span>
            </motion.div>

            {/* Main Heading */}
            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="text-4xl lg:text-6xl font-bold leading-tight"
            >
              <span className="bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
                Code. Learn. 
              </span>
              <br />
              <span className="text-gray-900">Create Amazing Things.</span>
            </motion.h1>

            {/* Subtitle */}
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="text-lg lg:text-xl text-gray-600 mt-6 max-w-2xl"
            >
              Start coding instantly with our interactive playground. No setup required. 
              Build projects, learn new skills, and collaborate with developers worldwide.
            </motion.p>

            {/* Features Grid */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="grid grid-cols-2 gap-4 mt-8 mb-8"
            >
              {features.map((feature, index) => {
                const Icon = feature.icon;
                return (
                  <div key={index} className="flex items-center space-x-3 bg-white/60 backdrop-blur-sm rounded-lg p-3 border border-gray-200">
                    <div className={`w-8 h-8 rounded-lg bg-gradient-to-r ${feature.color} flex items-center justify-center flex-shrink-0`}>
                      <Icon className="h-4 w-4 text-white" />
                    </div>
                    <div className="min-w-0">
                      <h3 className="font-semibold text-gray-900 text-sm">{feature.title}</h3>
                      <p className="text-xs text-gray-600 truncate">{feature.description}</p>
                    </div>
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
                onClick={onStartCoding}
                className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-8 py-4 text-lg font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 group"
              >
                <Play className="h-5 w-5 mr-2 group-hover:animate-pulse" />
                Start Coding Now
                <ArrowRight className="h-5 w-5 ml-2 group-hover:translate-x-1 transition-transform" />
              </Button>
              
              <Link href="/register">
                <Button 
                  variant="outline" 
                  size="lg"
                  className="border-2 border-gray-300 hover:border-blue-500 px-8 py-4 text-lg font-semibold rounded-xl transition-all duration-300 group"
                >
                  <FileCode className="h-5 w-5 mr-2" />
                  Sign Up Free
                </Button>
              </Link>
            </motion.div>

            {/* Social Proof */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.8 }}
              className="mt-8 flex items-center justify-center lg:justify-start space-x-6 text-sm text-gray-500"
            >
              <div className="flex items-center space-x-2">
                <div className="flex -space-x-2">
                  {[...Array(4)].map((_, i) => (
                    <div
                      key={i}
                      className={`w-8 h-8 rounded-full bg-gradient-to-r ${
                        i % 2 === 0 ? 'from-blue-400 to-purple-400' : 'from-green-400 to-teal-400'
                      } border-2 border-white flex items-center justify-center text-white text-xs font-bold`}
                    >
                      {String.fromCharCode(65 + i)}
                    </div>
                  ))}
                </div>
                <span>10k+ developers</span>
              </div>
              <div className="flex items-center space-x-1">
                <Terminal className="h-4 w-4" />
                <span>2M+ lines of code</span>
              </div>
            </motion.div>
          </motion.div>

          {/* Right Content - Code Preview */}
          <motion.div
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.3 }}
            className="relative"
          >
            <div className="relative bg-gray-900 rounded-xl shadow-2xl overflow-hidden">
              {/* Terminal Header */}
              <div className="flex items-center justify-between px-4 py-3 bg-gray-800 border-b border-gray-700">
                <div className="flex items-center space-x-3">
                  <div className="flex space-x-1">
                    <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                    <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                    <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                  </div>
                  <span className="text-gray-300 text-sm font-medium">
                    {codeExamples[currentExample].language} Playground
                  </span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-2xl">{codeExamples[currentExample].icon}</span>
                  <Button size="sm" className="bg-green-600 hover:bg-green-700 text-white">
                    <Play className="h-3 w-3 mr-1" />
                    Run
                  </Button>
                </div>
              </div>

              {/* Code Content */}
              <div className="p-4 h-64 overflow-hidden">
                <motion.pre
                  key={currentExample}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5 }}
                  className="text-sm text-gray-300 font-mono leading-relaxed"
                >
                  <code>{codeExamples[currentExample].code}</code>
                </motion.pre>
              </div>

              {/* Bottom Info */}
              <div className="bg-gray-800 px-4 py-3 border-t border-gray-700">
                <motion.p
                  key={currentExample}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ duration: 0.5 }}
                  className="text-sm text-gray-400"
                >
                  {codeExamples[currentExample].description}
                </motion.p>
              </div>

              {/* Language Indicator */}
              <div className="absolute top-16 right-4 flex space-x-1">
                {codeExamples.map((_, index) => (
                  <div
                    key={index}
                    className={`w-2 h-2 rounded-full transition-all duration-300 ${
                      index === currentExample ? 'bg-blue-500' : 'bg-gray-600'
                    }`}
                  />
                ))}
              </div>
            </div>

            {/* Floating Elements */}
            <motion.div
              animate={{ y: [0, -10, 0] }}
              transition={{ duration: 3, repeat: Infinity }}
              className="absolute -top-6 -right-6 bg-gradient-to-r from-pink-500 to-rose-500 text-white p-3 rounded-full shadow-lg"
            >
              <Code className="h-6 w-6" />
            </motion.div>

            <motion.div
              animate={{ y: [0, 10, 0] }}
              transition={{ duration: 4, repeat: Infinity, delay: 1 }}
              className="absolute -bottom-6 -left-6 bg-gradient-to-r from-green-500 to-teal-500 text-white p-3 rounded-full shadow-lg"
            >
              <Zap className="h-6 w-6" />
            </motion.div>
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default PlaygroundHero;