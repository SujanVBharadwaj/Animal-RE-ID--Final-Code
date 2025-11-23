import { Scan, Sparkles } from 'lucide-react';

export function Header() {
  return (
    <header className="bg-white/60 border-b border-emerald-200/50 shadow-sm backdrop-blur-xl sticky top-0 z-50">
      <div className="container mx-auto px-4 py-6 max-w-7xl">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-xl blur opacity-50 animate-pulse"></div>
              <div className="relative bg-gradient-to-br from-emerald-500 to-teal-600 p-3 rounded-xl shadow-lg">
                <Scan className="size-6 text-white" />
              </div>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-slate-900">Animal ReID System</h1>
                <Sparkles className="size-4 text-emerald-500" />
              </div>
              <p className="text-slate-600">Wildlife Identification & Tracking</p>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}