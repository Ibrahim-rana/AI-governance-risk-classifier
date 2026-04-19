import React, { useState, useEffect } from 'react';
import { getDocuments, ingestDocuments } from '../api';
import { FileText, Database, RefreshCw, AlertCircle, CheckCircle, Clock } from 'lucide-react';

const Documents = () => {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [ingesting, setIngesting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const fetchDocs = async () => {
    try {
      const data = await getDocuments();
      setDocuments(data);
    } catch (err) {
      setError('Failed to load documents.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocs();
  }, []);

  const handleIngest = async () => {
    setIngesting(true);
    setError('');
    setSuccess('');
    try {
      const result = await ingestDocuments();
      setSuccess(`Successfully ingested ${result.ingested_files} files into ${result.total_chunks} vector chunks.`);
      await fetchDocs();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to ingest documents.');
    } finally {
      setIngesting(false);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'ingested': return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'pending': return <Clock className="h-5 w-5 text-yellow-500" />;
      case 'error': return <AlertCircle className="h-5 w-5 text-red-500" />;
      default: return <Clock className="h-5 w-5 text-slate-400" />;
    }
  };

  const formatSize = (bytes) => {
    if (!bytes || bytes === 0) return '-';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Regulatory Corpus</h1>
          <p className="mt-1 text-sm text-slate-500">
            Manage the policy documents used by the RAG classifier for retrieval and citation.
          </p>
        </div>
        <div className="mt-4 sm:mt-0">
          <button
            onClick={handleIngest}
            disabled={ingesting || loading}
            className={`inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white ${
              ingesting ? 'bg-primary-400 cursor-not-allowed' : 'bg-primary-600 hover:bg-primary-700'
            }`}
          >
            <RefreshCw className={`-ml-1 mr-2 h-5 w-5 ${ingesting ? 'animate-spin' : ''}`} />
            {ingesting ? 'Processing...' : 'Run Ingestion Pipeline'}
          </button>
        </div>
      </div>

      {error && (
        <div className="rounded-md bg-red-50 p-4 border border-red-200">
          <div className="flex">
            <AlertCircle className="h-5 w-5 text-red-400 mr-3" />
            <div className="text-sm text-red-700">{error}</div>
          </div>
        </div>
      )}

      {success && (
        <div className="rounded-md bg-green-50 p-4 border border-green-200">
          <div className="flex">
            <CheckCircle className="h-5 w-5 text-green-400 mr-3" />
            <div className="text-sm text-green-700">{success}</div>
          </div>
        </div>
      )}

      <div className="bg-white shadow-sm rounded-lg border border-slate-200 overflow-hidden">
        <div className="px-4 py-5 border-b border-slate-200 sm:px-6 bg-slate-50 flex items-center justify-between">
          <h3 className="text-lg leading-6 font-medium text-slate-900 flex items-center">
            <Database className="h-5 w-5 mr-2 text-slate-500" />
            Document Store Status
          </h3>
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
            ChromaDB Vector Store
          </span>
        </div>

        {loading ? (
          <div className="p-12 text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
            <p className="mt-4 text-sm text-slate-500">Loading documents...</p>
          </div>
        ) : documents.length === 0 ? (
          <div className="p-12 text-center">
            <FileText className="mx-auto h-12 w-12 text-slate-300" />
            <h3 className="mt-2 text-sm font-medium text-slate-900">No documents found</h3>
            <p className="mt-1 text-sm text-slate-500">Add .txt or .pdf files to the <code>data/regulations</code> directory.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-200">
              <thead className="bg-slate-50">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Document Name</th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Status</th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Size</th>
                  <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-slate-500 uppercase tracking-wider">Ingested Date</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-slate-200">
                {documents.map((doc, idx) => (
                  <tr key={idx} className="hover:bg-slate-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <FileText className="flex-shrink-0 h-5 w-5 text-slate-400 mr-3" />
                        <span className="text-sm font-medium text-slate-900">{doc.filename}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        {getStatusIcon(doc.status)}
                        <span className="ml-2 text-sm text-slate-500 capitalize">{doc.status}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500">
                      {formatSize(doc.file_size)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-slate-500">
                      {doc.ingested_at ? new Date(doc.ingested_at).toLocaleDateString() : '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default Documents;
