"use client";

import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';

interface JobStatus {
    job_id: string;
    status: string;
    result?: any;
    error?: string;
}

export default function TrainingPage() {
    const [property, setProperty] = useState('tg');
    const [method, setMethod] = useState('basic');
    const [nEstimators, setNEstimators] = useState(100);
    const [nTrials, setNTrials] = useState(50);
    const [timeLimit, setTimeLimit] = useState(300);
    const [activeJob, setActiveJob] = useState<string | null>(null);
    const [jobStatus, setJobStatus] = useState<JobStatus | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const { token } = useAuth();

    // Poll for job status
    useEffect(() => {
        let interval: NodeJS.Timeout;
        if (activeJob && jobStatus?.status !== 'completed' && jobStatus?.status !== 'failed') {
            interval = setInterval(async () => {
                try {
                    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
                    const response = await fetch(`${apiUrl}/api/train/status/${activeJob}`);
                    const data = await response.json();
                    setJobStatus(data);

                    if (data.status === 'completed' || data.status === 'failed') {
                        setActiveJob(null);
                    }
                } catch (err) {
                    console.error('Failed to poll status:', err);
                }
            }, 2000);
        }
        return () => clearInterval(interval);
    }, [activeJob, jobStatus]);

    const handleTrain = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        setJobStatus(null);

        try {
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
            const response = await fetch(`${apiUrl}/api/train/start`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    // 'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    property,
                    method,
                    n_estimators: nEstimators,
                    n_trials: nTrials,
                    time_limit: timeLimit
                }),
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.detail || 'Failed to start training');
            }

            const data = await response.json();
            setActiveJob(data.job_id);
            setJobStatus({ job_id: data.job_id, status: 'pending' });
        } catch (err: any) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-4xl mx-auto">
                <h1 className="text-3xl font-bold text-gray-900 mb-8">Model Training</h1>

                <div className="bg-white rounded-lg shadow p-6 mb-8">
                    <form onSubmit={handleTrain} className="space-y-6">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Target Property
                                </label>
                                <select
                                    value={property}
                                    onChange={(e) => setProperty(e.target.value)}
                                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                                >
                                    <option value="tg">Glass Transition Temp (Tg)</option>
                                    <option value="ffv">Free Volume (FFV)</option>
                                    <option value="tc">Critical Temp (Tc)</option>
                                    <option value="density">Density</option>
                                    <option value="rg">Radius of Gyration (Rg)</option>
                                </select>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Training Method
                                </label>
                                <select
                                    value={method}
                                    onChange={(e) => setMethod(e.target.value)}
                                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                                >
                                    <option value="basic">Basic Random Forest</option>
                                    <option value="optuna">Optuna Optimization</option>
                                    <option value="autogluon">AutoGluon AutoML</option>
                                </select>
                            </div>
                        </div>

                        {method === 'basic' && (
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Number of Trees ({nEstimators})
                                </label>
                                <input
                                    type="range"
                                    min="10"
                                    max="500"
                                    step="10"
                                    value={nEstimators}
                                    onChange={(e) => setNEstimators(parseInt(e.target.value))}
                                    className="w-full"
                                />
                            </div>
                        )}

                        {method === 'optuna' && (
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Number of Trials ({nTrials})
                                </label>
                                <input
                                    type="number"
                                    min="10"
                                    max="200"
                                    value={nTrials}
                                    onChange={(e) => setNTrials(parseInt(e.target.value))}
                                    className="w-full px-4 py-2 border border-gray-300 rounded-md"
                                />
                            </div>
                        )}

                        {method === 'autogluon' && (
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Time Limit (seconds)
                                </label>
                                <input
                                    type="number"
                                    min="60"
                                    max="3600"
                                    value={timeLimit}
                                    onChange={(e) => setTimeLimit(parseInt(e.target.value))}
                                    className="w-full px-4 py-2 border border-gray-300 rounded-md"
                                />
                            </div>
                        )}

                        <button
                            type="submit"
                            disabled={loading || !!activeJob}
                            className="w-full bg-green-600 text-white py-3 px-4 rounded-md hover:bg-green-700 disabled:bg-gray-400 font-medium"
                        >
                            {activeJob ? 'Training in Progress...' : 'Start Training'}
                        </button>
                    </form>
                </div>

                {error && (
                    <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-8">
                        {error}
                    </div>
                )}

                {jobStatus && (
                    <div className="bg-white rounded-lg shadow p-6">
                        <h2 className="text-lg font-medium text-gray-900 mb-4">
                            Job Status: <span className={`uppercase ${jobStatus.status === 'completed' ? 'text-green-600' :
                                    jobStatus.status === 'failed' ? 'text-red-600' :
                                        'text-blue-600'
                                }`}>{jobStatus.status}</span>
                        </h2>

                        {jobStatus.status === 'running' && (
                            <div className="animate-pulse flex space-x-4">
                                <div className="flex-1 space-y-4 py-1">
                                    <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                                    <div className="space-y-2">
                                        <div className="h-4 bg-gray-200 rounded"></div>
                                        <div className="h-4 bg-gray-200 rounded w-5/6"></div>
                                    </div>
                                </div>
                            </div>
                        )}

                        {jobStatus.result && (
                            <div className="space-y-4">
                                <div className="grid grid-cols-2 gap-4">
                                    <div className="bg-gray-50 p-4 rounded">
                                        <div className="text-sm text-gray-500">Test R² Score</div>
                                        <div className="text-2xl font-bold text-gray-900">
                                            {jobStatus.result.test_r2.toFixed(4)}
                                        </div>
                                    </div>
                                    <div className="bg-gray-50 p-4 rounded">
                                        <div className="text-sm text-gray-500">Test MAE</div>
                                        <div className="text-2xl font-bold text-gray-900">
                                            {jobStatus.result.test_mae.toFixed(4)}
                                        </div>
                                    </div>
                                </div>
                                <pre className="bg-gray-900 text-gray-100 p-4 rounded overflow-x-auto text-sm">
                                    {JSON.stringify(jobStatus.result, null, 2)}
                                </pre>
                            </div>
                        )}

                        {jobStatus.error && (
                            <div className="text-red-600 bg-red-50 p-4 rounded">
                                Error: {jobStatus.error}
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}
