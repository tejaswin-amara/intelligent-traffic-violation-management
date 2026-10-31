
import { useQuery } from '@tanstack/react-query';
import { fetchWithAuth } from '../api/client';
import { Plus } from 'lucide-react';

export function Drivers() {
  const { data: drivers, isLoading, error } = useQuery({
    queryKey: ['drivers'],
    queryFn: () => fetchWithAuth('/drivers/')
  });

  if (isLoading) return <div>Loading drivers...</div>;
  if (error) return <div>Error loading drivers: {(error as Error).message}</div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Drivers</h1>
        <button className="bg-blue-600 text-white px-4 py-2 rounded flex items-center gap-2 hover:bg-blue-700">
          <Plus size={20} />
          <span>Register Driver</span>
        </button>
      </div>

      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <ul className="divide-y divide-gray-200">
          {drivers?.map((driver: any) => (
            <li key={driver.id} className="p-4 hover:bg-gray-50">
              <div className="flex justify-between items-center">
                <div>
                  <h3 className="text-lg font-medium text-blue-600">Licence ends in {driver.licence_last4}</h3>
                  <p className="text-sm text-gray-500">Class: {driver.licence_class}</p>
                </div>
                <div className="text-sm">
                  <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${driver.licence_status === 'valid' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                    {driver.licence_status}
                  </span>
                </div>
              </div>
            </li>
          ))}
          {(!drivers || drivers.length === 0) && (
            <li className="p-8 text-center text-gray-500">
              No drivers found.
            </li>
          )}
        </ul>
      </div>
    </div>
  );
}
