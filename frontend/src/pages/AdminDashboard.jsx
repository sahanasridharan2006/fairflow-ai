import React, { useState, useEffect } from 'react';
import { Card } from '../components/Card';
import { Badge } from '../components/Badge';
import FairnessDriftModal from '../components/FairnessDriftModal';
import MLSuggestionCell from '../components/MLSuggestionCell';
import { useNavigate } from 'react-router-dom';
import { CheckCircle, Info, ShieldAlert, Users, TrendingUp, Home } from 'lucide-react';

export default function AdminDashboard() {
    const navigate = useNavigate();
    const [drivers, setDrivers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState('');
    const [driftData, setDriftData] = useState(null);
    const [showDriftModal, setShowDriftModal] = useState(false);
    const [mlSuggestions, setMlSuggestions] = useState({});
    const [openPopupDriverId, setOpenPopupDriverId] = useState(null);
    const [routes, setRoutes] = useState([]); // Mock Addresses
    const [selectedRouteId, setSelectedRouteId] = useState(null); // Step 3: Route Selection
    const [mlLoading, setMlLoading] = useState(false);
    const [interventionError, setInterventionError] = useState(null); // NEW: Specifically for manual assignment blocks

    const fetchDrivers = () => {
        fetch('http://localhost:8000/admin/dashboard')
            .then(res => res.ok ? res.json() : [])
            .then(data => setDrivers(Array.isArray(data) ? data : []))
            .catch(() => setDrivers([]))
            .finally(() => setLoading(false));
    };

    const fetchDriftStatus = () => {
        fetch('http://localhost:8000/admin/fairness_drift')
            .then(res => res.ok ? res.json() : null)
            .then(data => setDriftData(data))
            .catch(() => setDriftData(null));
    };

    const fetchRoutes = () => {
        fetch('http://localhost:8000/admin/routes')
            .then(res => res.ok ? res.json() : [])
            .then(data => {
                setRoutes(Array.isArray(data) ? data : []);
                if (Array.isArray(data) && data.length > 0) setSelectedRouteId(data[0].address_id);
            })
            .catch(() => setRoutes([]));
    };

    // NEW: Fetch ML suggestions for selected route across all drivers
    // NEW: Fetch all ML suggestions in one batch for the selected route
    const fetchMLSuggestions = async (route) => {
        if (!route || !route.address_id) return;

        setMlLoading(true);
        try {
            const response = await fetch('http://localhost:8000/admin/recommend_routes_batch', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    route_features: route
                })
            });
            if (response.ok) {
                const data = await response.json();
                // Data is an array [{driver_id, ml_recommendation, fairflow_decision, preference_rank, preference_label}, ...]
                const suggestionsMap = {};
                data.forEach(item => {
                    suggestionsMap[item.driver_id] = item;
                });
                setMlSuggestions(suggestionsMap);
            } else {
                console.error('Batch ML fetch failed:', response.status, response.statusText);
                setMlSuggestions({});
            }
        } catch (err) {
            console.error('Batch ML fetch failed:', err);
            setMlSuggestions({});
        } finally {
            setMlLoading(false);
        }
    };

    useEffect(() => {
        fetchDrivers();
        fetchDriftStatus();
        fetchRoutes();

        const interval = setInterval(() => {
            fetchDrivers();
            fetchDriftStatus();
        }, 60000);
        return () => clearInterval(interval);
    }, []);

    // Fetch ML Suggestions ONLY when a route is actively selected and valid
    const selectedRoute = (Array.isArray(routes) ? routes : []).find(r => r && r.address_id === selectedRouteId);
    useEffect(() => {
        if (selectedRoute && selectedRouteId && (drivers || []).length > 0) {
            fetchMLSuggestions(selectedRoute);
        } else {
            setMlSuggestions({});
        }
    }, [selectedRouteId, drivers.length, selectedRoute]); // Re-run if route changes or drivers list updates

    // NEW: Close popup when clicking outside
    useEffect(() => {
        const handleClickOutside = (event) => {
            // Don't close if clicking on a badge or inside a popup
            if (event.target.closest('.ml-popup-container') ||
                event.target.closest('.ml-badge-button')) {
                return;
            }
            setOpenPopupDriverId(null);
        };

        if (openPopupDriverId !== null) {
            document.addEventListener('click', handleClickOutside);
            return () => document.removeEventListener('click', handleClickOutside);
        }
    }, [openPopupDriverId]);

    const toggleStatus = (driverId, newStatus) => {
        fetch(`http://localhost:8000/admin/toggle_status?driver_id=${driverId}&status=${newStatus}`, {
            method: 'POST'
        })
            .then(res => {
                if (res.ok) fetchDrivers();
                else alert("Failed to update status");
            });
    };

    const handleUnassign = async (driverId) => {
        if (!confirm('Are you sure you want to unassign this route?')) return;

        try {
            const response = await fetch(`http://localhost:8000/admin/unassign_route?driver_id=${driverId}`, {
                method: 'POST'
            });

            if (response.ok) {
                // Success
                fetchDrivers(); // Refresh list to show unassigned
                fetchDriftStatus();
                fetchRoutes(); // Refresh available routes list
            } else {
                const error = await response.json();
                alert(`⛔ ${error.detail}`);
            }
        } catch (err) {
            console.error('Unassign error:', err);
            alert('Failed to unassign route.');
        }
    };

    const assignRouteWithSelected = async (driverId, difficulty) => {
        const route = routes.find(r => r.address_id === selectedRouteId);
        if (!route) return;

        // Map mock route to backend-expected route_factors
        const routeFactors = {
            apartments: route.area_type === 'Apartment' ? route.floors : 0,
            stairs: route.stairs_present,
            heavy_boxes: route.heavy_packages_count,
            traffic: route.traffic_level === 'High',
            rain: route.weather_severity === 'Rain' || route.weather_severity === 'Snow'
        };

        try {
            const response = await fetch('http://localhost:8000/admin/assign_route', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    driver_id: driverId,
                    difficulty: difficulty,
                    address: route.address,
                    route_factors: routeFactors
                })
            });

            if (response.ok) {
                const result = await response.json();
                alert(`✅ Route assigned!\nEffort: ${result.effort_score}\nCredits: ${result.credits}\nNew Balance: ${result.new_balance}`);
                setInterventionError(null); // Clear popup on success
                fetchDrivers();
                fetchRoutes(); // Refresh available routes list
                fetchDriftStatus(); // NEW: Refresh monitor immediately
            } else {
                const error = await response.json();

                // NEW: Handle AI Intervention by showing it in the floating box instead of alert()
                if (error.detail && error.detail.startsWith('AI Intervention')) {
                    setInterventionError(error.detail);
                    // Scroll to top to ensure user sees the monitor/alert
                    window.scrollTo({ top: 0, behavior: 'smooth' });
                } else {
                    // Standard error alert
                    alert(`⛔ ${error.detail}`);
                }
            }
        } catch (err) {
            alert('Error assigning route');
        }
    };

    const handleAssign = (driverId, difficulty) => {
        setInterventionError(null); // Clear previous error
        assignRouteWithSelected(driverId, difficulty);
    };

    const autoAssign = async () => {
        setInterventionError(null); // Clear error on auto-assign attempt
        if (!selectedRoute) {
            alert('📍 Please select a route first!');
            return;
        }

        try {
            const response = await fetch('http://localhost:8000/admin/auto_assign', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    route_features: selectedRoute
                })
            });

            if (response.ok) {
                const result = await response.json();
                alert(`🤖 AI Auto-Assign Successful!\n\nDriver: ${result.driver_assigned}\nReason: ${result.reason}\nEffort: ${result.effort_score}`);
                fetchDrivers();
                fetchDriftStatus();
                fetchRoutes(); // Refresh available routes list
            } else {
                const error = await response.json();
                alert(`⛔ ${error.detail}`);
            }
        } catch (err) {
            alert('Error during auto-assignment');
        }
    };



    // Super-defensive Filter
    const filteredDrivers = (Array.isArray(drivers) ? drivers : []).filter(driver => {
        if (!driver || typeof driver.name !== 'string') return false;
        return driver.name.toLowerCase().includes((searchQuery || '').toLowerCase());
    });

    if (loading) return (
        <div className="flex items-center justify-center min-h-[400px]">
            <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
                <p className="text-lg text-gray-500 font-medium">Loading Logistics Data...</p>
            </div>
        </div>
    );

    return (
        <div className="layout">
            {/* Top-Floating AI Intervention Alert (Manual Error Only) */}
            {interventionError && (
                <div className="fixed top-6 left-1/2 -translate-x-1/2 z-[100] w-full max-w-xl px-4 pointer-events-none">
                    <div className="bg-red-400 text-white p-5 rounded-2xl border-2 border-red-300 flex items-start gap-4 pointer-events-auto shadow-md">
                        <div className="text-3xl mt-1">⚠️</div>
                        <div className="flex-1">
                            <h4 className="font-extrabold text-xl mb-1 tracking-tight text-white">AI Intervention Required</h4>
                            <p className="font-medium text-sm text-red-50 leading-snug">
                                {interventionError}
                            </p>
                            <div className="mt-3 flex gap-2">
                                <button
                                    onClick={() => setShowDriftModal(true)}
                                    className="bg-black/10 hover:bg-black/20 text-[10px] font-bold uppercase tracking-wider px-3 py-1 rounded-md transition-colors"
                                >
                                    Review Rules
                                </button>
                                <button
                                    onClick={() => setInterventionError(null)}
                                    className="bg-black/20 hover:bg-black/30 text-[10px] font-bold uppercase tracking-wider px-3 py-1 rounded-md transition-colors"
                                >
                                    Dismiss
                                </button>
                            </div>
                        </div>
                        <div className="text-xs font-bold bg-white/20 px-2 py-0.5 rounded text-white">INTERVENTION</div>
                    </div>
                </div>
            )}

            <div className="flex justify-between items-center mb-6">
                <div className="flex items-center gap-4">
                    <button
                        onClick={() => navigate('/')}
                        className="p-2.5 bg-white border border-gray-200 rounded-xl text-gray-400 hover:text-blue-600 hover:border-blue-200 hover:bg-blue-50 transition-all shadow-sm group"
                        title="Back to Portal Selection"
                    >
                        <Home size={22} className="group-hover:scale-110 transition-transform" />
                    </button>
                    <div className="flex items-center gap-3">
                        <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                            <span className="text-white font-black text-lg">F</span>
                        </div>
                        <h1 className="text-3xl font-bold text-gray-900">FairFlow Admin</h1>
                    </div>
                </div>
                <span className="text-sm bg-gray-100 text-gray-500 px-3 py-1 rounded-full font-medium">{new Date().toLocaleDateString()}</span>
            </div>

            {/* Top Section: Route Selection & AI Monitors */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 mb-8 items-start">
                {/* Step 1: Route Selection Card */}
                <div className="lg:col-span-4">
                    <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
                        <span>📍</span> Step 1: Select Route
                    </h2>
                    <Card className="p-0 overflow-hidden border-indigo-100 shadow-lg bg-white">
                        <div className="bg-indigo-600 p-4 text-white">
                            <label className="block text-xs font-bold uppercase tracking-wider mb-2 opacity-80">Available Addresses</label>
                            <select
                                value={selectedRouteId || ''}
                                onChange={(e) => setSelectedRouteId(e.target.value)}
                                className="w-full bg-indigo-700 text-white rounded-lg px-3 py-2 border border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-300 font-medium"
                            >
                                {(routes || []).length === 0 && <option value="">No Routes Available</option>}
                                {(routes || []).map(r => r && (
                                    <option key={r.address_id} value={r.address_id}>
                                        {r.address.length > 50 ? r.address.substring(0, 47) + '...' : r.address}
                                    </option>
                                ))}
                            </select>
                        </div>
                        <div className="p-4">
                            {!selectedRoute ? (
                                <div className="text-sm text-gray-400 italic">Select an address above...</div>
                            ) : (
                                <div className="space-y-3">
                                    <div className="flex flex-col text-sm">
                                        <span className="text-gray-500 mb-1">Full Address</span>
                                        <span className="font-semibold text-indigo-900 leading-tight">{selectedRoute.address}</span>
                                    </div>
                                    <div className="flex justify-between items-center text-sm pt-2">
                                        <span className="text-gray-500">Area Type</span>
                                        <span className="font-semibold">{selectedRoute.area_type}</span>
                                    </div>
                                    <div className="flex justify-between items-center text-sm">
                                        <span className="text-gray-500">Heavy Packages</span>
                                        <span className="font-semibold">{selectedRoute.heavy_packages_count}</span>
                                    </div>
                                    <div className="flex justify-between items-center text-sm">
                                        <span className="text-gray-500">Traffic Level</span>
                                        <Badge type={selectedRoute.traffic_level === 'High' ? 'danger' : 'success'}>
                                            {selectedRoute.traffic_level}
                                        </Badge>
                                    </div>
                                    <div className="pt-3 border-t border-gray-100 flex justify-between items-center">
                                        <span className="text-xs font-bold text-gray-400 uppercase">Pre-Classified</span>
                                        <div className="text-right">
                                            <div className={`text-sm font-bold ${selectedRoute.difficulty_label === 'Hard' ? 'text-red-600' :
                                                selectedRoute.difficulty_label === 'Medium' ? 'text-yellow-600' : 'text-green-600'
                                                }`}>
                                                {selectedRoute.difficulty_label} Logic
                                            </div>
                                            <div className="text-[10px] text-gray-500 font-medium">Effort Score: {selectedRoute.computed_effort}</div>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>
                    </Card>
                </div>

                {/* AI Center: Guidance + Monitor stacked */}
                <div className="lg:col-span-8 flex flex-col gap-4 pt-11">
                    {/* AI Assignment Guidance */}
                    <div className="bg-blue-50 border border-blue-100 rounded-2xl p-6 text-blue-800 shadow-sm">
                        <h3 className="font-bold flex items-center gap-2 mb-2">
                            <span>🤖</span> AI Assignment Guidance
                        </h3>
                        <p className="text-sm leading-relaxed">
                            {selectedRouteId ? (
                                <>
                                    You have selected <span className="font-semibold">{selectedRouteId}</span>.
                                    The AI has re-evaluated all drivers. Look for the <span className="bg-indigo-100 text-indigo-700 px-1.5 py-0.5 rounded text-[10px] font-bold">ML</span> badge
                                    and highlighted buttons below for optimized matches.
                                </>
                            ) : (
                                "Select a route on the left to activate AI dispatch guidance."
                            )}
                        </p>
                    </div>

                    {/* AI Fairness Monitor */}
                    <Card className={`border-l-4 shadow-sm p-6 transition-all duration-300 ${!driftData || driftData.severity === 'NONE'
                        ? 'border-l-indigo-500 bg-gradient-to-r from-indigo-50 to-purple-50'
                        : driftData.severity === 'HIGH'
                            ? 'border-l-red-600 bg-red-100'
                            : 'border-l-orange-500 bg-orange-50'
                        }`}>
                        <div className="flex items-center justify-between gap-4">
                            <div className="flex items-center gap-4">
                                <div className="text-3xl animate-bounce">
                                    {!driftData ? '🔄' : (
                                        driftData.severity === 'NONE' ? '🟢' :
                                            driftData.severity === 'LOW' ? '🟡' :
                                                driftData.severity === 'MEDIUM' ? '🟠' : '🔴'
                                    )}
                                </div>
                                <div>
                                    <p className="text-[10px] font-bold uppercase tracking-wider text-indigo-400 mb-1">AI Fairness Monitor</p>
                                    {!driftData ? (
                                        <p className="text-sm text-gray-500 animate-pulse">Analysing system drift...</p>
                                    ) : (
                                        <>
                                            <p className={`font-bold text-lg leading-tight ${driftData.severity === 'NONE' ? 'text-green-700' :
                                                driftData.severity === 'LOW' ? 'text-yellow-700' :
                                                    driftData.severity === 'MEDIUM' ? 'text-orange-700' : 'text-red-700'
                                                }`}>
                                                {driftData.severity === 'NONE' && 'Fair Distribution'}
                                                {driftData.severity === 'LOW' && 'Minor Drift'}
                                                {driftData.severity === 'MEDIUM' && 'Drift Detected'}
                                                {driftData.severity === 'HIGH' && 'Intervention Active'}
                                            </p>
                                            <p className="text-xs text-gray-600 mt-1">
                                                {driftData.severity === 'NONE' && 'Workload is balanced across the team.'}
                                                {driftData.severity === 'LOW' && 'Slight variance detected. Monitoring patterns.'}
                                                {driftData.severity === 'MEDIUM' && 'Imbalance detected. AI is rebalancing.'}
                                                {driftData.severity === 'HIGH' && 'Significant unfairness. Protecting drivers.'}
                                            </p>
                                        </>
                                    )}
                                </div>
                            </div>
                            {driftData && (
                                <button
                                    onClick={() => setShowDriftModal(true)}
                                    className="text-xs font-bold text-indigo-600 bg-white px-3 py-2 rounded-lg border border-indigo-200 hover:bg-indigo-50 transition-colors shadow-sm"
                                >
                                    Details
                                </button>
                            )}
                        </div>
                    </Card>
                </div>
            </div>

            {/* Driver Assignments Table */}
            <div>
                <div className="flex justify-between items-center mb-6 pt-4 border-t border-gray-100">
                    <h2 className="text-2xl font-bold text-gray-900">Driver Assignments</h2>
                    <div className="flex gap-3">
                        <button
                            onClick={autoAssign}
                            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-bold text-sm transition-all shadow-md active:scale-95 flex items-center gap-2"
                        >
                            🤖 Auto-Assign
                        </button>
                        <button
                            onClick={() => { fetchDrivers(); fetchDriftStatus(); fetchRoutes(); }}
                            className="bg-gray-100 hover:bg-gray-200 text-gray-600 p-2 rounded-lg transition-all"
                            title="Refresh Data"
                        >
                            🔄
                        </button>
                        <input
                            type="text"
                            placeholder="Search drivers..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="border border-gray-200 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-sm"
                        />
                    </div>
                </div>

                <div className="bg-white rounded-2xl shadow-soft border border-gray-100 overflow-x-auto mb-12">
                    <table className="w-full">
                        <thead>
                            <tr className="bg-gray-50 border-b border-gray-100">
                                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Driver Name</th>
                                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Status</th>
                                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider text-indigo-600">Assigned Route</th>
                                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">ML Suggest</th>
                                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Effort</th>
                                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Credits</th>
                                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider text-center">Effort Balance</th>
                                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Readiness</th>
                                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider min-w-[280px]">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-100 text-sm">
                            {filteredDrivers.map(driver => (
                                <tr key={driver.id} className="hover:bg-gray-50/50 transition-colors">
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="font-bold text-gray-900">{driver.name}</div>
                                        <div className="text-[10px] text-gray-400 font-medium uppercase tracking-tight">ID: #{driver.id + 8290}</div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <select
                                            className={`text-[10px] font-bold py-1 px-2 rounded border focus:outline-none ${driver.status === 'ACTIVE' ? 'bg-green-50 text-green-700 border-green-200' :
                                                driver.status === 'SICK' ? 'bg-orange-50 text-orange-700 border-orange-200' :
                                                    driver.status === 'HALF_SHIFT' ? 'bg-blue-50 text-blue-700 border-blue-200' :
                                                        'bg-gray-50 text-gray-500 border-gray-200'
                                                }`}
                                            value={driver.status}
                                            onChange={(e) => toggleStatus(driver.id, e.target.value)}
                                        >
                                            <option value="ACTIVE">ACTIVE</option>
                                            <option value="HALF_SHIFT">HALF SHIFT</option>
                                            <option value="SICK">SICK</option>
                                            <option value="ABSENT">ABSENT</option>
                                        </select>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        {driver.current_route_address ? (
                                            <div className="flex items-center justify-between gap-2 max-w-[220px]">
                                                <div className="flex flex-col overflow-hidden">
                                                    <span className={`text-[11px] font-bold leading-tight uppercase mb-0.5 ${driver.current_route_difficulty === 'Hard' ? 'text-red-700' :
                                                        driver.current_route_difficulty === 'Medium' ? 'text-yellow-700' : 'text-green-700'
                                                        }`}>{driver.current_route_difficulty} Route</span>
                                                    <span className="text-[10px] text-gray-600 truncate" title={driver.current_route_address}>
                                                        {driver.current_route_address}
                                                    </span>
                                                </div>
                                                <button
                                                    onClick={() => handleUnassign(driver.id)}
                                                    className="text-gray-400 hover:text-red-500 hover:bg-red-50 p-1.5 rounded-full transition-all"
                                                    title="Unassign Route"
                                                >
                                                    <span className="text-lg leading-none">×</span>
                                                </button>
                                            </div>
                                        ) : (
                                            <span className="text-gray-300 italic text-[10px]">Unassigned</span>
                                        )}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        {selectedRouteId ? (
                                            <MLSuggestionCell
                                                driverId={driver.id}
                                                driverName={driver.name}
                                                mlData={mlSuggestions[driver.id]}
                                                isOpen={openPopupDriverId === driver.id}
                                                onToggle={() => setOpenPopupDriverId(openPopupDriverId === driver.id ? null : driver.id)}
                                            />
                                        ) : (
                                            <span className="text-gray-400 italic text-xs">Waiting for route...</span>
                                        )}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <span className="font-bold text-gray-700">{Math.round(driver.effort_7d || 0)}</span>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <span className={`font-bold ${(driver.credits_7d || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                            {(driver.credits_7d || 0) > 0 ? '+' : ''}{Math.round(driver.credits_7d || 0)}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-center">
                                        <span className={`text-base font-bold ${(driver.balance_7d || 0) >= 0 ? 'text-green-600' : 'text-red-500'}`}>
                                            {(driver.balance_7d || 0) > 0 ? '+' : ''}{Math.round(driver.balance_7d || 0)}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <Badge
                                            type={driver.readiness_status === 'Overloaded' ? 'danger' : driver.readiness_status === 'Underloaded' ? 'warning' : 'success'}
                                            icon={driver.readiness_status === 'Overloaded' ? ShieldAlert : driver.readiness_status === 'Underloaded' ? Info : CheckCircle}
                                        >
                                            {driver.readiness_status}
                                        </Badge>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap min-w-[280px]">
                                        <div className="flex gap-2">
                                            {['Easy', 'Medium', 'Hard'].map(level => {
                                                const mlInfo = mlSuggestions[driver.id];
                                                const isApproved = mlInfo?.fairflow_decision?.approved_levels?.includes(level);
                                                const isRecommended = mlInfo?.fairflow_decision?.approved_difficulty === level;
                                                const isBestFit = mlInfo?.preference_rank === 1;

                                                return (
                                                    <button
                                                        key={level}
                                                        onClick={() => handleAssign(driver.id, level)}
                                                        disabled={!isApproved}
                                                        title={!isApproved ? `Blocked by FairFlow: ${mlInfo?.fairflow_decision?.reason || 'Workload constraints'}` : ''}
                                                        className={`
                                                            px-3 py-1.5 rounded-lg text-xs font-bold transition-all duration-200
                                                            ${isRecommended
                                                                ? (level === 'Easy' ? 'bg-green-600 text-white border-green-700 shadow-md ring-2 ring-green-200' :
                                                                    level === 'Medium' ? 'bg-yellow-600 text-white border-yellow-700 shadow-md ring-2 ring-yellow-200' :
                                                                        'bg-indigo-600 text-white border-indigo-700 shadow-md ring-2 ring-indigo-200')
                                                                : isApproved
                                                                    ? 'bg-white border border-gray-200 text-gray-700 hover:border-gray-400 hover:bg-gray-50'
                                                                    : 'bg-gray-50 border border-transparent text-gray-300 cursor-not-allowed opacity-50'
                                                            }
                                                            ${isBestFit && isRecommended ? 'animate-pulse scale-105 shadow-[0_0_15px_rgba(79,70,229,0.4)]' : ''}
                                                        `}
                                                    >
                                                        {isBestFit && isRecommended && <span className="mr-1">⭐</span>}
                                                        {level}
                                                    </button>
                                                );
                                            })}
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            <FairnessDriftModal
                isOpen={showDriftModal}
                onClose={() => setShowDriftModal(false)}
                driftData={driftData}
            />
        </div>
    );
}
