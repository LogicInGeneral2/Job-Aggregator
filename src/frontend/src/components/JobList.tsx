'use client';

import { trackJobClick } from "@/services/api";

type Job = {
    id: string;
    title: string;
    company: string;
    category: string;
    url: string;
};

const hasCategory = (category?: string): boolean => {
    return !!category && category.trim() !== '';
}

export default function JobList({ jobs }: { jobs: Job[] }) {
    return (
        <div className="grid gap-4 mt-4">
            {jobs.map((job) => (
                <div
                    key={job.id}
                    className="p-4 border border-gray-500 rounded-lg shadow-sm hover:border-green-500 transition"
                >
                    <h4 className="font-semibold text-lg">{job.title}</h4>

                    <p className="text-gray-500">
                        {job.company}
                        {hasCategory(job.category) && ` • ${job.category}`}
                    </p>

                    <a
                        href={job.url}
                        target="_blank"
                        rel="noreferrer"
                        onClick={() => trackJobClick(job.id, job.category)}
                        className="text-green-700 text-sm mt-2 inline-block"
                    >
                        View Details →
                    </a>
                </div>
            ))}
        </div>
    );
}