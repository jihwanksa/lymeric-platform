"use client";

import { useState, useEffect } from 'react';

interface Prediction {
    value: number;
    confidence: number;
}

interface PredictionResult {
    smiles: string;
    predictions: {
        tg: Prediction;
        ffv: Prediction;
        tc: Prediction;
        density: Prediction;
        rg: Prediction;
    };
}

// Molecule structure visualization component
function MoleculeImage({ smiles }: { smiles: string }) {
    const [imageUrl, setImageUrl] = useState<string | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchImage = async () => {
            try {
                const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
                const response = await fetch(`${apiUrl}/api/molecule/visualize`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ smiles, size: 300 }),
                });

                if (response.ok) {
                    const data = await response.json();
                    setImageUrl(`data:image/png;base64,${data.image_base64}`);
                }
            } catch (error) {
                console.error('Failed to load molecule image:', error);
            } finally {
                setLoading(false);
            }
        };

        if (smiles) {
            fetchImage();
        }
    }, [smiles]);

    if (loading) {
        return (
            <div className="w-[300px] h-[300px] bg-gray-100 rounded-lg flex items-center justify-center">
                <span className="text-gray-400">Loading...</span>
            </div>
        );
    }

    if (!imageUrl) {
        return (
            <div className="w-[300px] h-[300px] bg-gray-100 rounded-lg flex items-center justify-center">
                <span className="text-gray-400">No structure available</span>
            </div>
        );
    }

    return (
        <img
            src={imageUrl}
            alt="Molecule structure"
            className="w-[300px] h-[300px] rounded-lg border border-gray-200"
        />
    );
}


export default function PredictionsPage() {
    const [smiles, setSmiles] = useState('');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<PredictionResult | null>(null);
    const [error, setError] = useState<string | null>(null);

    const handlePredict = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
            const response = await fetch(`${apiUrl}/api/predictions`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ smiles }),
            });

            if (!response.ok) {
                throw new Error('Failed to get predictions');
            }

            const data = await response.json();
            setResult(data);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to predict');
            setResult(null);
        } finally {
            setLoading(false);
        }
    };

    const examples = [
        { name: 'Benzene', smiles: 'c1ccccc1' },
        { name: 'Ethanol', smiles: 'CCO' },
        { name: 'Polystyrene repeat unit', smiles: 'C(C)c1ccccc1' },
    ];

    return (
        <div className="min-h-screen bg-gradient-to-br from-purple-50 to-pink-100">
            <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
                <h1 className="text-4xl font-bold text-gray-900 mb-8 text-center">
                    Property Predictions
                </h1>

                {/* Input Form */}
                <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
                    <form onSubmit={handlePredict}>
                        <div className="mb-6">
                            <label className="block text-lg font-medium text-gray-700 mb-2">
                                Enter SMILES String
                            </label>
                            <input
                                type="text"
                                value={smiles}
                                onChange={(e) => setSmiles(e.target.value)}
                                required
                                className="w-full px-4 py-3 text-lg border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                                placeholder="e.g., c1ccccc1"
                            />
                        </div>

                        <div className="mb-6">
                            <div className="text-sm text-gray-600 mb-2">Quick examples:</div>
                            <div className="flex flex-wrap gap-2">
                                {examples.map((example) => (
                                    <button
                                        key={example.smiles}
                                        type="button"
                                        onClick={() => setSmiles(example.smiles)}
                                        className="text-sm bg-gray-100 hover:bg-gray-200 px-3 py-1 rounded-md transition-colors"
                                    >
                                        {example.name}
                                    </button>
                                ))}
                            </div>
                        </div>

                        <button
                            type="submit"
                            disabled={loading || !smiles}
                            className="w-full bg-purple-600 hover:bg-purple-700 disabled:bg-gray-400 text-white py-3 rounded-lg font-medium text-lg transition-colors"
                        >
                            {loading ? 'Predicting...' : 'Predict Properties'}
                        </button>
                    </form>
                </div>

                {/* Error Message */}
                {error && (
                    <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-8">
                        Error: {error}
                    </div>
                )}

                {/* Results */}
                {result && (
                    <div className="bg-white rounded-lg shadow-lg p-8">
                        <h2 className="text-2xl font-bold text-gray-900 mb-6">Prediction Results</h2>

                        {/* Molecule Visualization */}
                        <div className="mb-6 flex flex-col md:flex-row gap-6">
                            <div className="flex-1">
                                <div className="text-sm text-gray-600 mb-2">SMILES:</div>
                                <div className="text-lg font-mono text-gray-900 bg-gray-50 px-4 py-2 rounded">{result.smiles}</div>
                            </div>
                            <div className="flex-shrink-0">
                                <div className="text-sm text-gray-600 mb-2">2D Structure:</div>
                                <MoleculeImage smiles={result.smiles} />
                            </div>
                        </div>

                        <div className="grid md:grid-cols-2 gap-6">
                            {/* Tg */}
                            <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-4">
                                <h3 className="text-sm font-medium text-gray-700 mb-2">Glass Transition Temperature (Tg)</h3>
                                <div className="text-3xl font-bold text-blue-700">
                                    {result.predictions.tg.value.toFixed(2)}°C
                                </div>
                                <div className="text-sm text-gray-600 mt-1">
                                    Confidence: {(result.predictions.tg.confidence * 100).toFixed(1)}%
                                </div>
                            </div>

                            {/* FFV */}
                            <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-4">
                                <h3 className="text-sm font-medium text-gray-700 mb-2">Free Volume Fraction (FFV)</h3>
                                <div className="text-3xl font-bold text-green-700">
                                    {result.predictions.ffv.value.toFixed(4)}
                                </div>
                                <div className="text-sm text-gray-600 mt-1">
                                    Confidence: {(result.predictions.ffv.confidence * 100).toFixed(1)}%
                                </div>
                            </div>

                            {/* Tc */}
                            <div className="bg-gradient-to-br from-amber-50 to-amber-100 rounded-lg p-4">
                                <h3 className="text-sm font-medium text-gray-700 mb-2">Crystallization Temperature (Tc)</h3>
                                <div className="text-3xl font-bold text-amber-700">
                                    {result.predictions.tc.value.toFixed(2)}°C
                                </div>
                                <div className="text-sm text-gray-600 mt-1">
                                    Confidence: {(result.predictions.tc.confidence * 100).toFixed(1)}%
                                </div>
                            </div>

                            {/* Density */}
                            <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-4">
                                <h3 className="text-sm font-medium text-gray-700 mb-2">Density</h3>
                                <div className="text-3xl font-bold text-purple-700">
                                    {result.predictions.density.value.toFixed(3)} g/cm³
                                </div>
                                <div className="text-sm text-gray-600 mt-1">
                                    Confidence: {(result.predictions.density.confidence * 100).toFixed(1)}%
                                </div>
                            </div>

                            {/* Rg */}
                            <div className="bg-gradient-to-br from-pink-50 to-pink-100 rounded-lg p-4 md:col-span-2">
                                <h3 className="text-sm font-medium text-gray-700 mb-2">Radius of Gyration (Rg)</h3>
                                <div className="text-3xl font-bold text-pink-700">
                                    {result.predictions.rg.value.toFixed(2)} Å
                                </div>
                                <div className="text-sm text-gray-600 mt-1">
                                    Confidence: {(result.predictions.rg.confidence * 100).toFixed(1)}%
                                </div>
                            </div>
                        </div>

                        <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                            <div className="text-sm text-yellow-800">
                                <strong>Note:</strong> These predictions are currently placeholder values.
                                Integrate the v85 Random Forest model for real predictions.
                            </div>
                        </div>
                    </div>
                )}

                {/* Info Section */}
                <div className="mt-8 bg-white rounded-lg shadow-md p-6">
                    <h3 className="text-lg font-bold text-gray-900 mb-3">About the Model</h3>
                    <ul className="space-y-2 text-gray-600">
                        <li>• <strong>Model:</strong> Random Forest Ensemble (v85)</li>
                        <li>• <strong>Features:</strong> 21 chemistry features automatically extracted</li>
                        <li>• <strong>Score:</strong> 0.07533 (Private) - Tied 1st place on Kaggle</li>
                        <li>• <strong>Properties:</strong> Predicts Tg, FFV, Tc, Density, Rg</li>
                    </ul>
                </div>
            </div>
        </div>
    );
}
