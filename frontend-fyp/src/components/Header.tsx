import { Scan } from 'lucide-react';

export function Header() {
  return (
    <header className="bg-white border-b border-slate-200 shadow-sm">
      <div className="container mx-auto px-4 py-6 max-w-6xl">
        <div className="flex items-center gap-3">
          <div className="bg-blue-600 p-2 rounded-lg">
            <Scan className="size-6 text-white" />
          </div>
          <div>
            <h1 className="text-slate-900">Animal ReID System</h1>
            <p className="text-slate-600">Upload an image to identify and track animals</p>
          </div>
        </div>
      </div>
    </header>
  );
}
