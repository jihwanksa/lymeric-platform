"use client";

import { useState } from 'react';
import { useAuth } from '../context/AuthContext';

interface SearchResult {
    id: string;
    name: string;
    smiles: string;
    canonical_smiles: string;
    similarity?: number;
}

export default function SearchPage() {
    const [query, setQuery] = useState('');
    const [searchType, setSearchType] = useState<'substructure' | 'similarity'>('substructure');
    const [threshold, setThreshold] = useState(0.7);
    const [results, setResults] = useState<SearchResult[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const { token } = useAuth();

    const handleSearch = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        setResults([]);

        try {
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
            const endpoint = searchType === 'substructure' ? 'substructure' : 'similarity';

            const response = await fetch(`${apiUrl}/api/search/${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    // 'Authorization': `Bearer ${token}` // Optional: protect if needed
                },
                body: JSON.stringify({
                    query_smiles: query,
                    threshold: threshold,
                    limit: 100
                }),
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.detail || 'Search failed');
            }

            const data = await response.json();
            setResults(data);
        } catch (err: any) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-7xl mx-auto">
                <h1 className="text-3xl font-bold text-gray-900 mb-8">Advanced Search</h1>

                <div className="bg-white rounded-lg shadow p-6 mb-8">
                    <form onSubmit={handleSearch} className="space-y-6">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Search Type
                            </label>
                            <div className="flex space-x-4">
                                <button
                                    type="button"
                                    onClick={() => setSearchType('substructure')}
                                    className={`px-4 py-2 rounded-md ${searchType === 'substructure'
                                            ? 'bg-blue-600 text-white'
                                            : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                                        }`}
                                >
                                    Substructure Match
                                </button>
                                <button
                                    type="button"
                                    onClick={() => setSearchType('similarity')}
                                    className={`px-4 py-2 rounded-md ${searchType === 'similarity'
                                            ? 'bg-blue-600 text-white'
                                            : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                                        }`}
                                >
                                    Similarity Search
                                </button>
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Query SMILES
                            </label>
                            <input
                                type="text"
                                required
                                value={query}
                                onChange={(e) => setQuery(e.target.value)}
                                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                                placeholder="e.g., c1ccccc1"
                            />
                        </div>

                        {searchType === 'similarity' && (
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Similarity Threshold ({threshold})
                                </label>
                                <input
                                    type="range"
                                    min="0"
                                    max="1"
                                    step="0.05"
                                    value={threshold}
                                    onChange={(e) => setThreshold(parseFloat(e.target.value))}
                                    className="w-full"
                                />
                            </div>
                        )}

                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400"
                        >
                            {loading ? 'Searching...' : 'Search'}
                        </button>
                    </form>
                </div>

                {error && (
                    <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-8">
                        {error}
                    </div>
                )}

                {results.length > 0 && (
                    <div className="bg-white rounded-lg shadow overflow-hidden">
                        <div className="px-6 py-4 border-b border-gray-200">
                            <h2 className="text-lg font-medium text-gray-900">
                                Results ({results.length})
                            </h2>
                        </div>
                        <ul className="divide-y divide-gray-200">
                            {results.map((result) => (
                                <li key={result.id} className="px-6 py-4 hover:bg-gray-50">
                                    <div className="flex items-center justify-between">
                                        <div>
                                            <div className="text-sm font-medium text-blue-600">
                                                {result.name}
                                            </div>
                                            <div className="text-sm text-gray-500 font-mono mt-1">
                                                {result.smiles}
                                            </div>
                                        </div>
                                        {result.similarity !== undefined && (
                                            <div className="text-sm font-medium text-gray-900">
                                                {(result.similarity * 100).toFixed(1)}% match
                                            </div>
                                        )}
                                    </div>
                                </li>
                            ))}
                        </ul>
                    </div>
                )}
            </div>
        </div>
    );
}
