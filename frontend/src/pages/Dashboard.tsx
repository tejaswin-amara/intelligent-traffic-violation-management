
import { useAuth } from '../context/AuthContext';
import { CarFront, Users, AlertCircle, FileText } from 'lucide-react';

export function Dashboard() {
  const { user } = useAuth();
  const orgName = user?.memberships[0] ? "Organisation Data" : "No Organisation";

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Welcome, {user?.display_name}</h1>
      <p className="text-gray-500">Overview for {orgName}</p>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100 flex items-center">
            <div className="p-3 bg-blue-100 rounded-full text-blue-600 mr-4">
                <CarFront size={24} />
            </div>
            <div>
                <p className="text-sm font-medium text-gray-500">Total Vehicles</p>
                <p className="text-2xl font-bold text-gray-900">0</p>
            </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100 flex items-center">
            <div className="p-3 bg-green-100 rounded-full text-green-600 mr-4">
                <Users size={24} />
            </div>
            <div>
                <p className="text-sm font-medium text-gray-500">Total Drivers</p>
                <p className="text-2xl font-bold text-gray-900">0</p>
            </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100 flex items-center">
            <div className="p-3 bg-red-100 rounded-full text-red-600 mr-4">
                <AlertCircle size={24} />
            </div>
            <div>
                <p className="text-sm font-medium text-gray-500">Active Violations</p>
                <p className="text-2xl font-bold text-gray-900">0</p>
            </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100 flex items-center">
            <div className="p-3 bg-purple-100 rounded-full text-purple-600 mr-4">
                <FileText size={24} />
            </div>
            <div>
                <p className="text-sm font-medium text-gray-500">Notices Issued</p>
                <p className="text-2xl font-bold text-gray-900">0</p>
            </div>
        </div>
      </div>
    </div>
  );
}
