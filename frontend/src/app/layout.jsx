import './globals.css';
import { Inter } from 'next/font/google';
import Navbar from '../components/layout/Navbar';
import Footer from '../components/layout/Footer';

const inter = Inter({
	subsets: ['latin'],
	display: 'swap',
	variable: '--font-inter',
});

export const metadata = {
	title: {
		default: 'Gradvy - AI Personalized Learning Path Generator',
		template: '%s | Gradvy',
	},
	description:
		'Empower your future with cutting-edge AI solutions for personalized learning paths',
	keywords: [
		'AI learning',
		'personalized education',
		'career development',
		'online courses',
	],
	authors: [{ name: 'Gradvy Team' }],
	creator: 'Gradvy',
	openGraph: {
		type: 'website',
		locale: 'en_US',
		url: 'https://gradvy.com',
		title: 'Gradvy - AI Personalized Learning Path Generator',
		description:
			'Empower your future with cutting-edge AI solutions for personalized learning paths',
		siteName: 'Gradvy',
	},
	twitter: {
		card: 'summary_large_image',
		title: 'Gradvy - AI Personalized Learning Path Generator',
		description:
			'Empower your future with cutting-edge AI solutions for personalized learning paths',
		creator: '@gradvy',
	},
	robots: {
		index: true,
		follow: true,
	},
};

export default function RootLayout({ children }) {
	return (
		<html lang='en' className={inter.variable}>
			<body className={`${inter.className} antialiased`}>
				<div className='min-h-screen bg-slate-50 flex flex-col'>
					<Navbar />
					<main className='flex-1'>{children}</main>
					<Footer />
				</div>
			</body>
		</html>
	);
}
