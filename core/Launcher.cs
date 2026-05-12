using System;
using System.Diagnostics;
using System.IO;
using System.Net;
using System.Threading;
using System.Windows.Forms;
using System.Drawing;

namespace SPMH_Launcher
{
    public class Program : Form
    {
        private static string CorePath;
        private static string DataPath;
        private static string DebugLog;
        private static string MainPy;
        private static string StopUrl = "http://127.0.0.1:8888/api/stop";
        private static string HubUrl = "http://127.0.0.1:8888/api/hub";
        
        private Label lblStatus;

        public Program()
        {
            CorePath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "core");
            DataPath = Path.Combine(CorePath, "data");
            DebugLog = Path.Combine(DataPath, "DEBUG_LAUNCHER.log");
            MainPy = Path.Combine(CorePath, "backend", "main.py");

            if (!Directory.Exists(DataPath)) Directory.CreateDirectory(DataPath);
            File.WriteAllText(DebugLog, "=== SPMH DEBUG SESSION " + DateTime.Now + " ===\r\n");

            this.Text = "SPMH — Debug Mode";
            this.Size = new Size(400, 200);
            this.StartPosition = FormStartPosition.CenterScreen;
            this.BackColor = Color.FromArgb(15, 15, 15);
            this.ForeColor = Color.White;

            lblStatus = new Label() { 
                Text = "● Modo Debug Ativo...", 
                Location = new Point(20, 40), 
                Size = new Size(350, 60),
                Font = new Font("Segoe UI", 10)
            };

            this.Controls.Add(lblStatus);
            new Thread(StartEngine).Start();
        }

        private void Log(string msg) {
            try { File.AppendAllText(DebugLog, "[" + DateTime.Now.ToString("HH:mm:ss") + "] " + msg + "\r\n"); } catch {}
        }

        private void StartEngine()
        {
            try {
                Log("Caminho Base: " + AppDomain.CurrentDomain.BaseDirectory);
                Log("Caminho Core: " + CorePath);
                Log("Caminho Script: " + MainPy);

                // 1. Limpeza de Porta
                Log("Limpando porta 8888...");
                try {
                    ProcessStartInfo killPort = new ProcessStartInfo("cmd.exe", "/c \"for /f \"tokens=5\" %a in ('netstat -aon ^| findstr :8888') do taskkill /f /pid %a\"");
                    killPort.WindowStyle = ProcessWindowStyle.Hidden;
                    killPort.CreateNoWindow = true;
                    Process.Start(killPort).WaitForExit();
                    Log("Limpeza de porta concluída.");
                } catch (Exception ex) { Log("Falha na limpeza de porta: " + ex.Message); }

                // 2. Inicia o Python
                Log("Tentando iniciar Python...");
                ProcessStartInfo psi = new ProcessStartInfo();
                psi.FileName = "python"; // Assume que está no PATH
                psi.Arguments = "-u \"" + MainPy + "\""; // -u para unbuffered output
                psi.WindowStyle = ProcessWindowStyle.Hidden;
                psi.CreateNoWindow = true;
                psi.UseShellExecute = false;
                psi.WorkingDirectory = CorePath;
                
                // Tenta capturar erro de inicialização imediata
                try {
                    Process p = Process.Start(psi);
                    if (p == null) {
                        Log("ERRO: Process.Start retornou NULL");
                    } else {
                        Log("Processo Python iniciado com PID: " + p.Id);
                    }
                } catch (Exception ex) {
                    Log("ERRO CRÍTICO AO INICIAR PROCESSO: " + ex.Message);
                    Log("Dica: Verifique se 'python' está no PATH do Windows.");
                }

                // 3. Monitoramento da API
                Log("Iniciando monitoramento da API em " + HubUrl);
                for (int i = 1; i <= 20; i++)
                {
                    Log("Tentativa de conexão " + i + "/20...");
                    try {
                        HttpWebRequest request = (HttpWebRequest)WebRequest.Create(HubUrl);
                        request.Timeout = 1500;
                        using (HttpWebResponse response = (HttpWebResponse)request.GetResponse()) {
                            if (response.StatusCode == HttpStatusCode.OK) {
                                Log("SUCESSO: API respondeu com OK!");
                                Process.Start("http://127.0.0.1:8888");
                                Thread.Sleep(2000);
                                Application.Exit();
                                return;
                            }
                        }
                    } catch (WebException ex) {
                        Log("Aguardando... (WebException: " + ex.Message + ")");
                    } catch (Exception ex) {
                        Log("Erro inesperado na conexão: " + ex.Message);
                    }
                    Thread.Sleep(2000);
                }
                
                Log("TIMEOUT: O motor não respondeu após 20 tentativas.");
                MessageBox.Show("O motor não iniciou.\r\nVeja o log em: core/data/DEBUG_LAUNCHER.log", "SPMH Erro");
                Application.Exit();
            } catch (Exception ex) {
                Log("ERRO GERAL NO LAUNCHER: " + ex.Message);
                Application.Exit();
            }
        }

        [STAThread]
        static void Main() { Application.Run(new Program()); }
    }
}
