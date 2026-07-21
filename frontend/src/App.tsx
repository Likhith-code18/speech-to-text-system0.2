import React from 'react';
import { AppLayout } from './components/layout/AppLayout';
import { Dashboard } from './components/layout/dashboard/Dashboard';

function App() {
  return (
    <AppLayout>
      <Dashboard />
    </AppLayout>
  );
}

export default App;