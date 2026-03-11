import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Card } from '../components/Card';
import { LogIn, Mail, Lock, AlertCircle, Zap, Scale, Bot, ArrowRight, Home } from 'lucide-react';

export default function Login({ role }) {
    const navigate = useNavigate();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        if (role === 'driver') {
            try {
                const formData = new URLSearchParams();
                formData.append('username', email);
                formData.append('password', password);

                const response = await fetch('http://localhost:8000/token', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: formData
                });

                if (response.ok) {
                    const data = await response.json();
                    localStorage.setItem('driver_id', data.driver_id.toString());
                    localStorage.setItem('driver_email', data.email);
                    localStorage.setItem('driver_name', data.name);
                    localStorage.setItem('user_role', 'driver');
                    localStorage.setItem('access_token', data.access_token);
                    navigate('/driver');
                } else {
                    const errorData = await response.json();
                    setError(errorData.detail || 'Invalid email or password');
                }
            } catch (err) {
                console.error('Login error:', err);
                setError('Unable to connect to server. Please try again.');
            } finally {
                setLoading(false);
            }
        } else {
            // Admin Authentication
            setTimeout(() => {
                localStorage.setItem('user_role', 'admin');
                localStorage.setItem('admin_email', email);
                navigate('/admin');
                setLoading(false);
            }, 500);
        }
    };

    // Premium Driver Login Layout
    if (role === 'driver') {
        return (
            <div className="min-h-screen flex">
                {/* LEFT SIDE - Branding & Message (60%) */}
                <div className="hidden lg:flex lg:w-3/5 bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 relative overflow-hidden">
                    {/* Animated background patterns */}
                    <div className="absolute inset-0 opacity-20">
                        <div className="absolute top-0 left-0 w-96 h-96 bg-gradient-to-br from-blue-200 to-indigo-200 rounded-full blur-3xl animate-pulse"></div>
                        <div className="absolute bottom-0 right-0 w-96 h-96 bg-gradient-to-br from-purple-200 to-pink-200 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>
                    </div>

                    <div className="relative z-10 flex flex-col p-16 text-gray-800 space-y-12">
                        {/* Logo & Tagline */}
                        <div>
                            <div className="flex items-center gap-4 mb-6">
                                <button
                                    onClick={() => navigate('/')}
                                    className="p-3 bg-white border border-blue-100 rounded-2xl text-blue-500 hover:text-blue-700 hover:bg-blue-50 transition-all shadow-sm group"
                                    title="Back to Portal Selection"
                                >
                                    <Home size={28} className="group-hover:scale-110 transition-transform" />
                                </button>
                                <div className="flex items-center gap-3">
                                    <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl flex items-center justify-center shadow-lg">
                                        <LogIn size={36} className="text-white" />
                                    </div>
                                    <h1 className="text-7xl font-black tracking-tighter bg-gradient-to-r from-blue-600 to-indigo-700 bg-clip-text text-transparent">FairFlow</h1>
                                </div>
                            </div>
                            <p className="text-4xl font-extrabold text-gray-900 mb-4 tracking-tight">
                                Because hard work should be remembered.
                            </p>
                            <p className="text-2xl text-gray-600 max-w-xl leading-relaxed font-medium">
                                A human-centric dispatch system that balances effort, not just distance.
                            </p>
                        </div>

                        {/* Feature Highlights - Simple Icon + Text */}
                        <div className="space-y-8 max-w-2xl">
                            <div className="flex items-start gap-6">
                                <div className="w-16 h-16 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-2xl flex items-center justify-center flex-shrink-0 shadow-md">
                                    <Zap size={32} className="text-white" />
                                </div>
                                <div>
                                    <h3 className="font-bold text-2xl mb-2 text-gray-800">Effort-Based Routing</h3>
                                    <p className="text-gray-600 text-lg">Routes assigned based on real workload, not just mileage.</p>
                                </div>
                            </div>

                            <div className="flex items-start gap-6">
                                <div className="w-16 h-16 bg-gradient-to-br from-green-400 to-emerald-500 rounded-2xl flex items-center justify-center flex-shrink-0 shadow-md">
                                    <Scale size={32} className="text-white" />
                                </div>
                                <div>
                                    <h3 className="font-bold text-2xl mb-2 text-gray-800">Fairness Carried Forward</h3>
                                    <p className="text-gray-600 text-lg">Your effort is tracked across days, ensuring long-term balance.</p>
                                </div>
                            </div>

                            <div className="flex items-start gap-6">
                                <div className="w-16 h-16 bg-gradient-to-br from-purple-400 to-violet-500 rounded-2xl flex items-center justify-center flex-shrink-0 shadow-md">
                                    <Bot size={32} className="text-white" />
                                </div>
                                <div>
                                    <h3 className="font-bold text-2xl mb-2 text-gray-800">AI-Guided Balance</h3>
                                    <p className="text-gray-600 text-lg">Smart algorithms detect drift and protect overloaded drivers.</p>
                                </div>
                            </div>
                        </div>

                        {/* Footer tagline */}
                        <div className="text-gray-500 text-sm">
                            © 2026 FairFlow · Built with fairness in mind
                        </div>
                    </div>
                </div>

                {/* RIGHT SIDE - Login Card (40%) */}
                <div className="flex-1 lg:w-2/5 flex items-center justify-center p-12 bg-gradient-to-br from-gray-50 to-gray-100">
                    <div className="w-full max-w-lg">
                        {/* Login Card */}
                        <div className="bg-white rounded-[2rem] shadow-2xl p-14 border border-gray-100 relative overflow-hidden">
                            {/* Subtle gradient overlay */}
                            <div className="absolute top-0 right-0 w-80 h-80 bg-gradient-to-br from-blue-400 to-purple-500 rounded-full blur-3xl opacity-5"></div>

                            <div className="relative z-10">
                                {/* Icon Badge */}
                                <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl mb-8 shadow-lg">
                                    <ArrowRight size={40} className="text-white" />
                                </div>

                                {/* Title */}
                                <h2 className="text-4xl font-extrabold text-gray-900 mb-4">Driver Portal</h2>
                                <p className="text-xl text-gray-500 mb-10">
                                    Sign in to view your routes, effort score, and fairness balance
                                </p>

                                {/* Error Message */}
                                {error && (
                                    <div className="bg-red-50 border-l-4 border-red-500 text-red-700 px-4 py-3 rounded-lg mb-6 flex items-start gap-3">
                                        <AlertCircle size={20} className="mt-0.5 flex-shrink-0" />
                                        <span className="text-sm">{error}</span>
                                    </div>
                                )}

                                {/* Login Form */}
                                <form onSubmit={handleSubmit} className="space-y-5">
                                    {/* Email Field */}
                                    <div>
                                        <label className="block text-lg font-semibold text-gray-700 mb-3">
                                            Email Address
                                        </label>
                                        <div className="relative">
                                            <Mail className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                                            <input
                                                type="email"
                                                value={email}
                                                onChange={(e) => setEmail(e.target.value)}
                                                placeholder="your.email@example.com"
                                                className="w-full pl-12 pr-4 py-4 bg-gray-50 rounded-xl border-2 border-gray-200 focus:border-blue-500 focus:bg-white focus:outline-none transition-all text-gray-900 placeholder-gray-400"
                                                required
                                            />
                                        </div>
                                    </div>

                                    {/* Password Field */}
                                    <div>
                                        <label className="block text-lg font-semibold text-gray-700 mb-3">
                                            Password
                                        </label>
                                        <div className="relative">
                                            <Lock className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                                            <input
                                                type="password"
                                                value={password}
                                                onChange={(e) => setPassword(e.target.value)}
                                                placeholder="Enter your password"
                                                className="w-full pl-12 pr-4 py-4 bg-gray-50 rounded-xl border-2 border-gray-200 focus:border-blue-500 focus:bg-white focus:outline-none transition-all text-gray-900 placeholder-gray-400"
                                                required
                                            />
                                        </div>
                                        <p className="text-xs text-gray-500 mt-2">
                                            Use the password you created during signup
                                        </p>
                                    </div>

                                    {/* Sign In Button */}
                                    <button
                                        type="submit"
                                        disabled={loading}
                                        className={`w-full py-4 rounded-xl font-bold text-lg text-white shadow-lg transition-all transform ${loading
                                            ? 'bg-gray-300 cursor-not-allowed'
                                            : 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 hover:shadow-xl hover:-translate-y-0.5 active:translate-y-0'
                                            }`}
                                    >
                                        {loading ? 'Signing In...' : 'Sign In to FairFlow'}
                                    </button>

                                    {/* Create Account Link */}
                                    <div className="flex items-center justify-center gap-2 pt-4">
                                        <span className="text-sm text-gray-600">Don't have an account?</span>
                                        <Link
                                            to="/signup/driver"
                                            className="text-sm font-semibold text-blue-600 hover:text-blue-700 hover:underline"
                                        >
                                            Create Account
                                        </Link>
                                    </div>

                                    {/* Back to Home */}
                                    <div className="text-center pt-2">
                                        <button
                                            type="button"
                                            onClick={() => navigate('/')}
                                            className="text-sm text-gray-400 hover:text-gray-600 transition-colors"
                                        >
                                            ← Back to Home
                                        </button>
                                    </div>
                                </form>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    // Premium Admin Login Layout
    return (
        <div className="min-h-screen flex">
            {/* LEFT SIDE - Admin Branding & Message (60%) */}
            <div className="hidden lg:flex lg:w-3/5 bg-gradient-to-br from-slate-50 via-gray-50 to-stone-50 relative overflow-hidden">
                {/* Animated background patterns */}
                <div className="absolute inset-0 opacity-20">
                    <div className="absolute top-0 left-0 w-96 h-96 bg-gradient-to-br from-gray-200 to-slate-300 rounded-full blur-3xl animate-pulse"></div>
                    <div className="absolute bottom-0 right-0 w-96 h-96 bg-gradient-to-br from-stone-200 to-gray-300 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>
                </div>

                <div className="relative z-10 flex flex-col p-16 text-gray-800 space-y-12">
                    {/* Logo & Tagline */}
                    <div>
                        <div className="flex items-center gap-4 mb-6">
                            <button
                                onClick={() => navigate('/')}
                                className="p-3 bg-white border border-gray-200 rounded-2xl text-gray-500 hover:text-black hover:bg-gray-50 transition-all shadow-sm group"
                                title="Back to Portal Selection"
                            >
                                <Home size={28} className="group-hover:scale-110 transition-transform" />
                            </button>
                            <div className="flex items-center gap-3">
                                <div className="w-16 h-16 bg-gradient-to-br from-gray-700 to-gray-900 rounded-2xl flex items-center justify-center shadow-lg">
                                    <LogIn size={36} className="text-white" />
                                </div>
                                <h1 className="text-7xl font-black tracking-tighter bg-gradient-to-r from-gray-700 to-gray-900 bg-clip-text text-transparent">FairFlow</h1>
                            </div>
                        </div>
                        <p className="text-4xl font-extrabold text-gray-900 mb-4 tracking-tight">
                            Prevent burnout. Maintain morale.
                        </p>
                        <p className="text-2xl text-gray-600 max-w-xl leading-relaxed font-medium">
                            Let AI do the heavy lifting.
                        </p>
                    </div>

                    {/* Feature Highlights - Simple Icon + Text */}
                    <div className="space-y-8 max-w-2xl">
                        <div className="flex items-start gap-6">
                            <div className="w-16 h-16 bg-gradient-to-br from-red-500 to-rose-600 rounded-2xl flex items-center justify-center flex-shrink-0 shadow-md">
                                <AlertCircle size={32} className="text-white" />
                            </div>
                            <div>
                                <h3 className="font-bold text-2xl mb-2 text-gray-800">Automatic Drift Alerts</h3>
                                <p className="text-gray-600 text-lg">Get notified when workload variance spikes—before drivers complain or quit.</p>
                            </div>
                        </div>

                        <div className="flex items-start gap-6">
                            <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl flex items-center justify-center flex-shrink-0 shadow-md">
                                <Scale size={32} className="text-white" />
                            </div>
                            <div>
                                <h3 className="font-bold text-2xl mb-2 text-gray-800">Cumulative Fairness Ledger</h3>
                                <p className="text-gray-600 text-lg">See who's overloaded, who's coasting—tracked across weeks, not just today.</p>
                            </div>
                        </div>

                        <div className="flex items-start gap-6">
                            <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-2xl flex items-center justify-center flex-shrink-0 shadow-md">
                                <Bot size={32} className="text-white" />
                            </div>
                            <div>
                                <h3 className="font-bold text-2xl mb-2 text-gray-800">AI-Guided Route Blocking</h3>
                                <p className="text-gray-600 text-lg">System prevents assigning hard routes to burned-out drivers. No manual tracking needed.</p>
                            </div>
                        </div>
                    </div>

                    {/* Footer tagline */}
                    <div className="text-gray-500 text-sm">
                        © 2026 FairFlow · Built with fairness in mind
                    </div>
                </div>
            </div>

            {/* RIGHT SIDE - Login Card (40%) */}
            <div className="flex-1 lg:w-2/5 flex items-center justify-center p-12 bg-gradient-to-br from-gray-50 to-gray-100">
                <div className="w-full max-w-lg">
                    {/* Login Card */}
                    <div className="bg-white rounded-[2rem] shadow-2xl p-14 border border-gray-100 relative overflow-hidden">
                        {/* Subtle gradient overlay */}
                        <div className="absolute top-0 right-0 w-80 h-80 bg-gradient-to-br from-gray-400 to-gray-600 rounded-full blur-3xl opacity-5"></div>

                        <div className="relative z-10">
                            {/* Icon Badge */}
                            <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-gray-700 to-gray-900 rounded-2xl mb-8 shadow-lg">
                                <ArrowRight size={40} className="text-white" />
                            </div>

                            {/* Title */}
                            <h2 className="text-4xl font-extrabold text-gray-900 mb-4">Admin Portal</h2>
                            <p className="text-xl text-gray-500 mb-10">
                                Manage drivers, monitor fairness, and oversee route assignments
                            </p>

                            {/* Error Message */}
                            {error && (
                                <div className="bg-red-50 border-l-4 border-red-500 text-red-700 px-4 py-3 rounded-lg mb-6 flex items-start gap-3">
                                    <AlertCircle size={20} className="mt-0.5 flex-shrink-0" />
                                    <span className="text-sm">{error}</span>
                                </div>
                            )}

                            {/* Login Form */}
                            <form onSubmit={handleSubmit} className="space-y-5">
                                {/* Email Field */}
                                <div>
                                    <label className="block text-lg font-semibold text-gray-700 mb-3">
                                        Email Address
                                    </label>
                                    <div className="relative">
                                        <Mail className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                                        <input
                                            type="email"
                                            value={email}
                                            onChange={(e) => setEmail(e.target.value)}
                                            placeholder="admin@fairflow.com"
                                            className="w-full pl-12 pr-4 py-4 bg-gray-50 rounded-xl border-2 border-gray-200 focus:border-gray-700 focus:bg-white focus:outline-none transition-all text-gray-900 placeholder-gray-400"
                                            required
                                        />
                                    </div>
                                </div>

                                {/* Password Field */}
                                <div>
                                    <label className="block text-lg font-semibold text-gray-700 mb-3">
                                        Password
                                    </label>
                                    <div className="relative">
                                        <Lock className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                                        <input
                                            type="password"
                                            value={password}
                                            onChange={(e) => setPassword(e.target.value)}
                                            placeholder="Enter your password"
                                            className="w-full pl-12 pr-4 py-4 bg-gray-50 rounded-xl border-2 border-gray-200 focus:border-gray-700 focus:bg-white focus:outline-none transition-all text-gray-900 placeholder-gray-400"
                                            required
                                        />
                                    </div>
                                    <p className="text-xs text-gray-500 mt-2">
                                        Use the password you created during signup
                                    </p>
                                </div>

                                {/* Sign In Button */}
                                <button
                                    type="submit"
                                    disabled={loading}
                                    className={`w-full py-5 rounded-2xl font-black text-xl text-white shadow-xl transition-all transform ${loading
                                        ? 'bg-gray-300 cursor-not-allowed'
                                        : 'bg-gradient-to-r from-gray-700 to-gray-900 hover:from-gray-800 hover:to-black hover:shadow-2xl hover:-translate-y-1 active:translate-y-0'
                                        }`}
                                >
                                    {loading ? 'Signing In...' : 'Sign In to Dashboard'}
                                </button>

                                {/* Create Account Link */}
                                <div className="flex items-center justify-center gap-2 pt-4">
                                    <span className="text-sm text-gray-600">Don't have an account?</span>
                                    <Link
                                        to="/signup/admin"
                                        className="text-sm font-semibold text-gray-700 hover:text-gray-900 hover:underline"
                                    >
                                        Create Account
                                    </Link>
                                </div>

                                {/* Back to Home */}
                                <div className="text-center pt-2">
                                    <button
                                        type="button"
                                        onClick={() => navigate('/')}
                                        className="text-sm text-gray-400 hover:text-gray-600 transition-colors"
                                    >
                                        ← Back to Home
                                    </button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
