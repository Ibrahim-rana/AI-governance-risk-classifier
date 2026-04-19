import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getAssessments, getDocuments } from '../api';
import { Search, Plus, FileText, Activity, AlertTriangle } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns'; // We need to add this

const Dashboard = () => {
  const [assessments, setAssessments] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [assessData, docData] = await Promise.all([
          getAssessments().catch(() => []),
          getDocuments().catch(() => [])
        ]);
        setAssessments(assessData || []);
        setDocuments(docData || []);
      } catch (err) {
        console.error("Failed to fetch dashboard data", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const getRiskColor = (classification) => {
    if (classification?.includes('Prohibited')) return 'bg-risk-prohibited text-white';
    if (classification?.includes('High')) return 'bg-risk-high text-white';
    if (classification?.includes('Limited')) return 'bg-risk-limited text-white';
    return 'bg-risk-minimal text-white';
  };

  const getRiskBgLight = (classification) => {
    if (classification?.includes('Prohibited')) return 'bg-red-50 text-red-700 border-red-200';
    if (classification?.includes('High')) return 'bg-orange-50 text-orange-700 border-orange-200';
    if (classification?.includes('Limited')) return 'bg-yellow-50 text-yellow-700 border-yellow-200';
    return 'bg-green-50 text-green-700 border-green-200';
  };

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Dashboard</h1>
          <p className="mt-1 text-sm text-slate-500">Overview of AI governance risk assessments.</p>
        </div>
        <Link 
          to="/assessment" 
          className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700"
        >
          <Plus className="-ml-1 mr-2 h-5 w-5" aria-hidden="true" />
          New Assessment
        </Link>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white overflow-hidden shadow-sm rounded-lg border border-slate-200">
          <div className="p-5 flex items-center">
            <div className="flex-shrink-0">
              <Activity className="h-6 w-6 text-slate-400" />
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-slate-500 truncate">Total Assessments</dt>
                <dd className="text-2xl font-semibold text-slate-900">{assessments.length}</dd>
              </dl>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow-sm rounded-lg border border-slate-200">
          <div className="p-5 flex items-center">
            <div className="flex-shrink-0">
              <AlertTriangle className="h-6 w-6 text-orange-400" />
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-slate-500 truncate">High/Prohibited Risk</dt>
                <dd className="text-2xl font-semibold text-slate-900">
                  {assessments.filter(a => a.classification?.includes('High') || a.classification?.includes('Prohibited')).length}
                </dd>
              </dl>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow-sm rounded-lg border border-slate-200 flex flex-col">
          <div className="p-5 flex items-center flex-1">
            <div className="flex-shrink-0">
              <FileText className="h-6 w-6 pl-0.5 text-blue-400" />
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-slate-500 truncate">Ingested Documents</dt>
                <dd className="text-2xl font-semibold text-slate-900">
                  {documents.filter(d => d.status === 'ingested').length}
                </dd>
              </dl>
            </div>
          </div>
          <div className="bg-slate-50 px-5 py-3 border-t border-slate-200">
            <div className="text-sm">
              <Link to="/documents" className="font-medium text-primary-600 hover:text-primary-500">
                Manage references
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Assessments */}
      <div className="bg-white shadow-sm rounded-lg border border-slate-200">
        <div className="px-4 py-5 border-b border-slate-200 sm:px-6 flex justify-between items-center">
          <h3 className="text-lg leading-6 font-medium text-slate-900">Recent Assessments</h3>
          <div className="relative rounded-md shadow-sm">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search className="h-4 w-4 text-slate-400" />
            </div>
            <input
              type="text"
              className="focus:ring-primary-500 focus:border-primary-500 block w-full pl-10 sm:text-sm border-slate-300 rounded-md py-2 border"
              placeholder="Search use cases..."
            />
          </div>
        </div>
        
        {assessments.length === 0 ? (
          <div className="text-center py-12">
            <Activity className="mx-auto h-12 w-12 text-slate-300" />
            <h3 className="mt-2 text-sm font-medium text-slate-900">No assessments</h3>
            <p className="mt-1 text-sm text-slate-500">Get started by assessing a new AI use case.</p>
            <div className="mt-6">
              <Link
                to="/assessment"
                className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700"
              >
                <Plus className="-ml-1 mr-2 h-5 w-5" aria-hidden="true" />
                New Assessment
              </Link>
            </div>
          </div>
        ) : (
          <ul className="divide-y divide-slate-200">
            {assessments.map((assessment) => (
              <li key={assessment.id} className="hover:bg-slate-50 transition-colors">
                <div className="px-4 py-4 sm:px-6 flex items-center justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-medium text-primary-600 truncate">
                        {assessment.title}
                      </p>
                      <div className="ml-2 flex-shrink-0 flex">
                        <p className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full border ${getRiskBgLight(assessment.classification)}`}>
                          {assessment.classification}
                        </p>
                      </div>
                    </div>
                    <div className="mt-2 flex justify-between">
                      <div className="sm:flex">
                        <p className="flex items-center text-sm text-slate-500">
                          Confidence: {Math.round(assessment.confidence * 100)}%
                        </p>
                      </div>
                      <div className="mt-2 flex items-center text-sm text-slate-500 sm:mt-0">
                        <p>
                          {new Date(assessment.timestamp).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
