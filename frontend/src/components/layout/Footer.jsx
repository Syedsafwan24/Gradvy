import Link from 'next/link';
import { Brain, Twitter, Github, Linkedin, Mail } from 'lucide-react';

const Footer = () => {
	const footerLinks = {
		product: [
			{ name: 'Features', href: '#features' },
			{ name: 'How It Works', href: '#how-it-works' },
			{ name: 'Pricing', href: '#pricing' },
			{ name: 'Playground', href: '/playground' },
		],
		company: [
			{ name: 'About Us', href: '/team' },
			{ name: 'Careers', href: '/career' },
			{ name: 'Contact', href: '/contact' },
			{ name: 'Blog', href: '/blog' },
		],
		resources: [
			{ name: 'Documentation', href: '/docs' },
			{ name: 'Help Center', href: '/help' },
			{ name: 'FAQ', href: '/faq' },
			{ name: 'Community', href: '/community' },
		],
		legal: [
			{ name: 'Privacy Policy', href: '/privacy' },
			{ name: 'Terms of Service', href: '/terms' },
			{ name: 'Cookie Policy', href: '/cookies' },
		],
	};

	const socialLinks = [
		{ name: 'Twitter', icon: Twitter, href: 'https://twitter.com/gradvy' },
		{ name: 'GitHub', icon: Github, href: 'https://github.com/Syedsafwan24/Gradvy' },
		{
			name: 'LinkedIn',
			icon: Linkedin,
			href: 'https://linkedin.com/company/gradvy',
		},
		{ name: 'Email', icon: Mail, href: 'mailto:hello@gradvy.com' },
	];

	return (
		<footer className='bg-secondary text-white'>
			<div className='max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12'>
				<div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-8'>
					{/* Brand Section */}
					<div className='lg:col-span-2'>
						<Link href='/' className='flex items-center space-x-2 mb-4'>
							<div className='w-8 h-8 bg-gradient-to-r from-primary to-accent rounded-lg flex items-center justify-center'>
								<Brain className='h-5 w-5 text-white' />
							</div>
							<span className='text-xl font-bold'>Gradvy</span>
						</Link>
						<p className='text-gray-300 mb-6 max-w-sm'>
							Empower your future with cutting-edge AI solutions for
							personalized learning paths. Transform your career with
							intelligent guidance.
						</p>
						<div className='flex space-x-4'>
							{socialLinks.map((social) => {
								const Icon = social.icon;
								return (
									<a
										key={social.name}
										href={social.href}
										className='text-gray-400 hover:text-white transition-colors duration-200'
										aria-label={social.name}
									>
										<Icon className='h-5 w-5' />
									</a>
								);
							})}
						</div>
					</div>

					{/* Links Sections */}
					<div>
						<h3 className='text-sm font-semibold uppercase tracking-wider mb-4'>
							Product
						</h3>
						<ul className='space-y-3'>
							{footerLinks.product.map((link) => (
								<li key={link.name}>
									<Link
										href={link.href}
										className='text-gray-300 hover:text-white transition-colors duration-200'
									>
										{link.name}
									</Link>
								</li>
							))}
						</ul>
					</div>

					<div>
						<h3 className='text-sm font-semibold uppercase tracking-wider mb-4'>
							Company
						</h3>
						<ul className='space-y-3'>
							{footerLinks.company.map((link) => (
								<li key={link.name}>
									<Link
										href={link.href}
										className='text-gray-300 hover:text-white transition-colors duration-200'
									>
										{link.name}
									</Link>
								</li>
							))}
						</ul>
					</div>

					<div>
						<h3 className='text-sm font-semibold uppercase tracking-wider mb-4'>
							Resources
						</h3>
						<ul className='space-y-3'>
							{footerLinks.resources.map((link) => (
								<li key={link.name}>
									<Link
										href={link.href}
										className='text-gray-300 hover:text-white transition-colors duration-200'
									>
										{link.name}
									</Link>
								</li>
							))}
						</ul>
					</div>

					<div>
						<h3 className='text-sm font-semibold uppercase tracking-wider mb-4'>
							Legal
						</h3>
						<ul className='space-y-3'>
							{footerLinks.legal.map((link) => (
								<li key={link.name}>
									<Link
										href={link.href}
										className='text-gray-300 hover:text-white transition-colors duration-200'
									>
										{link.name}
									</Link>
								</li>
							))}
						</ul>
					</div>
				</div>

				{/* Newsletter Section */}
				<div className='border-t border-gray-700 mt-12 pt-8'>
					<div className='md:flex md:items-center md:justify-between'>
						<div className='mb-4 md:mb-0'>
							<h3 className='text-lg font-semibold mb-2'>Stay updated</h3>
							<p className='text-gray-300'>
								Get the latest news and updates from Gradvy.
							</p>
						</div>
						<div className='flex max-w-md'>
							<input
								type='email'
								placeholder='Enter your email'
								className='flex-1 px-4 py-2 bg-gray-700 border border-gray-600 rounded-l-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'
							/>
							<button className='px-6 py-2 bg-primary hover:bg-primary/90 text-white rounded-r-md transition-colors duration-200'>
								Subscribe
							</button>
						</div>
					</div>
				</div>

				{/* Bottom Section */}
				<div className='border-t border-gray-700 mt-8 pt-8 text-center'>
					<p className='text-gray-400'>
						© {new Date().getFullYear()} Gradvy. All rights reserved.
					</p>
				</div>
			</div>
		</footer>
	);
};

export default Footer;
