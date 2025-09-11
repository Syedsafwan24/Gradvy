'use client';

import { motion } from 'framer-motion';
import { Card, CardContent } from '@/components/ui/card';
import { Star, Quote } from 'lucide-react';

const Testimonials = () => {
	const testimonials = [
		{
			name: 'Sarah Chen',
			role: 'Software Engineer at Google',
			avatar:
				'https://images.unsplash.com/photo-1494790108755-2616b612b786?w=64&h=64&fit=crop&crop=face',
			content:
				'Gradvy completely transformed my career path. The AI recommendations were spot-on and helped me land my dream job at Google.',
			rating: 5,
		},
		{
			name: 'Marcus Johnson',
			role: 'Data Scientist at Netflix',
			avatar:
				'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=64&h=64&fit=crop&crop=face',
			content:
				'The personalized learning path saved me months of random course browsing. Everything was structured perfectly for my goals.',
			rating: 5,
		},
		{
			name: 'Emily Rodriguez',
			role: 'UX Designer at Airbnb',
			avatar:
				'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=64&h=64&fit=crop&crop=face',
			content:
				'The coding playground feature helped me practice real-world scenarios. The progress tracking kept me motivated throughout.',
			rating: 5,
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
		<section className='py-24 bg-gray-50'>
			<div className='max-w-7xl mx-auto px-4 sm:px-6 lg:px-8'>
				<motion.div
					initial={{ opacity: 0, y: 20 }}
					whileInView={{ opacity: 1, y: 0 }}
					viewport={{ once: true }}
					transition={{ duration: 0.6 }}
					className='text-center mb-16'
				>
					<h2 className='text-3xl sm:text-4xl lg:text-5xl font-bold text-gray-900 mb-4'>
						Success <span className='gradient-text'>Stories</span>
					</h2>
					<p className='text-xl text-gray-600 max-w-3xl mx-auto'>
						Hear from learners who accelerated their careers with Gradvy's
						AI-powered learning paths.
					</p>
				</motion.div>

				<motion.div
					variants={containerVariants}
					initial='hidden'
					whileInView='visible'
					viewport={{ once: true }}
					className='grid grid-cols-1 md:grid-cols-3 gap-8'
				>
					{testimonials.map((testimonial, index) => (
						<motion.div
							key={testimonial.name}
							variants={itemVariants}
							className='group'
						>
							<Card className='h-full bg-white border-0 shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-2'>
								<CardContent className='p-6'>
									<Quote className='h-8 w-8 text-primary mb-4 opacity-50' />

									<p className='text-gray-700 mb-6 leading-relaxed'>
										"{testimonial.content}"
									</p>

									<div className='flex items-center mb-4'>
										{[...Array(testimonial.rating)].map((_, i) => (
											<Star
												key={i}
												className='h-4 w-4 text-yellow-400 fill-current'
											/>
										))}
									</div>

									<div className='flex items-center'>
										<img
											src={testimonial.avatar}
											alt={testimonial.name}
											className='w-12 h-12 rounded-full mr-4 object-cover'
										/>
										<div>
											<h4 className='font-semibold text-gray-900'>
												{testimonial.name}
											</h4>
											<p className='text-gray-600 text-sm'>
												{testimonial.role}
											</p>
										</div>
									</div>
								</CardContent>
							</Card>
						</motion.div>
					))}
				</motion.div>
			</div>
		</section>
	);
};

export default Testimonials;
