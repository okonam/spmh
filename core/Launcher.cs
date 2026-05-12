using System;
using System.Diagnostics;
using System.IO;
using System.Threading;
using System.Windows.Forms;

namespace SPMH_Launcher
{
    class Program
    {
        [STAThread]
        static void Main(string[] args)
        {
            string baseDir = AppDomain.CurrentDomain.BaseDirectory;
            string corePath = Path.Combine(baseDir, "core");
            string mainPy = Path.Combine(corePath, "backend", "main.py");

            if (!File.Exists(mainPy)) return;

            // 1. Clean port 8888 (Silent)
            try {
                ProcessStartInfo killPort = new ProcessStartInfo("cmd.exe", "/c \"for /f \"tokens=5\" %a in ('netstat -aon ^| findstr :8888') do taskkill /f /pid %a\"");
                killPort.WindowStyle = ProcessWindowStyle.Hidden;
                killPort.CreateNoWindow = true;
                Process.Start(killPort).WaitForExit();
            } catch {}

            // 2. Start Python HIDDEN
            ProcessStartInfo psi = new ProcessStartInfo();
            psi.FileName = "python"; 
            psi.Arguments = "-u \"" + mainPy + "\"";
            psi.UseShellExecute = false;
            psi.CreateNoWindow = true;
            psi.WindowStyle = ProcessWindowStyle.Hidden;
            psi.WorkingDirectory = corePath;
            
            try {
                Process p = Process.Start(psi);
                if (p != null) {
                    // Wait a bit for the engine to warm up then launch browser
                    Thread.Sleep(2500);
                    Process.Start("http://127.0.0.1:8888");
                }
            }
            catch {}
        }
    }
}
