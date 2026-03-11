import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Card } from '../components/Card';
import { History, TrendingUp, AlertCircle } from 'lucide-react';
import { formatEffort, formatCredits, formatBalance, withSign } from '../utils/formatMetrics';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    Filler
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    Filler
);

export default function DriverHistory() {
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        // Get driver info from localStorage (same as dashboard)
        const driverId = localStorage.getItem('driver_id');
        const driverEmail = localStorage.getItem('driver_email');

        if (!driverId || !driverEmail) {
            setError('not_logged_in');
            setLoading(false);
            return;
        }

        // Fetch history using driver email (backend expects user_email query param)
        fetch(`http://localhost:8000/driver/history?user_email=${encodeURIComponent(driverEmail)}`)
            .then(res => {
                if (!res.ok) {
                    throw new Error('Failed to fetch history');
                }
                return res.json();
            })
            .then(data => {
                setHistory(data);
                setLoading(false);
                setError(null);
            })
            .catch(err => {
                console.error("Failed to fetch history", err);
                setError('backend_error');
                setLoading(false);
            });
    }, []);

    // Loading State
    if (loading) {
        return (
            <div className="p-8">
                <div className="animate-pulse space-y-6">
                    <div className="h-8 bg-gray-200 rounded w-1/3"></div>
                    <div className="h-64 bg-gray-200 rounded"></div>
                    <div className="space-y-3">
                        <div className="h-20 bg-gray-200 rounded"></div>
                        <div className="h-20 bg-gray-200 rounded"></div>
                        <div className="h-20 bg-gray-200 rounded"></div>
                    </div>
                </div>
            </div>
        );
    }

    // Not Logged In Error
    if (error === 'not_logged_in') {
        return (
            <div className="p-8 text-center">
                <div className="bg-yellow-50 border-l-4 border-yellow-500 p-6 rounded-lg max-w-md mx-auto">
                    <p className="text-yellow-800 font-semibold mb-2">⚠️ Not Logged In</p>
                    <p className="text-yellow-700 mb-4">Please log in to view your history.</p>
                    <Link to="/login/driver" className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg inline-block font-medium">
                        Go to Login
                    </Link>
                </div>
            </div>
        );
    }

    // Backend Error State
    if (error === 'backend_error') {
        return (
            <div className="p-8">
                <header className="px-4 mb-6">
                    <h1 className="text-2xl font-bold text-gray-900">Your Fairness History</h1>
                    <p className="text-gray-500 text-sm mt-1">Past 7 Days Performance</p>
                </header>
                <div className="bg-red-50 border-l-4 border-red-500 p-6 rounded-lg mx-4">
                    <div className="flex items-center mb-2">
                        <AlertCircle className="w-5 h-5 text-red-600 mr-2" />
                        <p className="text-red-800 font-semibold">Unable to Load History</p>
                    </div>
                    <p className="text-red-700 text-sm">There was a problem loading your fairness history. Please try refreshing the page.</p>
                    <button
                        onClick={() => window.location.reload()}
                        className="mt-4 bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg text-sm font-medium"
                    >
                        Refresh Page
                    </button>
                </div>
            </div>
        );
    }

    // Empty State (No History Yet)
    if (history.length === 0) {
        return (
            <div className="p-8">
                <header className="px-4 mb-6">
                    <h1 className="text-2xl font-bold text-gray-900">Your Fairness History</h1>
                    <p className="text-gray-500 text-sm mt-1">Past 7 Days Performance</p>
                </header>
                <Card className="mx-4">
                    <div className="text-center py-12">
                        <History className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                        <h3 className="text-lg font-semibold text-gray-700 mb-2">No History Available Yet</h3>
                        <p className="text-gray-500 text-sm max-w-md mx-auto">
                            Your route history will appear here after you receive route assignments.
                            Complete your first route to start building your fairness history!
                        </p>
                        <Link
                            to="/driver"
                            className="inline-block mt-6 bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium"
                        >
                            Go to Dashboard
                        </Link>
                    </div>
                </Card>
            </div>
        );
    }

    // Process data for Chart (when we have data)
    // API returns newest first (limit 7). Chart needs oldest first for Left->Right.
    const sortedHistory = [...history].reverse();

    const chartData = {
        labels: sortedHistory.map(h => {
            const d = new Date(h.date);
            return d.toLocaleDateString('en-US', { weekday: 'short' });
        }),
        datasets: [
            {
                label: 'Fairness Balance',
                data: sortedHistory.map(h => h.balance_snapshot),
                borderColor: 'rgb(37, 99, 235)', // Blue 600
                backgroundColor: 'rgba(37, 99, 235, 0.1)',
                tension: 0.4,
                fill: true,
                pointRadius: 4,
                pointBackgroundColor: 'white',
                pointBorderColor: 'rgb(37, 99, 235)',
                pointBorderWidth: 2,
            }
        ]
    };

    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { display: false },
            tooltip: {
                mode: 'index',
                intersect: false,
                backgroundColor: 'rgba(0, 0, 0, 0.8)',
                padding: 12,
                titleColor: '#fff',
                bodyColor: '#fff',
                borderColor: 'rgba(37, 99, 235, 0.5)',
                borderWidth: 1,
            }
        },
        scales: {
            y: {
                grid: { color: '#f3f4f6' },
                ticks: { font: { size: 11 } }
            },
            x: {
                grid: { display: false },
                ticks: { font: { size: 11 } }
            }
        },
        interaction: {
            mode: 'nearest',
            axis: 'x',
            intersect: false
        }
    };

    const currentBalance = sortedHistory[sortedHistory.length - 1]?.balance_snapshot || 0;

    return (
        <div className="p-8">
            <header className="px-4 mb-6">
                <h1 className="text-2xl font-bold text-gray-900">Your Fairness History</h1>
                <p className="text-gray-500 text-sm mt-1">Past 7 Days Performance</p>
            </header>

            {/* Chart Card */}
            <Card className="mb-6 mx-4">
                <div className="flex justify-between items-end mb-4">
                    <div>
                        <h3 className="font-bold text-gray-700">Balance Trend</h3>
                        <p className="text-xs text-gray-500 mt-1">Last {history.length} days</p>
                    </div>
                    <div className={`text-2xl font-bold ${currentBalance >= 0 ? 'text-green-600' : 'text-red-500'}`}>
                        {currentBalance > 0 ? '+' : ''}{Math.round(currentBalance)}
                        <span className="text-xs text-gray-400 font-normal ml-1">Current</span>
                    </div>
                </div>
                <div className="h-56 w-full">
                    <Line data={chartData} options={chartOptions} />
                </div>
            </Card>

            {/* List of Days */}
            <h3 className="font-bold text-gray-800 mb-3 px-4">Daily Breakdown</h3>
            <div className="space-y-3 px-4 pb-8">
                {history.map((day) => {
                    const d = new Date(day.date);
                    const dayName = d.toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' });
                    const isPositive = day.credits_earned >= 0;

                    return (
                        <div key={day.date} className="bg-white p-4 rounded-xl shadow-sm border border-gray-100">
                            <div className="flex justify-between items-center">
                                <div>
                                    <div className="font-bold text-gray-800">{dayName}</div>
                                    <div className="text-sm text-gray-600 mt-1">
                                        Effort Score: <span className="font-semibold">{formatEffort(day.daily_effort)}</span>
                                    </div>
                                </div>
                                <div className="text-right">
                                    <div className={`font-bold text-lg ${isPositive ? 'text-green-600' : 'text-red-500'}`}>
                                        {withSign(formatCredits(day.credits_earned))}
                                    </div>
                                    <div className="text-xs text-gray-400">
                                        {isPositive ? 'Credits Earned' : 'Credits Debited'}
                                    </div>
                                </div>
                            </div>
                            <div className="mt-3 pt-3 border-t border-gray-100">
                                <div className="flex justify-between text-xs text-gray-500">
                                    <span>Balance</span>
                                    <span className={`font-semibold ${day.balance_snapshot >= 0 ? 'text-green-600' : 'text-red-500'}`}>
                                        {withSign(formatBalance(day.balance_snapshot))}
                                    </span>
                                </div>
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
