import { Link, useLocation } from 'react-router-dom';
import { 
  Home, 
  Search, 
  FolderOpen, 
  TrendingUp, 
  BarChart2, 
  HelpCircle, 
  Heart, 
  Menu,
  Sun,
  Moon,
  Sparkles
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet';
import { useTheme } from '@/components/theme-provider';
import { cn } from '@/lib/utils';

const navItems = [
  { path: '/', label: 'Dashboard', icon: Home },
  { path: '/items', label: 'Research Items', icon: Search },
  { path: '/categories', label: 'Categories', icon: FolderOpen },
  { path: '/trends', label: 'Trends', icon: TrendingUp },
  { path: '/comparisons', label: 'Comparisons', icon: BarChart2 },
  { path: '/decision-support', label: 'Decision Support', icon: HelpCircle },
  { path: '/favorites', label: 'Favorites', icon: Heart },
];

function ThemeToggle() {
  const { theme, setTheme } = useTheme();

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
    >
      <Sun className="h-5 w-5 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
      <Moon className="absolute h-5 w-5 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
      <span className="sr-only">Toggle theme</span>
    </Button>
  );
}

function Navigation({ className }: { className?: string }) {
  const location = useLocation();

  return (
    <nav className={cn('flex flex-col gap-2', className)}>
      {navItems.map((item) => {
        const Icon = item.icon;
        const isActive = location.pathname === item.path || 
          (item.path !== '/' && location.pathname.startsWith(item.path));
        
        return (
          <Link
            key={item.path}
            to={item.path}
            className={cn(
              'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
              isActive 
                ? 'bg-primary text-primary-foreground' 
                : 'text-muted-foreground hover:bg-muted hover:text-foreground'
            )}
          >
            <Icon className="h-4 w-4" />
            {item.label}
          </Link>
        );
      })}
    </nav>
  );
}

export function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen flex-col">
      {/* Header */}
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-14 items-center">
          <div className="mr-4 flex items-center gap-2">
            <Sheet>
              <SheetTrigger asChild className="md:hidden">
                <Button variant="ghost" size="icon">
                  <Menu className="h-5 w-5" />
                  <span className="sr-only">Toggle menu</span>
                </Button>
              </SheetTrigger>
              <SheetContent side="left" className="w-64">
                <div className="flex items-center gap-2 mb-6">
                  <Sparkles className="h-6 w-6 text-primary" />
                  <span className="font-bold text-lg">CV Research Hub</span>
                </div>
                <Navigation />
              </SheetContent>
            </Sheet>
            <Link to="/" className="flex items-center gap-2">
              <Sparkles className="h-6 w-6 text-primary" />
              <span className="font-bold text-lg hidden md:inline">CV Research Hub</span>
            </Link>
          </div>
          
          <div className="flex-1" />
          
          <div className="flex items-center gap-2">
            <ThemeToggle />
          </div>
        </div>
      </header>

      <div className="flex flex-1">
        {/* Sidebar - Desktop */}
        <aside className="hidden md:flex w-64 flex-col border-r bg-muted/40 p-4">
          <Navigation />
        </aside>

        {/* Main content */}
        <main className="flex-1 overflow-auto">
          <div className="container py-6">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
