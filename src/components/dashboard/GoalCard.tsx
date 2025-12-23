import { Target, TrendingUp } from "lucide-react";
import { Progress } from "@/components/ui/progress";
import { useQuery } from "@tanstack/react-query";
import { useToast } from "@/hooks/use-toast";

const API_URL = import.meta.env.PROD
  ? "https://your-project.vercel.app"
  : "http://localhost:8000";

interface Goal {
  id: string;
  title: string;
  target: number;
  current: number;
  deadline: string;
  color: string;
}

const mockGoals: Goal[] = [
  { id: "1", title: "Emergency Fund", target: 10000, current: 7500, deadline: "Mar 2026", color: "primary" },
  { id: "2", title: "Vacation", target: 3000, current: 1800, deadline: "Jun 2026", color: "warning" },
  { id: "3", title: "New Car", target: 25000, current: 5000, deadline: "Dec 2026", color: "accent" },
];

const GoalCard = () => {
  const { toast } = useToast();

  const { data: goals, isLoading } = useQuery({
    queryKey: ['goals'],
    queryFn: async () => {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_URL}/api/goals`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (!response.ok) throw new Error('Failed to fetch');
      return response.json();
    }
  });
  if (isLoading) return <div className="glass-card rounded-2xl p-6">Loading goals...</div>;
  return (
    <div className="glass-card rounded-2xl p-6 opacity-0 animate-fade-in-up" style={{ animationDelay: "300ms" }}>
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-xl bg-primary/10 flex items-center justify-center">
            <Target className="h-5 w-5 text-primary" />
          </div>
          <h2 className="text-lg font-semibold text-foreground">Financial Goals</h2>
        </div>
        <button className="text-sm text-primary font-medium hover:underline">+ Add Goal</button>
      </div>

      <div className="space-y-5">
        {goals?.map((goal, index) => {
          const progress = (goal.current / goal.target) * 100;
          return (
            <div 
              key={goal.id} 
              className="opacity-0 animate-fade-in"
              style={{ animationDelay: `${400 + index * 150}ms` }}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium text-foreground">{goal.title}</span>
                <span className="text-sm text-muted-foreground">by {goal.deadline}</span>
              </div>
              <Progress value={progress} className="h-3" />
              <div className="flex items-center justify-between mt-2">
                <span className="text-sm text-muted-foreground">
                  ${goal.current.toLocaleString()} of ${goal.target.toLocaleString()}
                </span>
                <span className="text-sm font-medium text-primary">{progress.toFixed(0)}%</span>
              </div>
            </div>
          );
        })}
      </div>

      <div className="mt-6 p-4 rounded-xl bg-primary/5 border border-primary/20">
        <div className="flex items-center gap-2 text-primary">
          <TrendingUp className="h-4 w-4" />
          <span className="text-sm font-medium">AI Insight</span>
        </div>
        <p className="text-sm text-muted-foreground mt-2">
          Based on your spending patterns, you'll reach your Emergency Fund goal 2 months early!
        </p>
      </div>
    </div>
  );
};

export default GoalCard;
