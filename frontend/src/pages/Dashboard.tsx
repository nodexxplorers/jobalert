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

  // Sync search param from URL to filters
  useEffect(() => {
    const search = searchParams.get('search');
    if (search !== null && search !== filters.keywords) {
      setFilters(prev => ({ ...prev, keywords: search }));
    }
  }, [searchParams]);

  useEffect(() => {
    loadDashboardData();
    // Auto-refresh every 30 seconds
    const interval = setInterval(loadDashboardData, 30000);
    return () => clearInterval(interval);
  }, [filters]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);

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
        console.log('Fetching stats...');
        const statsData = await userAPI.getStats();
        setStats(statsData);
      } catch (error) {
        console.error('Failed to load stats:', error);
      }
    } catch (error) {
      console.error('CRITICAL: Failed to load dashboard data:', error);
    } finally {
      console.log('Dashboard loading finished.');
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
              showViewAll={activeTab === 'latest' && jobs.length > 5}
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
