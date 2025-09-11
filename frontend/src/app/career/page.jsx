/*
 * File: frontend/src/app/career/page.jsx
 * Description: Public career page showcasing tech career pathways and guidance
 * Purpose: Help users discover tech careers, explore learning paths, and convert to platform users
 * Relevant Files: components/career/*, components/sections/*, app/layout.js
 */

'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  TrendingUp,
  DollarSign,
  Users,
  ArrowRight,
  Building2,
  MapPin,
  Calendar,
  Award,
  BookOpen,
  Target,
  Lightbulb,
  CheckCircle,
  ExternalLink,
  MessageSquare,
  Star,
  Quote
} from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useSelector } from 'react-redux';
import { selectIsAuthenticated } from '@/store/slices/authSlice';
import Link from 'next/link';
import toast from 'react-hot-toast';
import Head from 'next/head';

import CareerHero from '@/components/career/CareerHero';
import CareerPathways from '@/components/career/CareerPathways';

export default function CareerPage() {
  const [showPathways, setShowPathways] = useState(false);
  const [selectedFilter, setSelectedFilter] = useState('all');
  const [showCareerForm, setShowCareerForm] = useState(false);
  
  const isAuthenticated = useSelector(selectIsAuthenticated);

  const industryInsights = [
    {
      title: 'Tech Hiring Boom',
      stat: '3.2M',
      description: 'New tech jobs expected by 2025',
      trend: '+22%',
      icon: TrendingUp,
      color: 'text-green-600 bg-green-100'
    },
    {
      title: 'Remote Work',
      stat: '73%',
      description: 'Of tech jobs offer remote options',
      trend: '+45%',
      icon: MapPin,
      color: 'text-blue-600 bg-blue-100'
    },
    {
      title: 'Salary Growth',
      stat: '$95K',
      description: 'Average tech salary in 2024',
      trend: '+12%',
      icon: DollarSign,
      color: 'text-purple-600 bg-purple-100'
    },
    {
      title: 'Skills Gap',
      stat: '85%',
      description: 'Companies struggle to find talent',
      trend: 'Opportunity',
      icon: Target,
      color: 'text-orange-600 bg-orange-100'
    }
  ];

  const testimonials = [
    {
      name: 'Alexandra Reed',
      role: 'Senior Frontend Developer',
      company: 'Microsoft',
      image: '👩‍💻',
      timeframe: '9 months',
      previousRole: 'Graphic Designer',
      quote: "Gradvy's structured approach helped me transition from design to development. The personalized learning path made all the difference.",
      salary: '+150% salary increase'
    },
    {
      name: 'David Kim',
      role: 'DevOps Engineer',
      company: 'Amazon',
      image: '👨‍💼',
      timeframe: '11 months',
      previousRole: 'Network Admin',
      quote: "The career guidance and hands-on projects prepared me for real-world challenges. Landing at Amazon was a dream come true.",
      salary: '+89% salary increase'
    },
    {
      name: 'Maria Santos',
      role: 'Data Scientist',
      company: 'Tesla',
      image: '👩‍🔬',
      timeframe: '14 months',
      previousRole: 'Business Analyst',
      quote: "From spreadsheets to machine learning models - Gradvy made the impossible possible. Now I'm building AI at Tesla.",
      salary: '+120% salary increase'
    }
  ];

  const learningPaths = [
    {
      title: 'Web Development Bootcamp',
      duration: '6-8 months',
      level: 'Beginner to Pro',
      skills: ['HTML/CSS', 'JavaScript', 'React', 'Node.js', 'MongoDB'],
      projects: 5,
      jobs: 'Frontend/Backend Developer',
      salary: '$70k - $120k',
      color: 'from-blue-500 to-cyan-500'
    },
    {
      title: 'Data Science Track',
      duration: '8-12 months',
      level: 'Beginner to Expert',
      skills: ['Python', 'Statistics', 'Machine Learning', 'SQL', 'Visualization'],
      projects: 4,
      jobs: 'Data Scientist/Analyst',
      salary: '$80k - $140k',
      color: 'from-purple-500 to-pink-500'
    },
    {
      title: 'Cloud Engineering Path',
      duration: '7-10 months',
      level: 'Intermediate to Pro',
      skills: ['AWS/Azure', 'Docker', 'Kubernetes', 'Infrastructure as Code'],
      projects: 6,
      jobs: 'Cloud/DevOps Engineer',
      salary: '$90k - $160k',
      color: 'from-green-500 to-teal-500'
    }
  ];

  const handleExploreCareer = () => {
    setShowPathways(true);
  };

  const handleStartLearning = (pathTitle) => {
    if (!isAuthenticated) {
      toast.success(`Ready to start "${pathTitle}"? Sign up to begin your journey!`);
      return;
    }
    toast.success(`Starting "${pathTitle}" learning path!`);
  };

  if (!showPathways) {
    return (
      <>
        <Head>
          <title>Tech Career Guide 2024 - Explore Programming Jobs & Salaries | Gradvy</title>
          <meta name="description" content="Discover high-paying tech careers in 2024. Explore software development, data science, DevOps, and more. Get salary insights, learning paths, and career roadmaps to land your dream tech job." />
          <meta name="keywords" content="tech careers 2024, software developer jobs, programming careers, tech job salaries, career change to tech, data science careers, web developer salary, DevOps jobs, tech career guide" />
          <meta property="og:title" content="Tech Career Guide 2024 - Programming Jobs & Salaries" />
          <meta property="og:description" content="Explore high-paying tech careers, salary insights, and personalized learning paths. Start your journey to a successful tech career today." />
          <meta property="og:type" content="website" />
          <meta property="og:url" content="/career" />
          <meta property="og:image" content="/images/career-og.jpg" />
          <meta name="twitter:card" content="summary_large_image" />
          <meta name="twitter:title" content="Tech Career Guide 2024 - Programming Jobs & Salaries" />
          <meta name="twitter:description" content="Explore high-paying tech careers and get personalized learning paths to land your dream job." />
          <meta name="twitter:image" content="/images/career-twitter.jpg" />
          <link rel="canonical" href="/career" />
        </Head>
        <div className="min-h-screen">
          <CareerHero onExploreCareer={handleExploreCareer} />
        
        {/* Industry Insights Section */}
        <section className="py-20 bg-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className="text-3xl lg:text-4xl font-bold text-gray-900 mb-4">
                The Tech Industry Today
              </h2>
              <p className="text-lg text-gray-600 max-w-3xl mx-auto">
                Understanding the landscape: opportunities, trends, and what it means for your career.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
              {industryInsights.map((insight, index) => {
                const Icon = insight.icon;
                return (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="text-center"
                  >
                    <Card className="p-6 h-full hover:shadow-lg transition-shadow">
                      <div className={`w-16 h-16 ${insight.color} rounded-full flex items-center justify-center mx-auto mb-4`}>
                        <Icon className="h-8 w-8" />
                      </div>
                      
                      <div className="space-y-2">
                        <h3 className="text-2xl font-bold text-gray-900">{insight.stat}</h3>
                        <h4 className="font-semibold text-gray-900">{insight.title}</h4>
                        <p className="text-sm text-gray-600">{insight.description}</p>
                        <Badge className="bg-green-100 text-green-700">
                          {insight.trend}
                        </Badge>
                      </div>
                    </Card>
                  </motion.div>
                );
              })}
            </div>
          </div>
        </section>

        {/* Learning Paths Preview */}
        <section className="py-20 bg-gradient-to-br from-gray-50 to-blue-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className="text-3xl lg:text-4xl font-bold text-gray-900 mb-4">
                Choose Your Learning Path
              </h2>
              <p className="text-lg text-gray-600 max-w-3xl mx-auto">
                Structured programs designed to take you from beginner to job-ready in months, not years.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {learningPaths.map((path, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <Card className="p-6 h-full hover:shadow-xl transition-all duration-300 group cursor-pointer">
                    <div className={`w-full h-2 bg-gradient-to-r ${path.color} rounded-full mb-4`}></div>
                    
                    <h3 className="text-xl font-bold text-gray-900 mb-2 group-hover:text-blue-600 transition-colors">
                      {path.title}
                    </h3>
                    
                    <div className="space-y-3 mb-6">
                      <div className="flex items-center justify-between text-sm">
                        <span className="flex items-center text-gray-600">
                          <Calendar className="h-4 w-4 mr-1" />
                          Duration
                        </span>
                        <span className="font-medium">{path.duration}</span>
                      </div>
                      
                      <div className="flex items-center justify-between text-sm">
                        <span className="flex items-center text-gray-600">
                          <Award className="h-4 w-4 mr-1" />
                          Level
                        </span>
                        <span className="font-medium">{path.level}</span>
                      </div>
                      
                      <div className="flex items-center justify-between text-sm">
                        <span className="flex items-center text-gray-600">
                          <DollarSign className="h-4 w-4 mr-1" />
                          Salary
                        </span>
                        <span className="font-medium text-green-600">{path.salary}</span>
                      </div>
                    </div>

                    <div className="space-y-4">
                      <div>
                        <p className="text-sm font-medium text-gray-900 mb-2">Skills You'll Learn:</p>
                        <div className="flex flex-wrap gap-1">
                          {path.skills.slice(0, 3).map(skill => (
                            <Badge key={skill} variant="secondary" className="text-xs">
                              {skill}
                            </Badge>
                          ))}
                          {path.skills.length > 3 && (
                            <Badge variant="outline" className="text-xs">
                              +{path.skills.length - 3} more
                            </Badge>
                          )}
                        </div>
                      </div>

                      <div className="flex items-center justify-between text-sm text-gray-600">
                        <span>{path.projects} Projects</span>
                        <span>Job: {path.jobs}</span>
                      </div>
                    </div>

                    <Button 
                      className="w-full mt-6 group-hover:shadow-md transition-shadow"
                      onClick={() => handleStartLearning(path.title)}
                    >
                      Start Learning Path
                      <ArrowRight className="h-4 w-4 ml-2 group-hover:translate-x-1 transition-transform" />
                    </Button>
                  </Card>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* Success Stories */}
        <section className="py-20 bg-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className="text-3xl lg:text-4xl font-bold text-gray-900 mb-4">
                Success Stories
              </h2>
              <p className="text-lg text-gray-600 max-w-3xl mx-auto">
                Real people, real career transformations. See how Gradvy helped them achieve their dreams.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {testimonials.map((testimonial, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <Card className="p-6 h-full hover:shadow-lg transition-shadow">
                    <div className="flex items-center space-x-3 mb-4">
                      <span className="text-4xl">{testimonial.image}</span>
                      <div>
                        <h3 className="font-semibold text-gray-900">{testimonial.name}</h3>
                        <p className="text-sm text-gray-600">{testimonial.role}</p>
                        <p className="text-sm font-medium text-blue-600">{testimonial.company}</p>
                      </div>
                    </div>

                    <div className="mb-4">
                      <Quote className="h-6 w-6 text-gray-300 mb-2" />
                      <p className="text-gray-700 italic">"{testimonial.quote}"</p>
                    </div>

                    <div className="space-y-2 pt-4 border-t border-gray-100">
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">Transition Time:</span>
                        <span className="font-medium">{testimonial.timeframe}</span>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">Previous Role:</span>
                        <span className="font-medium">{testimonial.previousRole}</span>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">Impact:</span>
                        <span className="font-medium text-green-600">{testimonial.salary}</span>
                      </div>
                    </div>

                    <div className="flex items-center mt-3">
                      {[...Array(5)].map((_, i) => (
                        <Star key={i} className="h-4 w-4 text-yellow-400 fill-current" />
                      ))}
                      <span className="text-sm text-gray-600 ml-2">Verified Graduate</span>
                    </div>
                  </Card>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-20 bg-gradient-to-r from-indigo-600 to-purple-600">
          <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
            <h2 className="text-3xl lg:text-4xl font-bold text-white mb-6">
              Your Tech Career Starts Today
            </h2>
            <p className="text-xl text-indigo-100 mb-8">
              Don't wait for the "perfect" moment. Join thousands of successful career changers who started with Gradvy.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-8">
              <Button
                size="lg"
                onClick={handleExploreCareer}
                className="bg-white text-indigo-600 hover:bg-gray-100 px-8 py-4 text-lg font-semibold rounded-xl"
              >
                <Target className="h-5 w-5 mr-2" />
                Explore Career Paths
              </Button>
              <Link href="/register">
                <Button
                  variant="outline"
                  size="lg"
                  className="border-2 border-white text-white hover:bg-white hover:text-indigo-600 px-8 py-4 text-lg font-semibold rounded-xl"
                >
                  <BookOpen className="h-5 w-5 mr-2" />
                  Start Learning Free
                </Button>
              </Link>
            </div>

            <div className="flex items-center justify-center space-x-6 text-indigo-100 text-sm">
              <div className="flex items-center">
                <CheckCircle className="h-4 w-4 mr-1" />
                <span>No commitments</span>
              </div>
              <div className="flex items-center">
                <CheckCircle className="h-4 w-4 mr-1" />
                <span>Free to start</span>
              </div>
              <div className="flex items-center">
                <CheckCircle className="h-4 w-4 mr-1" />
                <span>Job guarantee program</span>
              </div>
            </div>
          </div>
        </section>
        </div>
      </>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Back Button */}
      <div className="bg-white border-b border-gray-200 px-4 py-3">
        <div className="max-w-7xl mx-auto">
          <Button
            variant="ghost"
            onClick={() => setShowPathways(false)}
            className="flex items-center text-gray-600 hover:text-gray-900"
          >
            <ArrowRight className="h-4 w-4 mr-2 rotate-180" />
            Back to Career Overview
          </Button>
        </div>
      </div>

      {/* Career Pathways Component */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8 text-center">
          <h1 className="text-3xl lg:text-4xl font-bold text-gray-900 mb-4">
            Explore Tech Career Paths
          </h1>
          <p className="text-lg text-gray-600 max-w-3xl mx-auto">
            Discover detailed career information, salary insights, and learning roadmaps for different tech roles.
          </p>
        </div>

        <CareerPathways />

        {/* Additional CTA */}
        <div className="mt-16 text-center">
          <Card className="p-8 bg-gradient-to-br from-blue-50 to-indigo-100">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">
              Ready to Start Your Journey?
            </h3>
            <p className="text-gray-600 mb-6 max-w-2xl mx-auto">
              Take our career assessment to get personalized recommendations and start building the skills you need.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/register">
                <Button size="lg" className="bg-indigo-600 hover:bg-indigo-700">
                  <BookOpen className="h-5 w-5 mr-2" />
                  Start Free Assessment
                </Button>
              </Link>
              <Button variant="outline" size="lg">
                <MessageSquare className="h-5 w-5 mr-2" />
                Talk to Career Advisor
              </Button>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}