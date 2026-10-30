
import { useQuery } from '@tanstack/react-query';
import { fetchWithAuth } from '../api/client';
import { Plus } from 'lucide-react';

export function Vehicles() {
  const { data: vehicles, isLoading, error } = useQuery({
    queryKey: ['vehicles'],
    queryFn: () => fetchWithAuth('/vehicles/')
  });

  if (isLoading) return <div>Loading vehicles...</div>;
  if (error) return <div>Error loading vehicles: {(error as Error).message}</div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Vehicles</h1>
        <button className="bg-blue-600 text-white px-4 py-2 rounded flex items-center gap-2 hover:bg-blue-700">
          <Plus size={20} />
          <span>Register Vehicle</span>
        </button>
      </div>

      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <ul className="divide-y divide-gray-200">
          {vehicles?.map((vehicle: any) => (
            <li key={vehicle.id} className="p-4 hover:bg-gray-50">
              <div className="flex justify-between items-center">
                <div>
                  <h3 className="text-lg font-medium text-blue-600">{vehicle.registration_display}</h3>
                  <p className="text-sm text-gray-500">{vehicle.make} {vehicle.model} - {vehicle.vehicle_class}</p>
                </div>
                <div className="text-sm">
                  <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${vehicle.verification_status === 'verified' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                    {vehicle.verification_status}
                  </span>
                </div>
              </div>
            </li>
          ))}
          {(!vehicles || vehicles.length === 0) && (
            <li className="p-8 text-center text-gray-500">
              No vehicles found.
            </li>
          )}
        </ul>
      </div>
    </div>
  );
}
