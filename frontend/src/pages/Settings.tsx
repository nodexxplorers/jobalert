// src/pages/Settings.tsx 

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { useSettings } from '../hooks/useSettings';
import SettingsSidebar from '../components/Settings/SettingsSidebar';
import ProfileSection from '../components/Settings/ProfileSection';
import ContactChannels from '../components/Settings/ContactChannel';
import AlertSettings from '../components/Settings/AlertSettings';
import ConnectedAccounts from '../components/Settings/ConnectedAccounts';
import DashboardHeader from '../components/DashboardHeader';
import { Toaster } from 'react-hot-toast';

type SettingsTab = 'profile' | 'alerts' | 'keywords' | 'account';

export default function Settings() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<SettingsTab>('profile');
  const { settings, loading, saving, updateContactChannels, updateAlertSettings } = useSettings();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-500"></div>
      </div>
    );
  }

  if (!settings) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p>Failed to load settings</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-cyan-50 to-blue-50">
      <Toaster position="top-right" />
      <DashboardHeader />

      <div className="container mx-auto px-4 py-6">
        <div className="grid lg:grid-cols-[280px_1fr_320px] gap-6">
          {/* Left Sidebar */}
          <SettingsSidebar activeTab={activeTab} onTabChange={setActiveTab} />

          {/* Main Content */}
          <div className="space-y-6">
            <ProfileSection user={settings} />

            <div className="bg-white rounded-2xl shadow-lg p-8">
              <div className="flex items-center justify-between mb-8 pb-4 border-b border-gray-100">
                <div className="flex items-center gap-4">
                  <button
                    onClick={() => navigate('/dashboard')}
                    className="group flex items-center gap-2 px-3 py-2 bg-gray-50 hover:bg-gray-100 rounded-xl transition-all text-gray-600 hover:text-green-600 font-medium"
                    title="Return to Dashboard"
                  >
                    <ArrowLeft className="w-5 h-5 group-hover:-translate-x-1 transition-transform" />
                    <span>Back to Dashboard</span>
                  </button>
                </div>
                <h2 className="text-2xl font-bold text-gray-900">Settings</h2>
              </div>

              <ContactChannels
                email={settings.email}
                telegram={settings.telegram_chat_id || ''}
                inAppNotifications={settings.in_app_notifications}
                onSave={updateContactChannels}
                saving={saving}
              />

              <AlertSettings
                alertSpeed={settings.alert_speed}
                keywords={settings.keywords}
                onSave={updateAlertSettings}
                saving={saving}
              />

              <ConnectedAccounts user={settings as any} />
            </div>
          </div>

          {/* Right Sidebar */}
          <RightSidebar />
        </div>
      </div>
    </div>
  );
}

// Right sidebar component (same as before)
function RightSidebar() {
  return (
    <div className="space-y-6">
      {/* Boost Card */}
      <div className="bg-gradient-to-br from-purple-100 to-pink-50 rounded-2xl p-6 border border-purple-200">
        <h3 className="font-bold text-gray-900 mb-3">Boost Your Visibility</h3>
        <div className="flex items-start gap-2 mb-4">
          <span className="text-green-600">🚀</span>
          <p className="text-sm text-gray-700">
            Priority Alerts & Early Access to jobs
          </p>
        </div>
        <button className="w-full bg-green-500 text-white py-3 rounded-xl font-semibold hover:bg-green-600 transition-colors">
          Upgrade to Pro
        </button>
      </div>

      {/* Quick Links */}
      <div className="bg-white rounded-2xl shadow-lg p-6">
        <h3 className="font-bold text-gray-900 mb-4">Quick Links</h3>
        <div className="space-y-2">
          <QuickLinkItem
            icon="🔔"
            title="Manage Alerts"
            subtitle="You're getting notified instantly ✅"
          />
          <QuickLinkItem
            icon="📱"
            title="You have 15 Subscribers"
            iconColor="text-blue-500"
          />
          <QuickLinkItem
            icon="📗"
            title="Saved 17 Jobs"
            iconColor="text-green-500"
          />
        </div>
      </div>
    </div>
  );
}

function QuickLinkItem({ icon, title, subtitle, iconColor = 'text-blue-600' }: any) {
  return (
    <button className="flex items-center gap-3 w-full text-left py-3 hover:bg-gray-50 rounded-lg px-3 transition-colors">
      <span className={`text-xl ${iconColor}`}>{icon}</span>
      <div className="flex-1">
        <div className="font-medium text-gray-900 text-sm">{title}</div>
        {subtitle && <div className="text-xs text-gray-600">{subtitle}</div>}
      </div>
    </button>
  );
}

