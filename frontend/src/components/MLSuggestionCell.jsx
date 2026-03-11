import React, { useRef } from 'react';
import { Sparkles, X } from 'lucide-react';

export default function MLSuggestionCell({ driverId, driverName, mlData, isOpen, onToggle }) {
    const buttonRef = useRef(null);

    // Get difficulty color styling (neutral outline badges)
    const getDifficultyColor = (difficulty) => {
        const styles = {
            'Easy': 'border-green-500 text-green-700 hover:bg-green-50',
            'Medium': 'border-yellow-500 text-yellow-700 hover:bg-yellow-50',
            'Hard': 'border-red-500 text-red-700 hover:bg-red-50',
        };
        return styles[difficulty] || 'border-gray-400 text-gray-600';
    };

    // Loading state
    if (!mlData) {
        return (
            <div className="flex items-center justify-center">
                <span className="text-xs text-gray-400 italic">Evaluating...</span>
            </div>
        );
    }

    const mlDifficulty = mlData?.ml_recommendation?.recommended_difficulty;
    const fairflowDifficulty = mlData?.fairflow_decision?.approved_difficulty;
    const wasOverridden = mlData?.fairflow_decision?.fairness_override;
    const preferenceLabel = mlData?.preference_label;
    const preferenceRank = mlData?.preference_rank;

    return (
        <div className="relative">
            {/* Preference Badge */}
            <button
                ref={buttonRef}
                onClick={onToggle}
                className={`
                    flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-bold
                    border-2 transition-all hover:shadow-md cursor-pointer whitespace-nowrap
                    ${preferenceRank === 1 ? 'bg-indigo-50 border-indigo-400 text-indigo-700 shadow-sm animate-pulse' :
                        fairflowDifficulty === 'Easy' ? 'bg-green-50 border-green-200 text-green-700' :
                            fairflowDifficulty === 'Medium' ? 'bg-yellow-50 border-yellow-200 text-yellow-700' :
                                fairflowDifficulty === 'Hard' ? 'bg-red-50 border-red-200 text-red-700' :
                                    'bg-gray-50 border-gray-200 text-gray-500'}
                `}
                title="Click for AI reasoning"
            >
                {preferenceRank === 1 && <span>⭐</span>}
                <span>{fairflowDifficulty}</span>
                <span className="opacity-30 mx-0.5">·</span>
                <span className={preferenceRank === 1 ? 'text-indigo-800' : 'font-medium'}>
                    {preferenceRank ? `#${preferenceRank} ` : ''}{preferenceLabel}
                </span>
            </button>

            {/* Reasoning Popup (Fixed Positioning) */}
            {isOpen && (
                <div
                    className="ml-popup-container fixed z-50 bg-white rounded-lg shadow-2xl border-2 border-gray-200 p-4 w-96 max-h-[80vh] overflow-y-auto"
                    style={{
                        top: buttonRef.current
                            ? (buttonRef.current.getBoundingClientRect().bottom + 8 > window.innerHeight - 400
                                ? buttonRef.current.getBoundingClientRect().top - 420
                                : buttonRef.current.getBoundingClientRect().bottom + 8)
                            : '50%',
                        left: buttonRef.current
                            ? buttonRef.current.getBoundingClientRect().left
                            : '50%',
                    }}
                >
                    <div className="flex justify-between items-start mb-3">
                        <div>
                            <h4 className="font-bold text-sm text-gray-900">Why this recommendation?</h4>
                            {preferenceRank && (
                                <div className="mt-1 flex items-center gap-1.5">
                                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${preferenceRank === 1 ? 'bg-indigo-100 text-indigo-700' : 'bg-gray-100 text-gray-600'}`}>
                                        {preferenceRank === 1 ? '⭐ ' : ''}Ranked #{preferenceRank}
                                    </span>
                                    <span className="text-[10px] text-gray-500 font-medium">{preferenceLabel}</span>
                                </div>
                            )}
                        </div>
                        <button
                            onClick={onToggle}
                            className="text-gray-400 hover:text-gray-600 transition-colors"
                        >
                            <X size={20} />
                        </button>
                    </div>

                    {/* ML Suggestion */}
                    <div className="mb-3 p-3 bg-purple-50 rounded-lg border border-purple-200">
                        <div className="flex items-center gap-2 mb-2">
                            <Sparkles size={16} className="text-purple-600" />
                            <span className="text-xs font-semibold text-purple-900">ML Suggests:</span>
                            <span className={`px-2 py-0.5 rounded text-xs font-bold ${mlDifficulty === 'Easy' ? 'bg-green-100 text-green-700' :
                                mlDifficulty === 'Medium' ? 'bg-yellow-100 text-yellow-700' :
                                    'bg-red-100 text-red-700'
                                }`}>
                                {mlDifficulty}
                            </span>
                            <span className="text-xs text-purple-700 font-medium">
                                ({Math.round((mlData?.ml_recommendation?.confidence || 0) * 100)}%)
                            </span>
                        </div>
                        <div className="text-xs text-gray-700 leading-relaxed whitespace-normal break-words">
                            {mlData?.ml_recommendation?.reason}
                        </div>
                    </div>

                    {/* FairFlow Decision */}
                    <div className={`p-3 rounded-lg border ${mlData?.fairflow_decision?.action === 'approved' ? 'bg-green-50 border-green-200' :
                        mlData?.fairflow_decision?.action === 'adjusted' ? 'bg-yellow-50 border-yellow-200' :
                            'bg-red-50 border-red-200'
                        }`}>
                        <div className="flex items-center gap-2 mb-2">
                            <span className="text-xs font-semibold text-gray-900">🧠 FairFlow Decision:</span>
                            <span className={`px-2 py-0.5 rounded text-xs font-bold ${fairflowDifficulty === 'Easy' ? 'bg-green-100 text-green-700' :
                                fairflowDifficulty === 'Medium' ? 'bg-yellow-100 text-yellow-700' :
                                    fairflowDifficulty === 'Hard' ? 'bg-red-100 text-red-700' :
                                        'bg-gray-100 text-gray-700'
                                }`}>
                                {fairflowDifficulty}
                            </span>
                        </div>

                        {/* Show Approved/Blocked Levels */}
                        {mlData?.fairflow_decision?.approved_levels && (
                            <div className="mt-2 text-xs space-y-1">
                                <div className="flex items-center gap-2">
                                    <span className="font-semibold text-green-700">✓ Approved:</span>
                                    <div className="flex gap-1">
                                        {mlData?.fairflow_decision?.approved_levels?.map(level => (
                                            <span key={level} className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${level === 'Easy' ? 'bg-green-100 text-green-700' :
                                                level === 'Medium' ? 'bg-yellow-100 text-yellow-700' :
                                                    'bg-red-100 text-red-700'
                                                }`}>
                                                {level}
                                            </span>
                                        ))}
                                        {mlData?.fairflow_decision?.approved_levels?.length === 0 && (
                                            <span className="text-gray-500 italic">None - use Auto-Assign</span>
                                        )}
                                    </div>
                                </div>
                                {mlData?.fairflow_decision?.blocked_levels && mlData?.fairflow_decision?.blocked_levels?.length > 0 && (
                                    <div className="flex items-center gap-2">
                                        <span className="font-semibold text-red-700">✗ Blocked:</span>
                                        <div className="flex gap-1">
                                            {mlData?.fairflow_decision?.blocked_levels?.map(level => (
                                                <span key={level} className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-gray-200 text-gray-500 line-through">
                                                    {level}
                                                </span>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </div>
                        )}

                        {wasOverridden && (
                            <div className="text-xs text-yellow-800 font-semibold mt-2 pt-2 border-t border-yellow-300">
                                ⚠️ {mlData?.fairflow_decision?.override_reason}
                            </div>
                        )}

                        <div className="text-xs text-gray-600 mt-2 leading-relaxed whitespace-normal break-words">
                            {mlData?.fairflow_decision?.reason}
                        </div>
                    </div>

                    {/* Driver Context */}
                    <div className="mt-3 p-2 bg-gray-50 rounded text-xs text-gray-600">
                        <div className="font-semibold text-gray-700 mb-1">Driver Context:</div>
                        <div className="grid grid-cols-2 gap-1">
                            <span>Effort/hr:</span>
                            <span className="font-medium">{mlData?.driver_context?.normalized_effort_per_hour}</span>
                            <span>Balance:</span>
                            <span className={`font-medium ${(mlData?.driver_context?.fairness_balance || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                {(mlData?.driver_context?.fairness_balance || 0) > 0 ? '+' : ''}{mlData?.driver_context?.fairness_balance}
                            </span>
                            <span>Hours Today:</span>
                            <span className="font-medium">{mlData?.driver_context?.working_hours_today}h</span>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
