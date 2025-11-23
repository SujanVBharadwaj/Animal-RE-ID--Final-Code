import { CheckCircle2, TrendingUp, Image as ImageIcon, Microscope, Award, Fingerprint } from 'lucide-react';
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
      <div className="flex items-center justify-center h-full min-h-[500px]">
        <div className="text-center">
          <div className="relative mb-6">
            <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/20 to-teal-600/20 rounded-full blur-2xl"></div>
            <div className="relative bg-gradient-to-br from-emerald-500/10 to-teal-600/10 p-8 rounded-full border-2 border-emerald-500/20 inline-block">
              <Microscope className="size-20 text-emerald-600/40" />
            </div>
          </div>
          <p className="text-slate-600 mb-1">Awaiting Image Upload</p>
          <p className="text-slate-500">Results will appear here after analysis</p>
        </div>
      </div>
    );
  }

  if (isAnalyzing) {
    return (
      <div className="flex items-center justify-center h-full min-h-[500px]">
        <div className="text-center">
          <div className="relative mb-8">
            <div className="absolute inset-0 animate-pulse">
              <div className="bg-gradient-to-br from-emerald-500/30 to-teal-600/30 p-8 rounded-full blur-xl"></div>
            </div>
            <div className="relative animate-pulse">
              <div className="bg-gradient-to-br from-emerald-500/20 to-teal-600/20 p-8 rounded-full border-2 border-emerald-500/40 inline-block">
                <Microscope className="size-16 text-emerald-600" />
              </div>
            </div>
          </div>
          <div className="space-y-3">
            <p className="text-slate-800">Processing Image...</p>
            <div className="flex items-center justify-center gap-2 text-emerald-600">
              <div className="w-2 h-2 bg-emerald-500 rounded-full animate-bounce"></div>
              <div className="w-2 h-2 bg-emerald-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              <div className="w-2 h-2 bg-emerald-500 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
            </div>
            <p className="text-slate-500">Analyzing unique patterns & features</p>
          </div>
        </div>
      </div>
    );
  }

  if (!result) {
    return null;
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 90) return 'text-green-700 bg-green-500/20 border-green-500/50';
    if (confidence >= 75) return 'text-yellow-700 bg-yellow-500/20 border-yellow-500/50';
    return 'text-red-700 bg-red-500/20 border-red-500/50';
  };

  const getConfidenceBadgeColor = (confidence: number) => {
    if (confidence >= 90) return 'from-green-500 to-emerald-600';
    if (confidence >= 75) return 'from-yellow-500 to-orange-600';
    return 'from-red-500 to-rose-600';
  };

  return (
    <div className="space-y-5 animate-in fade-in duration-700">
      <div className="flex items-center gap-3">
        <div className="flex-1">
          <h2 className="text-slate-900 mb-1 flex items-center gap-2">
            <Award className="size-5 text-emerald-600" />
            Identification Results
          </h2>
          <p className="text-slate-700">Match found with high confidence</p>
        </div>
      </div>

      <Card className="p-6 bg-white/70 border-slate-200/50 backdrop-blur-xl shadow-xl hover:shadow-2xl transition-all duration-500">
        <div className="flex items-start gap-4 mb-4">
          <div className="relative">
            <div className="absolute inset-0 bg-gradient-to-br from-green-500/30 to-emerald-600/30 rounded-full blur-md animate-pulse"></div>
            <div className="relative bg-gradient-to-br from-green-500/20 to-emerald-600/20 p-3 rounded-full border-2 border-green-500/40">
              <CheckCircle2 className="size-6 text-green-600" />
            </div>
          </div>
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-3">
              <h3 className="text-slate-900 flex items-center gap-2">
                {result.name}
                <Fingerprint className="size-4 text-emerald-600" />
              </h3>
            </div>
            <div className="flex gap-2">
              <Badge variant="outline" className={`${getConfidenceColor(result.confidence)} px-3 py-1`}>
                <TrendingUp className="size-3 mr-1" />
                {result.confidence}% Match
              </Badge>
              <div className={`px-3 py-1 rounded-full bg-gradient-to-r ${getConfidenceBadgeColor(result.confidence)} text-white shadow-lg`}>
                <p className="flex items-center gap-1">
                  <Award className="size-3" />
                  High Confidence
                </p>
              </div>
            </div>
          </div>
        </div>

        <Separator className="my-4 bg-gradient-to-r from-transparent via-slate-300 to-transparent" />

        <div className="space-y-3">
          <div className="flex items-center gap-2 text-slate-800">
            <div className="p-2 rounded-lg bg-gradient-to-br from-emerald-500/20 to-teal-600/20 border border-emerald-500/30">
              <ImageIcon className="size-5 text-emerald-600" />
            </div>
            <p>Database Match Reference</p>
          </div>
          
          <div className="relative rounded-xl overflow-hidden border-2 border-emerald-500/30 shadow-lg group">
            <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/10 to-teal-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            <ImageWithFallback
              src={result.databaseImageUrl}
              alt={`${result.name} from database`}
              className="w-full h-auto"
            />
            <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/60 to-transparent p-4">
              <p className="text-white">Cropped image from database</p>
            </div>
          </div>
        </div>

        <Separator className="my-4 bg-gradient-to-r from-transparent via-slate-300 to-transparent" />

        <div className="bg-gradient-to-br from-emerald-50 to-teal-50 border-2 border-emerald-500/30 rounded-xl p-5 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-emerald-400/20 to-teal-400/20 rounded-full blur-2xl"></div>
          <div className="relative">
            <div className="flex items-center gap-2 mb-3">
              <div className="p-1.5 rounded-lg bg-gradient-to-br from-emerald-500/30 to-teal-600/30">
                <Fingerprint className="size-4 text-emerald-700" />
              </div>
              <h4 className="text-emerald-900">Identification Details</h4>
            </div>
            <p className="text-slate-700 leading-relaxed">
              This animal has been successfully identified with a cosine similarity score of <span className="text-emerald-700">{result.confidence}%</span>. 
              Our AI system analyzed unique physical characteristics, patterns, and features to match this individual against our comprehensive wildlife database.
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
}