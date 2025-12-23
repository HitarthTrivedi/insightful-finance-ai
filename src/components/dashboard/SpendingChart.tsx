import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";
import { useQuery } from "@tanstack/react-query";
const API_URL = import.meta.env.PROD
  ? "https://your-project.vercel.app"
  : "http://localhost:8000";
const spendingData = [
  { name: "Housing", value: 1500, color: "hsl(160, 84%, 39%)" },
  { name: "Food", value: 450, color: "hsl(38, 92%, 50%)" },
  { name: "Transport", value: 280, color: "hsl(200, 80%, 50%)" },
  { name: "Shopping", value: 320, color: "hsl(280, 70%, 50%)" },
  { name: "Utilities", value: 180, color: "hsl(340, 70%, 50%)" },
  { name: "Entertainment", value: 150, color: "hsl(60, 70%, 50%)" },
];

const SpendingChart = () => {
  const { data: analyticsData, isLoading } = useQuery({
    queryKey: ['spending-analytics'],
    queryFn: async () => {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_URL}/api/analytics/spending`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (!response.ok) throw new Error('Failed to fetch');
      return response.json();
    }
  });

  const spendingData = analyticsData?.data || [];
  const total = analyticsData?.total || 0;
  if (isLoading) return <div className="glass-card rounded-2xl p-6">Loading chart...</div>;
  return (
    <div className="glass-card rounded-2xl p-6 opacity-0 animate-fade-in-up" style={{ animationDelay: "200ms" }}>
      <h2 className="text-lg font-semibold text-foreground mb-6">Monthly Spending</h2>
      
      <div className="flex items-center gap-6">
        <div className="relative w-48 h-48">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={spendingData}
                cx="50%"
                cy="50%"
                innerRadius={55}
                outerRadius={80}
                paddingAngle={3}
                dataKey="value"
              >
                {spendingData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ 
                  background: "hsl(var(--card))", 
                  border: "1px solid hsl(var(--border))",
                  borderRadius: "8px",
                  boxShadow: "0 4px 12px rgba(0,0,0,0.1)"
                }}
                itemStyle={{ color: "hsl(var(--foreground))" }}
                formatter={(value: number) => [`$${value}`, ""]}
              />
            </PieChart>
          </ResponsiveContainer>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-2xl font-bold text-foreground">${total.toLocaleString()}</span>
            <span className="text-xs text-muted-foreground">Total</span>
          </div>
        </div>

        <div className="flex-1 space-y-3">
          {spendingData.map((item, index) => (
            <div 
              key={item.name} 
              className="flex items-center justify-between opacity-0 animate-fade-in"
              style={{ animationDelay: `${300 + index * 100}ms` }}
            >
              <div className="flex items-center gap-2">
                <div 
                  className="w-3 h-3 rounded-full" 
                  style={{ backgroundColor: item.color }}
                />
                <span className="text-sm text-muted-foreground">{item.name}</span>
              </div>
              <span className="text-sm font-medium text-foreground">${item.value}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default SpendingChart;
