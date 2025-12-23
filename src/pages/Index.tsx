import { Wallet, TrendingUp, TrendingDown, PiggyBank } from "lucide-react";
import Navbar from "@/components/dashboard/Navbar";
import StatCard from "@/components/dashboard/StatCard";
import GmailConnect from "@/components/dashboard/GmailConnect";
import SpendingChart from "@/components/dashboard/SpendingChart";
import GoalCard from "@/components/dashboard/GoalCard";
import TransactionList from "@/components/dashboard/TransactionList";
import AIAdvisor from "@/components/dashboard/AIAdvisor";
import { useQuery } from "@tanstack/react-query";
const API_URL = import.meta.env.PROD
  ? "https://your-project.vercel.app"
  : "http://localhost:8000";

const Index = () => {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: async () => {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_URL}/api/dashboard/stats`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (!response.ok) throw new Error('Failed to fetch');
      return response.json();
    }
  });
  return (
    <div className="min-h-screen bg-background dark">
      <Navbar />
      
      <main className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8 opacity-0 animate-fade-in">
          <h1 className="text-3xl font-bold text-foreground">Welcome back, John</h1>
          <p className="text-muted-foreground mt-1">Here's your financial overview for December 2025</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            title="Total Balance"
  value={`$${stats?.total_balance?.toFixed(2) || '0.00'}`}
            change="+12.5%"
            changeType="positive"
            icon={Wallet}
            delay={0}
          />
          <StatCard
            title="Monthly Income"
  value={`$${stats?.monthly_income?.toFixed(2) || '0.00'}`}
            change="+8.2%"
            changeType="positive"
            icon={TrendingUp}
            delay={100}
          />
          <StatCard
            title="Monthly Expenses"
  value={`$${stats?.monthly_expenses?.toFixed(2) || '0.00'}`}
            change="-5.4%"
            changeType="positive"
            icon={TrendingDown}
            delay={200}
          />
          <StatCard
            title="Savings Rate"
  value={`${stats?.savings_rate || 0}%`}
            change="+3.1%"
            changeType="positive"
            icon={PiggyBank}
            delay={300}
          />
        </div>

        {/* Main Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column */}
          <div className="lg:col-span-2 space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <GmailConnect />
              <SpendingChart />
            </div>
            <TransactionList />
          </div>

          {/* Right Column */}
          <div className="space-y-6">
            <GoalCard />
            <AIAdvisor />
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="container mx-auto px-4 py-8 mt-8 border-t border-border">
        <p className="text-center text-sm text-muted-foreground">
          FinanceAI — Connect to your Python backend via API endpoints
        </p>
      </footer>
    </div>
  );
};

export default Index;
