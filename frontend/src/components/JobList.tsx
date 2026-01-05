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
          <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
            <Filter className="w-5 h-5 text-gray-600" />
          </button>
          <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
            <MoreVertical className="w-5 h-5 text-gray-600" />
          </button>
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
        {loading && jobs.length > 0 && (
          <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none z-10">
            <div className="bg-white/80 p-4 rounded-2xl shadow-xl flex items-center gap-3 border border-green-100">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-green-500"></div>
              <span className="text-sm font-medium text-green-600">Refreshing jobs...</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}