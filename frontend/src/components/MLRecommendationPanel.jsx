import React, { useState } from 'react';
import { Sparkles, Brain, AlertCircle, CheckCircle, XCircle } from 'lucide-react';

/**
 * ML Route Recommendation Component
 * 
 * Displays 3-layer decision support:
 * Layer 1: ML Recommendation (suggestion)
 * Layer 2: FairFlow Decision (validation with override capability)
 * Layer 3: Admin Control (final decision)
 */
export default function MLRecommendationPanel({ driverId, drivers }) {
    const [routeFeatures, setRouteFeatures] = useState({
        apartments_count: 10,
        stairs_present: false,
        heavy_boxes_count: 5,
        traffic_level: 'Normal',
        weather_severity: 'Clear'
    });

    const [recommendation, setRecommendation] = useState(null);
    const [loading, setLoading] = useState(false);

    const getRecommendation = async () => {
        setLoading(true);
        try {
            const response = await fetch('http://localhost:8000/admin/recommend_route', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    route_features: routeFeatures,
                    driver_id: driverId
                })
            });
            const data = await response.json();
            setRecommendation(data);
        } catch (error) {
            console.error('Error getting recommendation:', error);
        }
        setLoading(false);
    };

    const getDifficultyColor = (difficulty) => {
        if (difficulty === 'Easy') return 'bg-green-100 text-green-800 border-green-200';
        if (difficulty === 'Medium') return 'bg-yellow-100 text-yellow-800 border-yellow-200';
        if (difficulty === 'Hard') return 'bg-red-100 text-red-800 border-red-200';
        return 'bg-gray-100 text-gray-800 border-gray-200';
    };

    const getActionIcon = (action) => {
        if (action === 'approved') return <CheckCircle className="text-green-600" size={20} />;
        if (action === 'adjusted') return <AlertCircle className="text-yellow-600" size={20} />;
        if (action === 'blocked') return <XCircle className="text-red-600" size={20} />;
        return null;
    };

    return (
        <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
            <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
                <Sparkles className="text-purple-600" />
                ML Route Recommendation Assistant
            </h2>

            <p className="text-gray-600 mb-6">
                Get AI-powered route difficulty suggestions validated by FairFlow's working-hours fairness system.
            </p>

            {/* Route Features Input */}
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6 p-4 bg-gray-50 rounded-lg">
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Apartments</label>
                    <input
                        type="number"
                        value={routeFeatures.apartments_count}
                        onChange={(e) => setRouteFeatures({ ...routeFeatures, apartments_count: parseInt(e.target.value) })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Heavy Boxes</label>
                    <input
                        type="number"
                        value={routeFeatures.heavy_boxes_count}
                        onChange={(e) => setRouteFeatures({ ...routeFeatures, heavy_boxes_count: parseInt(e.target.value) })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Traffic</label>
                    <select
                        value={routeFeatures.traffic_level}
                        onChange={(e) => setRouteFeatures({ ...routeFeatures, traffic_level: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    >
                        <option>Low</option>
                        <option>Normal</option>
                        <option>High</option>
                    </select>
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Weather</label>
                    <select
                        value={routeFeatures.weather_severity}
                        onChange={(e) => setRouteFeatures({ ...routeFeatures, weather_severity: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    >
                        <option>Clear</option>
                        <option>Rain</option>
                        <option>Snow</option>
                    </select>
                </div>

                <div className="flex items-end">
                    <label className="flex items-center gap-2 cursor-pointer">
                        <input
                            type="checkbox"
                            checked={routeFeatures.stairs_present}
                            onChange={(e) => setRouteFeatures({ ...routeFeatures, stairs_present: e.target.checked })}
                            className="w-4 h-4"
                        />
                        <span className="text-sm font-medium text-gray-700">Stairs Present</span>
                    </label>
                </div>

                <div className="flex items-end">
                    <select
                        value={driverId || ''}
                        onChange={(e) => onDriverChange(parseInt(e.target.value))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    >
                        <option value="">Select Driver</option>
                        {drivers.map(d => (
                            <option key={d.id} value={d.id}>{d.name}</option>
                        ))}
                    </select>
                </div>
            </div>

            <button
                onClick={getRecommendation}
                disabled={loading || !driverId}
                className="w-full bg-gradient-to-r from-purple-600 to-indigo-600 text-white py-3 rounded-lg font-semibold hover:from-purple-700 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
                {loading ? 'Getting Recommendation...' : 'Get ML Recommendation'}
            </button>

            {/* Results Display */}
            {recommendation && (
                <div className="mt-6 space-y-4">
                    {/* ML Recommendation */}
                    <div className="border-2 border-purple-200 rounded-lg p-4 bg-purple-50">
                        <div className="flex items-center gap-2 mb-3">
                            <Sparkles className="text-purple-600" size={24} />
                            <h3 className="text-lg font-bold text-purple-900">🤖 ML Recommendation</h3>
                        </div>

                        <div className="flex items-center gap-3 mb-2">
                            <span className={`px-4 py-2 rounded-lg border-2 font-bold ${getDifficultyColor(recommendation.ml_recommendation.suggested_difficulty)}`}>
                                {recommendation.ml_recommendation.suggested_difficulty}
                            </span>
                            <span className="text-sm text-purple-700 font-semibold">
                                Confidence: {(recommendation.ml_recommendation.confidence * 100).toFixed(0)}%
                            </span>
                        </div>

                        <p className="text-sm text-gray-700 mt-2">
                            <strong>Reasoning:</strong> {recommendation.ml_recommendation.reason}
                        </p>

                        <div className="mt-2 text-xs text-gray-600 flex gap-4">
                            <span>Route Score: {recommendation.ml_recommendation.route_score}</span>
                            <span>Driver Fatigue Factor: {recommendation.ml_recommendation.driver_fatigue_factor.toFixed(2)}</span>
                        </div>
                    </div>

                    {/* FairFlow Decision */}
                    <div className={`border-2 rounded-lg p-4 ${recommendation.fairflow_decision.action === 'approved' ? 'border-green-200 bg-green-50' :
                        recommendation.fairflow_decision.action === 'adjusted' ? 'border-yellow-200 bg-yellow-50' :
                            'border-red-200 bg-red-50'
                        }`}>
                        <div className="flex items-center gap-2 mb-3">
                            <Brain className={`${recommendation.fairflow_decision.action === 'approved' ? 'text-green-600' :
                                recommendation.fairflow_decision.action === 'adjusted' ? 'text-yellow-600' :
                                    'text-red-600'
                                }`} size={24} />
                            <h3 className="text-lg font-bold">🧠 FairFlow Decision</h3>
                            {getActionIcon(recommendation.fairflow_decision.action)}
                        </div>

                        <div className="mb-2">
                            <span className="text-sm font-semibold uppercase tracking-wide">
                                {recommendation.fairflow_decision.action}
                            </span>
                        </div>

                        <div className={`px-4 py-2 rounded-lg border-2 font-bold inline-block ${getDifficultyColor(recommendation.fairflow_decision.approved_difficulty)}`}>
                            {recommendation.fairflow_decision.approved_difficulty}
                        </div>

                        {recommendation.fairflow_decision.fairness_override && (
                            <div className="mt-2 p-2 bg-white rounded border-l-4 border-yellow-500">
                                <p className="text-sm font-semibold text-yellow-800">
                                    ⚠️ Fairness Override: {recommendation.fairflow_decision.override_reason}
                                </p>
                            </div>
                        )}

                        <p className="text-sm text-gray-700 mt-3">
                            <strong>Reasoning:</strong> {recommendation.fairflow_decision.reason}
                        </p>
                    </div>

                    {/* Driver Context */}
                    <div className="bg-gray-50 rounded-lg p-4 text-sm">
                        <h4 className="font-semibold mb-2">Driver Context:</h4>
                        <div className="grid grid-cols-2 gap-2 text-gray-700">
                            <div><strong>Name:</strong> {recommendation.driver_context.name}</div>
                            <div><strong>Status:</strong> {recommendation.driver_context.status}</div>
                            <div><strong>Effort per Hour (3-day avg):</strong> {recommendation.driver_context.normalized_effort_per_hour}</div>
                            <div><strong>Fairness Balance:</strong> {recommendation.driver_context.fairness_balance}</div>
                            <div><strong>Working Hours Today:</strong> {recommendation.driver_context.working_hours_today}</div>
                        </div>
                    </div>

                    {/* Admin Final Control */}
                    <div className="border-t-2 border-gray-200 pt-4">
                        <p className="text-sm text-gray-600 mb-3 italic">
                            ✅ {recommendation.final_note}
                        </p>
                        <div className="flex gap-3">
                            <button className="flex-1 bg-green-600 text-white py-2 rounded-lg hover:bg-green-700">
                                Assign as Recommended
                            </button>
                            <button className="flex-1 bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700">
                                Override Decision
                            </button>
                            <button className="flex-1 bg-purple-600 text-white py-2 rounded-lg hover:bg-purple-700">
                                Use Auto-Assign
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
