'use client';

import { useState, useEffect } from 'react';
import {
    ScatterChart,
    Scatter,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
    ZAxis
} from 'recharts';

interface CorrelationData {
    x: string;
    y: string;
    correlation: number;
    p_value: number;
    n: number;
    significant: boolean;
}

interface ScatterData {
    data: Array<{ x: number; y: number; name: string; id: string }>;
    x_property: string;
    y_property: string;
    correlation: number;
    p_value: number;
    n: number;
}

const PROPERTY_NAMES: Record<string, string> = {
    tg: 'Glass Transition (Tg)',
    ffv: 'Free Volume Fraction',
    tc: 'Crystallinity (Tc)',
    density: 'Density',
    rg: 'Radius of Gyration'
};

const PROPERTIES = ['tg', 'ffv', 'tc', 'density', 'rg'];

export default function VisualizationsPage() {
    const [correlations, setCorrelations] = useState<CorrelationData[]>([]);
    const [scatterData, setScatterData] = useState<ScatterData | null>(null);
    const [selectedX, setSelectedX] = useState<string>('tg');
    const [selectedY, setSelectedY] = useState<string>('density');
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchCorrelations();
    }, []);

    useEffect(() => {
        if (selectedX && selectedY && selectedX !== selectedY) {
            fetchScatterData();
        }
    }, [selectedX, selectedY]);

    const fetchCorrelations = async () => {
        try {
            const response = await fetch('http://localhost:8000/api/analytics/correlations');
            const data = await response.json();
            setCorrelations(data.matrix);
        } catch (error) {
            console.error('Failed to fetch correlations:', error);
        } finally {
            setLoading(false);
        }
    };

    const fetchScatterData = async () => {
        try {
            const response = await fetch(
                `http://localhost:8000/api/analytics/scatter?x=${selectedX}&y=${selectedY}`
            );
            const data = await response.json();
            setScatterData(data);
        } catch (error) {
            console.error('Failed to fetch scatter data:', error);
        }
    };

    const getCorrelationColor = (correlation: number) => {
        const abs = Math.abs(correlation);
        if (abs > 0.7) return 'text-green-700 bg-green-100';
        if (abs > 0.4) return 'text-yellow-700 bg-yellow-100';
        return 'text-gray-700 bg-gray-100';
    };

    if (loading) {
        return (
            <div className="max-w-7xl mx-auto px-4 py-8">
                <div className="text-center">Loading visualizations...</div>
            </div>
        );
    }

    return (
        <div className="max-w-7xl mx-auto px-4 py-8">
            {/* Header */}
            <div className="mb-8">
                <h1 className="text-3xl font-bold text-gray-900">Advanced Visualizations</h1>
                <p className="mt-2 text-gray-600">
                    Explore correlations and relationships between material properties
                </p>
            </div>

            {/* Correlation Matrix */}
            <div className="bg-white rounded-lg shadow p-6 mb-8">
                <h2 className="text-xl font-semibold mb-4">Correlation Matrix</h2>
                <p className="text-sm text-gray-600 mb-4">
                    Pearson correlation coefficients between property pairs (p &lt; 0.05 = significant)
                </p>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {correlations.map((corr, idx) => (
                        <div
                            key={idx}
                            className={`rounded-lg p-4 border-2 ${corr.significant ? 'border-blue-300' : 'border-gray-200'
                                }`}
                        >
                            <div className="flex justify-between items-start mb-2">
                                <div>
                                    <p className="text-sm font-medium text-gray-900">
                                        {PROPERTY_NAMES[corr.x]} vs {PROPERTY_NAMES[corr.y]}
                                    </p>
                                    <p className="text-xs text-gray-500">n = {corr.n} materials</p>
                                </div>
                                {corr.significant && (
                                    <span className="px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded">
                                        Significant
                                    </span>
                                )}
                            </div>

                            <div className={`inline-block px-3 py-1 rounded-full font-semibold ${getCorrelationColor(corr.correlation)}`}>
                                r = {corr.correlation.toFixed(3)}
                            </div>
                            <p className="text-xs text-gray-500 mt-2">p-value: {corr.p_value.toFixed(4)}</p>

                            <button
                                onClick={() => {
                                    setSelectedX(corr.x);
                                    setSelectedY(corr.y);
                                }}
                                className="mt-2 text-sm text-blue-600 hover:text-blue-800"
                            >
                                View Scatter Plot →
                            </button>
                        </div>
                    ))}
                </div>
            </div>

            {/* Scatter Plot */}
            <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-semibold mb-4">Scatter Plot</h2>

                {/* Property Selectors */}
                <div className="grid grid-cols-2 gap-4 mb-6">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">X-Axis</label>
                        <select
                            value={selectedX}
                            onChange={(e) => setSelectedX(e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md"
                        >
                            {PROPERTIES.map((prop) => (
                                <option key={prop} value={prop}>
                                    {PROPERTY_NAMES[prop]}
                                </option>
                            ))}
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Y-Axis</label>
                        <select
                            value={selectedY}
                            onChange={(e) => setSelectedY(e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md"
                        >
                            {PROPERTIES.map((prop) => (
                                <option key={prop} value={prop}>
                                    {PROPERTY_NAMES[prop]}
                                </option>
                            ))}
                        </select>
                    </div>
                </div>

                {scatterData && scatterData.data.length > 0 ? (
                    <>
                        {/* Statistics */}
                        <div className="bg-gray-50 rounded-lg p-4 mb-4">
                            <div className="grid grid-cols-3 gap-4 text-center">
                                <div>
                                    <p className="text-sm text-gray-600">Correlation</p>
                                    <p className="text-2xl font-bold text-blue-600">
                                        {scatterData.correlation.toFixed(3)}
                                    </p>
                                </div>
                                <div>
                                    <p className="text-sm text-gray-600">P-value</p>
                                    <p className="text-2xl font-bold text-gray-700">
                                        {scatterData.p_value.toFixed(4)}
                                    </p>
                                </div>
                                <div>
                                    <p className="text-sm text-gray-600">Data Points</p>
                                    <p className="text-2xl font-bold text-green-600">{scatterData.n}</p>
                                </div>
                            </div>
                        </div>

                        {/* Chart */}
                        <ResponsiveContainer width="100%" height={400}>
                            <ScatterChart margin={{ top: 20, right: 20, bottom: 60, left: 60 }}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis
                                    type="number"
                                    dataKey="x"
                                    name={PROPERTY_NAMES[scatterData.x_property]}
                                    label={{
                                        value: PROPERTY_NAMES[scatterData.x_property],
                                        position: 'insideBottom',
                                        offset: -10
                                    }}
                                />
                                <YAxis
                                    type="number"
                                    dataKey="y"
                                    name={PROPERTY_NAMES[scatterData.y_property]}
                                    label={{
                                        value: PROPERTY_NAMES[scatterData.y_property],
                                        angle: -90,
                                        position: 'insideLeft'
                                    }}
                                />
                                <ZAxis range={[60, 60]} />
                                <Tooltip
                                    cursor={{ strokeDasharray: '3 3' }}
                                    content={({ active, payload }) => {
                                        if (active && payload && payload.length) {
                                            const data = payload[0].payload;
                                            return (
                                                <div className="bg-white p-3 border border-gray-200 rounded shadow-lg">
                                                    <p className="font-medium">{data.name}</p>
                                                    <p className="text-sm text-gray-600">
                                                        {PROPERTY_NAMES[scatterData.x_property]}: {data.x}
                                                    </p>
                                                    <p className="text-sm text-gray-600">
                                                        {PROPERTY_NAMES[scatterData.y_property]}: {data.y}
                                                    </p>
                                                </div>
                                            );
                                        }
                                        return null;
                                    }}
                                />
                                <Scatter data={scatterData.data} fill="#3B82F6" />
                            </ScatterChart>
                        </ResponsiveContainer>
                    </>
                ) : (
                    <div className="text-center py-12 text-gray-500">
                        {selectedX === selectedY
                            ? 'Please select different properties for X and Y axes'
                            : 'No data available for this property combination'}
                    </div>
                )}
            </div>
        </div>
    );
}
