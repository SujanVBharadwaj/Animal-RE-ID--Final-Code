import { Database, TrendingUp, Zap } from "lucide-react";
import { Card } from "./ui/card";

export function StatsBar() {
  const stats = [
    {
      icon: Database,
      label: "Animals in Database",
      value: "3670",
      color: "emerald",
    },
    {
      icon: TrendingUp,
      label: "Accuracy Rate",
      value: "97%",
      color: "cyan",
    },
  ];

  return (
    <div className="container mx-auto px-4 py-6 max-w-7xl">
      <div className="grid grid-cols-2 gap-4">
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <Card
              key={index}
              className="p-4 bg-white/70 border-slate-200/50 backdrop-blur-lg hover:shadow-lg transition-all duration-300 hover:scale-105"
            >
              <div className="flex items-center gap-3">
                <div
                  className={`p-2.5 rounded-lg bg-gradient-to-br from-${stat.color}-500/20 to-${stat.color}-600/20 border border-${stat.color}-500/30`}
                >
                  <Icon
                    className={`size-5 text-${stat.color}-600`}
                  />
                </div>
                <div>
                  <p className="text-slate-600">{stat.label}</p>
                  <p className="text-slate-900">{stat.value}</p>
                </div>
              </div>
            </Card>
          );
        })}
      </div>
    </div>
  );
}