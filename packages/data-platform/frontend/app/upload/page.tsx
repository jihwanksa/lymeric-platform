'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

interface PreviewData {
    file_id: string;
    filename: string;
    columns: string[];
    row_count: number;
    preview_data: Record<string, any>[];
    suggested_smiles_column: string | null;
}

interface ValidationResult {
    valid_count: number;
    invalid_count: number;
    errors: Array<{
        row: number;
        smiles: string;
        error: string;
    }>;
}

export default function UploadPage() {
    const router = useRouter();
    const [file, setFile] = useState<File | null>(null);
    const [preview, setPreview] = useState<PreviewData | null>(null);
    const [smilesColumn, setSmilesColumn] = useState<string>('');
    const [validation, setValidation] = useState<ValidationResult | null>(null);
    const [importing, setImporting] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState<string | null>(null);

    const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const selectedFile = e.target.files?.[0];
        if (!selectedFile) return;

        setFile(selectedFile);
        setError(null);
        setPreview(null);
        setValidation(null);

        // Upload and preview
        const formData = new FormData();
        formData.append('file', selectedFile);

        try {
            const response = await fetch('http://localhost:8000/api/upload/preview', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                throw new Error('Failed to upload file');
            }

            const data: PreviewData = await response.json();
            setPreview(data);
            setSmilesColumn(data.suggested_smiles_column || '');
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Upload failed');
        }
    };

    const handleValidate = async () => {
        if (!preview || !smilesColumn) return;

        setError(null);
        setValidation(null);

        try {
            const response = await fetch('http://localhost:8000/api/upload/validate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    file_id: preview.file_id,
                    smiles_column: smilesColumn,
                }),
            });

            if (!response.ok) {
                throw new Error('Validation failed');
            }

            const data: ValidationResult = await response.json();
            setValidation(data);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Validation failed');
        }
    };

    const handleImport = async () => {
        if (!preview || !smilesColumn) return;

        setImporting(true);
        setError(null);
        setSuccess(null);

        try {
            const response = await fetch('http://localhost:8000/api/upload/import', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    file_id: preview.file_id,
                    smiles_column: smilesColumn,
                    skip_duplicates: true,
                }),
            });

            if (!response.ok) {
                throw new Error('Import failed');
            }

            const data = await response.json();
            setSuccess(
                `Successfully imported ${data.imported_count} materials! ` +
                `(${data.duplicate_count} duplicates skipped, ${data.skipped_count} errors)`
            );

            // Reset form
            setTimeout(() => {
                router.push('/materials');
            }, 2000);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Import failed');
        } finally {
            setImporting(false);
        }
    };

    return (
        <div className="max-w-6xl mx-auto px-4 py-8">
            <div className="mb-8">
                <h1 className="text-3xl font-bold text-gray-900">Upload Materials</h1>
                <p className="mt-2 text-gray-600">
                    Upload a CSV or Excel file with material data. The file should contain a SMILES column.
                </p>
            </div>

            {/* File Upload */}
            <div className="bg-white rounded-lg shadow p-6 mb-6">
                <label className="block mb-4">
                    <span className="text-sm font-medium text-gray-700">Select File</span>
                    <input
                        type="file"
                        accept=".csv,.xlsx,.xls"
                        onChange={handleFileChange}
                        className="mt-2 block w-full text-sm text-gray-500
              file:mr-4 file:py-2 file:px-4
              file:rounded-lg file:border-0
              file:text-sm file:font-semibold
              file:bg-blue-50 file:text-blue-700
              hover:file:bg-blue-100"
                    />
                </label>

                {file && (
                    <p className="text-sm text-gray-600">
                        Selected: {file.name} ({(file.size / 1024).toFixed(1)} KB)
                    </p>
                )}
            </div>

            {/* Preview */}
            {preview && (
                <div className="bg-white rounded-lg shadow p-6 mb-6">
                    <h2 className="text-xl font-semibold mb-4">File Preview</h2>
                    <div className="mb-4 grid grid-cols-3 gap-4">
                        <div>
                            <p className="text-sm text-gray-600">Filename</p>
                            <p className="font-medium">{preview.filename}</p>
                        </div>
                        <div>
                            <p className="text-sm text-gray-600">Total Rows</p>
                            <p className="font-medium">{preview.row_count}</p>
                        </div>
                        <div>
                            <p className="text-sm text-gray-600">Columns</p>
                            <p className="font-medium">{preview.columns.length}</p>
                        </div>
                    </div>

                    {/* SMILES Column Selector */}
                    <div className="mb-4">
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            SMILES Column
                        </label>
                        <select
                            value={smilesColumn}
                            onChange={(e) => {
                                setSmilesColumn(e.target.value);
                                setValidation(null);
                            }}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md"
                        >
                            <option value="">-- Select Column --</option>
                            {preview.columns.map((col) => (
                                <option key={col} value={col}>
                                    {col}
                                    {col === preview.suggested_smiles_column && ' (suggested)'}
                                </option>
                            ))}
                        </select>
                    </div>

                    {/* Preview Table */}
                    <div className="overflow-x-auto mb-4">
                        <table className="min-w-full divide-y divide-gray-200">
                            <thead className="bg-gray-50">
                                <tr>
                                    {preview.columns.map((col) => (
                                        <th
                                            key={col}
                                            className={`px-4 py-2 text-left text-xs font-medium uppercase tracking-wider ${col === smilesColumn ? 'text-blue-600 bg-blue-50' : 'text-gray-500'
                                                }`}
                                        >
                                            {col}
                                        </th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-200">
                                {preview.preview_data.map((row, idx) => (
                                    <tr key={idx}>
                                        {preview.columns.map((col) => (
                                            <td
                                                key={col}
                                                className={`px-4 py-2 text-sm ${col === smilesColumn ? 'bg-blue-50 font-mono' : ''
                                                    }`}
                                            >
                                                {row[col] || '-'}
                                            </td>
                                        ))}
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>

                    <button
                        onClick={handleValidate}
                        disabled={!smilesColumn}
                        className="px-6 py-2 bg-blue-600 text-white rounded-lg font-medium
              hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
                    >
                        Validate SMILES
                    </button>
                </div>
            )}

            {/* Validation Results */}
            {validation && (
                <div className="bg-white rounded-lg shadow p-6 mb-6">
                    <h2 className="text-xl font-semibold mb-4">Validation Results</h2>

                    <div className="grid grid-cols-2 gap-4 mb-4">
                        <div className="p-4 bg-green-50 rounded-lg">
                            <p className="text-sm text-green-600">Valid</p>
                            <p className="text-2xl font-bold text-green-700">{validation.valid_count}</p>
                        </div>
                        <div className="p-4 bg-red-50 rounded-lg">
                            <p className="text-sm text-red-600">Invalid</p>
                            <p className="text-2xl font-bold text-red-700">{validation.invalid_count}</p>
                        </div>
                    </div>

                    {validation.errors.length > 0 && (
                        <div className="mb-4">
                            <h3 className="font-medium text-gray-900 mb-2">Errors</h3>
                            <div className="max-h-40 overflow-y-auto bg-red-50 rounded p-3">
                                {validation.errors.slice(0, 10).map((err, idx) => (
                                    <p key={idx} className="text-sm text-red-700 mb-1">
                                        Row {err.row}: {err.error} ({err.smiles})
                                    </p>
                                ))}
                                {validation.errors.length > 10 && (
                                    <p className="text-sm text-red-600 italic">
                                        ...and {validation.errors.length - 10} more errors
                                    </p>
                                )}
                            </div>
                        </div>
                    )}

                    {validation.valid_count > 0 && (
                        <button
                            onClick={handleImport}
                            disabled={importing}
                            className="px-6 py-3 bg-green-600 text-white rounded-lg font-medium
                hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
                        >
                            {importing ? 'Importing...' : `Import ${validation.valid_count} Materials`}
                        </button>
                    )}
                </div>
            )}

            {/* Error Message */}
            {error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
                    <p className="text-red-700">{error}</p>
                </div>
            )}

            {/* Success Message */}
            {success && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
                    <p className="text-green-700">{success}</p>
                    <p className="text-sm text-green-600 mt-1">Redirecting to materials page...</p>
                </div>
            )}
        </div>
    );
}
