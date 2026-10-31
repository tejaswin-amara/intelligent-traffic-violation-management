import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { fetchWithAuth } from '../api/client';

export function ViolationCreate() {
  const navigate = useNavigate();
  const [jurisdictionId, setJurisdictionId] = useState('');
  const [vehicleId, setVehicleId] = useState('');
  const [offenceId, setOffenceId] = useState('');
  const [eventAt, setEventAt] = useState('');
  const [eventTimezone] = useState('UTC');
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsSubmitting(true);

    try {
      const response = await fetchWithAuth('/violations/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          jurisdiction_id: jurisdictionId,
          vehicle_id: vehicleId,
          offence_id: offenceId,
          event_at: new Date(eventAt).toISOString(),
          event_timezone: eventTimezone,
        }),
      });

      // Navigate to the review workbench or details page after creation
      navigate(`/violations/${response.id}`);
    } catch (err: any) {
      setError(err.message || 'Failed to create violation');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto bg-white p-8 shadow rounded">
      <h1 className="text-2xl font-bold mb-6">Create Violation</h1>

      {error && <div className="bg-red-50 text-red-600 p-4 rounded mb-6">{error}</div>}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">Jurisdiction ID</label>
          <input
            required
            type="text"
            className="mt-1 block w-full border border-gray-300 rounded-md p-2"
            value={jurisdictionId}
            onChange={(e) => setJurisdictionId(e.target.value)}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">Vehicle ID</label>
          <input
            required
            type="text"
            className="mt-1 block w-full border border-gray-300 rounded-md p-2"
            value={vehicleId}
            onChange={(e) => setVehicleId(e.target.value)}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">Offence ID</label>
          <input
            required
            type="text"
            className="mt-1 block w-full border border-gray-300 rounded-md p-2"
            value={offenceId}
            onChange={(e) => setOffenceId(e.target.value)}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">Event Time</label>
          <input
            required
            type="datetime-local"
            className="mt-1 block w-full border border-gray-300 rounded-md p-2"
            value={eventAt}
            onChange={(e) => setEventAt(e.target.value)}
          />
        </div>

        <div>
          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full bg-blue-600 text-white p-2 rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {isSubmitting ? 'Creating...' : 'Create Violation'}
          </button>
        </div>
      </form>
    </div>
  );
}
