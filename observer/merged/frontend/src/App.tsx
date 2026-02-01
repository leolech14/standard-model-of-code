/**
 * Control Room - Main Application
 *
 * Wraps the Dashboard (from source-a) with authentication.
 * The Dashboard component contains the full Refinery Dashboard UI.
 */

import { AuthProvider } from '@/contexts/AuthContext';
import { SecureGate } from '@/components/SecureGate';

// The original 68KB App.tsx from source-a, renamed to Dashboard
// Contains: PipelineInspector, Inventory, FileSystem, Timeline, etc.
import Dashboard from './Dashboard';

function App() {
  return (
    <AuthProvider>
      <SecureGate>
        <Dashboard />
      </SecureGate>
    </AuthProvider>
  );
}

export default App;
