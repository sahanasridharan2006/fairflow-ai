import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Card } from '../components/Card';
import { Truck, TrendingUp, Award, CloudRain, Wind, AlertCircle } from 'lucide-react';
import { formatEffort, formatCredits, formatBalance, withSign } from '../utils/formatMetrics';

export default function DriverDashboard() {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        // Get driver ID from localStorage
        const driverId = localStorage.getItem('driver_id');
        const driverName = localStorage.getItem('driver_name');

        if (!driverId) {
            setError('not_logged_in');
            setLoading(false);
            return;
        }

        // Fetch driver-specific data using ID
        fetch(`http://localhost:8000/driver/${driverId}/dashboard`)
            .then(res => {
                if (!res.ok) throw new Error('Backend error');
                return res.json();
            })
            .then(data => {
                setData({ ...data, name: driverName || data.name });
                setLoading(false);
                setError(null);
            })
            .catch(err => {
                console.error("Failed to fetch", err);
                setError('backend_error');
                setLoading(false);
            });
    }, []);

    if (loading) return <div className="p-8 text-center text-lg text-gray-500">Loading Dashboard...</div>;

    if (error === 'not_logged_in') {
        return (
            <div className="p-8 text-center">
                <div className="bg-yellow-50 border-l-4 border-yellow-500 p-6 rounded-lg max-w-md mx-auto">
                    <p className="text-yellow-800 font-semibold mb-2">⚠️ Not Logged In</p>
                    <p className="text-yellow-700 mb-4">Please log in to view your dashboard.</p>
                    <a href="/login/driver" className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg inline-block font-medium">
                        Go to Login
                    </a>
                </div>
            </div>
        );
    }

    if (error === 'backend_error') {
        return (
            <div className="p-8 text-center">
                <div className="bg-red-50 border-l-4 border-red-500 p-6 rounded-lg max-w-md mx-auto">
                    <p className="text-red-800 font-semibold mb-2">❌ Error Loading Data</p>
                    <p className="text-red-700 mb-4">Unable to connect to backend or invalid session.</p>
                    <button
                        onClick={() => {
                            localStorage.clear();
                            window.location.href = '/login/driver';
                        }}
                        className="bg-red-100 hover:bg-red-200 text-red-800 px-4 py-2 rounded-lg font-medium transition-colors"
                    >
                        Sign Out & Try Again
                    </button>
                </div>
            </div>
        );
    }

    if (!data) return <div className="p-8 text-red-500">No data available</div>;

    const { stats, route, team_average, message, status } = data;
    const isHard = route?.difficulty === 'Hard';
    const isEasy = route?.difficulty === 'Easy';

    return (
        <div className="layout">
            {/* Header - SINGLE DRIVER ONLY */}
            <div className="flex justify-between items-center mb-8">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">Welcome, {data.name}</h1>
                    <p className="text-gray-500 mt-1">{new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</p>
                </div>
                <div className={`px-4 py-2 rounded-full font-medium ${status === 'ACTIVE' ? 'bg-green-100 text-green-700' :
                    status === 'SICK' ? 'bg-orange-100 text-orange-700' :
                        'bg-gray-100 text-gray-700'
                    }`}>
                    {status}
                </div>
            </div>

            {/* Alert Message */}
            {message && (
                <div className={`mb-6 p-4 rounded-xl flex items-start gap-3 ${isHard ? 'bg-red-50 border-l-4 border-red-500' :
                    isEasy ? 'bg-green-50 border-l-4 border-green-500' :
                        'bg-blue-50 border-l-4 border-blue-500'
                    }`}>
                    <AlertCircle className={isHard ? 'text-red-500' : isEasy ? 'text-green-500' : 'text-blue-500'} size={20} />
                    <p className={`text-sm font-medium ${isHard ? 'text-red-800' : isEasy ? 'text-green-800' : 'text-blue-800'
                        }`}>{message}</p>
                </div>
            )}

            {/* AI Fairness Transparency Banner */}
            {stats && stats.total_balance && Math.abs(stats.total_balance) > 50 && (
                <div className="mb-6 p-4 rounded-xl flex items-start gap-3 bg-gradient-to-r from-indigo-50 to-purple-50 border border-indigo-200">
                    <div className="text-2xl">🤖</div>
                    <div className="flex-1">
                        <div className="font-bold text-indigo-900 mb-1">FairFlow AI is Balancing</div>
                        <p className="text-sm text-indigo-700">
                            {stats.total_balance > 50
                                ? "You're receiving lower effort per working hour to balance team workload. Our AI system prioritizes other drivers to maintain fairness."
                                : "Our system is balancing your workload per working hour. You may receive priority for easier routes as part of our fairness commitment."
                            }
                        </p>
                    </div>
                </div>
            )}

            {/* Stats Cards - SINGLE DRIVER DATA */}
            <div className="grid-4 mb-8">
                <Card className="border-l-4 border-l-blue-500">
                    <p className="stat-label">Today's Effort</p>
                    <div className="stat-value text-blue-600">{formatEffort(stats?.effort_today)}</div>
                    <div className="flex items-center gap-1 text-sm text-gray-500">
                        <TrendingUp size={14} />
                        <span>Workload Score</span>
                    </div>
                </Card>

                <Card className="border-l-4 border-l-purple-500">
                    <p className="stat-label">Credits Today</p>
                    <div className={`stat-value ${stats?.credits_today >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {withSign(formatCredits(stats?.credits_today))}
                    </div>
                    <div className="text-sm text-gray-500">vs Team Average</div>
                </Card>

                <Card className="border-l-4 border-l-yellow-500">
                    <p className="stat-label">Fairness Balance</p>
                    <div className={`stat-value ${stats?.total_balance >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {withSign(formatBalance(stats?.total_balance))}
                    </div>
                    <div className="flex items-center gap-1 text-sm text-gray-500">
                        <Award size={14} />
                        <span>Cumulative</span>
                    </div>
                </Card>

                <Card className="border-l-4 border-l-gray-400">
                    <p className="stat-label">Team Average</p>
                    <div className="stat-value text-gray-700">{formatEffort(team_average)}</div>
                    <div className="text-sm text-gray-500">Reference Point</div>
                </Card>
            </div>

            {/* Today's Route Card - SINGLE DRIVER */}
            <Card className="mb-8">
                <div className="flex items-center justify-between mb-2">
                    <h2 className="text-xl font-bold text-gray-800 flex items-center gap-2">
                        <Truck size={24} className="text-blue-600" />
                        Today's Route
                    </h2>
                    {route && (
                        <span className={`px-4 py-2 rounded-full font-bold text-sm ${route.difficulty === 'Hard' ? 'bg-red-100 text-red-700' :
                            route.difficulty === 'Medium' ? 'bg-yellow-100 text-yellow-700' :
                                'bg-green-100 text-green-700'
                            }`}>
                            {route.difficulty}
                        </span>
                    )}
                </div>

                {route?.address && (
                    <div className="mb-4 bg-blue-50/50 p-4 rounded-xl border border-blue-100">
                        <p className="text-[10px] font-bold text-blue-400 uppercase tracking-widest mb-1">Destination Address</p>
                        <p className="text-lg font-bold text-blue-900 leading-tight">{route.address}</p>
                    </div>
                )}

                {route ? (
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="bg-gray-50 p-4 rounded-lg">
                            <p className="text-xs text-gray-500 mb-1">Stops</p>
                            <p className="text-2xl font-bold text-gray-800">{route.stops || 0}</p>
                        </div>
                        <div className="bg-gray-50 p-4 rounded-lg">
                            <p className="text-xs text-gray-500 mb-1">Apartments</p>
                            <p className="text-2xl font-bold text-gray-800">{route.apartments || 0}</p>
                        </div>
                        <div className="bg-gray-50 p-4 rounded-lg flex items-center gap-3">
                            <Wind className="text-blue-500" size={24} />
                            <div>
                                <p className="text-xs text-gray-500">Traffic</p>
                                <p className="font-bold text-gray-800">{route.traffic_level}</p>
                            </div>
                        </div>
                        <div className="bg-gray-50 p-4 rounded-lg flex items-center gap-3">
                            <CloudRain className="text-blue-500" size={24} />
                            <div>
                                <p className="text-xs text-gray-500">Weather</p>
                                <p className="font-bold text-gray-800">{route.weather_condition}</p>
                            </div>
                        </div>
                    </div>
                ) : (
                    <div className="text-center py-8 text-gray-500">
                        <Truck size={48} className="mx-auto mb-3 text-gray-300" />
                        <p className="font-medium">No route assigned yet</p>
                        <p className="text-sm">Check back later for your assignment</p>
                    </div>
                )}
            </Card>

            {/* Quick Actions */}
            <div className="grid grid-cols-2 gap-4">
                <Link to="/driver/history">
                    <Card className="hover:shadow-lg transition-shadow cursor-pointer">
                        <div className="text-center py-4">
                            <TrendingUp size={32} className="mx-auto mb-2 text-blue-600" />
                            <p className="font-semibold text-gray-800">View History</p>
                            <p className="text-sm text-gray-500">Last 7 days</p>
                        </div>
                    </Card>
                </Link>
                <Link to="/driver/feedback">
                    <Card className="hover:shadow-lg transition-shadow cursor-pointer">
                        <div className="text-center py-4">
                            <AlertCircle size={32} className="mx-auto mb-2 text-purple-600" />
                            <p className="font-semibold text-gray-800">Route Feedback</p>
                            <p className="text-sm text-gray-500">Share concerns</p>
                        </div>
                    </Card>
                </Link>
            </div>
        </div>
    );
}
