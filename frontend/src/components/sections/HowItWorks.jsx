'use client';

import { motion } from 'framer-motion';
import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { ArrowRight, UserPlus, Brain, BookOpen, BarChart3 } from 'lucide-react';

const HowItWorks = () => {
	const steps = [
		{
			step: '01',
			icon: UserPlus,
			title: 'Choose Your Path',
			description:
				'Start with a clear goal or let our AI help you discover your interests through personalized assessments.',
			color: 'from-blue-500 to-blue-600',
		},
		{
			step: '02',
			icon: Brain,
			title: 'AI Analysis',
			description:
				'Our neural networks analyze your background, time availability, and learning preferences to create your custom roadmap.',
			color: 'from-purple-500 to-purple-600',
		},
		{
			step: '03',
			icon: BookOpen,
			title: 'Learn & Practice',
			description:
				'Follow your personalized curriculum with courses from top platforms, coding challenges, and progress tracking.',
			color: 'from-green-500 to-green-600',
		},
		{
			step: '04',
			icon: BarChart3,
			title: 'Track Progress',
			description:
				'Monitor your growth with detailed analytics, career insights, and adaptive recommendations for continuous improvement.',
			color: 'from-orange-500 to-orange-600',
		},
	];

	const containerVariants = {
		hidden: { opacity: 0 },
		visible: {
			opacity: 1,
			transition: {
				delayChildren: 0.2,
				staggerChildren: 0.1,
			},
		},
	};

	const itemVariants = {
		hidden: { y: 30, opacity: 0 },
		visible: {
			y: 0,
			opacity: 1,
			transition: {
				type: 'spring',
				stiffness: 80,
			},
		},
	};

	return (
		<section id='how-it-works' className='py-24 bg-gray-50'>
			<div className='max-w-7xl mx-auto px-4 sm:px-6 lg:px-8'>
				<motion.div
					initial={{ opacity: 0, y: 20 }}
					whileInView={{ opacity: 1, y: 0 }}
					viewport={{ once: true }}
					transition={{ duration: 0.6 }}
					className='text-center mb-16'
				>
					<h2 className='text-3xl sm:text-4xl lg:text-5xl font-bold text-gray-900 mb-4'>
						How It <span className='gradient-text'>Works</span>
					</h2>
					<p className='text-xl text-gray-600 max-w-3xl mx-auto'>
						Get started with Gradvy in four simple steps and transform your
						learning journey with AI-powered guidance.
					</p>
				</motion.div>

				<motion.div
					variants={containerVariants}
					initial='hidden'
					whileInView='visible'
					viewport={{ once: true }}
					className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-16'
				>
					{steps.map((step, index) => {
						const Icon = step.icon;
						return (
							<motion.div
								key={step.step}
								variants={itemVariants}
								className='relative'
							>
								<Card className='h-full bg-white border-0 shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-2 group'>
									<CardHeader className='text-center pb-4'>
										<div className='relative mb-6'>
											<div
												className={`w-16 h-16 mx-auto rounded-2xl bg-gradient-to-r ${step.color} flex items-center justify-center group-hover:scale-110 transition-transform duration-300`}
											>
												<Icon className='h-8 w-8 text-white' />
											</div>
											<div className='absolute -top-2 -right-2 w-8 h-8 bg-gray-900 text-white rounded-full flex items-center justify-center text-sm font-bold'>
												{step.step}
											</div>
										</div>
										<CardTitle className='text-xl font-bold text-gray-900 mb-2'>
											{step.title}
										</CardTitle>
									</CardHeader>
									<CardContent className='text-center'>
										<CardDescription className='text-gray-600 text-base leading-relaxed'>
											{step.description}
										</CardDescription>
									</CardContent>
								</Card>

								{/* Connector Line */}
								{index < steps.length - 1 && (
									<div className='hidden lg:block absolute top-1/2 -right-4 w-8 h-0.5 bg-gradient-to-r from-gray-300 to-gray-400 transform -translate-y-1/2 z-10'>
										<ArrowRight className='absolute -right-2 -top-2 h-4 w-4 text-gray-400' />
									</div>
								)}
							</motion.div>
						);
					})}
				</motion.div>

				{/* CTA Section */}
				<motion.div
					initial={{ opacity: 0, y: 20 }}
					whileInView={{ opacity: 1, y: 0 }}
					viewport={{ once: true }}
					transition={{ duration: 0.6, delay: 0.3 }}
					className='text-center'
				>
					<div className='bg-white rounded-2xl p-8 shadow-lg max-w-2xl mx-auto'>
						<h3 className='text-2xl font-bold text-gray-900 mb-4'>
							Ready to Start Your Learning Journey?
						</h3>
						<p className='text-gray-600 mb-6'>
							Join thousands of learners who have accelerated their careers with
							Gradvy's AI-powered learning paths.
						</p>
						<Button size='lg' variant='gradient' className='group'>
							Get Started Now
							<ArrowRight className='ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform' />
						</Button>
					</div>
				</motion.div>
			</div>
		</section>
	);
};

export default HowItWorks;
