import './globals.css';
import { Inter } from 'next/font/google';
import Navbar from '../components/layout/Navbar';
import Footer from '../components/layout/Footer';
import ReduxProvider from '../providers/ReduxProvider';
import { Toaster } from 'react-hot-toast';

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
				<ReduxProvider>
					<div className='min-h-screen bg-slate-50 flex flex-col'>
						<Navbar />
						<main className='flex-1'>{children}</main>
						<Footer />
					</div>
					<Toaster
						position="top-right"
						toastOptions={{
							duration: 4000,
							style: {
								background: '#363636',
								color: '#fff',
							},
							success: {
								duration: 3000,
								style: {
									background: '#10B981',
								},
							},
							error: {
								duration: 5000,
								style: {
									background: '#EF4444',
								},
							},
						}}
					/>
				</ReduxProvider>
			</body>
		</html>
	);
}
