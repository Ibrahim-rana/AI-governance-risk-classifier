import React, { useState } from 'react';
import { assessUseCase, downloadPdfReport } from '../api';
import { 
  AlertCircle, CheckCircle2, FileText, ChevronRight, ShieldAlert, 
  Download, Loader2, ArrowRight, ArrowLeft, BookOpen, AlertTriangle 
} from 'lucide-react';
import ChecklistPanel from '../components/ChecklistPanel';

const Assessment = () => {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    domain: '',
    user_type: '',
    deployment_context: '',
    ai_technique: '',
    human_oversight_level: '',
    affected_group_size: '',
    is_safety_component: false,
    personal_data: false,
    sensitive_data: false,
    automated_decisions: false,
    impacts_rights: false,
  });

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [pdfLoading, setPdfLoading] = useState(false);
  const [pdfError, setPdfError] = useState('');

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value,
    });
  };

  const nextStep = () => setStep((s) => Math.min(s + 1, 3));
  const prevStep = () => setStep((s) => Math.max(s - 1, 1));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      const data = await assessUseCase(formData);
      setResult(data);
      setStep(4); // Results step
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to analyze use case. Is the backend running?');
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPdf = async () => {
    if (!result?.id) return;
    setPdfLoading(true);
    setPdfError('');
    try {
      await downloadPdfReport(result.id, result.use_case_title);
    } catch (err) {
      const message =
        err.response?.status === 404
          ? 'Assessment not found. The server may have restarted.'
          : 'Failed to generate PDF report. Please try again.';
      setPdfError(message);
    } finally {
      setPdfLoading(false);
    }
  };

  const getRiskColor = (classification) => {
    if (classification?.includes('Prohibited')) return 'bg-red-100 text-red-800 border-red-200';
    if (classification?.includes('High')) return 'bg-orange-100 text-orange-800 border-orange-200';
    if (classification?.includes('Limited')) return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    return 'bg-green-100 text-green-800 border-green-200';
  };

  const getRiskIcon = (classification) => {
    if (classification?.includes('Prohibited') || classification?.includes('High')) {
      return <ShieldAlert className="h-8 w-8 text-current" />;
    }
    if (classification?.includes('Limited')) {
      return <AlertCircle className="h-8 w-8 text-current" />;
    }
    return <CheckCircle2 className="h-8 w-8 text-current" />;
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {!result && step < 4 && (
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-slate-900">New AI Risk Assessment</h1>
          <p className="mt-1 text-sm text-slate-500">
            Complete the structured intake form to evaluate compliance against the EU AI Act and GDPR.
          </p>
          
          {/* Progress Bar */}
          <div className="mt-6 flex items-center justify-between relative">
            <div className="absolute left-0 top-1/2 w-full h-1 bg-slate-200 -z-10 transform -translate-y-1/2 rounded"></div>
            <div className="absolute left-0 top-1/2 h-1 bg-primary-600 -z-10 transform -translate-y-1/2 transition-all duration-300" style={{ width: `${((step - 1) / 2) * 100}%` }}></div>
            
            {[1, 2, 3].map((num) => (
              <div key={num} className={`flex items-center justify-center w-8 h-8 rounded-full border-2 ${step >= num ? 'bg-primary-600 border-primary-600 text-white' : 'bg-white border-slate-300 text-slate-500'} font-semibold text-sm transition-colors`}>
                {num}
              </div>
            ))}
          </div>
          <div className="flex justify-between mt-2 text-xs font-medium text-slate-500">
            <span>System Profile</span>
            <span>Risk Factors</span>
            <span>Review & Submit</span>
          </div>
        </div>
      )}

      {/* Form Wizard */}
      {!result && step < 4 && (
        <div className="bg-white shadow-sm rounded-lg border border-slate-200 overflow-hidden">
          <div className="p-6">
            
            {/* Step 1: System Profile */}
            {step === 1 && (
              <div className="space-y-6 animate-in fade-in slide-in-from-right-4 duration-300">
                <h3 className="text-lg font-medium text-slate-900 border-b pb-2">1. System Profile</h3>
                <div>
                  <label className="block text-sm font-medium text-slate-700">System Title *</label>
                  <input type="text" name="title" required value={formData.title} onChange={handleInputChange} className="mt-1 block w-full border border-slate-300 rounded-md py-2 px-3 focus:ring-primary-500 focus:border-primary-500 sm:text-sm" placeholder="e.g., Automated Resume Screener" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700">Detailed Description *</label>
                  <textarea name="description" rows={4} required value={formData.description} onChange={handleInputChange} className="mt-1 block w-full border border-slate-300 rounded-md py-2 px-3 focus:ring-primary-500 focus:border-primary-500 sm:text-sm" placeholder="Describe what the AI system does..." />
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-700">Domain / Industry</label>
                    <select name="domain" value={formData.domain} onChange={handleInputChange} className="mt-1 block w-full border border-slate-300 rounded-md py-2 px-3 focus:ring-primary-500 focus:border-primary-500 sm:text-sm bg-white">
                      <option value="">Select Domain...</option>
                      <option value="Healthcare">Healthcare</option>
                      <option value="Finance">Finance / Banking</option>
                      <option value="Employment">HR / Employment</option>
                      <option value="Education">Education</option>
                      <option value="Law Enforcement">Law Enforcement</option>
                      <option value="Public Sector">Public Sector</option>
                      <option value="Other">Other</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700">AI Technique</label>
                    <select name="ai_technique" value={formData.ai_technique} onChange={handleInputChange} className="mt-1 block w-full border border-slate-300 rounded-md py-2 px-3 focus:ring-primary-500 focus:border-primary-500 sm:text-sm bg-white">
                      <option value="">Select Technique...</option>
                      <option value="ML classification">ML Classification</option>
                      <option value="LLM/GenAI">LLM / Generative AI</option>
                      <option value="Computer Vision">Computer Vision</option>
                      <option value="Biometrics">Biometric Recognition</option>
                      <option value="Other">Other / Classical AI</option>
                    </select>
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700">Deployment Context</label>
                  <select name="deployment_context" value={formData.deployment_context} onChange={handleInputChange} className="mt-1 block w-full border border-slate-300 rounded-md py-2 px-3 focus:ring-primary-500 focus:border-primary-500 sm:text-sm bg-white">
                    <option value="">Select Context...</option>
                    <option value="Internal Tool">Internal Tool (Employees)</option>
                    <option value="Customer-facing">Customer-facing Product</option>
                    <option value="Public-sector">Public-sector Service</option>
                  </select>
                </div>
              </div>
            )}

            {/* Step 2: Risk Factors */}
            {step === 2 && (
              <div className="space-y-6 animate-in fade-in slide-in-from-right-4 duration-300">
                <h3 className="text-lg font-medium text-slate-900 border-b pb-2">2. Deployment Details & Risk Factors</h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-slate-700">Human Oversight Level</label>
                    <select name="human_oversight_level" value={formData.human_oversight_level} onChange={handleInputChange} className="mt-1 block w-full border border-slate-300 rounded-md py-2 px-3 focus:ring-primary-500 focus:border-primary-500 sm:text-sm bg-white">
                      <option value="">Select Oversight...</option>
                      <option value="Full Automation">Full Automation (No Human)</option>
                      <option value="Human-in-the-loop">Human-in-the-loop (Approves before action)</option>
                      <option value="Human review after">Human review post-action</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700">Affected Group Size</label>
                    <select name="affected_group_size" value={formData.affected_group_size} onChange={handleInputChange} className="mt-1 block w-full border border-slate-300 rounded-md py-2 px-3 focus:ring-primary-500 focus:border-primary-500 sm:text-sm bg-white">
                      <option value="">Select Size...</option>
                      <option value="< 100">Less than 100</option>
                      <option value="100-10k">100 - 10,000</option>
                      <option value="> 10k">More than 10,000</option>
                    </select>
                  </div>
                </div>

                <div className="space-y-4 pt-4 border-t border-slate-200">
                  <div className="flex items-start bg-slate-50 p-3 rounded-md border border-slate-200">
                    <input id="is_safety_component" name="is_safety_component" type="checkbox" checked={formData.is_safety_component} onChange={handleInputChange} className="mt-1 focus:ring-primary-500 h-4 w-4 text-primary-600 border-slate-300 rounded" />
                    <div className="ml-3 text-sm">
                      <label htmlFor="is_safety_component" className="font-semibold text-slate-900">Safety Component</label>
                      <p className="text-slate-500">System is a safety component of a regulated product (e.g., medical device, vehicle).</p>
                    </div>
                  </div>

                  <div className="flex items-start">
                    <input id="automated_decisions" name="automated_decisions" type="checkbox" checked={formData.automated_decisions} onChange={handleInputChange} className="mt-1 focus:ring-primary-500 h-4 w-4 text-primary-600 border-slate-300 rounded" />
                    <div className="ml-3 text-sm">
                      <label htmlFor="automated_decisions" className="font-medium text-slate-700">Automated Decision-Making</label>
                      <p className="text-slate-500">System makes decisions without meaningful human intervention.</p>
                    </div>
                  </div>

                  <div className="flex items-start">
                    <input id="impacts_rights" name="impacts_rights" type="checkbox" checked={formData.impacts_rights} onChange={handleInputChange} className="mt-1 focus:ring-primary-500 h-4 w-4 text-primary-600 border-slate-300 rounded" />
                    <div className="ml-3 text-sm">
                      <label htmlFor="impacts_rights" className="font-medium text-slate-700">Impacts Rights or Opportunities</label>
                      <p className="text-slate-500">Output affects access to jobs, education, credit, public services, etc.</p>
                    </div>
                  </div>

                  <div className="flex items-start">
                    <input id="personal_data" name="personal_data" type="checkbox" checked={formData.personal_data} onChange={handleInputChange} className="mt-1 focus:ring-primary-500 h-4 w-4 text-primary-600 border-slate-300 rounded" />
                    <div className="ml-3 text-sm">
                      <label htmlFor="personal_data" className="font-medium text-slate-700">Processes Personal Data</label>
                    </div>
                  </div>

                  <div className="flex items-start">
                    <input id="sensitive_data" name="sensitive_data" type="checkbox" checked={formData.sensitive_data} onChange={handleInputChange} className="mt-1 focus:ring-primary-500 h-4 w-4 text-primary-600 border-slate-300 rounded" />
                    <div className="ml-3 text-sm">
                      <label htmlFor="sensitive_data" className="font-medium text-slate-700">Processes Sensitive Data</label>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Step 3: Review */}
            {step === 3 && (
              <div className="space-y-6 animate-in fade-in slide-in-from-right-4 duration-300">
                <h3 className="text-lg font-medium text-slate-900 border-b pb-2">3. Review & Submit</h3>
                <div className="bg-slate-50 p-4 rounded-lg border border-slate-200 space-y-3 text-sm">
                  <div className="grid grid-cols-3 border-b border-slate-200 pb-2">
                    <span className="font-medium text-slate-500">Title</span>
                    <span className="col-span-2 font-semibold text-slate-900">{formData.title}</span>
                  </div>
                  <div className="grid grid-cols-3 border-b border-slate-200 pb-2">
                    <span className="font-medium text-slate-500">Domain</span>
                    <span className="col-span-2 font-semibold text-slate-900">{formData.domain || 'Not specified'}</span>
                  </div>
                  <div className="grid grid-cols-3 border-b border-slate-200 pb-2">
                    <span className="font-medium text-slate-500">AI Technique</span>
                    <span className="col-span-2 font-semibold text-slate-900">{formData.ai_technique || 'Not specified'}</span>
                  </div>
                  <div className="grid grid-cols-3 border-b border-slate-200 pb-2">
                    <span className="font-medium text-slate-500">Human Oversight</span>
                    <span className="col-span-2 font-semibold text-slate-900">{formData.human_oversight_level || 'Not specified'}</span>
                  </div>
                  <div className="grid grid-cols-3 pt-2">
                    <span className="font-medium text-slate-500">Data Flags</span>
                    <span className="col-span-2 text-slate-900 space-x-2">
                      {formData.personal_data && <span className="bg-blue-100 text-blue-800 px-2 py-0.5 rounded text-xs">Personal Data</span>}
                      {formData.sensitive_data && <span className="bg-purple-100 text-purple-800 px-2 py-0.5 rounded text-xs">Sensitive Data</span>}
                      {formData.automated_decisions && <span className="bg-red-100 text-red-800 px-2 py-0.5 rounded text-xs">Auto Decisions</span>}
                      {!formData.personal_data && !formData.sensitive_data && !formData.automated_decisions && 'None Checked'}
                    </span>
                  </div>
                </div>

                {error && (
                  <div className="rounded-md bg-red-50 p-4 border border-red-200">
                    <div className="flex">
                      <AlertCircle className="h-5 w-5 text-red-400 mt-0.5" />
                      <p className="ml-3 text-sm text-red-700">{error}</p>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Navigation Buttons */}
            <div className="pt-6 mt-6 border-t border-slate-200 flex justify-between">
              {step > 1 ? (
                <button type="button" onClick={prevStep} className="inline-flex items-center px-4 py-2 border border-slate-300 shadow-sm text-sm font-medium rounded-md text-slate-700 bg-white hover:bg-slate-50">
                  <ArrowLeft className="mr-2 h-4 w-4" /> Back
                </button>
              ) : <div></div>}

              {step < 3 ? (
                <button type="button" onClick={nextStep} disabled={!formData.title || !formData.description} className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 disabled:bg-primary-300">
                  Continue <ArrowRight className="ml-2 h-4 w-4" />
                </button>
              ) : (
                <button type="button" onClick={handleSubmit} disabled={loading} className="inline-flex items-center px-6 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700">
                  {loading ? <Loader2 className="animate-spin -ml-1 mr-2 h-4 w-4" /> : <ShieldAlert className="mr-2 h-4 w-4" />}
                  Run Deterministic Assessment
                </button>
              )}
            </div>

          </div>
        </div>
      )}

      {/* Loading State for Assessment */}
      {loading && (
        <div className="bg-white shadow-sm rounded-lg border border-slate-200 h-[500px] flex flex-col items-center justify-center p-12">
          <div className="animate-pulse flex flex-col items-center">
            <div className="h-16 w-16 rounded-full bg-slate-200 mb-4 flex items-center justify-center">
              <Loader2 className="h-8 w-8 text-primary-500 animate-spin" />
            </div>
            <h3 className="text-lg font-medium text-slate-800">Applying Taxonomy Rules...</h3>
            <p className="mt-2 text-sm text-slate-500 text-center max-w-sm">
              Running deterministic mapping, evaluating triggered obligations, and generating evidence gap repository.
            </p>
          </div>
        </div>
      )}

      {/* Results View */}
      {result && !loading && (
        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
          <button onClick={() => {setResult(null); setStep(1);}} className="text-sm font-medium text-primary-600 hover:text-primary-800 flex items-center mb-2">
            <ArrowLeft className="w-4 h-4 mr-1" /> Start New Assessment
          </button>
          
          <div className="bg-white shadow-sm rounded-lg border border-slate-200 overflow-hidden">
            {/* Header Banner */}
            <div className={`px-6 py-6 border-b flex items-center justify-between ${getRiskColor(result.risk_classification)}`}>
              <div className="flex items-center">
                {getRiskIcon(result.risk_classification)}
                <div className="ml-4">
                  <h2 className="text-2xl font-bold leading-tight">{result.risk_classification}</h2>
                  <p className="text-sm opacity-90 mt-1 font-medium">Deterministic Rule Match</p>
                </div>
              </div>
            </div>

            <div className="p-6 space-y-8">
              {/* Rationale & LLM Analysis */}
              <div>
                <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider mb-3">Auditor Rationale</h3>
                <div className="prose prose-sm text-slate-700 bg-slate-50 p-5 rounded-md border border-slate-200 shadow-inner">
                  <p className="leading-relaxed">{result.summary_rationale}</p>
                </div>
              </div>

              {/* Why This Classification? - Deterministic reasoning */}
              {result.risk_reasoning && (
                <div>
                  <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider mb-3 flex items-center">
                    <AlertTriangle className="w-4 h-4 mr-2 text-amber-500" /> Why This Classification?
                  </h3>
                  <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 text-sm text-amber-900 leading-relaxed">
                    {result.risk_reasoning.split('**').map((part, i) =>
                      i % 2 === 1
                        ? <strong key={i}>{part}</strong>
                        : <span key={i}>{part}</span>
                    )}
                  </div>
                </div>
              )}

              {/* Obligations Panel */}
              {result.obligations && result.obligations.length > 0 && (
                <div>
                  <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider mb-3 flex items-center">
                    <BookOpen className="w-4 h-4 mr-2" /> Triggered Legal Obligations
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {result.obligations.map((obs, idx) => (
                      <div key={idx} className="bg-white border text-sm border-slate-200 rounded-lg p-4 shadow-sm border-l-4 border-l-indigo-500">
                        <div className="font-bold text-indigo-700 mb-1">{obs.article_ref}</div>
                        <p className="text-slate-800 font-medium mb-2">{obs.description}</p>
                        <div className="text-slate-500 text-xs bg-slate-50 p-2 rounded">
                          <span className="font-semibold text-slate-700">Evidence Required:</span> {obs.evidence_needed}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Evidence Checklist & Gap Repo */}
              <ChecklistPanel checklist={result.evidence_checklist} title="Evidence Checklist & Gap Repository" />

              {/* Flags with Traceability — only shown if a concrete reason exists */}
              {result.compliance_flags && result.compliance_flags.length > 0 && (() => {
                const flagsWithReasons = result.compliance_flags.filter(f => result.flag_details?.[f]);
                if (flagsWithReasons.length === 0) return null;

                return (
                  <div>
                    <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider mb-3">Compliance Concerns</h3>
                    <div className="flex flex-col gap-2">
                      {flagsWithReasons.map((flag, idx) => {
                        const reason = result.flag_details[flag];
                        // Extract article reference from brackets like [EU AI Act Art. 14]
                        const artMatch = reason.match(/\[([^\]]+)\]/);
                        const articleRef = artMatch ? artMatch[1] : null;
                        const reasonText = articleRef ? reason.replace(artMatch[0], '').trim() : reason;

                        return (
                          <div key={idx} className="flex items-start gap-3 bg-red-50 border border-red-200 rounded-lg px-4 py-3">
                            <AlertTriangle className="h-4 w-4 text-red-500 mt-0.5 flex-shrink-0" />
                            <div className="flex-1">
                              <div className="flex items-center gap-2 flex-wrap">
                                <span className="text-sm font-semibold text-red-700">{flag}</span>
                                {articleRef && (
                                  <span className="text-[10px] font-bold bg-red-200 text-red-800 px-1.5 py-0.5 rounded">
                                    {articleRef}
                                  </span>
                                )}
                              </div>
                              <p className="text-xs text-red-600 mt-1 leading-snug">
                                {reasonText}
                              </p>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                );
              })()}

              {/* Recommendations */}
              {result.recommendations && result.recommendations.length > 0 && (
                <div>
                  <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider mb-3">Recommended Actions</h3>
                  <ul className="space-y-2 bg-slate-50 rounded-lg border border-slate-200 p-4">
                    {result.recommendations.map((rec, idx) => (
                      <li key={idx} className="flex items-start text-sm text-slate-700">
                        <ChevronRight className="h-4 w-4 text-primary-500 mr-2 flex-shrink-0 mt-0.5" />
                        <span className="font-medium">{rec}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            {/* Export Footer */}
            <div className="bg-slate-100 px-6 py-5 border-t border-slate-200">
              <button
                onClick={handleDownloadPdf}
                disabled={pdfLoading}
                className="w-full inline-flex items-center justify-center px-5 py-3 border border-transparent rounded-lg shadow-sm text-base font-bold text-white bg-indigo-600 hover:bg-indigo-700 transition"
              >
                {pdfLoading ? (
                  <><Loader2 className="animate-spin h-5 w-5 mr-2" /> Generating Audit Report...</>
                ) : (
                  <><Download className="h-5 w-5 mr-2" /> Download Audit-Ready PDF</>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Assessment;
