
import { useAuth } from '../context/AuthContext';
import { Outlet, Navigate, Link } from 'react-router-dom';
import { LogOut, Home, CarFront, FileText, AlertCircle, Banknote, Users } from 'lucide-react';

export function Layout() {
  const { user, isLoading, logout } = useAuth();

  if (isLoading) {
    return <div className="flex h-screen items-center justify-center">Loading...</div>;
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="w-64 bg-slate-900 text-white flex flex-col">
        <div className="p-4 border-b border-slate-800">
          <h1 className="text-xl font-bold">ITVM Platform</h1>
        </div>
        <nav className="flex-1 p-4 space-y-2">
          <Link to="/" className="flex items-center space-x-2 p-2 hover:bg-slate-800 rounded">
            <Home size={20} /> <span>Dashboard</span>
          </Link>
          <Link to="/vehicles" className="flex items-center space-x-2 p-2 hover:bg-slate-800 rounded">
            <CarFront size={20} /> <span>Vehicles</span>
          </Link>
          <Link to="/drivers" className="flex items-center space-x-2 p-2 hover:bg-slate-800 rounded">
            <Users size={20} /> <span>Drivers</span>
          </Link>
          <Link to="/violations" className="flex items-center space-x-2 p-2 hover:bg-slate-800 rounded">
            <AlertCircle size={20} /> <span>Violations</span>
          </Link>
          <Link to="/fines" className="flex items-center space-x-2 p-2 hover:bg-slate-800 rounded">
            <Banknote size={20} /> <span>Fine Assessments</span>
          </Link>
          <Link to="/appeals" className="flex items-center space-x-2 p-2 hover:bg-slate-800 rounded">
            <FileText size={20} /> <span>Appeals</span>
          </Link>
        </nav>
        <div className="p-4 border-t border-slate-800">
            <div className="text-sm text-slate-300 mb-2 truncate">{user.display_name}</div>
            <button
                onClick={logout}
                className="flex items-center space-x-2 w-full p-2 text-left hover:bg-slate-800 rounded text-red-400"
            >
                <LogOut size={20} /> <span>Logout</span>
            </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-auto">
        <header className="bg-white shadow-sm h-16 flex items-center px-8">
            <h2 className="text-lg font-semibold text-gray-800">ITVM Dashboard</h2>
        </header>
        <main className="p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
