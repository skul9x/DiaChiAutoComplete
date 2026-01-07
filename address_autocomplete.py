"""
Address Autocomplete - Python Recreation (CSV Version) - V3 FIXED
Tái tạo ĐÚNG thuật toán Autocomplete Địa chỉ từ hệ thống HIS

BUG FIX: Tạo entry cho TẤT CẢ các cấp (Tỉnh, Huyện+Tỉnh, Xã+Huyện+Tỉnh)
không chỉ khi không có con.

Format: ShortCutTP + ShortCutQH + ShortCutXP
Ví dụ: "bnbn" → "Thành Phố Bắc Ninh, Tỉnh Bắc Ninh" (kết quả đầu tiên)
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import List, Tuple
import csv
import os


class AddressData:
    """Lớp quản lý dữ liệu địa chỉ - V3 FIXED"""
    
    def __init__(self):
        self.raw_data: List[Tuple[str, str, str, int, str]] = []
        # Format: (combined_shortcut, level, full_address)
        # level: 0=Tỉnh only, 1=Huyện+Tỉnh, 2=Xã+Huyện+Tỉnh
        self.autocomplete_list: List[Tuple[str, int, str]] = []
    
    def load_from_csv(self, filepath: str) -> bool:
        """Load dữ liệu từ file CSV"""
        try:
            self.raw_data.clear()
            
            with open(filepath, 'r', encoding='utf-8-sig') as f:
                sample = f.read(2048)
                f.seek(0)
                
                delimiter = '\t' if '\t' in sample else ','
                reader = csv.reader(f, delimiter=delimiter)
                
                first_row = next(reader)
                if not (first_row[0].lower().startswith('ma') or 'diachinh' in first_row[0].lower()):
                    self._process_row(first_row)
                
                for row in reader:
                    self._process_row(row)
            
            self._build_autocomplete_data()
            return True
            
        except Exception as e:
            print(f"Lỗi đọc CSV: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _process_row(self, row: list):
        """Xử lý một row từ CSV"""
        if len(row) >= 5:
            ma_diachinh = str(row[0]).strip()
            ten_diachinh = str(row[1]).strip()
            ma_cha = str(row[2]).strip()
            
            try:
                loai_diachinh = int(row[3])
            except:
                loai_diachinh = 0
            
            mota_them = str(row[4]).strip().lower()
            self.raw_data.append((ma_diachinh, ten_diachinh, ma_cha, loai_diachinh, mota_them))
    
    def _get_by_type(self, loai: int) -> List[tuple]:
        return [d for d in self.raw_data if d[3] == loai]
    
    def _get_children(self, ma_cha: str) -> List[tuple]:
        return [d for d in self.raw_data if d[2] == ma_cha]
    
    def _build_autocomplete_data(self):
        """
        Xây dựng bảng autocomplete - V3 FIXED
        Tạo TẤT CẢ các cấp entry:
        - Entry cho Tỉnh alone
        - Entry cho Huyện+Tỉnh (LUÔN LUÔN, kể cả khi có Xã con)
        - Entry cho Xã+Huyện+Tỉnh
        """
        self.autocomplete_list.clear()
        
        tinh_list = self._get_by_type(0)
        
        for tinh in tinh_list:
            ma_tinh, ten_tinh, _, _, shortcut_tp = tinh
            
            if not shortcut_tp:
                continue
            
            # ALWAYS add Tỉnh-only entry
            self.autocomplete_list.append((shortcut_tp, 0, ten_tinh))
            
            huyen_list = self._get_children(ma_tinh)
            
            for huyen in huyen_list:
                ma_huyen, ten_huyen, _, _, shortcut_qh = huyen
                
                if not shortcut_qh:
                    continue
                
                # ALWAYS add Huyện+Tỉnh entry (even if has Xã children!)
                combined_qh = f"{shortcut_tp}{shortcut_qh}"
                value_qh = f"{ten_huyen}, {ten_tinh}"
                self.autocomplete_list.append((combined_qh, 1, value_qh))
                
                xa_list = self._get_children(ma_huyen)
                
                for xa in xa_list:
                    _, ten_xa, _, _, shortcut_xp = xa
                    
                    if not shortcut_xp:
                        continue
                    
                    # Add Xã+Huyện+Tỉnh entry
                    combined_xp = f"{shortcut_tp}{shortcut_qh}{shortcut_xp}"
                    value_xp = f"{ten_xa}, {ten_huyen}, {ten_tinh}"
                    self.autocomplete_list.append((combined_xp, 2, value_xp))
        
        # Sắp xếp: theo shortcut, rồi theo level (level thấp hơn = ít chi tiết hơn = lên trước)
        self.autocomplete_list.sort(key=lambda x: (x[0], x[1]))
    
    def search(self, keyword: str) -> List[Tuple[str, str]]:
        """
        Tìm kiếm địa chỉ - ĐÚNG THUẬT TOÁN C#
        Ưu tiên: exact match > startswith > contains
        Trong cùng shortcut: level thấp (ít chi tiết) lên trước
        """
        if not keyword:
            return []
        
        keyword = keyword.lower().strip()
        results = []
        
        for combined, level, address in self.autocomplete_list:
            if combined == keyword:
                # Exact match - highest priority
                results.append((combined, address, 0, level))
            elif combined.startswith(keyword):
                # Starts with - second priority
                results.append((combined, address, 1, level))
            elif keyword in combined:
                # Contains - third priority
                results.append((combined, address, 2, level))
        
        # Sort: match_type first, then shortcut length, then level
        results.sort(key=lambda x: (x[2], len(x[0]), x[3]))
        
        # Return only (shortcut, address)
        return [(r[0], r[1]) for r in results[:50]]


class AddressAutocompleteApp:
    """Ứng dụng Tkinter - V3 FIXED"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Autocomplete Địa chỉ - Tái tạo từ HIS C# (V3)")
        self.root.geometry("850x650")
        self.root.configure(bg="#f0f0f0")
        
        self.address_data = AddressData()
        self.selected_address = tk.StringVar()
        self.status_text = tk.StringVar(value="Chưa load dữ liệu. Vui lòng chọn file CSV.")
        
        self._create_widgets()
        self._bind_events()
        self._auto_load_csv()
    
    def _create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        title_label = ttk.Label(
            main_frame, 
            text="🏠 Autocomplete Địa chỉ (V3 - Fixed)", 
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 10))
        
        # CSV frame
        csv_frame = ttk.LabelFrame(main_frame, text="Nguồn dữ liệu", padding="10")
        csv_frame.pack(fill=tk.X, pady=(0, 10))
        
        load_btn = ttk.Button(csv_frame, text="📁 Chọn file CSV", command=self._load_csv)
        load_btn.pack(side=tk.LEFT, padx=5)
        
        self.status_label = ttk.Label(csv_frame, textvariable=self.status_text, foreground="gray")
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        guide_text = """Hướng dẫn: Nhập mã viết tắt để tra cứu địa chỉ
VD: "bnbn" → "Thành Phố Bắc Ninh, Tỉnh Bắc Ninh" (kết quả đầu tiên!)"""
        
        guide_label = ttk.Label(main_frame, text=guide_text, font=("Arial", 10), foreground="gray")
        guide_label.pack(pady=(0, 10))
        
        # Input frame
        input_frame = ttk.LabelFrame(main_frame, text="Nhập mã viết tắt", padding="10")
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.shortcut_entry = ttk.Entry(input_frame, font=("Arial", 14), width=50)
        self.shortcut_entry.pack(fill=tk.X, pady=5)
        self.shortcut_entry.focus()
        
        # Results frame
        suggest_frame = ttk.LabelFrame(main_frame, text="Gợi ý địa chỉ (↓ để chọn, Enter để xác nhận)", padding="10")
        suggest_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        scrollbar = ttk.Scrollbar(suggest_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.result_listbox = tk.Listbox(
            suggest_frame, 
            font=("Arial", 11),
            height=12,
            yscrollcommand=scrollbar.set,
            selectbackground="#4CAF50",
            selectforeground="white"
        )
        self.result_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.result_listbox.yview)
        
        # Selected frame
        selected_frame = ttk.LabelFrame(main_frame, text="Địa chỉ đã chọn", padding="10")
        selected_frame.pack(fill=tk.X)
        
        self.selected_label = ttk.Label(
            selected_frame, 
            textvariable=self.selected_address,
            font=("Arial", 12, "bold"),
            foreground="#2196F3",
            wraplength=750
        )
        self.selected_label.pack(fill=tk.X)
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="🗑️ Xóa", command=self._clear_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="📋 Copy", command=self._copy_address).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🔍 Debug", command=self._show_debug).pack(side=tk.LEFT, padx=5)
    
    def _bind_events(self):
        self.shortcut_entry.bind("<KeyRelease>", self._on_key_release)
        self.shortcut_entry.bind("<Down>", self._on_down_arrow)
        self.shortcut_entry.bind("<Return>", self._on_enter)
        self.result_listbox.bind("<Double-Button-1>", self._on_listbox_select)
        self.result_listbox.bind("<Return>", self._on_listbox_select)
        self.result_listbox.bind("<Up>", self._on_listbox_up)
    
    def _auto_load_csv(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(script_dir, "dmuc_diachinh.csv")
        if os.path.exists(csv_path):
            self._do_load_csv(csv_path)
    
    def _load_csv(self):
        filepath = filedialog.askopenfilename(
            title="Chọn file CSV địa chính",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialdir=os.path.dirname(os.path.abspath(__file__))
        )
        if filepath:
            self._do_load_csv(filepath)
    
    def _do_load_csv(self, filepath: str):
        if self.address_data.load_from_csv(filepath):
            count = len(self.address_data.autocomplete_list)
            raw_count = len(self.address_data.raw_data)
            self.status_text.set(f"✅ Đã load {raw_count} địa danh → {count} địa chỉ")
            self.status_label.configure(foreground="green")
        else:
            self.status_text.set("❌ Lỗi đọc file CSV")
            self.status_label.configure(foreground="red")
    
    def _on_key_release(self, event):
        keyword = self.shortcut_entry.get()
        self._update_suggestions(keyword)
    
    def _update_suggestions(self, keyword: str):
        self.result_listbox.delete(0, tk.END)
        results = self.address_data.search(keyword)
        for shortcut, address in results:
            self.result_listbox.insert(tk.END, f"[{shortcut}] → {address}")
        if results:
            self.result_listbox.selection_set(0)
    
    def _on_down_arrow(self, event):
        if self.result_listbox.size() > 0:
            self.result_listbox.focus_set()
            self.result_listbox.selection_set(0)
    
    def _on_listbox_up(self, event):
        if self.result_listbox.curselection() == (0,):
            self.shortcut_entry.focus_set()
            return "break"
    
    def _on_enter(self, event):
        if self.result_listbox.size() > 0:
            sel = self.result_listbox.curselection()
            self._select_address(sel[0] if sel else 0)
    
    def _on_listbox_select(self, event):
        sel = self.result_listbox.curselection()
        if sel:
            self._select_address(sel[0])
    
    def _select_address(self, index: int):
        item = self.result_listbox.get(index)
        if " → " in item:
            address = item.split(" → ", 1)[1]
            self.selected_address.set(address)
            self.shortcut_entry.delete(0, tk.END)
            self.shortcut_entry.insert(0, address)
            self.shortcut_entry.select_range(0, tk.END)
    
    def _copy_address(self):
        address = self.selected_address.get()
        if address:
            self.root.clipboard_clear()
            self.root.clipboard_append(address)
            messagebox.showinfo("OK", "Đã copy!")
    
    def _show_debug(self):
        debug_info = "=== DEBUG: Các entry 'bnbn' ===\n\n"
        count = 0
        for combined, level, address in self.address_data.autocomplete_list:
            if combined.startswith("bnbn") or "bnbn" in combined:
                level_name = ["Tỉnh", "Huyện+Tỉnh", "Xã+Huyện+Tỉnh"][level]
                debug_info += f"[{combined}] (level {level}: {level_name})\n  → {address}\n\n"
                count += 1
                if count >= 30:
                    break
        
        win = tk.Toplevel(self.root)
        win.title("Debug")
        win.geometry("700x500")
        text = tk.Text(win, font=("Consolas", 10), wrap=tk.WORD)
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text.insert("1.0", debug_info)
        text.config(state=tk.DISABLED)
    
    def _clear_all(self):
        self.shortcut_entry.delete(0, tk.END)
        self.result_listbox.delete(0, tk.END)
        self.selected_address.set("")
        self.shortcut_entry.focus()


def main():
    root = tk.Tk()
    app = AddressAutocompleteApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
