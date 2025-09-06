import Hero from '../components/sections/Hero';
import Features from '../components/sections/Features';
import HowItWorks from '../components/sections/HowItWorks';
import HighlightCourses from '../components/sections/HighlightCourses';
import CodePlayground from '../components/sections/CodePlayground';
import Testimonials from '../components/sections/Testimonials';
import FAQ from '../components/sections/FAQ';
import Team from '../components/sections/Team';

export default function Home() {
	return (
		<div className='min-h-screen'>
			<Hero />
			<Features />
			<HowItWorks />
			<HighlightCourses />
			<CodePlayground />
			<Testimonials />
			<FAQ />
			<Team />
		</div>
	);
}
