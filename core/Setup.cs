using System;
using System.Diagnostics;
using System.IO;
using System.Windows.Forms;
using System.Drawing;

namespace SPMH_Setup
{
    public class SetupForm : Form
    {
        private Label lblStatus;
        private TextBox txtLog;
        private Button btnStart;
        private ProgressBar pBar;

        public SetupForm()
        {
            this.Text = "SPMH — Dependency Installer";
            this.Size = new Size(500, 400);
            this.StartPosition = FormStartPosition.CenterScreen;
            this.BackColor = Color.FromArgb(15, 15, 15);
            this.ForeColor = Color.White;
            this.FormBorderStyle = FormBorderStyle.FixedDialog;

            lblStatus = new Label() { Text = "Click to start environment preparation", Location = new Point(20, 20), Size = new Size(440, 30), Font = new Font("Segoe UI", 10, FontStyle.Bold) };
            txtLog = new TextBox() { Multiline = true, ReadOnly = true, Location = new Point(20, 60), Size = new Size(440, 200), BackColor = Color.Black, ForeColor = Color.Lime, Font = new Font("Consolas", 8), ScrollBars = ScrollBars.Vertical };
            pBar = new ProgressBar() { Location = new Point(20, 270), Size = new Size(440, 20) };
            btnStart = new Button() { Text = "INSTALL EVERYTHING NOW", Location = new Point(20, 300), Size = new Size(440, 40), BackColor = Color.FromArgb(0, 120, 215), FlatStyle = FlatStyle.Flat };
            
            btnStart.Click += (s, e) => RunInstall();

            this.Controls.Add(lblStatus);
            this.Controls.Add(txtLog);
            this.Controls.Add(pBar);
            this.Controls.Add(btnStart);
        }

        private async void RunInstall()
        {
            btnStart.Enabled = false;
            txtLog.AppendText("Starting installation...\r\n");
            
            // 1. Install Python via Winget
            UpdateStatus("Checking Python 3.12...", 20);
            RunCommand("winget install Python.Python.3.12 --silent --accept-package-agreements --accept-source-agreements");

            // 2. Install FFmpeg via Winget
            UpdateStatus("Checking FFmpeg...", 50);
            RunCommand("winget install Gyan.FFmpeg --silent --accept-package-agreements --accept-source-agreements");

            // 3. Install Python Libs
            UpdateStatus("Installing Hub libraries...", 80);
            string reqPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "core", "backend", "requirements.txt");
            RunCommand("python -m pip install -r \"" + reqPath + "\" --upgrade");

            UpdateStatus("All set! You can now open SPMH.exe", 100);
            MessageBox.Show("Dependencies installed successfully!", "SPMH Setup");
            btnStart.Enabled = true;
            btnStart.Text = "CLOSE INSTALLER";
            btnStart.Click += (s, e) => Application.Exit();
        }

        private void UpdateStatus(string msg, int progress)
        {
            lblStatus.Text = msg;
            pBar.Value = progress;
            txtLog.AppendText(msg + "\r\n");
        }

        private void RunCommand(string cmd)
        {
            try {
                ProcessStartInfo psi = new ProcessStartInfo("cmd.exe", "/c " + cmd);
                psi.RedirectStandardOutput = true;
                psi.UseShellExecute = false;
                psi.CreateNoWindow = true;
                Process p = Process.Start(psi);
                string output = p.StandardOutput.ReadToEnd();
                p.WaitForExit();
                txtLog.AppendText(output + "\r\n");
            } catch (Exception ex) {
                txtLog.AppendText("Erro: " + ex.Message + "\r\n");
            }
        }

        [STAThread]
        static void Main() { Application.EnableVisualStyles(); Application.Run(new SetupForm()); }
    }
}
