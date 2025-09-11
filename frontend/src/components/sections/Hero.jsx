'use client';

import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import {
	ArrowRight,
	Brain,
	Sparkles,
	Users,
	BookOpen,
	Award,
} from 'lucide-react';
import Link from 'next/link';

const Hero = () => {
	const containerVariants = {
		hidden: { opacity: 0 },
		visible: {
			opacity: 1,
			transition: {
				delayChildren: 0.3,
				staggerChildren: 0.2,
			},
		},
	};

	const itemVariants = {
		hidden: { y: 20, opacity: 0 },
		visible: {
			y: 0,
			opacity: 1,
			transition: {
				type: 'spring',
				stiffness: 100,
			},
		},
	};

	const stats = [
		{ icon: Users, label: '150k+', description: 'Learners Guided' },
		{ icon: BookOpen, label: '1000+', description: 'Course Partners' },
		{ icon: Award, label: '95%', description: 'Goal Achievement' },
	];

	return (
		<section className='relative min-h-screen flex items-center justify-center overflow-hidden neural-bg'>
			{/* Animated Background Elements */}
			<div className='absolute inset-0 overflow-hidden'>
				<div className='absolute -top-40 -right-32 w-80 h-80 bg-primary/10 rounded-full blur-3xl animate-pulse' />
				<div className='absolute -bottom-40 -left-32 w-80 h-80 bg-accent/10 rounded-full blur-3xl animate-pulse delay-1000' />
				<div className='absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-gradient-to-r from-primary/5 to-accent/5 rounded-full blur-3xl animate-float' />
			</div>

			<div className='relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16'>
				<motion.div
					variants={containerVariants}
					initial='hidden'
					animate='visible'
					className='text-center'
				>
					{/* Badge */}
					<motion.div
						variants={itemVariants}
						className='inline-flex items-center px-4 py-2 bg-white/80 backdrop-blur-sm rounded-full border border-gray-200 mb-8'
					>
						<Sparkles className='w-4 h-4 text-primary mr-2' />
						<span className='text-sm font-medium text-gray-700'>
							AI-Powered Learning Path Generator
						</span>
					</motion.div>

					{/* Main Heading */}
					<motion.h1
						variants={itemVariants}
						className='text-4xl sm:text-6xl lg:text-7xl font-bold text-gray-900 mb-6 leading-tight'
					>
						Build Your <span className='gradient-text'>Perfect Learning</span>{' '}
						Journey
					</motion.h1>

					{/* Subtitle */}
					<motion.p
						variants={itemVariants}
						className='text-xl sm:text-2xl text-gray-600 mb-8 max-w-4xl mx-auto leading-relaxed'
					>
						Let AI create personalized learning paths from top platforms like
						Udemy, Coursera, and YouTube. Track progress, practice coding, and
						accelerate your career growth.
					</motion.p>

					{/* CTA Buttons */}
					<motion.div
						variants={itemVariants}
						className='flex flex-col sm:flex-row gap-4 justify-center items-center mb-16'
					>
						<Link href='/app/onboarding'>
							<Button size='xl' variant='gradient' className='group'>
								Start with Goal
								<ArrowRight className='ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform' />
							</Button>
						</Link>
						<Link href='/onboarding?flow=discover'>
							<Button size='xl' variant='outline' className='group'>
								Help me decide
								<Brain className='ml-2 h-5 w-5 group-hover:rotate-12 transition-transform' />
							</Button>
						</Link>
					</motion.div>

					{/* Stats */}
					<motion.div
						variants={itemVariants}
						className='grid grid-cols-1 sm:grid-cols-3 gap-8 max-w-2xl mx-auto'
					>
						{stats.map((stat, index) => {
							const Icon = stat.icon;
							return (
								<motion.div
									key={stat.label}
									initial={{ scale: 0.8, opacity: 0 }}
									animate={{ scale: 1, opacity: 1 }}
									transition={{ delay: 0.8 + index * 0.1 }}
									className='text-center'
								>
									<div className='w-12 h-12 bg-gradient-to-r from-primary to-accent rounded-lg flex items-center justify-center mx-auto mb-3'>
										<Icon className='h-6 w-6 text-white' />
									</div>
									<div className='text-2xl font-bold text-gray-900'>
										{stat.label}
									</div>
									<div className='text-sm text-gray-600'>
										{stat.description}
									</div>
								</motion.div>
							);
						})}
					</motion.div>

					{/* Floating Elements */}
					<motion.div
						initial={{ opacity: 0, scale: 0.8 }}
						animate={{ opacity: 1, scale: 1 }}
						transition={{ delay: 1.2, duration: 0.8 }}
						className='absolute top-20 right-10 hidden lg:block'
					>
						<div className='w-16 h-16 bg-gradient-to-r from-primary to-accent rounded-2xl rotate-12 animate-float' />
					</motion.div>

					<motion.div
						initial={{ opacity: 0, scale: 0.8 }}
						animate={{ opacity: 1, scale: 1 }}
						transition={{ delay: 1.4, duration: 0.8 }}
						className='absolute bottom-32 left-10 hidden lg:block'
					>
						<div className='w-12 h-12 bg-gradient-to-r from-accent to-primary rounded-xl -rotate-12 animate-float' />
					</motion.div>
				</motion.div>
			</div>

			{/* Scroll Indicator */}
			<motion.div
				initial={{ opacity: 0, y: 20 }}
				animate={{ opacity: 1, y: 0 }}
				transition={{ delay: 2, duration: 0.8 }}
				className='absolute bottom-8 left-1/2 transform -translate-x-1/2'
			>
				<div className='flex flex-col items-center'>
					<span className='text-sm text-gray-500 mb-2'>Scroll to explore</span>
					<div className='w-6 h-10 border-2 border-gray-300 rounded-full flex justify-center'>
						<div className='w-1 h-3 bg-gray-400 rounded-full mt-2 animate-bounce' />
					</div>
				</div>
			</motion.div>
		</section>
	);
};

export default Hero;
