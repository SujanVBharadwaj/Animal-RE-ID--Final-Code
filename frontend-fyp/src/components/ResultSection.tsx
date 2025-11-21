import { CheckCircle2, TrendingUp, Image as ImageIcon, Microscope } from 'lucide-react';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { Separator } from './ui/separator';
import { ImageWithFallback } from './figma/ImageWithFallback';
import type { AnimalResult } from '../App';

interface ResultSectionProps {
  result: AnimalResult | null;
  isAnalyzing: boolean;
  hasUploadedImage: boolean;
}

export function ResultSection({ result, isAnalyzing, hasUploadedImage }: ResultSectionProps) {
  if (!hasUploadedImage) {
    return (
      <div className="flex items-center justify-center h-full min-h-[400px]">
        <div className="text-center text-slate-400">
          <Microscope className="size-16 mx-auto mb-4 opacity-50" />
          <p>Upload an image to see identification results</p>
        </div>
      </div>
    );
  }

  if (isAnalyzing) {
    return (
      <div className="flex items-center justify-center h-full min-h-[400px]">
        <div className="text-center">
          <div className="animate-pulse space-y-4">
            <div className="bg-blue-100 p-4 rounded-full inline-block">
              <Microscope className="size-12 text-blue-600" />
            </div>
            <p className="text-slate-600">Processing image...</p>
          </div>
        </div>
      </div>
    );
  }

  if (!result) {
    return null;
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 90) return 'text-green-600 bg-green-50';
    if (confidence >= 75) return 'text-yellow-600 bg-yellow-50';
    return 'text-red-600 bg-red-50';
  };

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-slate-900 mb-1">Identification Results</h2>
        <p className="text-slate-600">Animal successfully identified</p>
      </div>

      <Card className="p-6">
        <div className="flex items-start gap-3 mb-6">
          <div className="bg-green-100 p-2 rounded-full">
            <CheckCircle2 className="size-5 text-green-600" />
          </div>
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <h3 className="text-slate-900">{result.name}</h3>
              <Badge variant="outline" className={getConfidenceColor(result.confidence)}>
                <TrendingUp className="size-3 mr-1" />
                {result.confidence}% Match
              </Badge>
            </div>
          </div>
        </div>

        <Separator className="my-6" />

        <div className="space-y-3">
          <div className="flex items-center gap-2 text-slate-700">
            <ImageIcon className="size-5 text-slate-400" />
            <p>Database Match</p>
          </div>
          
          <div className="relative rounded-lg overflow-hidden border border-slate-200">
            <ImageWithFallback
              src={result.databaseImageUrl}
              alt={`${result.name} from database`}
              className="w-full h-auto"
            />
          </div>
          
          <p className="text-slate-500">Cropped image from database after processing</p>
        </div>

        <Separator className="my-6" />

        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h4 className="text-blue-900 mb-2">Identification Details</h4>
          <p className="text-blue-700">
            This animal has been successfully identified in our database with a confidence score of {result.confidence}%. 
            The identification is based on unique physical characteristics and patterns.
          </p>
        </div>
      </Card>
    </div>
  );
}