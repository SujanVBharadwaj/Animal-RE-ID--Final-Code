import { useRef, useState } from 'react';
import { Upload, X, Image as ImageIcon } from 'lucide-react';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { ImageWithFallback } from './figma/ImageWithFallback';

interface UploadSectionProps {
  onImageUpload: (file: File) => void;
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
    onImageUpload(file); 
  };


  const handleClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-slate-900 mb-1">Upload Image</h2>
        <p className="text-slate-600">Upload an image of an animal for identification</p>
      </div>

      <Card className="overflow-hidden">
        {!uploadedImage ? (
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={handleClick}
            className={`relative border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-all ${
              isDragging
                ? 'border-blue-500 bg-blue-50'
                : 'border-slate-300 hover:border-blue-400 hover:bg-slate-50'
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
              <div className="bg-blue-100 p-4 rounded-full">
                <Upload className="size-8 text-blue-600" />
              </div>
              
              <div>
                <p className="text-slate-900 mb-1">Drop your image here, or click to browse</p>
                <p className="text-slate-500">Supports: JPG, PNG, WEBP</p>
              </div>
              
              <Button type="button" className="mt-2">
                <ImageIcon className="size-4 mr-2" />
                Select Image
              </Button>
            </div>
          </div>
        ) : (
          <div className="relative">
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
                className="absolute top-4 right-4"
              >
                <X className="size-4 mr-2" />
                Remove
              </Button>
            )}
            
            {isAnalyzing && (
              <div className="absolute inset-0 bg-black/50 flex items-center justify-center rounded-lg">
                <div className="text-center text-white">
                  <div className="animate-spin rounded-full h-12 w-12 border-4 border-white border-t-transparent mx-auto mb-4"></div>
                  <p>Analyzing image...</p>
                </div>
              </div>
            )}
          </div>
        )}
      </Card>

      {uploadedImage && !isAnalyzing && (
        <div className="flex gap-2">
          <Button onClick={onReset} variant="outline" className="flex-1">
            Upload New Image
          </Button>
        </div>
      )}
    </div>
  );
}
