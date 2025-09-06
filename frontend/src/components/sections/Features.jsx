'use client';

import { motion } from 'framer-motion';
import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from '../ui/Card';
import { Brain, MapPin, BarChart3, Code, Timer, Layers } from 'lucide-react';

const Features = () => {
	const features = [
		{
			icon: Brain,
			title: 'Smart Path Generation',
			description:
				'AI analyzes your goals and creates personalized learning roadmaps with curated courses from top platforms.',
			gradient: 'from-blue-500 to-purple-600',
		},
		{
			icon: MapPin,
			title: 'Adaptive Learning Flow',
			description:
				'Dynamic curriculum that adjusts based on your progress, strengths, and learning preferences.',
			gradient: 'from-green-500 to-teal-600',
		},
		{
			icon: BarChart3,
			title: 'Progress Analytics',
			description:
				'Comprehensive tracking with visual insights, streaks, and performance metrics to keep you motivated.',
			gradient: 'from-orange-500 to-red-600',
		},
		{
			icon: Code,
			title: 'Coding Playground',
			description:
				'Practice programming with our integrated editor supporting multiple languages and instant feedback.',
			gradient: 'from-pink-500 to-rose-600',
		},
		{
			icon: Timer,
			title: 'Time Optimization',
			description:
				'Efficient learning schedules that fit your availability and maximize knowledge retention.',
			gradient: 'from-yellow-500 to-orange-600',
		},
		{
			icon: Layers,
			title: 'Multi-Platform Integration',
			description:
				'Seamlessly access courses from Udemy, Coursera, YouTube, and other leading educational platforms.',
			gradient: 'from-indigo-500 to-blue-600',
		},
	];

	const containerVariants = {
		hidden: { opacity: 0 },
		visible: {
			opacity: 1,
			transition: {
				delayChildren: 0.3,
				staggerChildren: 0.1,
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

	return (
		<section id='features' className='py-24 bg-white'>
			<div className='max-w-7xl mx-auto px-4 sm:px-6 lg:px-8'>
				<motion.div
					initial={{ opacity: 0, y: 20 }}
					whileInView={{ opacity: 1, y: 0 }}
					viewport={{ once: true }}
					transition={{ duration: 0.6 }}
					className='text-center mb-16'
				>
					<h2 className='text-3xl sm:text-4xl lg:text-5xl font-bold text-gray-900 mb-4'>
						Powerful Features for{' '}
						<span className='gradient-text'>Accelerated Learning</span>
					</h2>
					<p className='text-xl text-gray-600 max-w-3xl mx-auto'>
						Discover how Gradvy's intelligent platform transforms your learning
						experience with personalized guidance and cutting-edge tools.
					</p>
				</motion.div>

				<motion.div
					variants={containerVariants}
					initial='hidden'
					whileInView='visible'
					viewport={{ once: true }}
					className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8'
				>
					{features.map((feature, index) => {
						const Icon = feature.icon;
						return (
							<motion.div
								key={feature.title}
								variants={itemVariants}
								className='group'
							>
								<Card className='h-full border-0 shadow-lg hover:shadow-xl transition-all duration-300 group-hover:-translate-y-2 bg-gradient-to-br from-white to-gray-50'>
									<CardHeader className='text-center pb-4'>
										<div
											className={`w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-r ${feature.gradient} flex items-center justify-center group-hover:scale-110 transition-transform duration-300`}
										>
											<Icon className='h-8 w-8 text-white' />
										</div>
										<CardTitle className='text-xl font-bold text-gray-900 group-hover:text-primary transition-colors duration-300'>
											{feature.title}
										</CardTitle>
									</CardHeader>
									<CardContent className='text-center'>
										<CardDescription className='text-gray-600 text-base leading-relaxed'>
											{feature.description}
										</CardDescription>
									</CardContent>
								</Card>
							</motion.div>
						);
					})}
				</motion.div>

				{/* Additional Stats Section */}
				<motion.div
					initial={{ opacity: 0, y: 20 }}
					whileInView={{ opacity: 1, y: 0 }}
					viewport={{ once: true }}
					transition={{ duration: 0.6, delay: 0.3 }}
					className='mt-24 text-center'
				>
					<div className='bg-gradient-to-r from-primary to-accent rounded-2xl p-8 text-white'>
						<h3 className='text-2xl font-bold mb-4'>
							Transform Your Learning Journey Today
						</h3>
						<div className='grid grid-cols-1 sm:grid-cols-3 gap-8'>
							<div>
								<div className='text-3xl font-bold mb-2'>24/7</div>
								<div className='text-blue-100'>AI Guidance Available</div>
							</div>
							<div>
								<div className='text-3xl font-bold mb-2'>100+</div>
								<div className='text-blue-100'>Career Paths Supported</div>
							</div>
							<div>
								<div className='text-3xl font-bold mb-2'>5min</div>
								<div className='text-blue-100'>Quick Setup Time</div>
							</div>
						</div>
					</div>
				</motion.div>
			</div>
		</section>
	);
};

export default Features;
