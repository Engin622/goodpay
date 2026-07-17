# -*- coding: utf-8 -*-
"""
GoodPay - GoodbyeDPI Türkiye GUI
Basit ve kullanıcı dostu arayüz
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os

# Uygulama dizini
APP_DIR = os.path.dirname(os.path.abspath(__file__))

# Metod tanımlamaları: (parametreler, açıklama, Windows DNS gerekli mi?)
METHODS = {
    "Varsayılan (Önerilen)": {
        "params": "-5 --set-ttl 5 --dns-addr 77.88.8.8 --dns-port 1253 --dnsv6-addr 2a02:6b8::feed:0ff --dnsv6-port 1253",
        "desc": "DNS dahil, Windows DNS değiştirmenize gerek yok",
        "need_dns": False
    },
    "Alternatif 1": {
        "params": "--set-ttl 3",
        "desc": "Sadece TTL. Windows'ta DNS değiştirmeniz gerekir",
        "need_dns": True
    },
    "Alternatif 2": {
        "params": "-5",
        "desc": "Bazı sitelerde daha iyi. Windows'ta DNS değiştirin",
        "need_dns": True
    },
    "Alternatif 3": {
        "params": "--set-ttl 3 --dns-addr 77.88.8.8 --dns-port 1253 --dnsv6-addr 2a02:6b8::feed:0ff --dnsv6-port 1253",
        "desc": "TTL + Yandex DNS dahil",
        "need_dns": False
    },
    "Alternatif 4": {
        "params": "-5 --dns-addr 77.88.8.8 --dns-port 1253 --dnsv6-addr 2a02:6b8::feed:0ff --dnsv6-port 1253",
        "desc": "TTL olmadan, bazı siteler için daha iyi",
        "need_dns": False
    },
    "Alternatif 5": {
        "params": "-9 --dns-addr 77.88.8.8 --dns-port 1253 --dnsv6-addr 2a02:6b8::feed:0ff --dnsv6-port 1253",
        "desc": "Gelişmiş mod + DNS",
        "need_dns": False
    },
    "Alternatif 6": {
        "params": "-9",
        "desc": "Gelişmiş mod. Windows'ta DNS değiştirin",
        "need_dns": True
    }
}


def is_admin():
    """Yönetici yetkisi kontrolü"""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False


def get_arch():
    """Sistem mimarisini belirle"""
    import platform
    return "x86_64" if platform.machine().upper() in ("AMD64", "X86_64") else "x86"


def get_exe_path():
    """GoodbyeDPI exe dosya yolu"""
    arch = get_arch()
    return os.path.join(APP_DIR, arch, "goodbyedpi.exe")


def run_cmd(cmd, shell=True):
    """Komut çalıştır"""
    try:
        result = subprocess.run(cmd, shell=shell, capture_output=True, text=True, cwd=APP_DIR)
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, str(e)


def check_service_status():
    """GoodbyeDPI hizmet durumunu kontrol et"""
    success, output = run_cmd('sc query "GoodbyeDPI"')
    if success and "RUNNING" in output:
        return "Çalışıyor"
    return "Durduruldu"


class GoodPayGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("GoodPay - GoodbyeDPI Türkiye")
        self.root.geometry("480x420")
        self.root.resizable(False, False)
        self.root.configure(bg="#1a1a2e")
        
        # Stil
        style = ttk.Style()
        style.theme_use("clam")
        
        self.setup_ui()
        self.update_status()
        
    def setup_ui(self):
        # Ana frame
        main = tk.Frame(self.root, padx=24, pady=20, bg="#1a1a2e")
        main.pack(fill=tk.BOTH, expand=True)
        
        # Başlık
        title = tk.Label(main, text="🔓 GoodPay", font=("Segoe UI", 22, "bold"), 
                        fg="#e94560", bg="#1a1a2e")
        title.pack(pady=(0, 4))
        
        subtitle = tk.Label(main, text="DPI Atlatma - Basit Arayüz", 
                           font=("Segoe UI", 10), fg="#a0a0a0", bg="#1a1a2e")
        subtitle.pack(pady=(0, 20))
        
        # Metod seçimi
        method_frame = tk.Frame(main, bg="#1a1a2e")
        method_frame.pack(fill=tk.X, pady=(0, 8))
        
        tk.Label(method_frame, text="Metod:", font=("Segoe UI", 10), 
                 fg="#eee", bg="#1a1a2e").pack(side=tk.LEFT, padx=(0, 10))
        
        self.method_var = tk.StringVar(value="Varsayılan (Önerilen)")
        self.method_combo = ttk.Combobox(method_frame, textvariable=self.method_var, 
                                         values=list(METHODS.keys()), state="readonly", width=28)
        self.method_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.method_combo.bind("<<ComboboxSelected>>", self.on_method_change)
        
        # Açıklama
        self.desc_label = tk.Label(main, text="", font=("Segoe UI", 9), 
                                   fg="#7cb342", bg="#1a1a2e", wraplength=420, justify=tk.LEFT)
        self.desc_label.pack(pady=(4, 16), anchor=tk.W)
        self.on_method_change(None)
        
        # Durum
        status_frame = tk.Frame(main, bg="#16213e", relief=tk.FLAT, padx=12, pady=10)
        status_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(status_frame, text="Durum:", font=("Segoe UI", 10, "bold"), 
                 fg="#eee", bg="#16213e").pack(side=tk.LEFT, padx=(0, 8))
        self.status_label = tk.Label(status_frame, text="Kontrol ediliyor...", 
                                     font=("Segoe UI", 10), fg="#7cb342", bg="#16213e")
        self.status_label.pack(side=tk.LEFT)
        
        # Butonlar
        btn_frame = tk.Frame(main, bg="#1a1a2e")
        btn_frame.pack(fill=tk.X, pady=(0, 16))
        
        self.btn_install = tk.Button(btn_frame, text="Hizmet Kur", font=("Segoe UI", 10),
                                     bg="#e94560", fg="white", activebackground="#ff6b6b",
                                     activeforeground="white", relief=tk.FLAT, padx=16, pady=8,
                                     cursor="hand2", command=self.install_service)
        self.btn_install.pack(side=tk.LEFT, padx=(0, 10), pady=4)
        
        self.btn_remove = tk.Button(btn_frame, text="Hizmet Kaldır", font=("Segoe UI", 10),
                                    bg="#37474f", fg="white", activebackground="#546e7a",
                                    activeforeground="white", relief=tk.FLAT, padx=16, pady=8,
                                    cursor="hand2", command=self.remove_service)
        self.btn_remove.pack(side=tk.LEFT, padx=(0, 10), pady=4)
        
        self.btn_run = tk.Button(btn_frame, text="Tek Seferlik Çalıştır", font=("Segoe UI", 10),
                                 bg="#0f3460", fg="white", activebackground="#16213e",
                                 activeforeground="white", relief=tk.FLAT, padx=16, pady=8,
                                 cursor="hand2", command=self.run_once)
        self.btn_run.pack(side=tk.LEFT, padx=(0, 10), pady=4)
        
        # Durum güncelle butonu
        self.btn_refresh = tk.Button(btn_frame, text="↻ Yenile", font=("Segoe UI", 9),
                                     bg="#2d2d44", fg="#a0a0a0", relief=tk.FLAT, padx=10, pady=6,
                                     cursor="hand2", command=self.update_status)
        self.btn_refresh.pack(side=tk.LEFT, pady=4)
        
        # Bilgi
        info = tk.Label(main, text="⚠ Yönetici olarak çalıştırmanız gerekir.\n"
                         "Dosyaları orijinal klasörden taşımayın.",
                         font=("Segoe UI", 9), fg="#888", bg="#1a1a2e", justify=tk.LEFT)
        info.pack(pady=(16, 0), anchor=tk.W)
        
    def on_method_change(self, event):
        m = METHODS.get(self.method_var.get(), {})
        self.desc_label.config(text=m.get("desc", ""))
        if m.get("need_dns"):
            self.desc_label.config(fg="#ffa726")
        else:
            self.desc_label.config(fg="#7cb342")
    
    def update_status(self):
        if not is_admin():
            self.status_label.config(text="⚠ Yönetici yetkisi gerekli", fg="#ffa726")
            return
        status = check_service_status()
        self.status_label.config(text=status, 
                                 fg="#7cb342" if status == "Çalışıyor" else "#a0a0a0")
    
    def install_service(self):
        if not is_admin():
            messagebox.showerror("Hata", "Bu işlem için uygulamayı Yönetici olarak çalıştırın.\n"
                              "Sağ tık → Yönetici olarak çalıştır")
            return
        
        method = self.method_var.get()
        params = METHODS.get(method, METHODS["Varsayılan (Önerilen)"])["params"]
        exe_path = get_exe_path()
        
        if not os.path.exists(exe_path):
            messagebox.showerror("Hata", f"GoodbyeDPI bulunamadı:\n{exe_path}")
            return
        
        # sc create için: binPath= "\"C:\path\exe.exe\" param1 param2"
        full_exe = os.path.join(APP_DIR, get_arch(), "goodbyedpi.exe")
        bin_path = f'\\"{full_exe}\\" {params}'
        
        # Önce kaldır, sonra kur
        run_cmd('sc stop "GoodbyeDPI"')
        run_cmd('sc delete "GoodbyeDPI"')
        success, out = run_cmd(f'sc create "GoodbyeDPI" binPath= "{bin_path}" start= "auto"')
        
        if success:
            run_cmd('sc description "GoodbyeDPI" "Turkiye icin DNS zorlamasini kaldirir"')
            run_cmd('sc start "GoodbyeDPI"')
            messagebox.showinfo("Başarılı", "Hizmet kuruldu ve başlatıldı!\n"
                              "Bilgisayar her açıldığında otomatik çalışacak.")
        else:
            messagebox.showerror("Hata", f"Hizmet kurulamadı:\n{out}")
        
        self.update_status()
    
    def remove_service(self):
        if not is_admin():
            messagebox.showerror("Hata", "Bu işlem için uygulamayı Yönetici olarak çalıştırın.")
            return
        
        run_cmd('sc stop "GoodbyeDPI"')
        run_cmd('sc delete "GoodbyeDPI"')
        run_cmd('sc stop "WinDivert"')
        run_cmd('sc delete "WinDivert"')
        run_cmd('sc stop "WinDivert14"')
        run_cmd('sc delete "WinDivert14"')
        
        messagebox.showinfo("Tamamlandı", "GoodbyeDPI hizmeti kaldırıldı.")
        self.update_status()
    
    def run_once(self):
        if not is_admin():
            messagebox.showerror("Hata", "Bu işlem için uygulamayı Yönetici olarak çalıştırın.")
            return
        
        method = self.method_var.get()
        params = METHODS.get(method, METHODS["Varsayılan (Önerilen)"])["params"]
        exe_path = get_exe_path()
        
        if not os.path.exists(exe_path):
            messagebox.showerror("Hata", f"GoodbyeDPI bulunamadı:\n{exe_path}")
            return
        
        work_dir = os.path.join(APP_DIR, get_arch())
        try:
            subprocess.Popen([exe_path] + params.split(), cwd=work_dir,
                           creationflags=subprocess.CREATE_NEW_CONSOLE)
            messagebox.showinfo("Başlatıldı", "GoodbyeDPI tek seferlik çalıştırıldı.\n"
                              "Pencereyi kapatırsanız duracaktır.")
        except Exception as e:
            messagebox.showerror("Hata", str(e))
    
    def run(self):
        if not is_admin():
            self.root.after(100, lambda: messagebox.showwarning("Uyarı", 
                "Bazı işlemler için Yönetici yetkisi gerekir.\n"
                "Hizmet kurma/kaldırma yapamazsanız uygulamayı\n"
                "Sağ tık → Yönetici olarak çalıştır ile açın."))
        self.root.mainloop()


if __name__ == "__main__":
    app = GoodPayGUI()
    app.run()
