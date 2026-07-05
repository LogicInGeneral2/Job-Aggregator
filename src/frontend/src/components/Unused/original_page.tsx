import JobGraphDashboard from "@/components/JobGraph";

export default function Home() {
  return (
    <main className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        
        <header className="mb-8">
          <h1 className="text-4xl font-extrabold text-gray-900 tracking-tight">
            Global Job Market Topology
          </h1>
          <p className="text-gray-500 mt-2">
            Interactive semantic exploration powered by Elasticsearch and Redis Cache Warming.
          </p>
        </header>

        {/* The Phase 14 Master Component */}
        <JobGraphDashboard />

      </div>
    </main>
  );
}