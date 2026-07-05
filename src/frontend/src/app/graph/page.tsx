import JobGraphDashboard from "@/components/JobGraph";

export default async function GraphPage({
    searchParams,
}: {
    searchParams: Promise<{ q?: string }>;
}) {
    const { q } = await searchParams;

    return (
        <main>
            <JobGraphDashboard />
        </main>
    );
}