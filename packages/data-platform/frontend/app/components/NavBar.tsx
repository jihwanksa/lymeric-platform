"use client";

import Link from 'next/link';
import { useAuth } from '../context/AuthContext';
import { usePathname } from 'next/navigation';

export default function NavBar() {
    const { user, logout, isAuthenticated } = useAuth();
    const pathname = usePathname();

    const isActive = (path: string) => pathname === path;

    return (
        <nav className="border-b bg-white">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between h-16 items-center">
                    <div className="flex-shrink-0 flex items-center">
                        <Link href="/" className="text-2xl font-bold text-blue-600">
                            Lymeric Data Platform
                        </Link>
                    </div>
                    <div className="hidden md:flex space-x-4">
                        <Link href="/" className={`px-3 py-2 text-sm font-medium ${isActive('/') ? 'text-blue-600' : 'text-gray-700 hover:text-blue-600'}`}>
                            Dashboard
                        </Link>
                        <Link href="/materials" className={`px-3 py-2 text-sm font-medium ${isActive('/materials') ? 'text-blue-600' : 'text-gray-700 hover:text-blue-600'}`}>
                            Materials
                        </Link>
                        <Link href="/search" className={`px-3 py-2 text-sm font-medium ${isActive('/search') ? 'text-blue-600' : 'text-gray-700 hover:text-blue-600'}`}>
                            Search
                        </Link>
                        <Link href="/upload" className={`px-3 py-2 text-sm font-medium ${isActive('/upload') ? 'text-blue-600' : 'text-gray-700 hover:text-blue-600'}`}>
                            Upload
                        </Link>
                        <Link href="/quality" className={`px-3 py-2 text-sm font-medium ${isActive('/quality') ? 'text-blue-600' : 'text-gray-700 hover:text-blue-600'}`}>
                            Quality
                        </Link>
                        <Link href="/visualizations" className={`px-3 py-2 text-sm font-medium ${isActive('/visualizations') ? 'text-blue-600' : 'text-gray-700 hover:text-blue-600'}`}>
                            Visualizations
                        </Link>
                        <Link href="/predictions" className={`px-3 py-2 text-sm font-medium ${isActive('/predictions') ? 'text-blue-600' : 'text-gray-700 hover:text-blue-600'}`}>
                            Predictions
                        </Link>
                        <Link href="/training" className={`px-3 py-2 text-sm font-medium ${isActive('/training') ? 'text-blue-600' : 'text-gray-700 hover:text-blue-600'}`}>
                            Training
                        </Link>
                        <Link href="/chat" className={`px-3 py-2 text-sm font-medium ${isActive('/chat') ? 'text-blue-600' : 'text-gray-700 hover:text-blue-600'}`}>
                            Chat
                        </Link>
                    </div>
                    <div className="flex items-center space-x-4">
                        {isAuthenticated ? (
                            <div className="flex items-center space-x-4">
                                <span className="text-sm text-gray-600">
                                    {user?.email}
                                </span>
                                <button
                                    onClick={logout}
                                    className="text-sm text-red-600 hover:text-red-800 font-medium"
                                >
                                    Logout
                                </button>
                            </div>
                        ) : (
                            <div className="flex space-x-2">
                                <Link href="/login" className="text-sm text-gray-700 hover:text-blue-600 font-medium">
                                    Login
                                </Link>
                                <Link href="/register" className="text-sm bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700 font-medium">
                                    Sign Up
                                </Link>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </nav>
    );
}
