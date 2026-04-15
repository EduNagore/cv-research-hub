import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from '@/components/theme-provider';
import { Toaster } from '@/components/ui/sonner';

import { Layout } from '@/components/layout';
import { Dashboard } from '@/pages/dashboard';
import { ResearchItems } from '@/pages/research-items';
import { ResearchItemDetail } from '@/pages/research-item-detail';
import { Categories } from '@/pages/categories';
import { Trends } from '@/pages/trends';
import { Comparisons } from '@/pages/comparisons';
import { DecisionSupport } from '@/pages/decision-support';
import { Favorites } from '@/pages/favorites';
import { Search } from '@/pages/search';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: 2,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider defaultTheme="dark" storageKey="cv-research-hub-theme">
        <Router>
          <Layout>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/items" element={<ResearchItems />} />
              <Route path="/items/:slug" element={<ResearchItemDetail />} />
              <Route path="/categories" element={<Categories />} />
              <Route path="/categories/:slug" element={<ResearchItems />} />
              <Route path="/trends" element={<Trends />} />
              <Route path="/comparisons" element={<Comparisons />} />
              <Route path="/decision-support" element={<DecisionSupport />} />
              <Route path="/favorites" element={<Favorites />} />
              <Route path="/search" element={<Search />} />
            </Routes>
          </Layout>
        </Router>
        <Toaster />
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
