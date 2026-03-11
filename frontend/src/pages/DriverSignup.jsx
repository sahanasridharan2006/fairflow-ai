import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '../components/Card';
import { UserPlus, AlertCircle, Zap, Scale, Bot } from 'lucide-react';

export default function DriverSignup() {
    const navigate = useNavigate();
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        if (!name.trim() || !email.trim() || !password.trim()) {
            setError('Please fill in all fields');
            return;
        }

        if (password.length < 6) {
            setError('Password must be at least 6 characters');
            return;
        }

        setLoading(true);
        try {
            const res = await fetch('http://localhost:8000/signup/driver', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, email, password })
            });

            const data = await res.json();

            if (res.ok) {
                // Success - show message and redirect to login
                alert('✅ Account created successfully! Please sign in.');
                navigate('/login/driver');
            } else {
                setError(data.detail || 'Failed to create account');
            }
        } catch (err) {
            console.error(err);
            setError('Network error. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex">
            {/* LEFT SIDE - Branding & Features (60%) */}
            <div className="hidden lg:flex lg:w-3/5 bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 relative overflow-hidden">
                {/* Animated background patterns */}
                <div className="absolute inset-0 opacity-20">
                    <div className="absolute top-0 left-0 w-96 h-96 bg-gradient-to-br from-blue-200 to-indigo-200 rounded-full blur-3xl animate-pulse"></div>
                    <div className="absolute bottom-0 right-0 w-96 h-96 bg-gradient-to-br from-purple-200 to-pink-200 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>
                </div>

                <div className="relative z-10 flex flex-col justify-between p-16 text-gray-800">
                    {/* Logo & Tagline */}
                    <div>
                        <div className="flex items-center gap-3 mb-6">
                            <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl flex items-center justify-center shadow-lg">
                                <UserPlus size={28} className="text-white" />
                            </div>
                            <h1 className="text-5xl font-bold tracking-tight bg-gradient-to-r from-blue-600 to-indigo-700 bg-clip-text text-transparent">FairFlow</h1>
                        </div>
                        <p className="text-2xl font-semibold text-gray-800 mb-3">
                            Because hard work should be remembered.
                        </p>
                        <p className="text-lg text-gray-600 max-w-lg leading-relaxed">
                            A human-centric dispatch system that balances effort, not just distance.
                        </p>
                    </div>

                    {/* Feature Highlights */}
                    <div className="space-y-6 max-w-xl">
                        <div className="flex items-start gap-4 bg-white bg-opacity-70 backdrop-blur-sm p-5 rounded-2xl border border-gray-200 hover:shadow-md transition-all">
                            <div className="w-12 h-12 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-xl flex items-center justify-center flex-shrink-0 shadow-sm">
                                <Zap size={24} className="text-white" />
                            </div>
                            <div>
                                <h3 className="font-semibold text-lg mb-1 text-gray-800">Effort-Based Routing</h3>
                                <p className="text-gray-600 text-sm">Routes assigned based on real workload, not just mileage.</p>
                            </div>
                        </div>

                        <div className="flex items-start gap-4 bg-white bg-opacity-70 backdrop-blur-sm p-5 rounded-2xl border border-gray-200 hover:shadow-md transition-all">
                            <div className="w-12 h-12 bg-gradient-to-br from-green-400 to-emerald-500 rounded-xl flex items-center justify-center flex-shrink-0 shadow-sm">
                                <Scale size={24} className="text-white" />
                            </div>
                            <div>
                                <h3 className="font-semibold text-lg mb-1 text-gray-800">Fairness Carried Forward</h3>
                                <p className="text-gray-600 text-sm">Your effort is tracked across days, ensuring long-term balance.</p>
                            </div>
                        </div>

                        <div className="flex items-start gap-4 bg-white bg-opacity-70 backdrop-blur-sm p-5 rounded-2xl border border-gray-200 hover:shadow-md transition-all">
                            <div className="w-12 h-12 bg-gradient-to-br from-purple-400 to-violet-500 rounded-xl flex items-center justify-center flex-shrink-0 shadow-sm">
                                <Bot size={24} className="text-white" />
                            </div>
                            <div>
                                <h3 className="font-semibold text-lg mb-1 text-gray-800">AI-Guided Balance</h3>
                                <p className="text-gray-600 text-sm">Smart algorithms detect drift and protect overloaded drivers.</p>
                            </div>
                        </div>
                    </div>

                    {/* Footer */}
                    <div className="text-sm text-gray-500">
                        © 2026 FairFlow · Built with fairness in mind
                    </div>
                </div>
            </div>

            {/* RIGHT SIDE - Signup Form (40%) */}
            <div className="w-full lg:w-2/5 flex items-center justify-center p-8 bg-white">
                <div className="w-full max-w-md">
                    <div className="mb-8">
                        <div className="bg-blue-600 w-16 h-16 rounded-2xl flex items-center justify-center mb-4 shadow-lg">
                            <UserPlus size={32} className="text-white" />
                        </div>
                        <h2 className="text-3xl font-bold text-gray-900 mb-2">Create Account</h2>
                        <p className="text-gray-600">Join FairFlow and experience fair routing</p>
                    </div>

                    <form onSubmit={handleSubmit} className="space-y-5">
                        {error && (
                            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl flex items-start gap-3">
                                <AlertCircle size={20} className="mt-0.5 flex-shrink-0" />
                                <span className="text-sm">{error}</span>
                            </div>
                        )}

                        <div>
                            <label className="block text-sm font-semibold text-gray-700 mb-2">
                                Full Name
                            </label>
                            <input
                                type="text"
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                placeholder="Enter your full name"
                                className="w-full px-4 py-3 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                                required
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-semibold text-gray-700 mb-2">
                                Email Address
                            </label>
                            <input
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                placeholder="your.email@example.com"
                                className="w-full px-4 py-3 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                                required
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-semibold text-gray-700 mb-2">
                                Password
                            </label>
                            <input
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                placeholder="Minimum 6 characters"
                                className="w-full px-4 py-3 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                                required
                                minLength={6}
                            />
                            <p className="text-xs text-gray-500 mt-1">Use the password you created during signup</p>
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className={`w-full py-3.5 rounded-xl font-semibold text-white shadow-lg transition-all transform active:scale-[0.98] ${loading
                                    ? 'bg-gray-400 cursor-not-allowed'
                                    : 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 hover:shadow-xl'
                                }`}
                        >
                            {loading ? 'Creating Account...' : 'Create Driver Account'}
                        </button>

                        <div className="flex items-center justify-between pt-4 border-t border-gray-200">
                            <button
                                type="button"
                                onClick={() => navigate('/')}
                                className="text-sm text-gray-600 hover:text-gray-800 font-medium transition-colors"
                            >
                                ← Back to Home
                            </button>
                            <button
                                type="button"
                                onClick={() => navigate('/login/driver')}
                                className="text-sm text-blue-600 hover:text-blue-700 font-medium transition-colors"
                            >
                                Already have an account?
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
}
