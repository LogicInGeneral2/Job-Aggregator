import Heatmap from '@/components/Globe';
import Omnibox from '@/components/Omnibox';
import TrendingJobs from '@/components/TrendingJobs';
import TrendingSkills from '@/components/TrendingSkills';
import UserProfile from '@/components/UserProfile';

export default function Home() {
  return (
    <main className="min-h-screen flex flex-col items-center p-8 font-sans">
      
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-4xl font-extrabold tracking-tight">Global Job Board Aggregator</h1>
        <p className="text-gray-500 mt-2">Powered by Kubernetes, Kafka, Elasticsearch, and Redis</p>
      </div>

      {/* Primary Components */}
      <Omnibox />
      
      <div className="w-full max-w-4xl border-t my-12 border-gray-200"></div>
      
      {/* Feeds Layout */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {/* Left Column: Job Feed (Takes up 2/3 of the screen) */}
        <div className="md:col-span-2">
            <TrendingJobs /> 
        </div>
        
        {/* Right Column: Sidebar (Takes up 1/3 of the screen) */}
        <div className="md:col-span-1 space-y-6">
            <TrendingSkills />
            <UserProfile />
        </div>
      </section>

      <Heatmap />



    </main>
  );
}