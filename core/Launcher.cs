using System;
using System.Diagnostics;
using System.IO;
using System.Threading;

namespace SPMH_Launcher
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.Title = "SPMH — Self Portable Media Hub";
            string baseDir = AppDomain.CurrentDomain.BaseDirectory;
            string corePath = Path.Combine(baseDir, "core");
            string mainPy = Path.Combine(corePath, "backend", "main.py");

            Console.WriteLine("====================================================");
            Console.WriteLine("      SPMH - SELF PORTABLE MEDIA HUB");
            Console.WriteLine("====================================================");
            Console.WriteLine("[!] Initializing Engine...");

            if (!File.Exists(mainPy))
            {
                Console.WriteLine("[ERROR] Engine core not found at: " + mainPy);
                Console.WriteLine("Press any key to exit...");
                Console.ReadKey();
                return;
            }

            // 1. Kill any existing process on port 8888
            try {
                ProcessStartInfo killPort = new ProcessStartInfo("cmd.exe", "/c \"for /f \"tokens=5\" %a in ('netstat -aon ^| findstr :8888') do taskkill /f /pid %a\"");
                killPort.WindowStyle = ProcessWindowStyle.Hidden;
                killPort.CreateNoWindow = true;
                Process.Start(killPort).WaitForExit();
            } catch {}

            // 2. Start Python
            ProcessStartInfo psi = new ProcessStartInfo();
            psi.FileName = "python"; 
            psi.Arguments = "-u \"" + mainPy + "\"";
            psi.UseShellExecute = false;
            psi.WorkingDirectory = corePath;
            
            try {
                Process p = Process.Start(psi);
                if (p != null) {
                    Console.WriteLine("[OK] Engine started (PID: " + p.Id + ")");
                    Console.WriteLine("[>] Launching Portal in 3s...");
                    
                    Thread.Sleep(3000);
                    Process.Start("http://127.0.0.1:8888");
                    
                    // Keep open to show TIPS
                    p.WaitForExit();
                }
            }
            catch (Exception ex) {
                Console.WriteLine("[CRITICAL ERROR] Could not start Python: " + ex.Message);
                Console.WriteLine("Ensure Python is installed and in your PATH.");
                Console.ReadKey();
            }
        }
    }
}
