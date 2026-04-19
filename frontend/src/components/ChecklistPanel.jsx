import React from 'react';
import { CheckCircle2, XCircle, AlertTriangle } from 'lucide-react';

const ChecklistPanel = ({ checklist = [], title = "Required Evidence Checklist" }) => {
  if (!checklist || checklist.length === 0) return null;

  return (
    <div className="mt-6 border border-slate-200 rounded-lg overflow-hidden">
      <div className="bg-slate-50 px-4 py-3 border-b border-slate-200">
        <h3 className="text-sm font-semibold text-slate-800">{title}</h3>
      </div>
      <table className="min-w-full divide-y divide-slate-200">
        <thead className="bg-white">
          <tr className="text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
            <th className="px-4 py-3">Requirement</th>
            <th className="px-4 py-3">Article/Reference</th>
            <th className="px-4 py-3">Status</th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-slate-100">
          {checklist.map((item, idx) => (
            <tr key={idx} className="hover:bg-slate-50">
              <td className="px-4 py-3 text-sm text-slate-800 font-medium">{item.item}</td>
              <td className="px-4 py-3 text-sm text-slate-600">{item.article_ref}</td>
              <td className="px-4 py-3 text-sm">
                {item.status === 'present' ? (
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    <CheckCircle2 className="w-3.5 h-3.5 mr-1" />
                    Present
                  </span>
                ) : (
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                    <AlertTriangle className="w-3.5 h-3.5 mr-1" />
                    Gap Detected
                  </span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ChecklistPanel;
