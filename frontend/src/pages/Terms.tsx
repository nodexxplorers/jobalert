// src/pages/Terms.tsx

import Navigation from '../components/Navigation';
import Footer from '../components/Footer';

export default function Terms() {
    return (
        <div className="min-h-screen bg-gray-50 flex flex-col">
            <Navigation />

            <main className="flex-grow container mx-auto px-4 py-32">
                <div className="max-w-4xl mx-auto bg-white rounded-2xl shadow-sm p-8 md:p-12">
                    <h1 className="text-4xl font-bold text-gray-900 mb-8 text-center text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-cyan-500">
                        Terms and Conditions
                    </h1>

                    <div className="prose prose-blue max-w-none text-gray-600 space-y-6">
                        <section>
                            <h2 className="text-2xl font-semibold text-gray-800 mb-4">1. Agreement to Terms</h2>
                            <p>
                                By accessing or using X Job Bot, you agree to be bound by these Terms and Conditions and all applicable laws and regulations. If you do not agree with any of these terms, you are prohibited from using or accessing this site.
                            </p>
                        </section>

                        <section>
                            <h2 className="text-2xl font-semibold text-gray-800 mb-4">2. Use License</h2>
                            <p>
                                Permission is granted to temporarily use the service for personal, non-commercial viewing or job seeking purposes. This is the grant of a license, not a transfer of title.
                            </p>
                        </section>

                        <section>
                            <h2 className="text-2xl font-semibold text-gray-800 mb-4">3. User Obligations</h2>
                            <p>
                                You agree not to use the service for any unlawful purpose or any purpose prohibited under this clause. You agree not to use the service in any way that could damage the service or business of X Job Bot.
                            </p>
                        </section>

                        <section>
                            <h2 className="text-2xl font-semibold text-gray-800 mb-4">4. Disclaimer</h2>
                            <p>
                                The materials on X Job Bot are provided on an 'as is' basis. X Job Bot makes no warranties, expressed or implied, and hereby disclaims and negates all other warranties including, without limitation, implied warranties or conditions of merchantability.
                            </p>
                        </section>

                        <section>
                            <h2 className="text-2xl font-semibold text-gray-800 mb-4">5. Limitations</h2>
                            <p>
                                In no event shall X Job Bot or its suppliers be liable for any damages arising out of the use or inability to use the materials on the service.
                            </p>
                        </section>

                        <section>
                            <h2 className="text-2xl font-semibold text-gray-800 mb-4">6. Governing Law</h2>
                            <p>
                                These terms and conditions are governed by and construed in accordance with the laws of your jurisdiction and you irrevocably submit to the exclusive jurisdiction of the courts in that State or location.
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
