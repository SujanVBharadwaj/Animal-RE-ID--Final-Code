import { useRef, useState } from 'react';
import { Upload, X, Image as ImageIcon, CloudUpload } from 'lucide-react';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { ImageWithFallback } from './figma/ImageWithFallback';

interface UploadSectionProps {
  onImageUpload: (imageUrl: string) => void;
  uploadedImage: string | null;
  isAnalyzing: boolean;
  onReset: () => void;
}

export function UploadSection({ onImageUpload, uploadedImage, isAnalyzing, onReset }: UploadSectionProps) {
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
      handleFile(file);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFile(file);
    }
  };

  const handleFile = (file: File) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const imageUrl = e.target?.result as string;
      onImageUpload(imageUrl);
    };
    reader.readAsDataURL(file);
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="space-y-5">
      <div className="flex items-center gap-3">
        <div className="flex-1">
          <h2 className="text-slate-900 mb-1 flex items-center gap-2">
            <CloudUpload className="size-5 text-emerald-600" />
            Upload Image
          </h2>
          <p className="text-slate-700">Drop an animal image for instant AI-powered identification</p>
        </div>
      </div>

      <Card className="overflow-hidden bg-white/70 border-slate-200/50 backdrop-blur-xl shadow-xl hover:shadow-2xl transition-all duration-500">
        {!uploadedImage ? (
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={handleClick}
            className={`relative border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-all duration-300 ${
              isDragging
                ? 'border-emerald-500 bg-gradient-to-br from-emerald-50 to-teal-50 scale-[0.98]'
                : 'border-slate-300 hover:border-emerald-400 hover:bg-gradient-to-br hover:from-emerald-50/50 hover:to-teal-50/50'
            }`}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleFileSelect}
              className="hidden"
            />
            
            <div className="flex flex-col items-center gap-4">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/30 to-teal-600/30 rounded-full blur-xl animate-pulse"></div>
                <div className="relative bg-gradient-to-br from-emerald-500/20 to-teal-600/20 p-5 rounded-full border-2 border-emerald-500/40">
                  <Upload className="size-9 text-emerald-600" />
                </div>
              </div>
              
              <div>
                <p className="text-slate-900 mb-2">Drop your wildlife image here</p>
                <p className="text-slate-600">or click to browse your files</p>
                <p className="text-slate-500 mt-2">Supports: JPG, PNG, WEBP • Max 10MB</p>
              </div>
              
              <Button type="button" className="mt-4 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105">
                <ImageIcon className="size-4 mr-2" />
                Select Image
              </Button>
            </div>
          </div>
        ) : (
          <div className="relative group">
            <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/10 to-teal-500/10 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            <ImageWithFallback
              src={uploadedImage}
              alt="Uploaded animal"
              className="w-full h-auto rounded-lg"
            />
            
            {!isAnalyzing && (
              <Button
                variant="destructive"
                size="sm"
                onClick={onReset}
                className="absolute top-4 right-4 shadow-lg hover:shadow-xl transition-all duration-300"
              >
                <X className="size-4 mr-2" />
                Remove
              </Button>
            )}
            
            {isAnalyzing && (
              <div className="absolute inset-0 bg-gradient-to-br from-emerald-900/90 to-teal-900/90 flex items-center justify-center rounded-lg backdrop-blur-sm">
                <div className="text-center text-white">
                  <div className="relative mb-6">
                    <div className="absolute inset-0 animate-ping">
                      <div className="h-16 w-16 border-4 border-emerald-400 rounded-full mx-auto"></div>
                    </div>
                    <div className="relative animate-spin rounded-full h-16 w-16 border-4 border-white border-t-transparent mx-auto"></div>
                  </div>
                  <p className="text-xl mb-2">Analyzing image...</p>
                  <p className="text-emerald-300">AI is processing unique features</p>
                </div>
              </div>
            )}
          </div>
        )}
      </Card>

      {uploadedImage && !isAnalyzing && (
        <div className="flex gap-3">
          <Button onClick={onReset} variant="outline" className="flex-1 border-slate-300 text-slate-700 hover:bg-slate-100 hover:text-slate-900 hover:border-emerald-400 transition-all duration-300">
            <Upload className="size-4 mr-2" />
            Upload New Image
          </Button>
        </div>
      )}
    </div>
  );
}