// FILE: src/components/Dashboard/JobsList.tsx

import { Zap, Star, Filter, MoreVertical, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import JobCard from './JobCard';
import type { Job } from '../types';

interface JobsListProps {
  jobs: Job[];
  activeTab: 'latest' | 'saved';
  onTabChange: (tab: 'latest' | 'saved') => void;
  onSaveJob: (jobId: number) => void;
  onUnsaveJob: (jobId: number) => void;
  savedJobIds: number[];
  loading: boolean;
  isRefreshing?: boolean;
  onToggleFilters?: () => void;
  showViewAll?: boolean;
}

export default function JobsList({
  jobs,
  activeTab,
  onTabChange,
  onSaveJob,
  onUnsaveJob,
  savedJobIds,
  loading,
  isRefreshing = false,
  onToggleFilters,
  showViewAll = false,
}: JobsListProps) {
  return (
    <div className="bg-white rounded-2xl shadow-lg p-6">
      {/* Tabs */}
      <div className="flex items-center justify-between mb-6 border-b border-gray-200">
        <div className="flex gap-6">
          <button
            onClick={() => onTabChange('latest')}
            className={`pb-3 px-2 font-semibold border-b-2 transition-colors flex items-center gap-2 ${activeTab === 'latest'
              ? 'border-green-500 text-green-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
          >
            <Zap className="w-5 h-5" />
            Latest Jobs
          </button>
          <button
            onClick={() => onTabChange('saved')}
            className={`pb-3 px-2 font-semibold border-b-2 transition-colors flex items-center gap-2 ${activeTab === 'saved'
              ? 'border-yellow-500 text-yellow-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
          >
            <Star className="w-5 h-5" />
            Saved Jobs
          </button>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2">
          <button
            onClick={onToggleFilters}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors lg:hidden"
          >
            <Filter className="w-5 h-5 text-gray-600" />
          </button>
          <div className="relative group">
            <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
              <MoreVertical className="w-5 h-5 text-gray-600" />
            </button>
            <div className="absolute right-0 top-full mt-2 w-48 bg-white rounded-xl shadow-xl border border-gray-100 hidden group-hover:block z-10">
              <button
                onClick={() => window.location.reload()}
                className="w-full text-left px-4 py-2 hover:bg-gray-50 rounded-lg text-sm text-gray-700"
              >
                Refresh Jobs
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Jobs List */}
      <div className="relative">
        {loading && jobs.length === 0 ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-500"></div>
          </div>
        ) : !loading && jobs.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-500">No jobs found. Adjust your filters or check back later!</p>
          </div>
        ) : (
          <div className={`space-y-4 transition-opacity duration-300 ${loading ? 'opacity-50' : 'opacity-100'}`}>
            {jobs.map((job) => (
              <JobCard
                key={job.id}
                job={job}
                isSaved={savedJobIds.includes(job.id)}
                onSave={() => onSaveJob(job.id)}
                onUnsave={() => onUnsaveJob(job.id)}
              />
            ))}

            {showViewAll && (
              <div className="pt-4 border-t border-gray-100 flex justify-center">
                <Link
                  to="/jobs"
                  className="flex items-center gap-2 text-green-600 font-semibold hover:text-green-700 transition-colors py-2 px-4 rounded-lg hover:bg-green-50"
                >
                  View All Jobs
                  <ArrowRight className="w-4 h-4" />
                </Link>
              </div>
            )}
          </div>
        )}

        {/* Loading Overlay for background updates */}
        {isRefreshing && jobs.length > 0 && (
          <div className="absolute top-4 left-1/2 -translate-x-1/2 pointer-events-none z-10 transition-opacity duration-300">
            <div className="bg-black/80 backdrop-blur-md text-white px-4 py-2 rounded-full shadow-lg flex items-center gap-2 text-sm">
              <div className="animate-spin rounded-full h-3 w-3 border-2 border-white/30 border-t-white"></div>
              <span>Updating...</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}