import React from 'react';
import { X } from 'lucide-react';
import { Card } from './Card';
import { Badge } from './Badge';

export default function FairnessDriftModal({ isOpen, onClose, driftData }) {
    if (!isOpen || !driftData) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 p-4" onClick={onClose}>
            <div className="relative bg-white rounded-2xl shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
                {/* Header */}
                <div className="sticky top-0 bg-gradient-to-r from-indigo-600 to-purple-600 text-white p-6 rounded-t-2xl">
                    <div className="flex items-start justify-between">
                        <div>
                            <h2 className="text-2xl font-bold flex items-center gap-3">
                                <span>🤖</span>
                                <span>AI Fairness Analysis</span>
                            </h2>
                            <p className="text-indigo-100 text-sm mt-1">Statistical Drift Detection Report</p>
                        </div>
                        <button
                            onClick={onClose}
                            className="text-white hover:bg-white hover:bg-opacity-20 p-2 rounded-lg transition-colors"
                        >
                            <X size={24} />
                        </button>
                    </div>
                </div>

                {/* Content */}
                <div className="p-6">
                    {/* Severity Badge */}
                    <div className="mb-6 flex items-center gap-3">
                        <div className="text-4xl">
                            {driftData.severity === 'LOW' && '🟡'}
                            {driftData.severity === 'MEDIUM' && '🟠'}
                            {driftData.severity === 'HIGH' && '🔴'}
                        </div>
                        <div>
                            <Badge
                                type={
                                    driftData.severity === 'HIGH' ? 'danger' :
                                        driftData.severity === 'MEDIUM' ? 'warning' :
                                            'success'
                                }
                                className="text-lg px-4 py-2 font-bold"
                            >
                                {driftData.severity} SEVERITY
                            </Badge>
                        </div>
                    </div>

                    {/* Metrics Grid */}
                    <div className="grid grid-cols-3 gap-4 mb-6">
                        <Card className="bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
                            <p className="text-sm text-gray-600 font-medium mb-1">Current Variance</p>
                            <p className="text-3xl font-bold text-blue-700">{(driftData.metrics?.current_variance || 0).toFixed(2)}</p>
                        </Card>
                        <Card className="bg-gradient-to-br from-purple-50 to-purple-100 border-purple-200">
                            <p className="text-sm text-gray-600 font-medium mb-1">Baseline Variance</p>
                            <p className="text-3xl font-bold text-purple-700">{(driftData.metrics?.baseline_variance || 0).toFixed(2)}</p>
                        </Card>
                        <Card className={`bg-gradient-to-br ${(driftData.metrics?.variance_change_pct || 0) > 40 ? 'from-red-50 to-red-100 border-red-200' : 'from-yellow-50 to-yellow-100 border-yellow-200'
                            }`}>
                            <p className="text-sm text-gray-600 font-medium mb-1">Change from Baseline</p>
                            <p className={`text-3xl font-bold ${(driftData.metrics?.variance_change_pct || 0) > 40 ? 'text-red-700' : 'text-yellow-700'
                                }`}>
                                +{(driftData.metrics?.variance_change_pct || 0).toFixed(1)}%
                            </p>
                        </Card>
                    </div>

                    {/* AI Explanation */}
                    <div className="mb-6 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl border border-indigo-200">
                        <p className="text-sm font-semibold text-indigo-900 mb-2">🧠 AI Explanation</p>
                        <p className="text-indigo-800 leading-relaxed">{driftData.explanation}</p>
                    </div>

                    {/* Affected Drivers */}
                    {driftData.affected_drivers && driftData.affected_drivers.length > 0 && (
                        <div>
                            <h3 className="text-lg font-bold text-gray-800 mb-4">Affected Drivers ({driftData.affected_drivers.length})</h3>
                            <div className="bg-gray-50 rounded-xl border border-gray-200 overflow-hidden">
                                <table className="w-full">
                                    <thead className="bg-gray-100 border-b border-gray-300">
                                        <tr>
                                            <th className="text-left px-4 py-3 text-sm font-semibold text-gray-700">Driver</th>
                                            <th className="text-right px-4 py-3 text-sm font-semibold text-gray-700">Avg Effort (3 days)</th>
                                            <th className="text-right px-4 py-3 text-sm font-semibold text-gray-700">Deviation</th>
                                            <th className="text-right px-4 py-3 text-sm font-semibold text-gray-700">Status</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {driftData.affected_drivers.map((driver, idx) => (
                                            <tr key={driver.id} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                                                <td className="px-4 py-3 font-semibold text-gray-900">{driver.name}</td>
                                                <td className="px-4 py-3 text-right text-gray-700">{(driver.avg_effort || 0).toFixed(1)}</td>
                                                <td className={`px-4 py-3 text-right font-bold ${(driver.deviation || 0) > 0 ? 'text-red-600' : 'text-green-600'
                                                    }`}>
                                                    {(driver.deviation || 0) > 0 ? '+' : ''}{(driver.deviation || 0).toFixed(1)}%
                                                </td>
                                                <td className="px-4 py-3 text-right">
                                                    <Badge type={(driver.deviation || 0) > 20 ? 'danger' : (driver.deviation || 0) < -20 ? 'success' : 'warning'}>
                                                        {(driver.deviation || 0) > 20 ? 'Overloaded' : (driver.deviation || 0) < -20 ? 'Underloaded' : 'Monitored'}
                                                    </Badge>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    )}

                    {/* Info Box */}
                    <div className="mt-6 p-4 bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl border border-green-200">
                        <p className="text-sm text-green-900">
                            <span className="font-semibold">✅ AI Protection:</span> The system automatically blocks hard route assignments to overloaded drivers and prioritizes underloaded drivers for new work.
                        </p>
                    </div>
                </div>

                {/* Footer */}
                <div className="sticky bottom-0 bg-gray-50 p-4 rounded-b-2xl border-t border-gray-200">
                    <button
                        onClick={onClose}
                        className="w-full bg-indigo-600 text-white py-3 rounded-lg hover:bg-indigo-700 transition-colors font-medium"
                    >
                        Close
                    </button>
                </div>
            </div>
        </div>
    );
}
