// src/components/Settings/ProfileSection.tsx
import { Camera } from 'lucide-react';

export default function ProfileSection({ user }: { user: any }) {
  // Use passed user data or fallbacks
  const displayUser = {
    name: user?.name || 'User',
    username: user?.username || 'user',
    email: user?.email || '',
    memberSince: user?.created_at ? new Date(user.created_at).toLocaleDateString('en-US', { month: 'long', year: 'numeric' }) : 'Recently',
    avatar: user?.avatar || '/user-avatar.jpg',
    badge: user?.subscription_tier === 'pro' ? 'Pro Member' : 'Free Plan',
  };

  return (
    <div className="bg-gradient-to-br from-green-100 via-cyan-50 to-blue-50 rounded-2xl p-8 border border-green-200">
      <div className="flex items-start gap-6">
        {/* Avatar */}
        <div className="relative group">
          <img
            src={displayUser.avatar}
            alt={displayUser.name}
            className="w-24 h-24 rounded-full object-cover ring-4 ring-white shadow-lg"
            onError={(e) => {
              e.currentTarget.src = `https://ui-avatars.com/api/?name=${displayUser.name}&background=667eea&color=fff&size=128`;
            }}
          />
          <button className="absolute bottom-0 right-0 p-2 bg-white rounded-full shadow-lg hover:bg-gray-50 transition-colors opacity-0 group-hover:opacity-100">
            <Camera className="w-4 h-4 text-gray-600" />
          </button>
        </div>

        {/* Info */}
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <h2 className="text-2xl font-bold text-gray-900">{displayUser.name}</h2>
            <span className="px-3 py-1 bg-yellow-100 text-yellow-700 text-xs font-bold rounded-full">
              🏆 {displayUser.badge}
            </span>
          </div>
          <div className="flex items-center gap-2 text-gray-600 mb-2">
            <span>@{displayUser.username}</span>
            <span>•</span>
            <button className="text-blue-600 hover:underline text-sm font-medium">
              View Profile
            </button>
          </div>
          <p className="text-sm text-gray-600">Member since {displayUser.memberSince}</p>
        </div>
      </div>
    </div>
  );
}