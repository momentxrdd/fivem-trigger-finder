import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import re
from pathlib import Path
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

class TriggerFinderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FiveM Trigger Bulucu")
        self.root.geometry("1200x800")
        self.root.minsize(900, 600)
        
        # Değişkenler
        self.server_path = tk.StringVar()
        self.search_query = tk.StringVar()
        self.all_triggers = []
        self.filtered_triggers = []
        
        # Özel kelimeler (önceden tanımlı)
        self.special_keywords = [
            "additem",
            "vehicle", "admin", "giveitem", "removeitem", "openinventory" , "drug"       ]
        
        self.setup_ui()
        self.load_special_keywords()
        
    def setup_ui(self):
        # Ana çerçeve
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Stil
        style = ttk.Style()
        style.theme_use('clam')
        
        # Üst panel - Sunucu seçimi
        top_frame = ttk.LabelFrame(main_frame, text="Sunucu Lokasyonu", padding="10")
        top_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Entry(top_frame, textvariable=self.server_path, width=80).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(top_frame, text="Klasör Seç", command=self.select_folder).grid(row=0, column=1, padx=(0, 5))
        ttk.Button(top_frame, text="Triggerleri Tara", command=self.scan_triggers).grid(row=0, column=2)
        
        # Orta panel - Arama ve filtreler
        search_frame = ttk.LabelFrame(main_frame, text="Arama ve Filtreler", padding="10")
        search_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(search_frame, text="Arama:").grid(row=0, column=0, padx=(0, 5))
        search_entry = ttk.Entry(search_frame, textvariable=self.search_query, width=40)
        search_entry.grid(row=0, column=1, padx=(0, 5))
        search_entry.bind('<KeyRelease>', lambda e: self.filter_triggers())
        
        ttk.Button(search_frame, text="Ara", command=self.filter_triggers).grid(row=0, column=2, padx=(0, 10))
        ttk.Button(search_frame, text="Tümünü Göster", command=self.show_all_triggers).grid(row=0, column=3, padx=(0, 10))
        ttk.Button(search_frame, text="Özel Kelimeler", command=self.show_special_keywords).grid(row=0, column=4)
        
        # Alt panel - Sonuçlar
        results_frame = ttk.LabelFrame(main_frame, text="Bulunan Triggerler", padding="10")
        results_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.rowconfigure(2, weight=1)
        
        # Treeview (tablo görünümü)
        columns = ("trigger", "dosya", "satir", "kod", "tip")
        self.tree = ttk.Treeview(results_frame, columns=columns, show="tree headings", height=20)
        
        self.tree.heading("#0", text="")
        self.tree.heading("trigger", text="Trigger İsmi")
        self.tree.heading("dosya", text="Dosya Yolu")
        self.tree.heading("satir", text="Satır")
        self.tree.heading("kod", text="Kod Satırı")
        self.tree.heading("tip", text="Tip")
        
        self.tree.column("#0", width=30)
        self.tree.column("trigger", width=250)
        self.tree.column("dosya", width=300)
        self.tree.column("satir", width=60)
        self.tree.column("kod", width=400)
        self.tree.column("tip", width=120)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        # Alt durum çubuğu
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.status_label = ttk.Label(status_frame, text="Hazır", relief=tk.SUNKEN)
        self.status_label.pack(fill=tk.X, side=tk.LEFT, expand=True)
        
        self.count_label = ttk.Label(status_frame, text="Toplam: 0", relief=tk.SUNKEN)
        self.count_label.pack(side=tk.RIGHT, padx=(5, 0))
        
    def select_folder(self):
        folder = filedialog.askdirectory(title="FiveM Sunucu Klasörünü Seçin")
        if folder:
            self.server_path.set(folder)
            self.status_label.config(text=f"Seçildi: {folder}")
            
    def process_file(self, file_path, path, patterns):
        """Tek bir dosyayı işle"""
        triggers = []
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.readlines()
                
            for line_num, line in enumerate(content, 1):
                for pattern, trigger_type in patterns:
                    matches = re.finditer(pattern, line)
                    for match in matches:
                        trigger_name = match.group(1)
                        relative_path = os.path.relpath(file_path, path)
                        code_line = line.strip()[:100]  # İlk 100 karakter
                        
                        triggers.append({
                            'name': trigger_name,
                            'file': str(relative_path),
                            'line': line_num,
                            'code': code_line,
                            'type': trigger_type,
                            'full_path': str(file_path)
                        })
        except Exception as e:
            print(f"Hata: {file_path} - {e}")
        
        return triggers
    
    def scan_triggers(self):
        path = self.server_path.get()
        if not path or not os.path.exists(path):
            messagebox.showerror("Hata", "Lütfen geçerli bir sunucu klasörü seçin!")
            return
            
        self.status_label.config(text="Triggerler taranıyor...")
        self.root.update()
        
        self.all_triggers = []
        
        # Lua ve JS dosyalarını bul
        lua_files = list(Path(path).rglob("*.lua"))
        js_files = list(Path(path).rglob("*.js"))
        all_files = lua_files + js_files
        
        total_files = len(all_files)
        
        # Trigger pattern'leri
        patterns = [
            # Client triggers
            (r'TriggerEvent\(["\']([^"\']+)["\']', 'Client Event'),
            (r'TriggerServerEvent\(["\']([^"\']+)["\']', 'Server Event'),
            (r'RegisterNetEvent\(["\']([^"\']+)["\']', 'Net Event'),
            (r'AddEventHandler\(["\']([^"\']+)["\']', 'Event Handler'),
            # Server triggers
            (r'RegisterServerEvent\(["\']([^"\']+)["\']', 'Server Event'),
            (r'RegisterCommand\(["\']([^"\']+)["\']', 'Command'),
            # Callbacks
            (r'ESX\.RegisterServerCallback\(["\']([^"\']+)["\']', 'Server Callback'),
            (r'ESX\.TriggerServerCallback\(["\']([^"\']+)["\']', 'Server Callback'),
            (r'QBCore\.Functions\.CreateCallback\(["\']([^"\']+)["\']', 'QB Callback'),
            (r'QBCore\.Functions\.TriggerCallback\(["\']([^"\']+)["\']', 'QB Callback'),
        ]
        
        processed = 0
        self.processing_lock = threading.Lock()
        
        # Çoklu thread ile paralel işleme
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = {executor.submit(self.process_file, file_path, path, patterns): file_path 
                      for file_path in all_files}
            
            for future in as_completed(futures):
                triggers = future.result()
                with self.processing_lock:
                    self.all_triggers.extend(triggers)
                    processed += 1
                    
                    if processed % 5 == 0:
                        self.status_label.config(text=f"Taranıyor... {processed}/{total_files}")
                        self.root.update()
                
        # Sonuçları göster
        self.show_all_triggers()
        self.status_label.config(text=f"Tarama tamamlandı! {len(self.all_triggers)} trigger bulundu.")
        messagebox.showinfo("Tamamlandı", f"{len(self.all_triggers)} adet trigger bulundu!\n{total_files} dosya tarandı.")
        
    def show_all_triggers(self):
        self.search_query.set("")
        self.filtered_triggers = self.all_triggers.copy()
        self.update_treeview()
        
    def filter_triggers(self):
        query = self.search_query.get().lower()
        if not query:
            self.show_all_triggers()
            return
            
        self.filtered_triggers = [
            t for t in self.all_triggers
            if query in t['name'].lower() or query in t['file'].lower() or query in t['type'].lower()
        ]
        self.update_treeview()
        self.status_label.config(text=f"Arama: '{query}' - {len(self.filtered_triggers)} sonuç")
        
    def show_special_keywords(self):
        # Özel kelimeleri içeren triggerleri filtrele
        self.filtered_triggers = [
            t for t in self.all_triggers
            if any(keyword.lower() in t['name'].lower() for keyword in self.special_keywords)
        ]
        self.update_treeview()
        self.status_label.config(text=f"Özel kelimeler filtresi - {len(self.filtered_triggers)} sonuç")
        
    def update_treeview(self):
        # Treeview'i temizle
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Yeni verileri ekle
        for trigger in self.filtered_triggers:
            self.tree.insert("", tk.END, values=(
                trigger['name'],
                trigger['file'],
                trigger['line'],
                trigger['code'],
                trigger['type']
            ))
            
        self.count_label.config(text=f"Toplam: {len(self.filtered_triggers)}")
        
    def load_special_keywords(self):
        # Özel kelimeleri dosyadan yükle (varsa)
        if os.path.exists('special_keywords.json'):
            try:
                with open('special_keywords.json', 'r', encoding='utf-8') as f:
                    self.special_keywords = json.load(f)
            except:
                pass
        else:
            # Varsayılan kelimeleri kaydet
            self.save_special_keywords()
            
    def save_special_keywords(self):
        with open('special_keywords.json', 'w', encoding='utf-8') as f:
            json.dump(self.special_keywords, f, indent=2, ensure_ascii=False)

def main():
    root = tk.Tk()
    app = TriggerFinderApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

