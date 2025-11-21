import { useState } from 'react';
import { UploadSection } from './components/UploadSection';
import { ResultSection } from './components/ResultSection';
import { Header } from './components/Header';

export interface AnimalResult {
  name: string;
  confidence: number;
  imageUrl: string;
  databaseImageUrl: string;
}

export default function App() {
  const [uploadedImage, setUploadedImage] = useState<string | null>(null);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null); 
  const [result, setResult] = useState<AnimalResult | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

const handleImageUpload = async (file: File) => {
  setIsAnalyzing(true);
  setResult(null);

  // Show preview
  setUploadedImage(URL.createObjectURL(file));

  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch("http://localhost:8000/identify", {
    method: "POST",
    body: formData,
  });

  const data = await response.json();

  setResult({
    name: data.name,
    confidence: 100,
    imageUrl: URL.createObjectURL(file),
    databaseImageUrl: `data:image/jpeg;base64,${data.databaseImage}`,
  });

  setIsAnalyzing(false);
};

  const handleReset = () => {
    setUploadedImage(null);
    setResult(null);
    setIsAnalyzing(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <Header />
      
      <main className="container mx-auto px-4 py-8 max-w-6xl">
        <div className="grid lg:grid-cols-2 gap-8">
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
      </main>
    </div>
  );
}