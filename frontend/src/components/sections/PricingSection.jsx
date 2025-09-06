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
import { Check, Sparkles, Crown, Zap } from 'lucide-react';

const PricingSection = () => {
	const plans = [
		{
			name: 'Starter',
			price: '0',
			period: 'Forever',
			description: 'Perfect for getting started with AI-powered learning',
			features: [
				'Basic learning path generation',
				'Access to free courses',
				'Progress tracking',
				'Community access',
				'Basic career insights',
			],
			recommended: false,
			icon: Sparkles,
			gradient: 'from-gray-500 to-gray-600',
		},
		{
			name: 'Pro',
			price: '29',
			period: 'per month',
			description: 'Most popular choice for serious learners',
			features: [
				'Advanced AI path optimization',
				'Premium course access',
				'Coding playground',
				'Priority support',
				'Detailed analytics',
				'Career coaching',
				'Custom assessments',
			],
			recommended: true,
			icon: Crown,
			gradient: 'from-blue-500 to-purple-600',
		},
		{
			name: 'Enterprise',
			price: '99',
			period: 'per month',
			description: 'For teams and organizations',
			features: [
				'Everything in Pro',
				'Team management',
				'Custom integrations',
				'White-label options',
				'Dedicated support',
				'Advanced reporting',
				'API access',
			],
			recommended: false,
			icon: Zap,
			gradient: 'from-purple-500 to-pink-600',
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
		<section id='pricing' className='py-24 bg-white'>
			<div className='max-w-7xl mx-auto px-4 sm:px-6 lg:px-8'>
				<motion.div
					initial={{ opacity: 0, y: 20 }}
					whileInView={{ opacity: 1, y: 0 }}
					viewport={{ once: true }}
					transition={{ duration: 0.6 }}
					className='text-center mb-16'
				>
					<h2 className='text-3xl sm:text-4xl lg:text-5xl font-bold text-gray-900 mb-4'>
						Simple and Flexible <span className='gradient-text'>Pricing</span>
					</h2>
					<p className='text-xl text-gray-600 max-w-3xl mx-auto'>
						Choose the perfect plan for your learning journey. Start free and
						upgrade as you grow.
					</p>
				</motion.div>

				<motion.div
					variants={containerVariants}
					initial='hidden'
					whileInView='visible'
					viewport={{ once: true }}
					className='grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto'
				>
					{plans.map((plan, index) => {
						const Icon = plan.icon;
						return (
							<motion.div
								key={plan.name}
								variants={itemVariants}
								className={`relative ${plan.recommended ? 'md:-mt-4' : ''}`}
							>
								{plan.recommended && (
									<div className='absolute -top-4 left-1/2 transform -translate-x-1/2 z-10'>
										<span className='bg-gradient-to-r from-blue-500 to-purple-600 text-white px-4 py-1 rounded-full text-sm font-medium'>
											Most Popular
										</span>
									</div>
								)}

								<Card
									className={`h-full border-0 shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-2 ${
										plan.recommended
											? 'bg-gradient-to-br from-blue-50 to-purple-50 border-2 border-blue-200'
											: 'bg-white'
									}`}
								>
									<CardHeader className='text-center pb-4'>
										<div
											className={`w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-r ${plan.gradient} flex items-center justify-center`}
										>
											<Icon className='h-8 w-8 text-white' />
										</div>
										<CardTitle className='text-2xl font-bold text-gray-900 mb-2'>
											{plan.name}
										</CardTitle>
										<div className='mb-4'>
											<span className='text-4xl font-bold text-gray-900'>
												${plan.price}
											</span>
											<span className='text-gray-600 ml-2'>{plan.period}</span>
										</div>
										<CardDescription className='text-gray-600'>
											{plan.description}
										</CardDescription>
									</CardHeader>

									<CardContent className='space-y-4'>
										<ul className='space-y-3 mb-8'>
											{plan.features.map((feature, featureIndex) => (
												<li key={featureIndex} className='flex items-center'>
													<Check className='h-5 w-5 text-green-500 mr-3 flex-shrink-0' />
													<span className='text-gray-700'>{feature}</span>
												</li>
											))}
										</ul>

										<Button
											className='w-full'
											variant={plan.recommended ? 'gradient' : 'outline'}
											size='lg'
										>
											{plan.price === '0'
												? 'Get Started Free'
												: `Choose ${plan.name}`}
										</Button>
									</CardContent>
								</Card>
							</motion.div>
						);
					})}
				</motion.div>

				{/* Additional Info */}
				<motion.div
					initial={{ opacity: 0, y: 20 }}
					whileInView={{ opacity: 1, y: 0 }}
					viewport={{ once: true }}
					transition={{ duration: 0.6, delay: 0.3 }}
					className='text-center mt-16'
				>
					<p className='text-gray-600 mb-8'>
						All plans include 14-day money-back guarantee. No setup fees. Cancel
						anytime.
					</p>

					<div className='grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto'>
						<div className='text-center'>
							<div className='w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3'>
								<Check className='h-6 w-6 text-green-600' />
							</div>
							<h4 className='font-semibold text-gray-900 mb-2'>
								No Hidden Fees
							</h4>
							<p className='text-gray-600 text-sm'>
								Transparent pricing with no surprise charges
							</p>
						</div>

						<div className='text-center'>
							<div className='w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3'>
								<Sparkles className='h-6 w-6 text-blue-600' />
							</div>
							<h4 className='font-semibold text-gray-900 mb-2'>
								14-Day Free Trial
							</h4>
							<p className='text-gray-600 text-sm'>
								Try Pro features risk-free for two weeks
							</p>
						</div>

						<div className='text-center'>
							<div className='w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-3'>
								<Crown className='h-6 w-6 text-purple-600' />
							</div>
							<h4 className='font-semibold text-gray-900 mb-2'>
								Cancel Anytime
							</h4>
							<p className='text-gray-600 text-sm'>
								No long-term commitments required
							</p>
						</div>
					</div>
				</motion.div>
			</div>
		</section>
	);
};

export default PricingSection;
