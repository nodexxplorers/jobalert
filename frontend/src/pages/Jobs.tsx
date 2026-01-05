// src/pages/Jobs.tsx

import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import DashboardHeader from '../components/DashboardHeader';
import JobsList from '../components/JobList';
import Sidebar from '../components/Sidebar';
import { jobsAPI, userAPI } from '../services/api';
import type { Job, User } from '../types';

export default function Jobs() {
    const [jobs, setJobs] = useState<Job[]>([]);
    const [savedJobs, setSavedJobs] = useState<Job[]>([]);
    const [, setUser] = useState<User | null>(null);
    const [filters, setFilters] = useState({
        jobType: ['short_form'],
        payment: ['paid'],
        postedWithin: 'last_10_mins',
        keywords: '',
    });
    const [activeTab, setActiveTab] = useState<'latest' | 'saved'>('latest');
    const [searchParams] = useSearchParams();
    const [loading, setLoading] = useState(true);

    // Sync search param from URL to filters
    useEffect(() => {
        const search = searchParams.get('search');
        if (search !== null && search !== filters.keywords) {
            setFilters(prev => ({ ...prev, keywords: search }));
        }
    }, [searchParams]);

    useEffect(() => {
        loadJobsData();
        // Auto-refresh every 30 seconds
        const interval = setInterval(loadJobsData, 30000);
        return () => clearInterval(interval);
    }, [filters]);

    const loadJobsData = async () => {
        try {
            setLoading(true);

            // Fetch user data
            const userData = await userAPI.getCurrentUser();
            setUser(userData);

            // Fetch more jobs for the dedicated page (e.g., 200)
            const primaryCategory = userData?.preferences?.[0] || 'video-editing';
            const jobsData = await jobsAPI.getJobs(primaryCategory, 200, filters.keywords);
            setJobs(jobsData);

            // Fetch saved jobs
            try {
                const savedJobsData = await jobsAPI.getSavedJobs();
                setSavedJobs(savedJobsData);
            } catch (error) {
                console.error('Failed to load saved jobs:', error);
            }
        } catch (error) {
            console.error('Failed to load jobs data:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleSaveJob = (jobId: number) => {
        const job = jobs.find(j => j.id === jobId);
        if (job && !savedJobs.find(j => j.id === jobId)) {
            setSavedJobs([...savedJobs, job]);
        }
    };

    const handleUnsaveJob = (jobId: number) => {
        setSavedJobs(savedJobs.filter(j => j.id !== jobId));
    };

    const displayedJobs = activeTab === 'latest' ? jobs : savedJobs;

    return (
        <div className="min-h-screen bg-gradient-to-br from-green-50 via-cyan-50 to-blue-50">
            <DashboardHeader />

            <div className="container mx-auto px-4 py-6">
                <div className="mb-6">
                    <h1 className="text-3xl font-bold text-gray-900">Opportunities</h1>
                    <p className="text-gray-600">Browse all available jobs tailored for you.</p>
                </div>

                <div className="grid lg:grid-cols-[1fr_320px] gap-6">
                    {/* Main Content */}
                    <div>
                        <JobsList
                            jobs={displayedJobs}
                            activeTab={activeTab}
                            onTabChange={setActiveTab}
                            onSaveJob={handleSaveJob}
                            onUnsaveJob={handleUnsaveJob}
                            savedJobIds={savedJobs.map(j => j.id)}
                            loading={loading}
                            showViewAll={false}
                        />
                    </div>

                    {/* Sidebar */}
                    <Sidebar
                        filters={filters}
                        onFiltersChange={setFilters}
                    />
                </div>
            </div>
        </div>
    );
}
