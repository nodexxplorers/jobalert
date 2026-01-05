// ADMIN DASHBOARD

import { useNavigate } from 'react-router-dom';
import { useEffect, useState, useRef } from 'react';
import { adminAPI, userAPI } from '../../services/api';
import { authService } from '../../services/auth';
import type { User } from '../../types';
import { BarChart3, Users, Briefcase, Bell, Activity, RefreshCw, Download, Trash2, UserCheck, Filter, MoreVertical, Search, ArrowLeft, LogOut, Shield, ShieldOff, Ban, Unlock, X } from 'lucide-react';

function AdminDashboard() {
    const [view, setView] = useState<'overview' | 'users' | 'jobs'>('overview');
    const [overview, setOverview] = useState<any>(null);
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    const [error, setError] = useState<string | null>(null);

    const loadOverview = async () => {
        try {
            setError(null);
            setLoading(true);
            const data = await adminAPI.getAdminOverview();
            setOverview(data);
        } catch (err) {
            console.error('Failed to load admin overview:', err);
            setError('Failed to load system overview. Please check your connection or permissions.');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        const initDashboard = async () => {
            try {
                const [overviewData, userData] = await Promise.all([
                    adminAPI.getAdminOverview(),
                    userAPI.getCurrentUser()
                ]);
                setOverview(overviewData);
                setUser(userData);
            } catch (err) {
                console.error('Failed to initialize admin dashboard:', err);
                setError('Failed to load system data. Please check your connection or permissions.');
            } finally {
                setLoading(false);
            }
        };
        initDashboard();
    }, []);

    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center h-screen gap-4">
                <div className="animate-spin w-8 h-8 border-4 border-blue-200 border-t-blue-500 rounded-full" />
                <p className="text-gray-500 animate-pulse">Loading administrator tools...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex flex-col items-center justify-center h-screen gap-6 p-6 text-center">
                <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center text-red-600 mb-2">
                    <Activity className="w-8 h-8" />
                </div>
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 mb-2">Something went wrong</h1>
                    <p className="text-gray-600 max-w-md">{error}</p>
                </div>
                <button
                    onClick={loadOverview}
                    className="px-6 py-3 bg-blue-600 text-white rounded-xl font-semibold hover:bg-blue-700 transition shadow-lg"
                >
                    Try Again
                </button>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Admin Header */}
            <div className="bg-white border-b border-gray-200">
                <div className="max-w-7xl mx-auto px-6 py-4">
                    <div className="flex items-center justify-between">
                        <div>
                            <h1 className="text-2xl font-bold text-gray-900">Admin Dashboard</h1>
                            <p className="text-gray-600">System overview and management</p>
                        </div>

                        <div className="flex items-center gap-6">
                            <button
                                onClick={() => navigate('/dashboard')}
                                className="flex items-center gap-2 text-gray-600 hover:text-gray-900 font-medium transition-colors"
                            >
                                <ArrowLeft className="w-4 h-4" />
                                <span className="hidden sm:inline">Back to Dashboard</span>
                            </button>

                            {user && (
                                <div className="flex items-center gap-3 pl-6 border-l border-gray-200">
                                    <div className="text-right hidden sm:block">
                                        <div className="text-sm font-semibold text-gray-900">{user.username}</div>
                                        <div className="text-xs text-gray-500">Administrator</div>
                                    </div>
                                    <img
                                        src={user.profile_image || `https://ui-avatars.com/api/?name=${user.username}&background=667eea&color=fff`}
                                        alt={user.username}
                                        className="w-10 h-10 rounded-full border border-gray-200 shadow-sm"
                                    />
                                    <button
                                        onClick={() => authService.logout()}
                                        className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors border border-transparent hover:border-red-100"
                                        title="Logout"
                                    >
                                        <LogOut className="w-5 h-5" />
                                    </button>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>

            {/* Navigation Tabs */}
            <div className="bg-white border-b border-gray-200">
                <div className="max-w-7xl mx-auto px-6">
                    <div className="flex gap-8">
                        {[
                            { id: 'overview', label: 'Overview', icon: BarChart3 },
                            { id: 'users', label: 'Users', icon: Users },
                            { id: 'jobs', label: 'Jobs', icon: Briefcase }
                        ].map(tab => {
                            const Icon = tab.icon;
                            return (
                                <button
                                    key={tab.id}
                                    onClick={() => setView(tab.id as any)}
                                    className={`flex items-center gap-2 py-4 px-2 border-b-2 transition ${view === tab.id
                                        ? 'border-blue-600 text-blue-600'
                                        : 'border-transparent text-gray-600 hover:text-gray-900'
                                        }`}
                                >
                                    <Icon className="w-5 h-5" />
                                    {tab.label}
                                </button>
                            );
                        })}
                    </div>
                </div>
            </div>

            {/* Content */}
            <div className="max-w-7xl mx-auto p-6">
                {view === 'overview' && <AdminOverview data={overview} user={user} />}
                {view === 'users' && <AdminUsers />}
                {view === 'jobs' && <AdminJobs />}
            </div>
        </div>
    );
}

// Sub-components
function MetricCard({ title, value, subtitle, icon: Icon, color, trend }: any) {
    const colors: any = {
        blue: 'bg-blue-50 text-blue-600 text-blue-600',
        green: 'bg-green-50 text-green-600 text-green-600',
        purple: 'bg-purple-50 text-purple-600 text-purple-600',
    };
    // Fix duplication in color classes if any, just simple lookup
    const colorClass = colors[color] || 'bg-gray-50 text-gray-600';

    return (
        <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center justify-between mb-4">
                <div className={`p-3 rounded-lg ${colorClass}`}>
                    <Icon className="w-6 h-6" />
                </div>
                {trend && <span className="text-sm font-medium text-green-600 bg-green-50 px-2 py-1 rounded-full">{trend}</span>}
            </div>
            <h3 className="text-gray-500 text-sm font-medium">{title}</h3>
            <div className="flex items-baseline gap-2 mt-1">
                <span className="text-2xl font-bold text-gray-900">{value}</span>
                <span className="text-sm text-gray-500">{subtitle}</span>
            </div>
        </div>
    );
}

function HealthIndicator({ label, status, value }: any) {
    return (
        <div className="p-4 bg-gray-50 rounded-lg">
            <div className="text-sm text-gray-500 mb-1">{label}</div>
            <div className="flex items-center justify-between">
                <span className="font-semibold text-gray-900">{value}</span>
                <div className={`w-2 h-2 rounded-full ${status === 'healthy' ? 'bg-green-500' : 'bg-red-500'}`} />
            </div>
        </div>
    );
}

function ActionButton({ label, icon: Icon, onClick, loading }: any) {
    return (
        <button
            onClick={onClick}
            disabled={loading}
            className="w-full flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg transition border border-gray-100 group disabled:opacity-50"
        >
            <span className="text-gray-700 font-medium group-hover:text-gray-900">{label}</span>
            {loading ? (
                <div className="animate-spin w-4 h-4 border-2 border-blue-200 border-t-blue-500 rounded-full" />
            ) : (
                <Icon className="w-4 h-4 text-gray-400 group-hover:text-gray-600" />
            )}
        </button>
    );
}

function AdminOverview({ data, user }: { data: any, user: any }) {
    const [actionLoading, setActionLoading] = useState<string | null>(null);
    const [cookies, setCookies] = useState(data?.system?.twitter_cookies || '');

    useEffect(() => {
        if (data?.system?.twitter_cookies) {
            setCookies(data.system.twitter_cookies);
        }
    }, [data?.system?.twitter_cookies]);

    const handleAction = async (name: string, apiCall: () => Promise<any>) => {
        try {
            setActionLoading(name);
            const response = await apiCall();
            alert(response.message || 'Action completed successfully');
        } catch (err: any) {
            console.error(`Action ${name} failed:`, err);
            alert(`Failed to ${name}: ${err.response?.data?.detail || err.message}`);
        } finally {
            setActionLoading(null);
        }
    };

    if (!data) return null;
    return (
        <div>
            {/* Key Metrics */}
            <div className="grid md:grid-cols-3 gap-6 mb-8">
                <MetricCard
                    title="Total Users"
                    value={data?.users?.total?.toLocaleString() || 0}
                    subtitle={`${data?.users?.active_percentage || 0}% active`}
                    icon={Users}
                    color="blue"
                    trend={`+${data?.users?.new_this_week || 0} this week`}
                />
                <MetricCard
                    title="Total Jobs"
                    value={data?.jobs?.total?.toLocaleString() || 0}
                    subtitle={`${data?.jobs?.today || 0} today`}
                    icon={Briefcase}
                    color="green"
                    trend={`${data?.jobs?.duplicate_rate || 0} duplicates`}
                />
                <MetricCard
                    title="Notifications"
                    value={data?.notifications?.total?.toLocaleString() || 0}
                    subtitle={`${data?.notifications?.today || 0} today`}
                    icon={Bell}
                    color="purple"
                    trend={`Avg ${data?.notifications?.avg_per_user || 0} per user`}
                />
            </div>

            {/* System Health */}
            <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <Activity className="w-5 h-5 text-green-500" />
                    System Health
                </h3>
                <div className="grid md:grid-cols-4 gap-4">
                    <HealthIndicator label="API Status" status="healthy" value="99.9%" />
                    <HealthIndicator
                        label="Scraping"
                        status={data?.system?.is_scraping ? 'warning' : 'healthy'}
                        value={data?.system?.is_scraping ? 'In Progress...' : 'Idle'}
                    />
                    <HealthIndicator label="Last Scrape" status="healthy" value={data?.system?.last_scrape_at ? new Date(data.system.last_scrape_at).toLocaleTimeString() : 'Never'} />
                    <HealthIndicator label="Jobs (Last Run)" status="healthy" value={data?.system?.last_jobs_found || 0} />
                </div>
            </div>

            {/* Quick Actions */}
            <div className="grid md:grid-cols-2 gap-6">
                <div className="bg-white rounded-xl shadow-lg p-6">
                    <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
                    <div className="space-y-3">
                        <ActionButton
                            label={data?.system?.is_scraping ? "Scraping in Progress..." : "Trigger Manual Scrape"}
                            icon={RefreshCw}
                            loading={actionLoading === 'scrape' || data?.system?.is_scraping}
                            onClick={async () => {
                                if (data?.system?.is_scraping) {
                                    // If already scraping, show option to reset
                                    if (confirm('Scraping is already in progress. Do you want to reset the status? This will mark scraping as complete.')) {
                                        try {
                                            setActionLoading('reset');
                                            await adminAPI.resetSystemStatus();
                                            alert('Status reset successfully. Refreshing...');
                                            window.location.reload();
                                        } catch (err: any) {
                                            console.error('Reset failed:', err);
                                            alert(`Failed to reset status: ${err.response?.data?.detail || err.message}`);
                                        } finally {
                                            setActionLoading(null);
                                        }
                                    }
                                    return;
                                }

                                try {
                                    setActionLoading('scrape');
                                    // Use sync=false for background processing
                                    const response = await adminAPI.triggerScrape(false);
                                    if (response.sync) {
                                        alert(`Scraping completed! Found ${response.new_jobs || 0} new jobs.\n\nCheck console for detailed output.`);
                                    } else {
                                        alert(response.message || 'Scraping started in background. Check console for output.');
                                    }
                                    // Refresh data after a short delay
                                    setTimeout(() => {
                                        window.location.reload();
                                    }, 2000);
                                } catch (err: any) {
                                    console.error('Scrape failed:', err);
                                    alert(`Failed to start scrape: ${err.response?.data?.detail || err.message}\n\nCheck console for details.`);
                                } finally {
                                    setActionLoading(null);
                                }
                            }}
                        />
                        {data?.system?.is_scraping && (
                            <ActionButton
                                label="Reset Status (If Stuck)"
                                icon={RefreshCw}
                                loading={actionLoading === 'reset'}
                                onClick={async () => {
                                    if (confirm('Are you sure you want to reset the scraping status? This should only be used if scraping appears stuck.')) {
                                        try {
                                            setActionLoading('reset');
                                            await adminAPI.resetSystemStatus();
                                            alert('Status reset successfully. Refreshing...');
                                            window.location.reload();
                                        } catch (err: any) {
                                            console.error('Reset failed:', err);
                                            alert(`Failed to reset status: ${err.response?.data?.detail || err.message}`);
                                        } finally {
                                            setActionLoading(null);
                                        }
                                    }
                                }}
                            />
                        )}
                        <ActionButton
                            label="Migrate Categories"
                            icon={Filter}
                            loading={actionLoading === 'migrate'}
                            onClick={() => handleAction('migrate', adminAPI.migrateCategories)}
                        />
                        <ActionButton
                            label="Send Test Notification"
                            icon={Bell}
                            loading={actionLoading === 'test-notify'}
                            onClick={() => handleAction('test-notify', () => adminAPI.sendTestNotification(user?.id || 0))}
                        />
                        <ActionButton
                            label="Clean Up Duplicates"
                            icon={Trash2}
                            loading={actionLoading === 'cleanup'}
                            onClick={() => handleAction('cleanup', adminAPI.cleanupDuplicates)}
                        />
                        <ActionButton
                            label="Export User Data"
                            icon={Download}
                            loading={actionLoading === 'export'}
                            onClick={() => handleAction('export', adminAPI.exportUserData)}
                        />
                    </div>
                </div>

                <div className="bg-white rounded-xl shadow-lg p-6">
                    <h3 className="text-lg font-semibold mb-4">Recent Activity</h3>
                    <div className="space-y-3">
                        {[
                            { text: "127 new jobs scraped", time: "5 min ago" },
                            { text: "34 users registered", time: "2 hours ago" },
                            { text: "342 notifications sent", time: "3 hours ago" },
                            { text: "Database backup completed", time: "6 hours ago" }
                        ].map((activity, i) => (
                            <div key={i} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0">
                                <span className="text-gray-700">{activity.text}</span>
                                <span className="text-sm text-gray-500">{activity.time}</span>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Cookie Manager */}
                <div className="bg-white rounded-xl shadow-lg p-6">
                    <div className="flex items-center gap-2 mb-4">
                        <Shield className="w-5 h-5 text-blue-600" />
                        <h3 className="text-lg font-semibold">Twitter Session Cookies</h3>
                    </div>
                    <p className="text-sm text-gray-600 mb-4">
                        Pasting session cookies allows the scraper to bypass login challenges.
                        Use a browser extension (like "EditThisCookie") to export cookies as JSON from x.com.
                    </p>
                    <textarea
                        className="w-full h-32 p-3 bg-gray-50 border border-gray-200 rounded-lg text-xs font-mono focus:ring-2 focus:ring-blue-500 focus:border-transparent mb-4"
                        placeholder='[{"name": "auth_token", "value": "..."}, ...]'
                        value={cookies}
                        onChange={(e) => setCookies(e.target.value)}
                        id="cookie-textarea"
                    />
                    <button
                        onClick={async () => {
                            if (!cookies) return alert('Please paste cookies first');

                            try {
                                setActionLoading('cookies');
                                await adminAPI.updateCookies(cookies);
                                alert('Cookies updated successfully!');
                                window.location.reload();
                            } catch (err: any) {
                                alert(`Failed to update cookies: ${err.message}`);
                            } finally {
                                setActionLoading(null);
                            }
                        }}
                        disabled={actionLoading === 'cookies'}
                        className="w-full py-3 bg-blue-600 text-white rounded-xl font-semibold hover:bg-blue-700 transition disabled:opacity-50 flex items-center justify-center gap-2"
                    >
                        {actionLoading === 'cookies' ? (
                            <div className="animate-spin w-4 h-4 border-2 border-white/20 border-t-white rounded-full" />
                        ) : (
                            <Shield className="w-4 h-4" />
                        )}
                        Update Session Cookies
                    </button>
                </div>
            </div>
        </div>
    );
}

function AdminUsers() {
    const [users, setUsers] = useState<any[]>([]);
    const [search, setSearch] = useState('');
    const [debouncedSearch, setDebouncedSearch] = useState('');
    const [page, setPage] = useState(1);
    const [loading, setLoading] = useState(true);
    const [selectedUsers, setSelectedUsers] = useState<Set<number>>(new Set());
    const [actionLoading, setActionLoading] = useState<string | null>(null);
    const [openMenuId, setOpenMenuId] = useState<number | null>(null);
    const [selectedUser, setSelectedUser] = useState<any | null>(null);
    const [showUserModal, setShowUserModal] = useState(false);
    const [statusFilter, setStatusFilter] = useState<'all' | 'active' | 'inactive'>('all');
    const menuRef = useRef<HTMLDivElement>(null);

    // Debounce search
    useEffect(() => {
        const timer = setTimeout(() => {
            setDebouncedSearch(search);
            setPage(1); // Reset to first page on search
        }, 500);
        return () => clearTimeout(timer);
    }, [search]);

    useEffect(() => {
        loadUsers();
    }, [page, debouncedSearch, statusFilter]);

    // Close menu when clicking outside
    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
                setOpenMenuId(null);
            }
        };

        if (openMenuId !== null) {
            document.addEventListener('mousedown', handleClickOutside);
        }

        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, [openMenuId]);

    const loadUsers = async () => {
        try {
            setLoading(true);
            const data = await adminAPI.getAdminUsers(page, debouncedSearch, statusFilter === 'all' ? undefined : statusFilter);
            setUsers(data.users);
        } catch (err) {
            console.error('Failed to load users:', err);
        } finally {
            setLoading(false);
        }
    };

    const loadUserDetails = async (userId: number) => {
        try {
            const data = await adminAPI.getUserDetails(userId);
            setSelectedUser(data);
            setShowUserModal(true);
        } catch (err) {
            console.error('Failed to load user details:', err);
            alert('Failed to load user details');
        }
    };

    const toggleUser = (userId: number) => {
        const newSelected = new Set(selectedUsers);
        if (newSelected.has(userId)) {
            newSelected.delete(userId);
        } else {
            newSelected.add(userId);
        }
        setSelectedUsers(newSelected);
    };

    const handleBulkAction = async (action: 'activate' | 'deactivate' | 'verify' | 'delete' | 'promote_admin' | 'demote_admin') => {
        if (selectedUsers.size === 0) {
            alert('Please select at least one user');
            return;
        }

        const confirmMessage = {
            activate: 'Are you sure you want to activate (unban) the selected users?',
            deactivate: 'Are you sure you want to deactivate (ban) the selected users?',
            verify: 'Are you sure you want to verify the selected users?',
            promote_admin: 'Are you sure you want to promote the selected users to admin?',
            demote_admin: 'Are you sure you want to remove admin privileges from the selected users?',
            delete: 'Are you sure you want to delete the selected users? This action cannot be undone.'
        };

        if (!confirm(confirmMessage[action])) {
            return;
        }

        try {
            setActionLoading(action);
            const response = await adminAPI.bulkUserAction(Array.from(selectedUsers), action);
            alert(response.message || 'Action completed successfully');
            setSelectedUsers(new Set());
            loadUsers();
        } catch (err: any) {
            console.error(`Bulk action ${action} failed:`, err);
            alert(`Failed to ${action} users: ${err.response?.data?.detail || err.message}`);
        } finally {
            setActionLoading(null);
        }
    };

    return (
        <div>
            {loading && (
                <div className="flex items-center justify-center py-12">
                    <div className="animate-spin w-8 h-8 border-4 border-blue-200 border-t-blue-500 rounded-full" />
                </div>
            )}
            {!loading && (
                <div>
                    {/* Toolbar */}
                    <div className="bg-white rounded-xl shadow-lg p-4 mb-6">
                        <div className="flex items-center justify-between gap-4">
                            <div className="flex-1 relative">
                                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                                <input
                                    type="text"
                                    placeholder="Search users..."
                                    value={search}
                                    onChange={(e) => setSearch(e.target.value)}
                                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                />
                            </div>

                            <div className="flex items-center gap-2">
                                {selectedUsers.size > 0 && (
                                    <>
                                        <button
                                            onClick={() => handleBulkAction('verify')}
                                            disabled={actionLoading !== null}
                                            className="px-4 py-2 bg-green-100 text-green-700 rounded-lg hover:bg-green-200 transition flex items-center gap-2 disabled:opacity-50"
                                        >
                                            <UserCheck className="w-4 h-4" />
                                            Verify ({selectedUsers.size})
                                        </button>
                                        <button
                                            onClick={() => handleBulkAction('activate')}
                                            disabled={actionLoading !== null}
                                            className="px-4 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition flex items-center gap-2 disabled:opacity-50"
                                        >
                                            <Unlock className="w-4 h-4" />
                                            Unban ({selectedUsers.size})
                                        </button>
                                        <button
                                            onClick={() => handleBulkAction('deactivate')}
                                            disabled={actionLoading !== null}
                                            className="px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition flex items-center gap-2 disabled:opacity-50"
                                        >
                                            <Ban className="w-4 h-4" />
                                            Ban ({selectedUsers.size})
                                        </button>
                                        <button
                                            onClick={() => handleBulkAction('promote_admin')}
                                            disabled={actionLoading !== null}
                                            className="px-4 py-2 bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200 transition flex items-center gap-2 disabled:opacity-50"
                                        >
                                            <Shield className="w-4 h-4" />
                                            Promote ({selectedUsers.size})
                                        </button>
                                        <button
                                            onClick={() => handleBulkAction('delete')}
                                            disabled={actionLoading !== null}
                                            className="px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition flex items-center gap-2 disabled:opacity-50"
                                        >
                                            <Trash2 className="w-4 h-4" />
                                            Delete ({selectedUsers.size})
                                        </button>
                                    </>
                                )}
                                <div className="flex items-center gap-2 border border-gray-300 rounded-lg p-1">
                                    <Filter className="w-4 h-4 text-gray-400 ml-2" />
                                    <select
                                        value={statusFilter}
                                        onChange={(e) => {
                                            setStatusFilter(e.target.value as any);
                                            setPage(1);
                                        }}
                                        className="px-3 py-1 border-none outline-none bg-transparent text-sm"
                                    >
                                        <option value="all">All Users</option>
                                        <option value="active">Active</option>
                                        <option value="inactive">Inactive</option>
                                    </select>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Users Table */}
                    <div className="bg-white rounded-xl shadow-lg overflow-hidden">
                        <table className="w-full">
                            <thead className="bg-gray-50 border-b border-gray-200">
                                <tr>
                                    <th className="px-6 py-3 text-left">
                                        <input
                                            type="checkbox"
                                            className="rounded border-gray-300"
                                            onChange={(e) => {
                                                if (e.target.checked) {
                                                    setSelectedUsers(new Set(users.map(u => u.id)));
                                                } else {
                                                    setSelectedUsers(new Set());
                                                }
                                            }}
                                        />
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">User</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Joined</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Last Active</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-200">
                                {users.map(user => (
                                    <tr key={user.id} className="hover:bg-gray-50">
                                        <td className="px-6 py-4">
                                            <input
                                                type="checkbox"
                                                checked={selectedUsers.has(user.id)}
                                                onChange={() => toggleUser(user.id)}
                                                className="rounded border-gray-300"
                                            />
                                        </td>
                                        <td className="px-6 py-4">
                                            <button
                                                onClick={() => loadUserDetails(user.id)}
                                                className="flex items-center gap-3 hover:opacity-80 transition-opacity cursor-pointer"
                                            >
                                                <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 font-semibold">
                                                    {user.twitter_name?.[0] || user.username?.[0] || 'U'}
                                                </div>
                                                <div>
                                                    <div className="font-medium text-gray-900">{user.twitter_name || user.display_name || user.username}</div>
                                                    <div className="text-sm text-gray-500">@{user.twitter_username || user.username}</div>
                                                </div>
                                            </button>
                                        </td>
                                        <td className="px-6 py-4">
                                            <div className="flex flex-col gap-1">
                                                <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${user.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                                                    }`}>
                                                    {user.is_active ? 'Active' : 'Inactive'}
                                                </span>
                                                {user.is_verified && (
                                                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                                        Verified
                                                    </span>
                                                )}
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 text-sm text-gray-600">
                                            {new Date(user.created_at).toLocaleDateString()}
                                        </td>
                                        <td className="px-6 py-4 text-sm text-gray-600">
                                            {new Date(user.last_login).toLocaleDateString()}
                                        </td>
                                        <td className="px-6 py-4 relative">
                                            <div ref={menuRef}>
                                                <button
                                                    onClick={() => setOpenMenuId(openMenuId === user.id ? null : user.id)}
                                                    className="p-2 hover:bg-gray-100 rounded-lg transition"
                                                >
                                                    <MoreVertical className="w-5 h-5 text-gray-600" />
                                                </button>
                                                {openMenuId === user.id && (
                                                    <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 z-10">
                                                        <div className="py-1">
                                                            <button
                                                                onClick={async () => {
                                                                    setOpenMenuId(null);
                                                                    try {
                                                                        setActionLoading('verify');
                                                                        const response = await adminAPI.bulkUserAction([user.id], 'verify');
                                                                        alert(response.message || 'User verified successfully');
                                                                        loadUsers();
                                                                    } catch (err: any) {
                                                                        alert(`Failed to verify user: ${err.response?.data?.detail || err.message}`);
                                                                    } finally {
                                                                        setActionLoading(null);
                                                                    }
                                                                }}
                                                                className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center gap-2"
                                                            >
                                                                <UserCheck className="w-4 h-4" />
                                                                Verify User
                                                            </button>
                                                            {user.is_active ? (
                                                                <button
                                                                    onClick={async () => {
                                                                        setOpenMenuId(null);
                                                                        if (confirm('Are you sure you want to ban this user?')) {
                                                                            try {
                                                                                setActionLoading('deactivate');
                                                                                const response = await adminAPI.bulkUserAction([user.id], 'deactivate');
                                                                                alert(response.message || 'User banned successfully');
                                                                                loadUsers();
                                                                            } catch (err: any) {
                                                                                alert(`Failed to ban user: ${err.response?.data?.detail || err.message}`);
                                                                            } finally {
                                                                                setActionLoading(null);
                                                                            }
                                                                        }
                                                                    }}
                                                                    className="w-full text-left px-4 py-2 text-sm text-orange-600 hover:bg-orange-50 flex items-center gap-2"
                                                                >
                                                                    <Ban className="w-4 h-4" />
                                                                    Ban User
                                                                </button>
                                                            ) : (
                                                                <button
                                                                    onClick={async () => {
                                                                        setOpenMenuId(null);
                                                                        try {
                                                                            setActionLoading('activate');
                                                                            const response = await adminAPI.bulkUserAction([user.id], 'activate');
                                                                            alert(response.message || 'User unbanned successfully');
                                                                            loadUsers();
                                                                        } catch (err: any) {
                                                                            alert(`Failed to unban user: ${err.response?.data?.detail || err.message}`);
                                                                        } finally {
                                                                            setActionLoading(null);
                                                                        }
                                                                    }}
                                                                    className="w-full text-left px-4 py-2 text-sm text-blue-600 hover:bg-blue-50 flex items-center gap-2"
                                                                >
                                                                    <Unlock className="w-4 h-4" />
                                                                    Unban User
                                                                </button>
                                                            )}
                                                            {user.is_admin ? (
                                                                <button
                                                                    onClick={async () => {
                                                                        setOpenMenuId(null);
                                                                        if (confirm('Are you sure you want to remove admin privileges from this user?')) {
                                                                            try {
                                                                                setActionLoading('demote_admin');
                                                                                const response = await adminAPI.bulkUserAction([user.id], 'demote_admin');
                                                                                alert(response.message || 'Admin privileges removed successfully');
                                                                                loadUsers();
                                                                            } catch (err: any) {
                                                                                alert(`Failed to demote user: ${err.response?.data?.detail || err.message}`);
                                                                            } finally {
                                                                                setActionLoading(null);
                                                                            }
                                                                        }
                                                                    }}
                                                                    className="w-full text-left px-4 py-2 text-sm text-purple-600 hover:bg-purple-50 flex items-center gap-2"
                                                                >
                                                                    <ShieldOff className="w-4 h-4" />
                                                                    Remove Admin
                                                                </button>
                                                            ) : (
                                                                <button
                                                                    onClick={async () => {
                                                                        setOpenMenuId(null);
                                                                        if (confirm('Are you sure you want to promote this user to admin?')) {
                                                                            try {
                                                                                setActionLoading('promote_admin');
                                                                                const response = await adminAPI.bulkUserAction([user.id], 'promote_admin');
                                                                                alert(response.message || 'User promoted to admin successfully');
                                                                                loadUsers();
                                                                            } catch (err: any) {
                                                                                alert(`Failed to promote user: ${err.response?.data?.detail || err.message}`);
                                                                            } finally {
                                                                                setActionLoading(null);
                                                                            }
                                                                        }
                                                                    }}
                                                                    className="w-full text-left px-4 py-2 text-sm text-purple-600 hover:bg-purple-50 flex items-center gap-2"
                                                                >
                                                                    <Shield className="w-4 h-4" />
                                                                    Promote to Admin
                                                                </button>
                                                            )}
                                                            <button
                                                                onClick={async () => {
                                                                    setOpenMenuId(null);
                                                                    if (confirm('Are you sure you want to delete this user? This action cannot be undone.')) {
                                                                        try {
                                                                            setActionLoading('delete');
                                                                            const response = await adminAPI.bulkUserAction([user.id], 'delete');
                                                                            alert(response.message || 'User deleted successfully');
                                                                            loadUsers();
                                                                        } catch (err: any) {
                                                                            alert(`Failed to delete user: ${err.response?.data?.detail || err.message}`);
                                                                        } finally {
                                                                            setActionLoading(null);
                                                                        }
                                                                    }
                                                                }}
                                                                className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 flex items-center gap-2"
                                                            >
                                                                <Trash2 className="w-4 h-4" />
                                                                Delete
                                                            </button>
                                                        </div>
                                                    </div>
                                                )}
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>

                        {/* Pagination */}
                        <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
                            <div className="text-sm text-gray-600">
                                Showing {(page - 1) * 10 + 1} to {Math.min(page * 10, 1247)} of 1,247 users
                            </div>
                            <div className="flex gap-2">
                                <button
                                    onClick={() => setPage(p => Math.max(1, p - 1))}
                                    disabled={page === 1}
                                    className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition disabled:opacity-50"
                                >
                                    Previous
                                </button>
                                <button
                                    onClick={() => setPage(p => p + 1)}
                                    className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
                                >
                                    Next
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* User Detail Modal */}
            {showUserModal && selectedUser && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
                    <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
                        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
                            <h2 className="text-2xl font-bold text-gray-900">User Details</h2>
                            <button
                                onClick={() => {
                                    setShowUserModal(false);
                                    setSelectedUser(null);
                                }}
                                className="p-2 hover:bg-gray-100 rounded-lg transition"
                            >
                                <X className="w-5 h-5 text-gray-600" />
                            </button>
                        </div>
                        <div className="p-6 space-y-6">
                            {/* User Info */}
                            <div className="flex items-center gap-4 pb-4 border-b border-gray-200">
                                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 font-bold text-xl">
                                    {selectedUser.user?.display_name?.[0] || selectedUser.user?.username?.[0] || 'U'}
                                </div>
                                <div>
                                    <h3 className="text-xl font-semibold text-gray-900">
                                        {selectedUser.user?.display_name || selectedUser.user?.username}
                                    </h3>
                                    <p className="text-gray-600">@{selectedUser.user?.username}</p>
                                    <p className="text-sm text-gray-500">{selectedUser.user?.email}</p>
                                </div>
                            </div>

                            {/* Status Badges */}
                            <div className="flex flex-wrap gap-2">
                                <span className={`px-3 py-1 rounded-full text-sm font-medium ${selectedUser.user?.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                                    {selectedUser.user?.is_active ? 'Active' : 'Inactive'}
                                </span>
                                {selectedUser.user?.is_verified && (
                                    <span className="px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
                                        Verified
                                    </span>
                                )}
                                {selectedUser.user?.is_admin && (
                                    <span className="px-3 py-1 rounded-full text-sm font-medium bg-purple-100 text-purple-800">
                                        Admin
                                    </span>
                                )}
                            </div>

                            {/* Stats */}
                            <div className="grid grid-cols-2 gap-4">
                                <div className="bg-gray-50 rounded-lg p-4">
                                    <div className="text-sm text-gray-600">Notifications</div>
                                    <div className="text-2xl font-bold text-gray-900">{selectedUser.stats?.total_notifications || 0}</div>
                                </div>
                                <div className="bg-gray-50 rounded-lg p-4">
                                    <div className="text-sm text-gray-600">Matched Jobs</div>
                                    <div className="text-2xl font-bold text-gray-900">{selectedUser.stats?.total_jobs_matched || 0}</div>
                                </div>
                                <div className="bg-gray-50 rounded-lg p-4">
                                    <div className="text-sm text-gray-600">Days Active</div>
                                    <div className="text-2xl font-bold text-gray-900">{selectedUser.stats?.days_active || 0}</div>
                                </div>
                                <div className="bg-gray-50 rounded-lg p-4">
                                    <div className="text-sm text-gray-600">Joined</div>
                                    <div className="text-lg font-semibold text-gray-900">
                                        {new Date(selectedUser.user?.created_at).toLocaleDateString()}
                                    </div>
                                </div>
                            </div>

                            {/* Preferences */}
                            {selectedUser.user?.preferences && selectedUser.user.preferences.length > 0 && (
                                <div>
                                    <h4 className="text-lg font-semibold text-gray-900 mb-3">Job Preferences</h4>
                                    <div className="flex flex-wrap gap-2">
                                        {selectedUser.user.preferences.map((pref: string, idx: number) => (
                                            <span key={idx} className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                                                {pref.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Alert Settings */}
                            <div>
                                <h4 className="text-lg font-semibold text-gray-900 mb-3">Alert Settings</h4>
                                <div className="bg-gray-50 rounded-lg p-4 space-y-2">
                                    <div className="flex justify-between">
                                        <span className="text-gray-600">Alert Speed:</span>
                                        <span className="font-medium">{selectedUser.user?.alert_speed || 'Not set'}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-gray-600">In-App Notifications:</span>
                                        <span className="font-medium">{selectedUser.user?.in_app_notifications ? 'Enabled' : 'Disabled'}</span>
                                    </div>
                                </div>
                            </div>

                            {/* Recent Activity */}
                            {selectedUser.recent_activity && selectedUser.recent_activity.length > 0 && (
                                <div>
                                    <h4 className="text-lg font-semibold text-gray-900 mb-3">Recent Activity</h4>
                                    <div className="space-y-2">
                                        {selectedUser.recent_activity.slice(0, 5).map((activity: any, idx: number) => (
                                            <div key={idx} className="bg-gray-50 rounded-lg p-3 flex items-center justify-between">
                                                <div>
                                                    <div className="font-medium text-gray-900">{activity.type}</div>
                                                    <div className="text-sm text-gray-500">
                                                        {new Date(activity.created_at).toLocaleString()}
                                                    </div>
                                                </div>
                                                <span className={`px-2 py-1 rounded text-xs ${activity.status === 'read' ? 'bg-green-100 text-green-800' : 'bg-gray-200 text-gray-800'}`}>
                                                    {activity.status}
                                                </span>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

function AdminJobs() {
    return (
        <div className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="text-lg font-semibold mb-4">Job Management</h3>
            <p className="text-gray-600">Job management interface coming soon...</p>
        </div>
    );
}

export default AdminDashboard;
