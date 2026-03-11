import React from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import { Home } from 'lucide-react';
import BottomNavigation from './BottomNavigation';

export default function DriverLayout() {
    const navigate = useNavigate();

    return (
        <div className="min-h-screen bg-gray-50 pb-20"> {/* pb-20 for bottom nav space */}
            {/* Top Navigation / Header */}
            <div className="bg-white border-b border-gray-100 shadow-sm sticky top-0 z-50 mb-6">
                <div className="max-w-7xl mx-auto px-4 md:px-8 h-16 flex items-center gap-4">
                    <button
                        onClick={() => navigate('/')}
                        className="p-2.5 bg-white border border-gray-100 rounded-xl text-gray-400 hover:text-blue-600 hover:border-blue-200 hover:bg-blue-50 transition-all shadow-sm group"
                        title="Back to portal selection"
                    >
                        <Home size={22} className="group-hover:scale-110 transition-transform" />
                    </button>
                    <div className="flex items-center gap-3">
                        <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                            <span className="text-white font-black text-lg">F</span>
                        </div>
                        <h1 className="font-bold text-xl text-gray-900 tracking-tight">FairFlow</h1>
                    </div>

                </div>
            </div>

            <div className="max-w-7xl mx-auto px-4 md:px-8">
                <Outlet />
            </div>
            <BottomNavigation />
        </div>
    );
}
