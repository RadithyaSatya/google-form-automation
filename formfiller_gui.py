import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import threading
import webbrowser

class FormFillerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Google Form Filler - Universal")
        self.root.geometry("700x600")
        self.root.resizable(True, True)
        
        # Variabel GUI
        self.form_url = tk.StringVar()
        self.total_responses = tk.StringVar(value="10")
        self.per_session = tk.StringVar(value="5")
        self.use_proxy = tk.BooleanVar(value=False)
        self.proxy_file = tk.StringVar()
        self.headless_mode = tk.BooleanVar(value=False)
        self.language = tk.StringVar(value="id_ID")
        
        # Buat tab
        self.tab_control = ttk.Notebook(root)
        
        # Tab utama
        self.main_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.main_tab, text="Form Filler")
        
        # Tab log
        self.log_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.log_tab, text="Log")
        
        # Tab tentang
        self.about_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.about_tab, text="Tentang")
        
        self.tab_control.pack(expand=1, fill="both")
        
        # Buat konten tab utama
        self.create_main_tab()
        
        # Buat konten tab log
        self.create_log_tab()
        
        # Buat konten tab tentang
        self.create_about_tab()
        
        # Status process
        self.process_running = False
        self.current_process = None
        
    def create_main_tab(self):
        main_frame = ttk.LabelFrame(self.main_tab, text="Konfigurasi")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # URL Form
        ttk.Label(main_frame, text="URL Google Form:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(main_frame, textvariable=self.form_url, width=50).grid(row=0, column=1, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        # Total Respons
        ttk.Label(main_frame, text="Jumlah Total Respons:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(main_frame, textvariable=self.total_responses, width=10).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Per Sesi
        ttk.Label(main_frame, text="Respons Per Sesi:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(main_frame, textvariable=self.per_session, width=10).grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Mode Headless
        ttk.Checkbutton(main_frame, text="Mode Headless (tanpa UI browser)", variable=self.headless_mode).grid(row=3, column=0, columnspan=3, sticky=tk.W, padx=5, pady=5)
        
        # Pemilihan bahasa
        ttk.Label(main_frame, text="Bahasa:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        language_combo = ttk.Combobox(main_frame, textvariable=self.language, width=10)
        language_combo['values'] = ('id_ID', 'en_US', 'es_ES', 'fr_FR', 'de_DE')
        language_combo.grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Frame Proxy
        proxy_frame = ttk.LabelFrame(main_frame, text="Konfigurasi Proxy")
        proxy_frame.grid(row=5, column=0, columnspan=3, sticky=tk.W+tk.E, padx=5, pady=5)
        
        ttk.Checkbutton(proxy_frame, text="Gunakan Proxy", variable=self.use_proxy).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Label(proxy_frame, text="File Proxy:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(proxy_frame, textvariable=self.proxy_file, width=40).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Button(proxy_frame, text="Browse", command=self.browse_proxy_file).grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Frame Tombol
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=3, pady=20)
        
        ttk.Button(button_frame, text="Uji Form (Tanpa Submit)", command=self.run_test_mode, width=25).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(button_frame, text="Mulai Pengisian", command=self.start_filling, width=25).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(button_frame, text="Berhenti", command=self.stop_filling, width=25).grid(row=0, column=2, padx=5, pady=5)
    
    def create_log_tab(self):
        log_frame = ttk.Frame(self.log_tab)
        log_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Teks log
        self.log_text = tk.Text(log_frame, wrap=tk.WORD, width=80, height=20)
        self.log_text.pack(fill="both", expand=True, side=tk.LEFT)
        
        # Scrollbar untuk log
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        scrollbar.pack(fill="y", side=tk.RIGHT)
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        # Tombol untuk buka file log
        button_frame = ttk.Frame(self.log_tab)
        button_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(button_frame, text="Buka Folder Log", command=lambda: self.open_folder("logs")).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(button_frame, text="Buka Folder Screenshot", command=lambda: self.open_folder("screenshots")).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(button_frame, text="Buka Folder Test Results", command=lambda: self.open_folder("test_results")).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(button_frame, text="Bersihkan Log", command=self.clear_log).pack(side=tk.RIGHT, padx=5, pady=5)
    
    def create_about_tab(self):
        about_frame = ttk.Frame(self.about_tab)
        about_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Judul
        ttk.Label(about_frame, text="Google Form Filler Universal", font=("Arial", 16, "bold")).pack(pady=10)
        
        # Informasi Versi
        ttk.Label(about_frame, text="Versi 1.0").pack(pady=5)
        
        # Deskripsi
        description = tk.Text(about_frame, wrap=tk.WORD, width=60, height=10, borderwidth=0, highlightthickness=0)
        description.pack(pady=10, fill="both", expand=True)
        description.insert(tk.END, """
Google Form Filler Universal adalah aplikasi untuk mengotomatisasi pengisian formulir Google Form.

Fitur:
- Deteksi otomatis pertanyaan dan opsi
- Dukungan multi-bahasa
- Dukungan proxy
- Mode headless
- Deteksi dan penanganan captcha
- Perilaku pengisian yang menyerupai manusia
- Mode pengujian tanpa submit

PERINGATAN: Gunakan aplikasi ini hanya untuk tujuan pendidikan dan dengan izin pemilik formulir. Penggunaan untuk spam atau tujuan yang melanggar Syarat Layanan Google dapat mengakibatkan pemblokiran akun.
        """)
        description.config(state="disabled")
        
        # Credits
        ttk.Label(about_frame, text="Dibuat oleh: AI Assistant", font=("Arial", 10)).pack(pady=10)
    
    def browse_proxy_file(self):
        file_path = filedialog.askopenfilename(
            title="Pilih File Proxy",
            filetypes=(("Text files", "*.txt"), ("All files", "*.*"))
        )
        if file_path:
            self.proxy_file.set(file_path)
    
    def open_folder(self, folder_name):
        if not os.path.exists(folder_name):
            messagebox.showinfo("Informasi", f"Folder {folder_name} belum ada. Folder akan dibuat saat program dijalankan.")
            return
        
        # Buka folder dengan explorer/finder
        if sys.platform == 'win32':
            os.startfile(folder_name)
        elif sys.platform == 'darwin':  # macOS
            subprocess.run(['open', folder_name])
        else:  # Linux
            subprocess.run(['xdg-open', folder_name])
    
    def clear_log(self):
        self.log_text.delete(1.0, tk.END)
    
    def update_log(self, process):
        """Update log dari proses yang berjalan"""
        while process.poll() is None:
            output = process.stdout.readline()
            if output:
                self.log_text.insert(tk.END, output)
                self.log_text.see(tk.END)
                self.root.update_idletasks()
        
        # Baca output yang tersisa
        remaining_output = process.stdout.read()
        if remaining_output:
            self.log_text.insert(tk.END, remaining_output)
            self.log_text.see(tk.END)
        
        self.process_running = False
    
    def build_command(self, test_mode=False):
        """Bangun perintah untuk menjalankan script filler"""
        cmd = ["python", "playwright_form_filler.py"]
        
        # Tambahkan parameter
        cmd.append(self.form_url.get())
        cmd.append(self.total_responses.get())
        cmd.append(self.per_session.get())
        
        # Tambahkan flag opsional
        if self.headless_mode.get():
            cmd.append("--headless")
        
        if self.use_proxy.get() and self.proxy_file.get():
            cmd.append("--proxy-file")
            cmd.append(self.proxy_file.get())
        
        if self.language.get():
            cmd.append("--language")
            cmd.append(self.language.get())
        
        if test_mode:
            cmd.append("--test")
        
        return cmd
    
    def run_command(self, cmd):
        """Jalankan perintah dalam subprocess"""
        if self.process_running:
            messagebox.showerror("Error", "Proses sedang berjalan. Hentikan proses terlebih dahulu.")
            return
        
        try:
            self.log_text.insert(tk.END, f"Menjalankan perintah: {' '.join(cmd)}\n")
            self.log_text.see(tk.END)
            
            # Buka subprocess
            self.current_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            self.process_running = True
            
            # Update log dalam thread terpisah
            threading.Thread(target=self.update_log, args=(self.current_process,), daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menjalankan perintah: {str(e)}")
    
    def validate_input(self):
        """Validasi input sebelum menjalankan script"""
        if not self.form_url.get():
            messagebox.showerror("Error", "URL Google Form tidak boleh kosong")
            return False
        
        try:
            total = int(self.total_responses.get())
            if total <= 0:
                messagebox.showerror("Error", "Jumlah total respons harus lebih dari 0")
                return False
        except ValueError:
            messagebox.showerror("Error", "Jumlah total respons harus berupa angka")
            return False
        
        try:
            per_session = int(self.per_session.get())
            if per_session <= 0:
                messagebox.showerror("Error", "Respons per sesi harus lebih dari 0")
                return False
        except ValueError:
            messagebox.showerror("Error", "Respons per sesi harus berupa angka")
            return False
        
        if self.use_proxy.get() and not self.proxy_file.get():
            messagebox.showerror("Error", "File proxy diperlukan jika menggunakan proxy")
            return False
        
        return True
    
    def run_test_mode(self):
        """Jalankan dalam mode pengujian"""
        if not self.validate_input():
            return
        
        cmd = self.build_command(test_mode=True)
        self.run_command(cmd)
    
    def start_filling(self):
        """Mulai proses pengisian formulir"""
        if not self.validate_input():
            return
        
        # Konfirmasi sebelum mulai untuk pengisian dalam jumlah besar
        total = int(self.total_responses.get())
        if total > 20:
            confirm = messagebox.askyesno(
                "Konfirmasi", 
                f"Anda akan mengisi formulir sebanyak {total} kali. Pastikan Anda memiliki izin pemilik formulir. Lanjutkan?"
            )
            if not confirm:
                return
        
        cmd = self.build_command()
        self.run_command(cmd)
    
    def stop_filling(self):
        """Hentikan proses pengisian yang sedang berjalan"""
        if not self.process_running or not self.current_process:
            messagebox.showinfo("Informasi", "Tidak ada proses yang sedang berjalan")
            return
        
        confirm = messagebox.askyesno("Konfirmasi", "Yakin ingin menghentikan proses?")
        if confirm:
            self.current_process.terminate()
            self.log_text.insert(tk.END, "\n*** Proses dihentikan oleh pengguna ***\n")
            self.process_running = False

if __name__ == "__main__":
    root = tk.Tk()
    app = FormFillerGUI(root)
    root.mainloop()