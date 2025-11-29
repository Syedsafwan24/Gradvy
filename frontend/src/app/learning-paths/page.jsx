/*
 * File: frontend/src/app/learning-paths/page.jsx
 * Description: Public showcase page for Learning Paths feature
 * Purpose: Market the AI-powered learning paths feature with examples and drive conversions to registration
 * Relevant Files: app/career/page.jsx, app/app/learning-paths/page.jsx (functional version)
 */

'use client';

import React from 'react';
import { motion } from 'framer-motion';
import {
  Route,
  Sparkles,
  Target,
  Clock,
  TrendingUp,
  Award,
  BookOpen,
  CheckCircle,
  ArrowRight,
  Brain,
  Zap,
  Users
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useSelector } from 'react-redux';
import { selectIsAuthenticated } from '@/store/slices/authSlice';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

export default function LearningPathsShowcase() {
  const isAuthenticated = useSelector(selectIsAuthenticated);
  const router = useRouter();

  // Hardcoded example paths for showcase (NO API calls)
  const examplePaths = [
    {
      title: "Full Stack Web Development",
      description: "Master frontend and backend development with React, Node.js, and databases",
      modules: 12,
      duration: "6 months",
      difficulty: "Beginner to Advanced",
      skills: ['React', 'Node.js', 'MongoDB', 'TypeScript', 'REST APIs'],
      color: 'from-blue-500 to-cyan-500',
      icon: '💻'
    },
    {
      title: "AI & Machine Learning",
      description: "Build intelligent applications with Python, TensorFlow, and neural networks",
      modules: 10,
      duration: "8 months",
      difficulty: "Intermediate to Advanced",
      skills: ['Python', 'TensorFlow', 'Neural Networks', 'NLP', 'Computer Vision'],
      color: 'from-purple-500 to-pink-500',
      icon: '🤖'
    },
    {
      title: "DevOps & Cloud Engineering",
      description: "Learn deployment, CI/CD, containers, and cloud infrastructure management",
      modules: 8,
      duration: "5 months",
      difficulty: "Intermediate",
      skills: ['Docker', 'Kubernetes', 'AWS', 'CI/CD', 'Terraform'],
      color: 'from-green-500 to-teal-500',
      icon: '☁️'
    },
    {
      title: "Data Science & Analytics",
      description: "Extract insights from data using statistics, visualization, and machine learning",
      modules: 11,
      duration: "7 months",
      difficulty: "Beginner to Intermediate",
      skills: ['Python', 'Pandas', 'SQL', 'Data Viz', 'Statistics'],
      color: 'from-orange-500 to-red-500',
      icon: '📊'
    }
  ];

  const features = [
    {
      icon: Brain,
      title: "AI-Powered Personalization",
      description: "Our AI analyzes your goals, experience, and learning style to create a path tailored specifically for you"
    },
    {
      icon: Target,
      title: "Goal-Oriented Structure",
      description: "Every path is designed around your career goals with clear milestones and checkpoints"
    },
    {
      icon: Clock,
      title: "Flexible Pacing",
      description: "Learn at your own pace with adaptive scheduling that fits your lifestyle and commitments"
    },
    {
      icon: TrendingUp,
      title: "Progress Tracking",
      description: "Monitor your journey with detailed analytics and insights on your learning progress"
    }
  ];

  const benefits = [
    "Personalized curriculum based on your unique profile",
    "Curated resources from top platforms like YouTube and Udemy",
    "Structured learning path with clear progression",
    "Real-world projects and hands-on practice",
    "Progress tracking and analytics",
    "Adaptive difficulty based on your performance"
  ];

  const handleGetStarted = () => {
    if (isAuthenticated) {
      router.push('/app/learning-paths');
    } else {
      router.push('/register');
    }
  };

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-700 text-white py-20 overflow-hidden">
        <div className="absolute inset-0 bg-black opacity-10"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center"
          >
            <div className="inline-flex items-center gap-2 bg-white/10 backdrop-blur-sm px-4 py-2 rounded-full mb-6">
              <Sparkles className="h-5 w-5 text-yellow-300" />
              <span className="text-sm font-medium">AI-Powered Learning Paths</span>
            </div>

            <h1 className="text-5xl lg:text-6xl font-bold mb-6">
              Your Personalized Journey to<br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-yellow-300 to-pink-300">
                Tech Mastery
              </span>
            </h1>

            <p className="text-xl text-indigo-100 mb-8 max-w-3xl mx-auto">
              Let AI create a custom learning path tailored to your goals, experience, and learning style.
              From beginner to expert, we'll guide you every step of the way.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button
                size="lg"
                onClick={handleGetStarted}
                className="bg-white text-indigo-600 hover:bg-gray-100 px-8 py-4 text-lg font-semibold rounded-xl shadow-xl hover:shadow-2xl transition-all"
              >
                <Sparkles className="h-5 w-5 mr-2" />
                {isAuthenticated ? 'Go to My Learning Paths' : 'Start Your Journey Free'}
              </Button>

              <Link href={isAuthenticated ? "/app/learning-paths/generate" : "/register"}>
                <Button
                  variant="outline"
                  size="lg"
                  className="border-2 border-white text-white hover:bg-white hover:text-indigo-600 px-8 py-4 text-lg font-semibold rounded-xl"
                >
                  <Route className="h-5 w-5 mr-2" />
                  Generate AI Path
                </Button>
              </Link>
            </div>

            <div className="flex items-center justify-center gap-6 mt-8 text-indigo-100">
              <div className="flex items-center gap-2">
                <Users className="h-4 w-4" />
                <span className="text-sm">10,000+ learners</span>
              </div>
              <div className="flex items-center gap-2">
                <Route className="h-4 w-4" />
                <span className="text-sm">50+ learning paths</span>
              </div>
              <div className="flex items-center gap-2">
                <Award className="h-4 w-4" />
                <span className="text-sm">89% success rate</span>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-4xl font-bold text-gray-900 mb-4">
              How AI Learning Paths Work
            </h2>
            <p className="text-lg text-gray-600 max-w-3xl mx-auto">
              Our AI analyzes your profile to create a personalized, structured learning path that adapts to you
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            {[
              { step: 1, title: "Tell Us Your Goals", description: "Share your learning objectives, experience level, and time commitment", icon: Target },
              { step: 2, title: "AI Analyzes Your Profile", description: "Our AI processes your preferences and creates a custom roadmap", icon: Brain },
              { step: 3, title: "Get Your Path", description: "Receive a structured learning path with curated resources", icon: Route },
              { step: 4, title: "Learn & Track Progress", description: "Follow your path, complete modules, and track your growth", icon: TrendingUp }
            ].map((item, index) => {
              const Icon = item.icon;
              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="text-center"
                >
                  <div className="relative mb-6">
                    <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center mx-auto shadow-lg">
                      <Icon className="h-10 w-10 text-white" />
                    </div>
                    <div className="absolute -top-2 -right-2 w-8 h-8 bg-yellow-400 rounded-full flex items-center justify-center font-bold text-gray-900">
                      {item.step}
                    </div>
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">{item.title}</h3>
                  <p className="text-gray-600">{item.description}</p>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Example Learning Paths */}
      <section className="py-20 bg-gradient-to-br from-gray-50 to-blue-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-4xl font-bold text-gray-900 mb-4">
              Popular Learning Paths
            </h2>
            <p className="text-lg text-gray-600 max-w-3xl mx-auto">
              Explore some of our AI-generated learning paths. Yours will be customized just for you!
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {examplePaths.map((path, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <Card className="p-6 h-full hover:shadow-xl transition-all duration-300 group cursor-pointer">
                  <div className="flex items-start gap-4 mb-4">
                    <div className="text-4xl">{path.icon}</div>
                    <div className="flex-1">
                      <div className={`w-full h-2 bg-gradient-to-r ${path.color} rounded-full mb-3`}></div>
                      <h3 className="text-xl font-bold text-gray-900 mb-2 group-hover:text-blue-600 transition-colors">
                        {path.title}
                      </h3>
                      <p className="text-gray-600 text-sm mb-4">{path.description}</p>
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-4 mb-4 text-sm">
                    <div>
                      <p className="text-gray-500">Modules</p>
                      <p className="font-semibold text-gray-900">{path.modules}</p>
                    </div>
                    <div>
                      <p className="text-gray-500">Duration</p>
                      <p className="font-semibold text-gray-900">{path.duration}</p>
                    </div>
                    <div>
                      <p className="text-gray-500">Level</p>
                      <p className="font-semibold text-gray-900">{path.difficulty.split(' ')[0]}</p>
                    </div>
                  </div>

                  <div className="mb-4">
                    <p className="text-sm font-medium text-gray-900 mb-2">Skills You'll Master:</p>
                    <div className="flex flex-wrap gap-1">
                      {path.skills.map(skill => (
                        <Badge key={skill} variant="secondary" className="text-xs">
                          {skill}
                        </Badge>
                      ))}
                    </div>
                  </div>

                  <Button
                    className="w-full group-hover:shadow-md transition-shadow"
                    onClick={handleGetStarted}
                  >
                    {isAuthenticated ? 'Start This Path' : 'Sign Up to Start'}
                    <ArrowRight className="h-4 w-4 ml-2 group-hover:translate-x-1 transition-transform" />
                  </Button>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-4xl font-bold text-gray-900 mb-4">
              Why Choose AI Learning Paths?
            </h2>
            <p className="text-lg text-gray-600 max-w-3xl mx-auto">
              Powered by advanced AI to give you the most effective learning experience
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: index % 2 === 0 ? -20 : 20 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <Card className="p-6 h-full hover:shadow-lg transition-shadow">
                    <div className="flex items-start gap-4">
                      <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center flex-shrink-0">
                        <Icon className="h-6 w-6 text-white" />
                      </div>
                      <div>
                        <h3 className="text-xl font-semibold text-gray-900 mb-2">{feature.title}</h3>
                        <p className="text-gray-600">{feature.description}</p>
                      </div>
                    </div>
                  </Card>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="py-20 bg-gradient-to-br from-indigo-50 to-purple-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl lg:text-4xl font-bold text-gray-900 mb-6">
                Everything You Need to Succeed
              </h2>
              <p className="text-lg text-gray-600 mb-8">
                Our AI-powered learning paths include all the tools and resources you need to achieve your learning goals efficiently.
              </p>
              <ul className="space-y-4">
                {benefits.map((benefit, index) => (
                  <motion.li
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="flex items-start gap-3"
                  >
                    <CheckCircle className="h-6 w-6 text-green-600 flex-shrink-0 mt-0.5" />
                    <span className="text-gray-700">{benefit}</span>
                  </motion.li>
                ))}
              </ul>
            </div>

            <div className="relative">
              <div className="bg-gradient-to-br from-blue-600 to-indigo-600 rounded-2xl p-8 text-white shadow-2xl">
                <div className="flex items-center gap-3 mb-6">
                  <Zap className="h-8 w-8 text-yellow-300" />
                  <h3 className="text-2xl font-bold">Start Learning Today</h3>
                </div>
                <p className="text-indigo-100 mb-6">
                  Join thousands of learners who have transformed their careers with AI-powered learning paths. It's free to start!
                </p>
                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <CheckCircle className="h-5 w-5 text-green-300" />
                    <span>No credit card required</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle className="h-5 w-5 text-green-300" />
                    <span>Get started in 2 minutes</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle className="h-5 w-5 text-green-300" />
                    <span>Cancel anytime</span>
                  </div>
                </div>
                <Button
                  size="lg"
                  onClick={handleGetStarted}
                  className="w-full mt-6 bg-white text-indigo-600 hover:bg-gray-100 font-semibold"
                >
                  {isAuthenticated ? 'Go to My Paths' : 'Create Free Account'}
                  <ArrowRight className="h-5 w-5 ml-2" />
                </Button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="py-20 bg-gradient-to-r from-blue-600 to-indigo-600">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl lg:text-4xl font-bold text-white mb-6">
            Ready to Start Your Learning Journey?
          </h2>
          <p className="text-xl text-indigo-100 mb-8">
            Let AI create a personalized learning path tailored to your goals and experience level.
          </p>
          <Button
            size="lg"
            onClick={handleGetStarted}
            className="bg-white text-indigo-600 hover:bg-gray-100 px-8 py-4 text-lg font-semibold rounded-xl shadow-xl hover:shadow-2xl transition-all"
          >
            <Sparkles className="h-5 w-5 mr-2" />
            {isAuthenticated ? 'View My Learning Paths' : 'Get Started Free'}
          </Button>
        </div>
      </section>
    </div>
  );
}
