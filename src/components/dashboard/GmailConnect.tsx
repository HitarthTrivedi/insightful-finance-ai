import { Mail, CheckCircle2, RefreshCw, Shield } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useState } from "react";

const GmailConnect = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [isSyncing, setIsSyncing] = useState(false);

  const handleConnect = () => {
    // This would trigger OAuth flow to your Python backend
    setIsConnected(true);
  };

  const handleSync = () => {
    setIsSyncing(true);
    setTimeout(() => setIsSyncing(false), 2000);
  };

  return (
    <div className="glass-card rounded-2xl p-6 opacity-0 animate-fade-in-up" style={{ animationDelay: "100ms" }}>
      <div className="flex items-center gap-3 mb-4">
        <div className="h-10 w-10 rounded-xl bg-destructive/10 flex items-center justify-center">
          <Mail className="h-5 w-5 text-destructive" />
        </div>
        <div>
          <h2 className="text-lg font-semibold text-foreground">Gmail Integration</h2>
          <p className="text-xs text-muted-foreground">Sync bank transactions from emails</p>
        </div>
      </div>

      {isConnected ? (
        <div className="space-y-4">
          <div className="flex items-center gap-2 text-success">
            <CheckCircle2 className="h-4 w-4" />
            <span className="text-sm font-medium">Connected to john.doe@gmail.com</span>
          </div>
          
          <div className="grid grid-cols-2 gap-3 text-sm">
            <div className="p-3 rounded-xl bg-secondary/50">
              <p className="text-muted-foreground">Last Synced</p>
              <p className="font-medium text-foreground">2 hours ago</p>
            </div>
            <div className="p-3 rounded-xl bg-secondary/50">
              <p className="text-muted-foreground">Transactions Found</p>
              <p className="font-medium text-foreground">24 this month</p>
            </div>
          </div>

          <Button 
            variant="outline" 
            className="w-full" 
            onClick={handleSync}
            disabled={isSyncing}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${isSyncing ? 'animate-spin' : ''}`} />
            {isSyncing ? 'Syncing...' : 'Sync Now'}
          </Button>
        </div>
      ) : (
        <div className="space-y-4">
          <p className="text-sm text-muted-foreground">
            Connect your Gmail to automatically detect and import bank transaction emails.
          </p>
          
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <Shield className="h-4 w-4" />
            <span>Read-only access • Your data stays private</span>
          </div>

          <Button className="w-full gradient-primary" onClick={handleConnect}>
            <Mail className="h-4 w-4 mr-2" />
            Connect Gmail
          </Button>
        </div>
      )}
    </div>
  );
};

export default GmailConnect;
