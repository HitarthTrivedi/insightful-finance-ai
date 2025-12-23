import { Bot, Send, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useState } from "react";

const suggestions = [
  "Analyze my spending patterns",
  "How can I save more?",
  "Review my goal progress",
  "Suggest budget adjustments",
];

const AIAdvisor = () => {
  const [input, setInput] = useState("");

  return (
    <div className="glass-card rounded-2xl p-6 opacity-0 animate-fade-in-up" style={{ animationDelay: "500ms" }}>
      <div className="flex items-center gap-3 mb-6">
        <div className="h-10 w-10 rounded-xl gradient-primary flex items-center justify-center glow-primary">
          <Bot className="h-5 w-5 text-primary-foreground" />
        </div>
        <div>
          <h2 className="text-lg font-semibold text-foreground">AI Financial Advisor</h2>
          <p className="text-xs text-muted-foreground">Powered by Grok (Llama 3.3 70B)</p>
        </div>
      </div>

      <div className="bg-secondary/50 rounded-xl p-4 mb-4">
        <div className="flex items-start gap-3">
          <div className="h-8 w-8 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0 mt-1">
            <Sparkles className="h-4 w-4 text-primary" />
          </div>
          <div>
            <p className="text-sm text-foreground leading-relaxed">
              Based on your recent transactions, I noticed you spent <span className="font-semibold text-primary">23% more</span> on dining out this month. 
              To reach your vacation goal faster, consider cooking at home 2-3 more days per week. 
              This could save you approximately <span className="font-semibold text-primary">$180/month</span>.
            </p>
          </div>
        </div>
      </div>

      <div className="flex flex-wrap gap-2 mb-4">
        {suggestions.map((suggestion, index) => (
          <button
            key={index}
            className="px-3 py-1.5 text-xs font-medium rounded-full bg-secondary hover:bg-secondary/80 text-secondary-foreground transition-colors"
          >
            {suggestion}
          </button>
        ))}
      </div>

      <div className="flex items-center gap-2">
        <input
          type="text"
          placeholder="Ask about your finances..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          className="flex-1 h-11 px-4 rounded-xl bg-secondary border-0 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
        />
        <Button size="icon" className="h-11 w-11 rounded-xl gradient-primary">
          <Send className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
};

export default AIAdvisor;
