// src/components/Footer.tsx

import { Link } from 'react-router-dom';
import { Twitter, Mail, ExternalLink } from 'lucide-react';

export default function Footer() {
    const currentYear = new Date().getFullYear();

    return (
        <footer className="bg-gray-900 border-t border-gray-800 py-12">
            <div className="container mx-auto px-4">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-12 mb-12">
                    {/* Brand */}
                    <div className="md:col-span-2">
                        <div className="flex items-center gap-3 mb-6">
                            <img src="/logos.png" alt="Logo" className="w-10 h-10 rounded-xl" />
                            <span className="text-white font-bold text-xl">X Job Bot</span>
                        </div>
                        <p className="text-gray-400 max-w-sm mb-6">
                            The smartest way to find job opportunities on X/Twitter.
                            Real-time alerts tailored to your skills and preferences.
                        </p>
                        <div className="flex gap-4">
                            <a href="https://x.com/codewithXplorer" className="p-2 bg-gray-800 rounded-lg text-gray-400 hover:text-white transition-colors">
                                <Twitter className="w-5 h-5" />
                            </a>
                            <a href="" className="p-2 bg-gray-800 rounded-lg text-gray-400 hover:text-white transition-colors">
                                <Mail className="w-5 h-5" />
                            </a>
                        </div>
                    </div>

                    {/* Quick Links */}
                    <div>
                        <h4 className="text-white font-semibold mb-6">Product</h4>
                        <ul className="space-y-4">
                            <li><Link to="/#features" className="text-gray-400 hover:text-white transition-colors">Features</Link></li>
                            <li><Link to="/#pricing" className="text-gray-400 hover:text-white transition-colors">Pricing</Link></li>
                            <li><Link to="/register" className="text-gray-400 hover:text-white transition-colors">Get Started</Link></li>
                        </ul>
                    </div>

                    {/* Legal */}
                    <div>
                        <h4 className="text-white font-semibold mb-6">Legal</h4>
                        <ul className="space-y-4">
                            <li><Link to="/privacy" className="text-gray-400 hover:text-white transition-colors">Privacy Policy</Link></li>
                            <li><Link to="/terms" className="text-gray-400 hover:text-white transition-colors">Terms of Service</Link></li>
                            <li><Link to="/#help" className="text-gray-400 hover:text-white transition-colors flex items-center gap-2">
                                Help Center <ExternalLink className="w-3 h-3" />
                            </Link></li>
                        </ul>
                    </div>
                </div>

                <div className="pt-8 border-t border-gray-800 flex flex-col md:flex-row justify-between items-center gap-4">
                    <p className="text-gray-500 text-sm">
                        © {currentYear} X Job Bot. All rights reserved.
                    </p>
                    <div className="flex items-center gap-3 text-sm text-gray-500">
                        Built with 💙 for the professional community.
                    </div>
                </div>
            </div>
        </footer>
    );
}
