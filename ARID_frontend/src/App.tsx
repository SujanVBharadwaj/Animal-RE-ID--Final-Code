import { useState } from 'react';
import { UploadSection } from './components/UploadSection';
import { ResultSection } from './components/ResultSection';
import { Header } from './components/Header';
import { StatsBar } from './components/StatsBar';
// Use a public asset path; place your image at: public/assets/background.png
const backgroundImage = '/assets/bg_img.png';

export interface AnimalResult {
  name: string;
  confidence: number; // Cosine similarity score (0-100)
  imageUrl: string;
  databaseImageUrl: string; // Cropped database match image
  galleryImages: { url: string; score: number }[]; // Top 5 ranked gallery images
}

export default function App() {
  const [uploadedImage, setUploadedImage] = useState<string | null>(null);
  const [result, setResult] = useState<AnimalResult | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const handleImageUpload = async (imageUrl: string) => {
    setUploadedImage(imageUrl); // Show preview immediately
    setIsAnalyzing(true);
    setResult(null);

    try {
      // 1. Fetch the blob from the local preview URL
      const response = await fetch(imageUrl);
      const blob = await response.blob();

      // 2. Create a File object
      const file = new File([blob], "upload.jpg", { type: "image/jpeg" });

      // 3. Create FormData
      const formData = new FormData();
      formData.append("file", file);

      // 4. Send to your API
      const apiResponse = await fetch("http://localhost:8000/identify", {
        method: "POST",
        body: formData,
      });

      const data = await apiResponse.json();

      if (data.error) {
        console.error("Error:", data.error);
        alert("Identification failed.");
        setIsAnalyzing(false);
        return;
      }

      // 5. Set the result (API now matches the interface structure)
      setResult(data);

    } catch (error) {
      console.error("Connection error:", error);
      alert("Could not connect to the Python backend.");
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleReset = () => {
    setUploadedImage(null);
    setResult(null);
    setIsAnalyzing(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-teal-50 to-cyan-50 relative overflow-hidden">
      {/* Animated gradient orbs */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 -left-4 w-96 h-96 bg-gradient-to-br from-emerald-400/20 to-teal-400/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-0 -right-4 w-96 h-96 bg-gradient-to-br from-cyan-400/20 to-blue-400/20 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-gradient-to-br from-teal-400/10 to-emerald-400/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '2s' }}></div>
      </div>

      {/* Background decorative image */}
      <div className="absolute inset-0 opacity-[0.06]">
        <img
          src={backgroundImage}
          alt=""
          className="w-full h-full object-cover"
        />
      </div>

      {/* Grid pattern overlay */}
      <div className="absolute inset-0 opacity-[0.02]" style={{
        backgroundImage: `
          linear-gradient(to right, rgb(0 0 0) 1px, transparent 1px),
          linear-gradient(to bottom, rgb(0 0 0) 1px, transparent 1px)
        `,
        backgroundSize: '40px 40px'
      }}></div>

      <div className="relative z-10">
        <Header />
        <StatsBar />

        <main className="container mx-auto px-4 py-8 max-w-7xl">
          <div className="grid lg:grid-cols-2 gap-8 items-start">
            <UploadSection
              onImageUpload={handleImageUpload}
              uploadedImage={uploadedImage}
              isAnalyzing={isAnalyzing}
              onReset={handleReset}
            />

            <ResultSection
              result={result}
              isAnalyzing={isAnalyzing}
              hasUploadedImage={!!uploadedImage}
            />
          </div>

          {/* Top 5 Ranked Gallery Images - Full Width */}
          {result && !isAnalyzing && (
            <div className="mt-12 animate-in fade-in duration-700">
              <div className="flex items-center gap-3 mb-6">
                <div className="p-2.5 rounded-lg bg-gradient-to-br from-cyan-500/20 to-blue-600/20 border border-cyan-500/30">
                  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-cyan-600">
                    <rect width="18" height="18" x="3" y="3" rx="2" ry="2" />
                    <circle cx="9" cy="9" r="2" />
                    <path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21" />
                  </svg>
                </div>
                <div>
                  <h3 className="text-slate-900">Top 5 Ranked Gallery Images</h3>
                  <p className="text-slate-600">Similarity scores based on cosine distance</p>
                </div>
              </div>

              <div className="grid grid-cols-5 gap-6">
                {result.galleryImages.map((image, index) => (
                  <div key={index} className="relative group">
                    <div className="relative rounded-xl overflow-hidden border-2 border-slate-200/50 shadow-lg hover:shadow-2xl transition-all duration-300 hover:scale-105 bg-white/70 backdrop-blur-lg">
                      <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/10 to-blue-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300 z-10"></div>
                      <img
                        src={image.url}
                        alt={`Gallery match ${index + 1}`}
                        className="w-full aspect-square object-cover"
                      />
                      <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 via-black/50 to-transparent p-4">
                        <div className="flex items-center justify-between">
                          <p className="text-white">Rank #{index + 1}</p>
                          <p className="text-white">{image.score}%</p>
                        </div>
                      </div>
                      {index === 0 && (
                        <div className="absolute top-3 right-3 bg-gradient-to-r from-yellow-400 to-orange-500 rounded-full p-2 shadow-lg">
                          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-white">
                            <path d="M15.477 12.89 17 22l-5-3-5 3 1.523-9.11L2 8h9.382l2.618-8 2.618 8H26z" />
                          </svg>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </main>

        <footer className="relative z-10 mt-16 pb-8">
          <div className="container mx-auto px-4 max-w-7xl">
            <div className="text-center text-slate-600">
              <p className="flex items-center justify-center gap-2">
                <span className="inline-block w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></span>
                Real-time Animal Recognition
              </p>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
}