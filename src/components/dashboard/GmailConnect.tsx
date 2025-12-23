import { Mail, CheckCircle2, RefreshCw, Shield, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useState } from "react";
import { useToast } from "@/hooks/use-toast";

const API_URL = import.meta.env.PROD
  ? "https://your-project.vercel.app"
  : "http://localhost:8000";

const GmailConnect = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [isSyncing, setIsSyncing] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [showForm, setShowForm] = useState(false);

  const [email, setEmail] = useState("");
  const [appPassword, setAppPassword] = useState("");
  const [lastSynced, setLastSynced] = useState<string | null>(null);
  const [transactionCount, setTransactionCount] = useState(0);

  const { toast } = useToast();

  const handleConnect = async () => {
    if (!email || !appPassword) {
      toast({
        title: "Missing credentials",
        description: "Please enter your email and app password",
        variant: "destructive"
      });
      return;
    }

    setIsConnecting(true);

    try {
      const token = localStorage.getItem("token");
      const response = await fetch(`${API_URL}/api/gmail/connect`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({
          email: email,
          app_password: appPassword
        })
      });

      const data = await response.json();

      if (response.ok) {
        setIsConnected(true);
        setShowForm(false);
        toast({
          title: "Connected!",
          description: "Gmail connected successfully"
        });
      } else {
        toast({
          title: "Connection failed",
          description: data.detail || "Failed to connect to Gmail",
          variant: "destructive"
        });
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to connect to Gmail. Check your credentials.",
        variant: "destructive"
      });
    } finally {
      setIsConnecting(false);
    }
  };

  const handleSync = async () => {
    if (!email || !appPassword) {
      toast({
        title: "Missing credentials",
        description: "Please reconnect your Gmail account",
        variant: "destructive"
      });
      return;
    }

    setIsSyncing(true);

    try {
      const token = localStorage.getItem("token");
      const response = await fetch(`${API_URL}/api/gmail/sync`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({
          email: email,
          app_password: appPassword
        })
      });

      const data = await response.json();

      if (response.ok) {
        setLastSynced("Just now");
        setTransactionCount(data.new_transactions || 0);
        toast({
          title: "Sync completed!",
          description: `Found ${data.total_found} transactions, added ${data.new_transactions} new ones`
        });
      } else {
        toast({
          title: "Sync failed",
          description: data.detail || "Failed to sync transactions",
          variant: "destructive"
        });
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to sync transactions",
        variant: "destructive"
      });
    } finally {
      setIsSyncing(false);
    }
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
            <span className="text-sm font-medium">Connected to {email}</span>
          </div>

          <div className="grid grid-cols-2 gap-3 text-sm">
            <div className="p-3 rounded-xl bg-secondary/50">
              <p className="text-muted-foreground">Last Synced</p>
              <p className="font-medium text-foreground">{lastSynced || "Not synced yet"}</p>
            </div>
            <div className="p-3 rounded-xl bg-secondary/50">
              <p className="text-muted-foreground">New Transactions</p>
              <p className="font-medium text-foreground">{transactionCount} this month</p>
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

          <Button
            variant="ghost"
            className="w-full text-xs"
            onClick={() => {
              setIsConnected(false);
              setShowForm(true);
            }}
          >
            Disconnect
          </Button>
        </div>
      ) : (
        <div className="space-y-4">
          {!showForm ? (
            <>
              <p className="text-sm text-muted-foreground">
                Connect your Gmail to automatically detect and import bank transaction emails.
              </p>

              <div className="flex items-start gap-2 text-xs text-muted-foreground bg-blue-500/10 p-3 rounded-lg">
                <AlertCircle className="h-4 w-4 mt-0.5 flex-shrink-0" />
                <span>You need a Gmail App Password. Enable 2FA first, then create one at: myaccount.google.com/apppasswords</span>
              </div>

              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                <Shield className="h-4 w-4" />
                <span>Read-only access • Your data stays private</span>
              </div>

              <Button
                className="w-full gradient-primary"
                onClick={() => setShowForm(true)}
              >
                <Mail className="h-4 w-4 mr-2" />
                Connect Gmail
              </Button>
            </>
          ) : (
            <>
              <div className="space-y-3">
                <div>
                  <label className="text-sm font-medium text-foreground mb-1 block">
                    Gmail Address
                  </label>
                  <Input
                    type="email"
                    placeholder="your.email@gmail.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="bg-secondary"
                  />
                </div>

                <div>
                  <label className="text-sm font-medium text-foreground mb-1 block">
                    App Password
                  </label>
                  <Input
                    type="password"
                    placeholder="16-character app password"
                    value={appPassword}
                    onChange={(e) => setAppPassword(e.target.value)}
                    className="bg-secondary"
                  />
                  <p className="text-xs text-muted-foreground mt-1">
                    Not your Gmail password. Generate at myaccount.google.com/apppasswords
                  </p>
                </div>
              </div>

              <div className="flex gap-2">
                <Button
                  variant="outline"
                  className="flex-1"
                  onClick={() => setShowForm(false)}
                >
                  Cancel
                </Button>
                <Button
                  className="flex-1 gradient-primary"
                  onClick={handleConnect}
                  disabled={isConnecting}
                >
                  {isConnecting ? "Connecting..." : "Connect"}
                </Button>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default GmailConnect;