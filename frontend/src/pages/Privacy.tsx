// src/pages/Privacy.tsx

import Navigation from '../components/Navigation';
import Footer from '../components/Footer';

export default function Privacy() {
    return (
        <div className="min-h-screen bg-gray-50 flex flex-col">
            <Navigation />

            <main className="flex-grow container mx-auto px-4 py-32">
                <div className="max-w-4xl mx-auto bg-white rounded-2xl shadow-sm p-8 md:p-12">
                    <h1 className="text-4xl font-bold text-gray-900 mb-8 text-center text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-cyan-500">
                        Privacy Policy
                    </h1>

                    <div className="prose prose-blue max-w-none text-gray-600 space-y-6">
                        <section>
                            <h2 className="text-2xl font-semibold text-gray-800 mb-4">1. Introduction</h2>
                            <p>
                                At X Job Bot, we take your privacy seriously. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our service.
                            </p>
                        </section>

                        <section>
                            <h2 className="text-2xl font-semibold text-gray-800 mb-4">2. Information Collection</h2>
                            <p>
                                We collect information that you provide directly to us when you register, such as your email address, preferences, and Twitter/X account information used for the bot's functionality.
                            </p>
                            <ul className="list-disc pl-5 mt-2 space-y-2">
                                <li>Personal data (email address)</li>
                                <li>Twitter/X account identifiers</li>
                                <li>Job preferences and search keywords</li>
                                <li>Notification settings</li>
                            </ul>
                        </section>

                        <section>
                            <h2 className="text-2xl font-semibold text-gray-800 mb-4">3. Use of Information</h2>
                            <p>
                                We use the information we collect to:
                            </p>
                            <ul className="list-disc pl-5 mt-2 space-y-2">
                                <li>Provide, operate, and maintain our service</li>
                                <li>Send you job alerts based on your preferences</li>
                                <li>Improve and personalize your user experience</li>
                                <li>Communicating with you regarding updates or support</li>
                            </ul>
                        </section>

                        <section>
                            <h2 className="text-2xl font-semibold text-gray-800 mb-4">4. Data Security</h2>
                            <p>
                                We implement industry-standard security measures to protect your personal information. However, please remember that no method of transmission over the internet or electronic storage is 100% secure.
                            </p>
                        </section>

                        <section>
                            <h2 className="text-2xl font-semibold text-gray-800 mb-4">5. Contact Us</h2>
                            <p>
                                If you have any questions or suggestions about our Privacy Policy, do not hesitate to contact us.
                            </p>
                        </section>
                    </div>

                    <div className="mt-12 text-sm text-gray-400 text-center border-t pt-8">
                        Last updated: January 2026
                    </div>
                </div>
            </main>

            <Footer />
        </div>
    );
}
