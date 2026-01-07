// src/pages/Dashboard.tsx

import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import DashboardHeader from '../components/DashboardHeader';
import StatsCards from '../components/StatsCard';
import JobsList from '../components/JobList';
import Sidebar from '../components/Sidebar';
import { jobsAPI, userAPI } from '../services/api';
import type { Job, User } from '../types';

export default function Dashboard() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [savedJobs, setSavedJobs] = useState<Job[]>([]);
  const [user, setUser] = useState<User | null>(null);
  const [stats, setStats] = useState({
    appliedCount: 0,
    alertsToday: 0,
  });
  const [filters, setFilters] = useState({
    jobType: ['short_form'],
    payment: ['paid'],
    postedWithin: 'last_10_mins',
    keywords: '',
  });
  const [activeTab, setActiveTab] = useState<'latest' | 'saved'>('latest');
  const [searchParams] = useSearchParams();
  const [loading, setLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [showMobileFilters, setShowMobileFilters] = useState(false);

  // Sync search param from URL to filters and active tab
  useEffect(() => {
    const search = searchParams.get('search');
    const tab = searchParams.get('tab');

    if (search !== null && search !== filters.keywords) {
      setFilters(prev => ({ ...prev, keywords: search }));
    }

    if (tab === 'saved') {
      setActiveTab('saved');
    } else if (tab === 'latest') {
      setActiveTab('latest');
    }
  }, [searchParams]);

  useEffect(() => {
    loadDashboardData();
    // Auto-refresh every 30 seconds
    const interval = setInterval(() => loadDashboardData(true), 30000);
    return () => clearInterval(interval);
  }, [filters]);

  const loadDashboardData = async (isBackground = false) => {
    try {
      if (!isBackground) setLoading(true);
      else setIsRefreshing(true);

      // Fetch user data
      const userData = await userAPI.getCurrentUser();
      setUser(userData);

      // Fetch jobs based on user preferences and search keywords
      const primaryCategory = userData?.preferences?.[0] || 'video-editing';
      const jobsData = await jobsAPI.getJobs(primaryCategory, 50, filters.keywords);
      setJobs(jobsData);

      // Fetch saved jobs
      try {
        const savedJobsData = await jobsAPI.getSavedJobs();
        setSavedJobs(savedJobsData);
      } catch (error) {
        console.error('Failed to load saved jobs:', error);
      }

      // Fetch analytics stats
      try {
        const statsData = await userAPI.getStats();
        setStats(statsData);
      } catch (error) {
        console.error('Failed to load stats:', error);
      }
    } catch (error) {
      console.error('CRITICAL: Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  };

  const handleSaveJob = async (jobId: number) => {
    // Optimistic update
    const job = jobs.find(j => j.id === jobId);
    if (job && !savedJobs.find(j => j.id === jobId)) {
      setSavedJobs(prev => [...prev, job]);
      try {
        await jobsAPI.saveJob(job.id);
      } catch (e) {
        // Revert on failure
        console.error("Failed to save job", e);
        setSavedJobs(prev => prev.filter(j => j.id !== jobId));
      }
    }
  };

  const handleUnsaveJob = async (jobId: number) => {
    // Optimistic update
    const prevSaved = [...savedJobs];
    setSavedJobs(prev => prev.filter(j => j.id !== jobId));

    try {
      await jobsAPI.unsaveJob(jobId);
    } catch (e) {
      // Revert
      console.error("Failed to unsave job", e);
      setSavedJobs(prevSaved);
    }
  };

  const displayedJobs = activeTab === 'latest' ? jobs.slice(0, 5) : savedJobs;

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-cyan-50 to-blue-50">
      <DashboardHeader />

      <div className="container mx-auto px-4 py-4">
        <div className="grid lg:grid-cols-[1fr_320px] gap-6">
          {/* Main Content */}
          <div>
            <StatsCards
              user={user}
              savedCount={savedJobs.length}
              appliedCount={stats.appliedCount}
              alertsToday={stats.alertsToday}
            />

            <JobsList
              jobs={displayedJobs}
              activeTab={activeTab}
              onTabChange={setActiveTab}
              onSaveJob={handleSaveJob}
              onUnsaveJob={handleUnsaveJob}
              savedJobIds={savedJobs.map(j => j.id)}
              loading={loading}
              isRefreshing={isRefreshing}
              onToggleFilters={() => setShowMobileFilters(!showMobileFilters)}
              showViewAll={activeTab === 'latest' && jobs.length > 5}
            />
          </div>

          {/* Sidebar */}
          <div className={`${showMobileFilters ? 'fixed inset-0 z-50 bg-white p-4 overflow-y-auto' : 'hidden lg:block'}`}>
            <div className="lg:hidden flex justify-end mb-4">
              <button onClick={() => setShowMobileFilters(false)} className="p-2 text-gray-500">Close</button>
            </div>
            <Sidebar
              filters={filters}
              onFiltersChange={setFilters}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
