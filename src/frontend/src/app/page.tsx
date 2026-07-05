import Heatmap from '@/components/Globe';
import TrendingJobs from '@/components/TrendingJobs';
import TrendingSkills from '@/components/TrendingSkills';
import UserProfile from '@/components/UserProfile';

export default function Home() {
  return (
    <main>
    
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

      <div className="mb-12">
          <div className="flex justify-between items-end mb-4">
              <div>
                  <h2 className="text-2xl font-bold text-gray-800">🌍 Global Topology Network</h2>
                  <p className="text-gray-500 text-sm">
                      Live Force-Directed graph powered by Elasticsearch Bucket Aggregations & D3 Physics.
                  </p>
              </div>
          </div>          
      </div>

      <Heatmap />



    </main>
  );
}
