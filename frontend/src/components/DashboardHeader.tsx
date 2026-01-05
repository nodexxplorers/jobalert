// FILE: src/components/Dashboard/DashboardHeader.tsx

import { Search, Bell, LogOut, Settings, LayoutDashboard, Briefcase, Menu, X } from 'lucide-react';
import { useState, useEffect } from 'react';
import { useNavigate, Link, useLocation } from 'react-router-dom';
import { userAPI } from '../services/api';
import { authService } from '../services/auth';
import { notificationAPI } from '../services/notificationAPI';
import type { User } from '../types';

export default function DashboardHeader() {
  const [searchQuery, setSearchQuery] = useState('');
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [showDropdown, setShowDropdown] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const navigate = useNavigate();
  const location = useLocation();

  const navigateToSearch = (query: string) => {
    if (!query.trim()) return;

    // Determine target page based on current page
    const base = location.pathname.startsWith('/jobs') ? '/jobs' : '/dashboard';
    navigate(`${base}?search=${encodeURIComponent(query.trim())}`);
    setMobileMenuOpen(false);
  };

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const [userData, stats] = await Promise.all([
          userAPI.getCurrentUser(),
          notificationAPI.getStats()
        ]);
        setUser(userData);
        setUnreadCount(stats.unread);
      } catch (error) {
        console.error('Failed to fetch header data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchUser();
  }, []);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      if (!target.closest('[data-dropdown]')) {
        setShowDropdown(false);
      }
    };

    if (showDropdown) {
      document.addEventListener('click', handleClickOutside);
      return () => document.removeEventListener('click', handleClickOutside);
    }
  }, [showDropdown]);

  const handleLogout = () => {
    authService.logout();
  };

  const handleSettings = () => {
    setShowDropdown(false);
    navigate('/settings');
  };

  return (
    <header className="bg-gradient-to-r from-green-500 to-cyan-400 shadow-lg sticky top-0 z-50">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            {/* Mobile Menu Toggle */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 text-white hover:bg-white/20 rounded-lg transition-colors"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>

            {/* Logo */}
            <Link to="/dashboard" className="flex items-center gap-3 shrink-0">
              <img src="/logos.png" alt="Logo" className="w-10 h-10 rounded-xl" />
              <span className="text-white font-bold text-xl hidden sm:block">JobAlert</span>
            </Link>
          </div>

          {/* Desktop Navigation Links */}
          <div className="hidden md:flex items-center gap-1 bg-white/10 p-1 rounded-xl backdrop-blur-sm">
            <Link
              to="/dashboard"
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all ${location.pathname === '/dashboard'
                ? 'bg-white text-green-600 shadow-sm'
                : 'text-white hover:bg-white/10'
                }`}
            >
              <LayoutDashboard className="w-4 h-4" />
              Dashboard
            </Link>
            <Link
              to="/jobs"
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all ${location.pathname === '/jobs'
                ? 'bg-white text-green-600 shadow-sm'
                : 'text-white hover:bg-white/10'
                }`}
            >
              <Briefcase className="w-4 h-4" />
              Jobs
            </Link>
          </div>

          {/* Search Bar - Hidden on very small screens, visible on med+ or as expanded search */}
          <div className="flex-1 max-w-2xl hidden sm:block">
            <div className="relative">
              <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    navigateToSearch(searchQuery);
                  }
                }}
                placeholder="Search jobs..."
                className="w-full pl-12 pr-4 py-2.5 rounded-xl border-none shadow-lg focus:ring-2 focus:ring-white/50 outline-none text-sm"
              />
            </div>
          </div>

          {/* Right Actions */}
          <div className="flex items-center gap-2 sm:gap-4">
            {/* Notifications */}
            <button
              onClick={() => navigate('/notifications')}
              className="relative p-2 hover:bg-white/20 rounded-lg transition-colors"
            >
              <Bell className="w-6 h-6 text-white" />
              {unreadCount > 0 && (
                <span className="absolute top-1 right-1 w-5 h-5 bg-red-500 text-white text-[10px] font-bold flex items-center justify-center rounded-full border-2 border-green-500">
                  {unreadCount > 9 ? '9+' : unreadCount}
                </span>
              )}
            </button>

            {/* User Avatar with Dropdown */}
            {!loading && user && (
              <div className="relative" data-dropdown>
                <button
                  onClick={() => setShowDropdown(!showDropdown)}
                  className="w-10 h-10 rounded-full overflow-hidden ring-2 ring-white/50 hover:ring-white transition-all focus:outline-none"
                >
                  <img
                    src={user.profile_image || `https://ui-avatars.com/api/?name=${user.username || user.email}&background=667eea&color=fff`}
                    alt={user.username}
                    className="w-full h-full object-cover"
                  />
                </button>

                {/* Dropdown Menu */}
                {showDropdown && (
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-xl z-50 overflow-hidden py-1 border border-gray-100">
                    <div className="px-4 py-3 border-b border-gray-100 bg-gray-50/50">
                      <p className="text-sm font-semibold text-gray-900 truncate">{user.username || user.email}</p>
                      <p className="text-xs text-gray-500 truncate">{user.email}</p>
                    </div>

                    <button
                      onClick={handleSettings}
                      className="w-full text-left px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-3 transition-colors"
                    >
                      <Settings className="w-4 h-4 text-gray-400" />
                      Settings
                    </button>

                    {user.is_admin && (
                      <button
                        onClick={() => {
                          setShowDropdown(false);
                          navigate('/admin');
                        }}
                        className="w-full text-left px-4 py-2.5 text-sm text-blue-600 hover:bg-blue-50 flex items-center gap-3 transition-colors border-t border-gray-100"
                      >
                        <LayoutDashboard className="w-4 h-4 text-blue-400" />
                        Admin Dashboard
                      </button>
                    )}

                    <button
                      onClick={handleLogout}
                      className="w-full text-left px-4 py-2.5 text-sm text-red-600 hover:bg-red-50 flex items-center gap-3 transition-colors border-t border-gray-100"
                    >
                      <LogOut className="w-4 h-4 text-red-400" />
                      Logout
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Mobile Menu & Search Overlay */}
        {(mobileMenuOpen) && (
          <div className="md:hidden mt-4 pb-2 space-y-4 animate-in slide-in-from-top duration-200">
            {/* Mobile Search */}
            <div className="sm:hidden relative">
              <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    navigateToSearch(searchQuery);
                  }
                }}
                placeholder="Search jobs..."
                className="w-full pl-10 pr-4 py-2.5 rounded-xl border-none shadow-inner bg-white/10 text-white placeholder-white/60 focus:bg-white focus:text-gray-900 focus:placeholder-gray-400 outline-none text-sm transition-all"
              />
            </div>

            {/* Mobile Nav Links */}
            <div className="grid grid-cols-2 gap-2">
              <Link
                to="/dashboard"
                onClick={() => setMobileMenuOpen(false)}
                className={`flex items-center justify-center gap-2 px-4 py-3 rounded-xl text-sm font-semibold transition-all ${location.pathname === '/dashboard'
                  ? 'bg-white text-green-600'
                  : 'bg-white/10 text-white'
                  }`}
              >
                <LayoutDashboard className="w-4 h-4" />
                Dashboard
              </Link>
              <Link
                to="/jobs"
                onClick={() => setMobileMenuOpen(false)}
                className={`flex items-center justify-center gap-2 px-4 py-3 rounded-xl text-sm font-semibold transition-all ${location.pathname === '/jobs'
                  ? 'bg-white text-green-600'
                  : 'bg-white/10 text-white'
                  }`}
              >
                <Briefcase className="w-4 h-4" />
                Jobs
              </Link>
            </div>
          </div>
        )}
      </div>
    </header>
  );
}
