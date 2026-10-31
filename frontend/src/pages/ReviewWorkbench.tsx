import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchWithAuth } from '../api/client';
import { Check, X, AlertCircle } from 'lucide-react';

export function ReviewWorkbench() {
  const { data: violations, refetch, isLoading } = useQuery({
    queryKey: ['violations-draft'],
    queryFn: () => fetchWithAuth('/violations/')
  });

  const [rationale, setRationale] = useState('');
  const [error, setError] = useState('');

  const handleReview = async (id: string, decision: string) => {
    if (!rationale) {
        setError('Rationale is required');
        return;
    }
    setError('');

    try {
        await fetchWithAuth(`/violations/${id}/review`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ decision, rationale })
        });
        setRationale('');
        refetch();
    } catch (err: any) {
        setError(err.message || 'Review action failed');
    }
  };

  const pendingViolations = violations?.filter((v: any) => v.status === 'draft') || [];

  if (isLoading) return <div>Loading...</div>;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Review Workbench</h1>

      {error && <div className="bg-red-50 text-red-600 p-4 rounded">{error}</div>}

      {pendingViolations.length === 0 ? (
          <div className="bg-white p-8 text-center text-gray-500 shadow rounded">
              No pending violations to review.
          </div>
      ) : (
        <div className="grid gap-6 grid-cols-1">
          {pendingViolations.map((violation: any) => (
            <div key={violation.id} className="bg-white shadow rounded p-6">
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div>
                  <span className="text-gray-500 text-sm">Violation ID</span>
                  <p className="font-medium truncate">{violation.id}</p>
                </div>
                <div>
                  <span className="text-gray-500 text-sm">Event Time</span>
                  <p className="font-medium">{new Date(violation.event_at).toLocaleString()}</p>
                </div>
              </div>

              <div className="mt-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">Decision Rationale</label>
                <textarea
                    value={rationale}
                    onChange={e => setRationale(e.target.value)}
                    className="w-full border-gray-300 rounded-md border p-2"
                    rows={3}
                    placeholder="Enter reason for decision..."
                />
              </div>

              <div className="mt-4 flex gap-4">
                <button
                  onClick={() => handleReview(violation.id, 'approved')}
                  className="flex-1 bg-green-600 text-white p-2 rounded flex items-center justify-center gap-2 hover:bg-green-700"
                >
                  <Check size={18} /> Approve
                </button>
                <button
                  onClick={() => handleReview(violation.id, 'needs_information')}
                  className="flex-1 bg-yellow-500 text-white p-2 rounded flex items-center justify-center gap-2 hover:bg-yellow-600"
                >
                  <AlertCircle size={18} /> Return
                </button>
                <button
                  onClick={() => handleReview(violation.id, 'rejected')}
                  className="flex-1 bg-red-600 text-white p-2 rounded flex items-center justify-center gap-2 hover:bg-red-700"
                >
                  <X size={18} /> Reject
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
