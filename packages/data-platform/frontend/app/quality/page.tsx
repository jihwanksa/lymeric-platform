'use client';

import { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

interface QualityData {
    completeness: {
        total_materials: number;
        property_completeness: Record<string, { count: number; percentage: number }>;
    };
    outliers: Record<string, { outliers: any[]; count: number }>;
    distributions: Record<string, any>;
}

const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'];
const PROPERTY_NAMES: Record<string, string> = {
    tg: 'Glass Transition (Tg)',
    ffv: 'Free Volume Fraction',
    tc: 'Crystallinity (Tc)',
    density: 'Density',
    rg: 'Radius of Gyration'
};

export default function QualityPage() {
    const [data, setData] = useState<QualityData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        fetchQualityData();
    }, []);

    const fetchQualityData = async () => {
        try {
            const response = await fetch('http://localhost:8000/api/quality/summary');
            if (!response.ok) throw new Error('Failed to fetch quality data');
            const result = await response.json();
            setData(result);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load data');
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="max-w-7xl mx-auto px-4 py-8">
                <div className="text-center">Loading quality analysis...</div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="max-w-7xl mx-auto px-4 py-8">
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                    <p className="text-red-700">{error}</p>
                </div>
            </div>
        );
    }

    if (!data) return null;

    // Prepare completeness chart data
    const completenessData = Object.entries(data.completeness.property_completeness).map(([key, value]) => ({
        name: PROPERTY_NAMES[key] || key,
        percentage: value.percentage,
        count: value.count
    }));

    // Count total outliers
    const totalOutliers = Object.values(data.outliers).reduce((sum, prop) => sum + prop.count, 0);

    return (
        <div className="max-w-7xl mx-auto px-4 py-8">
            {/* Header */}
            <div className="mb-8">
                <h1 className="text-3xl font-bold text-gray-900">Data Quality Dashboard</h1>
                <p className="mt-2 text-gray-600">
                    Analysis of {data.completeness.total_materials} materials in the database
                </p>
            </div>

            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="bg-white rounded-lg shadow p-6">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-gray-600">Total Materials</p>
                            <p className="text-3xl font-bold text-blue-600">{data.completeness.total_materials}</p>
                        </div>
                        <div className="p-3 bg-blue-100 rounded-full">
                            <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                            </svg>
                        </div>
                    </div>
                </div>

                <div className="bg-white rounded-lg shadow p-6">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-gray-600">Properties Tracked</p>
                            <p className="text-3xl font-bold text-green-600">5</p>
                        </div>
                        <div className="p-3 bg-green-100 rounded-full">
                            <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                            </svg>
                        </div>
                    </div>
                </div>

                <div className="bg-white rounded-lg shadow p-6">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-gray-600">Outliers Detected</p>
                            <p className="text-3xl font-bold text-red-600">{totalOutliers}</p>
                        </div>
                        <div className="p-3 bg-red-100 rounded-full">
                            <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                            </svg>
                        </div>
                    </div>
                </div>
            </div>

            {/* Completeness Chart */}
            <div className="bg-white rounded-lg shadow p-6 mb-8">
                <h2 className="text-xl font-semibold mb-4">Property Completeness</h2>
                <p className="text-sm text-gray-600 mb-4">
                    Percentage of materials with each property measured
                </p>
                <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={completenessData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
                        <YAxis label={{ value: 'Completeness (%)', angle: -90, position: 'insideLeft' }} />
                        <Tooltip />
                        <Bar dataKey="percentage" fill="#3B82F6" />
                    </BarChart>
                </ResponsiveContainer>
            </div>

            {/* Outliers Section */}
            <div className="bg-white rounded-lg shadow p-6 mb-8">
                <h2 className="text-xl font-semibold mb-4">Outlier Detection (Z-score &gt; 3)</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {Object.entries(data.outliers).map(([prop, outlierData]) => (
                        <div key={prop} className="border rounded-lg p-4">
                            <h3 className="font-medium text-gray-900 mb-2">{PROPERTY_NAMES[prop] || prop}</h3>
                            <p className="text-2xl font-bold text-red-600 mb-2">{outlierData.count}</p>
                            {outlierData.outliers.length > 0 && (
                                <div className="text-sm text-gray-600">
                                    <p className="font-medium mb-1">Examples:</p>
                                    <ul className="list-disc list-inside space-y-1">
                                        {outlierData.outliers.slice(0, 3).map((outlier: any, idx: number) => (
                                            <li key={idx} className="truncate">
                                                {outlier.name}: {outlier.value} (Z={outlier.z_score})
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            </div>

            {/* Distribution Stats */}
            <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-semibold mb-4">Distribution Statistics</h2>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {Object.entries(data.distributions).map(([prop, stats]) => {
                        if (!stats) return null;
                        return (
                            <div key={prop} className="border rounded-lg p-4">
                                <h3 className="font-medium text-gray-900 mb-3">{PROPERTY_NAMES[prop] || prop}</h3>
                                <div className="grid grid-cols-2 gap-3 text-sm mb-4">
                                    <div>
                                        <p className="text-gray-600">Mean</p>
                                        <p className="font-semibold">{stats.mean}</p>
                                    </div>
                                    <div>
                                        <p className="text-gray-600">Median</p>
                                        <p className="font-semibold">{stats.median}</p>
                                    </div>
                                    <div>
                                        <p className="text-gray-600">Std Dev</p>
                                        <p className="font-semibold">{stats.std}</p>
                                    </div>
                                    <div>
                                        <p className="text-gray-600">Range</p>
                                        <p className="font-semibold">{stats.min} - {stats.max}</p>
                                    </div>
                                </div>
                                {/* Histogram */}
                                <ResponsiveContainer width="100%" height={150}>
                                    <BarChart data={stats.histogram}>
                                        <CartesianGrid strokeDasharray="3 3" />
                                        <XAxis dataKey="bin" angle={-45} textAnchor="end" height={60} fontSize={10} />
                                        <YAxis fontSize={10} />
                                        <Tooltip />
                                        <Bar dataKey="count" fill="#8B5CF6" />
                                    </BarChart>
                                </ResponsiveContainer>
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
}
