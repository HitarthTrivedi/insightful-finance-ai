import { ArrowDownLeft, ArrowUpRight, Building2, ShoppingCart, Utensils, Car, Zap } from "lucide-react";
import { cn } from "@/lib/utils";

interface Transaction {
  id: string;
  title: string;
  category: string;
  amount: number;
  date: string;
  type: "income" | "expense";
  bank: string;
}

const mockTransactions: Transaction[] = [
  { id: "1", title: "Salary Deposit", category: "Income", amount: 5200, date: "Dec 23, 2025", type: "income", bank: "Chase Bank" },
  { id: "2", title: "Amazon Purchase", category: "Shopping", amount: -89.99, date: "Dec 22, 2025", type: "expense", bank: "Chase Bank" },
  { id: "3", title: "Uber Ride", category: "Transport", amount: -24.50, date: "Dec 22, 2025", type: "expense", bank: "Wells Fargo" },
  { id: "4", title: "Electric Bill", category: "Utilities", amount: -145.00, date: "Dec 21, 2025", type: "expense", bank: "Bank of America" },
  { id: "5", title: "Restaurant", category: "Food", amount: -67.80, date: "Dec 20, 2025", type: "expense", bank: "Chase Bank" },
  { id: "6", title: "Freelance Payment", category: "Income", amount: 850, date: "Dec 19, 2025", type: "income", bank: "PayPal" },
];

const getCategoryIcon = (category: string) => {
  switch (category) {
    case "Income": return Building2;
    case "Shopping": return ShoppingCart;
    case "Food": return Utensils;
    case "Transport": return Car;
    case "Utilities": return Zap;
    default: return Building2;
  }
};

const TransactionList = () => {
  return (
    <div className="glass-card rounded-2xl p-6 opacity-0 animate-fade-in-up" style={{ animationDelay: "400ms" }}>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-semibold text-foreground">Recent Transactions</h2>
        <span className="text-sm text-primary font-medium cursor-pointer hover:underline">View All</span>
      </div>

      <div className="space-y-4">
        {mockTransactions.map((transaction, index) => {
          const Icon = getCategoryIcon(transaction.category);
          return (
            <div
              key={transaction.id}
              className="flex items-center justify-between p-4 rounded-xl bg-secondary/50 hover:bg-secondary transition-colors cursor-pointer opacity-0 animate-slide-in-right"
              style={{ animationDelay: `${500 + index * 100}ms` }}
            >
              <div className="flex items-center gap-4">
                <div className={cn(
                  "h-12 w-12 rounded-xl flex items-center justify-center",
                  transaction.type === "income" ? "bg-success/10" : "bg-secondary"
                )}>
                  <Icon className={cn(
                    "h-5 w-5",
                    transaction.type === "income" ? "text-success" : "text-muted-foreground"
                  )} />
                </div>
                <div>
                  <p className="font-medium text-foreground">{transaction.title}</p>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-xs text-muted-foreground">{transaction.bank}</span>
                    <span className="text-xs text-muted-foreground">•</span>
                    <span className="text-xs text-muted-foreground">{transaction.date}</span>
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className={cn(
                  "font-semibold",
                  transaction.type === "income" ? "text-success" : "text-foreground"
                )}>
                  {transaction.type === "income" ? "+" : ""}${Math.abs(transaction.amount).toFixed(2)}
                </span>
                {transaction.type === "income" ? (
                  <ArrowDownLeft className="h-4 w-4 text-success" />
                ) : (
                  <ArrowUpRight className="h-4 w-4 text-muted-foreground" />
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default TransactionList;
