import React, { useRef, useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ArrowDown, Zap, Scale, Eye, BarChart3, Users, CheckCircle, Settings } from 'lucide-react';
import heroImage from '../assets/hero_image.jpg';

export default function RoleSelection() {
    const roleSectionRef = useRef(null);
    const [loaded, setLoaded] = useState(false);

    useEffect(() => {
        setLoaded(true);
    }, []);

    const scrollToRoles = () => {
        roleSectionRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    return (
        <div className="bg-slate-50 font-sans min-h-screen">

            {/* 
              ========================
              TOP HEADER
              ========================
            */}
            <header className="absolute top-0 left-0 w-full px-6 py-8 flex items-center justify-between max-w-7xl mx-auto z-10">
                <div>
                    <h1 className="text-4xl font-black text-slate-900 tracking-tighter leading-none drop-shadow-sm">
                        FairFlow
                    </h1>
                    <div className="inline-flex items-center mt-2 px-3 py-1 rounded-full bg-blue-100 text-blue-700 text-[10px] font-bold tracking-wide uppercase border border-blue-200">
                        Human-Centric Dispatch
                    </div>
                </div>
            </header>

            {/* 
              ========================
              HERO SECTION (Split Layout)
              ========================
            */}
            <section className="min-h-[90vh] flex items-center justify-center relative overflow-hidden px-6 py-12 lg:py-0">

                {/* Background Decor */}
                <div className="absolute top-0 right-0 w-2/3 h-full bg-blue-50/50 skew-x-12 transform origin-top-right -z-10"></div>

                <div className="w-full max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-20 items-center">

                    {/* LEFT COLUMN: Content */}
                    <div className={`space-y-8 transition-all duration-1000 transform ${loaded ? 'translate-x-0 opacity-100' : '-translate-x-10 opacity-0'}`}>

                        {/* Headings - Simplified since Brand is now Top */}
                        <div>
                            <p className="text-2xl lg:text-3xl font-medium text-slate-700 leading-snug">
                                Because hard work should be <span className="text-blue-600">remembered</span>.
                            </p>
                        </div>

                        {/* Description */}
                        <p className="text-lg text-slate-500 leading-relaxed max-w-lg">
                            A delivery dispatch system that assigns routes based on real human effort—not just distance or package count.
                        </p>

                        {/* Feature Cards - White Box Style */}
                        <div className="space-y-4 max-w-xl">
                            <div className="flex items-start gap-4 bg-white p-5 rounded-2xl shadow-md border border-slate-100 hover:shadow-lg transition-all">
                                <div className="w-12 h-12 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-xl flex items-center justify-center flex-shrink-0 shadow-sm">
                                    <Zap size={24} className="text-white" />
                                </div>
                                <div>
                                    <h3 className="font-bold text-lg text-slate-900 mb-1">Effort-Based Routing</h3>
                                    <p className="text-slate-600 text-sm leading-relaxed">Routes assigned based on real workload, not just mileage.</p>
                                </div>
                            </div>

                            <div className="flex items-start gap-4 bg-white p-5 rounded-2xl shadow-md border border-slate-100 hover:shadow-lg transition-all">
                                <div className="w-12 h-12 bg-gradient-to-br from-green-400 to-emerald-500 rounded-xl flex items-center justify-center flex-shrink-0 shadow-sm">
                                    <Scale size={24} className="text-white" />
                                </div>
                                <div>
                                    <h3 className="font-bold text-lg text-slate-900 mb-1">Fairness Carried Forward</h3>
                                    <p className="text-slate-600 text-sm leading-relaxed">Your effort is tracked across days, ensuring long-term balance.</p>
                                </div>
                            </div>

                            <div className="flex items-start gap-4 bg-white p-5 rounded-2xl shadow-md border border-slate-100 hover:shadow-lg transition-all">
                                <div className="w-12 h-12 bg-gradient-to-br from-purple-400 to-violet-500 rounded-xl flex items-center justify-center flex-shrink-0 shadow-sm">
                                    <Eye size={24} className="text-white" />
                                </div>
                                <div>
                                    <h3 className="font-bold text-lg text-slate-900 mb-1">AI-Guided Balance</h3>
                                    <p className="text-slate-600 text-sm leading-relaxed">Smart algorithms detect drift and protect overloaded drivers.</p>
                                </div>
                            </div>
                        </div>

                        {/* CTA Button */}
                        <button
                            onClick={scrollToRoles}
                            className="group inline-flex items-center px-8 py-4 text-lg font-bold text-white transition-all bg-blue-600 rounded-full shadow-lg hover:bg-blue-700 hover:shadow-blue-500/30 hover:-translate-y-1 focus:ring-4 focus:ring-blue-200 mt-4"
                        >
                            Get Started
                            <ArrowDown className="ml-2 h-5 w-5 group-hover:translate-y-1 transition-transform" />
                        </button>
                    </div>

                    {/* RIGHT COLUMN: Illustration */}
                    <div className={`relative hidden lg:block transition-all duration-1000 delay-200 transform ${loaded ? 'translate-x-0 opacity-100' : 'translate-x-10 opacity-0'}`}>
                        {/* Image Illustration */}
                        <div className="relative w-full max-w-sm mx-auto">
                            {/* Main Image with Crop */}
                            <div className="relative rounded-2xl overflow-hidden shadow-2xl transform rotate-1 hover:rotate-0 transition-all duration-500 border-4 border-white" style={{ clipPath: 'inset(0 0 5% 0 round 16px)' }}>
                                <div className="absolute inset-0 bg-blue-500/10 mix-blend-overlay z-10"></div>
                                <img
                                    src={heroImage}
                                    alt="FairFlow Logistics Dashboard"
                                    className="w-full h-auto object-cover transform hover:scale-105 transition-transform duration-700"
                                />
                            </div>

                            {/* Tertiary Card (Team Trust) - Floating Left */}
                            <div className="absolute top-10 -left-16 bg-white p-4 rounded-2xl shadow-xl border border-slate-100 z-30 animate-bounce cursor-default hidden md:block" style={{ animationDuration: '6s' }}>
                                <div className="flex items-center space-x-3">
                                    <div className="flex -space-x-3">
                                        <div className="w-10 h-10 rounded-full border-2 border-white bg-blue-100 flex items-center justify-center text-xs font-bold text-blue-600">JD</div>
                                        <div className="w-10 h-10 rounded-full border-2 border-white bg-green-100 flex items-center justify-center text-xs font-bold text-green-600">AS</div>
                                        <div className="w-10 h-10 rounded-full border-2 border-white bg-purple-100 flex items-center justify-center text-xs font-bold text-purple-600">MR</div>
                                    </div>
                                    <div>
                                        <div className="text-xs font-bold text-slate-400 uppercase tracking-wider">Trusted by</div>
                                        <div className="text-sm font-bold text-slate-800">500+ Drivers</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                </div>
            </section>


            {/* 
              ========================
              ROLE SELECTION SECTION
              ========================
            */}
            <section ref={roleSectionRef} className="min-h-screen flex flex-col items-center justify-center py-24 bg-white border-t border-slate-100">
                <div className="w-full max-w-6xl px-6">

                    <div className="text-center mb-16">
                        <div className="inline-block mb-3 px-3 py-1 bg-slate-100 rounded-full text-slate-500 text-xs font-bold tracking-widest uppercase">
                            Get Started
                        </div>
                        <h2 className="text-4xl font-bold text-slate-900 mb-4">Choose your portal</h2>
                        <p className="text-xl text-slate-500">Select how you want to continue</p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">

                        {/* Driver Card */}
                        <Link to="/login/driver" className="group relative block h-80 w-full">
                            <div className="absolute inset-0 bg-gradient-to-br from-blue-50 to-white rounded-[28px] border border-blue-200 shadow-[0_0_20px_rgba(59,130,246,0.15)] transition-all duration-500 ease-out transform group-hover:scale-[1.02] group-hover:shadow-[0_0_25px_rgba(59,130,246,0.25)]"></div>

                            {/* Floating Icon Badge */}
                            <div className="absolute -top-6 left-1/2 -translate-x-1/2 w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl shadow-lg shadow-blue-500/30 flex items-center justify-center transform transition-transform group-hover:scale-110 duration-300 z-10">
                                <Zap className="text-white w-8 h-8" strokeWidth={2} />
                            </div>

                            <div className="relative h-full flex flex-col items-center text-center pt-16 pb-8 px-8 z-0">
                                <h3 className="text-2xl font-bold text-gray-900 mb-3 tracking-tight group-hover:text-blue-600 transition-colors">Driver Portal</h3>
                                <p className="text-gray-500 text-sm leading-relaxed mb-auto px-2">
                                    Check today’s route, effort score, fairness credits, and history.
                                </p>

                                <span className="w-full py-3 px-6 bg-white border border-blue-100 text-blue-600 font-semibold rounded-full shadow-sm transition-all duration-300 group-hover:bg-blue-600 group-hover:text-white group-hover:shadow-md group-hover:border-transparent mt-4">
                                    Continue as Driver
                                </span>
                            </div>
                        </Link>

                        {/* Admin Card */}
                        <Link to="/login/admin" className="group relative block h-80 w-full">
                            <div className="absolute inset-0 bg-gradient-to-br from-slate-50 to-white rounded-[28px] border border-slate-200 shadow-[0_0_20px_rgba(148,163,184,0.15)] transition-all duration-500 ease-out transform group-hover:scale-[1.02] group-hover:shadow-[0_0_25px_rgba(148,163,184,0.25)]"></div>

                            {/* Floating Icon Badge */}
                            <div className="absolute -top-6 left-1/2 -translate-x-1/2 w-16 h-16 bg-gradient-to-br from-slate-700 to-gray-900 rounded-2xl shadow-lg shadow-slate-500/30 flex items-center justify-center transform transition-transform group-hover:scale-110 duration-300 z-10">
                                <Settings className="text-white w-8 h-8" strokeWidth={2} />
                            </div>

                            <div className="relative h-full flex flex-col items-center text-center pt-16 pb-8 px-8 z-0">
                                <h3 className="text-2xl font-bold text-gray-900 mb-3 tracking-tight group-hover:text-slate-800 transition-colors">Admin Portal</h3>
                                <p className="text-gray-500 text-sm leading-relaxed mb-auto px-2">
                                    Monitor fairness, manage driver status, and assign routes responsibly.
                                </p>

                                <span className="w-full py-3 px-6 bg-white border border-slate-200 text-slate-700 font-semibold rounded-full shadow-sm transition-all duration-300 group-hover:bg-slate-800 group-hover:text-white group-hover:shadow-md group-hover:border-transparent mt-4">
                                    Continue as Admin
                                </span>
                            </div>
                        </Link>
                    </div>

                    <div className="mt-20 text-center border-t border-slate-100 pt-8">
                        <p className="text-slate-400 text-sm font-medium">
                            FairFlow v1.0 • Built for fairness, not just speed.
                        </p>
                    </div>

                </div>
            </section>
        </div>
    );
}
