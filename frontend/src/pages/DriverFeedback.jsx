import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '../components/Card';
import { CheckCircle, AlertCircle } from 'lucide-react';

export default function DriverFeedback() {
    const navigate = useNavigate();
    const [difficulty, setDifficulty] = useState(null);
    const [comment, setComment] = useState('');
    const [loading, setLoading] = useState(false);
    const [routeId, setRouteId] = useState(null);
    const [submitting, setSubmitting] = useState(false);

    useEffect(() => {
        // Fetch dashboard data to get the current route ID
        const driverId = localStorage.getItem('driver_id');

        if (!driverId) {
            setLoading(false);
            return;
        }

        setLoading(true);
        fetch(`http://localhost:8000/driver/${driverId}/dashboard`)
            .then(res => res.json())
            .then(data => {
                if (data.route) {
                    setRouteId(data.route.id);
                }
                setLoading(false);
            })
            .catch(err => {
                console.error("Failed to fetch route info", err);
                setLoading(false);
            });
    }, []);

    const handleSubmit = async () => {
        if (!routeId || !difficulty) return;

        setSubmitting(true);
        try {
            const res = await fetch('http://localhost:8000/driver/feedback', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    route_id: routeId,
                    difficulty: difficulty,
                    comment: comment
                })
            });

            if (res.ok) {
                // Success - show alert and navigate back
                alert('✅ Feedback submitted successfully!');
                navigate('/driver');
            } else {
                alert("Failed to submit feedback");
            }
        } catch (err) {
            console.error(err);
            alert("Error submitting feedback");
        } finally {
            setSubmitting(false);
        }
    };

    if (loading) return <div className="p-8 text-center text-gray-500">Loading...</div>;

    if (!routeId) return (
        <div className="layout p-6 flex flex-col items-center justify-center h-[80vh]">
            <div className="bg-gray-100 p-6 rounded-full mb-4">
                <CheckCircle size={48} className="text-gray-400" />
            </div>
            <h2 className="text-xl font-bold text-gray-700">No Active Route</h2>
            <p className="text-gray-500 mt-2 text-center">You don't have a route assigned for today yet to give feedback on.</p>
        </div>
    );

    return (
        <div className="layout pt-8">
            <h1 className="text-2xl font-bold text-gray-900 mb-6 px-4">Daily Feedback</h1>

            <Card className="h-full flex flex-col justify-between min-h-[60vh]">
                <div>
                    <h2 className="text-xl font-bold text-gray-800 text-center mb-8">How was today's route?</h2>

                    <div className="flex flex-col gap-4 mb-8">
                        <button
                            onClick={() => setDifficulty('Easy')}
                            className={`p-6 rounded-2xl border-2 transition-all flex items-center justify-between group ${difficulty === 'Easy'
                                ? 'border-green-500 bg-green-50 text-green-700'
                                : 'border-gray-100 hover:border-green-200 hover:bg-green-50/50 text-gray-600'
                                }`}
                        >
                            <span className="text-lg font-bold">🟢 Easy</span>
                            {difficulty === 'Easy' && <CheckCircle size={24} />}
                        </button>

                        <button
                            onClick={() => setDifficulty('Normal')}
                            className={`p-6 rounded-2xl border-2 transition-all flex items-center justify-between group ${difficulty === 'Normal'
                                ? 'border-yellow-500 bg-yellow-50 text-yellow-700'
                                : 'border-gray-100 hover:border-yellow-200 hover:bg-yellow-50/50 text-gray-600'
                                }`}
                        >
                            <span className="text-lg font-bold">🟡 Okay</span>
                            {difficulty === 'Normal' && <CheckCircle size={24} />}
                        </button>

                        <button
                            onClick={() => setDifficulty('Hard')}
                            className={`p-6 rounded-2xl border-2 transition-all flex items-center justify-between group ${difficulty === 'Hard'
                                ? 'border-red-500 bg-red-50 text-red-700'
                                : 'border-gray-100 hover:border-red-200 hover:bg-red-50/50 text-gray-600'
                                }`}
                        >
                            <span className="text-lg font-bold">🔴 Tough</span>
                            {difficulty === 'Hard' && <CheckCircle size={24} />}
                        </button>
                    </div>

                    <div className="mb-6">
                        <textarea
                            className="w-full p-4 rounded-xl bg-gray-50 border border-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                            rows="3"
                            placeholder="Optional comments... (e.g. Traffic was terrible)"
                            value={comment}
                            onChange={(e) => setComment(e.target.value)}
                            maxLength={200}
                        ></textarea>
                        <div className="text-right text-xs text-gray-400 mt-1">
                            {comment.length}/200
                        </div>
                    </div>
                </div>

                <button
                    disabled={!difficulty || submitting}
                    onClick={handleSubmit}
                    className={`w-full py-4 rounded-xl font-bold text-lg text-white shadow-lg transition-all transform active:scale-95 ${!difficulty || submitting
                        ? 'bg-gray-300 cursor-not-allowed shadow-none'
                        : 'bg-blue-600 hover:bg-blue-700 hover:shadow-xl'
                        }`}
                >
                    {submitting ? 'Submitting...' : 'Submit Feedback'}
                </button>
            </Card>
        </div>
    );
}
