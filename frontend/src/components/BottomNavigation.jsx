import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, MessageSquarePlus, History } from 'lucide-react';

export default function BottomNavigation() {
    const navItems = [
        { path: '/driver', icon: LayoutDashboard, label: 'Dashboard', exact: true },
        { path: '/driver/feedback', icon: MessageSquarePlus, label: 'Feedback' },
        { path: '/driver/history', icon: History, label: 'History' },
    ];

    return (
        <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.05)] z-50 pb-safe">
            <div className="flex justify-around items-center h-16 max-w-7xl mx-auto px-4">
                {navItems.map((item) => (
                    <NavLink
                        key={item.path}
                        to={item.path}
                        end={item.exact}
                        className={({ isActive }) =>
                            `flex flex-col items-center justify-center w-full h-full transition-colors duration-200 ${isActive ? 'text-blue-600' : 'text-gray-400 hover:text-gray-600'
                            }`
                        }
                    >
                        <item.icon size={24} strokeWidth={2.5} />
                        <span className="text-xs font-medium mt-1">{item.label}</span>
                    </NavLink>
                ))}
            </div>
        </nav>
    );
}
