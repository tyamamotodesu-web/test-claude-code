"""
証拠番号スタンプアプリ
PDFファイルの1ページ目右上に 甲1, 甲2 / 乙1, 乙2 ... を赤文字で連番押印する
"""
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import fitz  # pip install pymupdf

# Windows で使える日本語フォント（優先順）
JAPANESE_FONTS = [
    "C:/Windows/Fonts/YuGothB.ttc",
    "C:/Windows/Fonts/msgothic.ttc",
    "C:/Windows/Fonts/meiryo.ttc",
]

def find_font() -> str | None:
    for path in JAPANESE_FONTS:
        if os.path.exists(path):
            return path
    return None

def stamp_page(page: fitz.Page, text: str, font_path: str | None) -> None:
    font_size = 36
    margin = 20

    if font_path:
        # 日本語フォントでテキスト幅を計測
        doc_tmp = fitz.open()
        page_tmp = doc_tmp.new_page()
        tw = page_tmp.insert_text((0, 50), text, fontfile=font_path, fontsize=font_size)
        text_width = tw  # insert_text は描画幅を返さないので近似
        doc_tmp.close()
        # 近似：1文字あたり font_size * 0.9
        text_width = len(text) * font_size * 0.9
        x = page.rect.width - text_width - margin
        y = margin + font_size
        page.insert_text((x, y), text, fontfile=font_path, fontsize=font_size, color=(1, 0, 0))
    else:
        text_width = fitz.get_text_length(text, fontname="helvetica", fontsize=font_size)
        x = page.rect.width - text_width - margin
        y = margin + font_size
        page.insert_text((x, y), text, fontname="helvetica", fontsize=font_size, color=(1, 0, 0))

def stamp_pdf(input_path: str, output_path: str, text: str, font_path: str | None) -> None:
    doc = fitz.open(input_path)
    stamp_page(doc[0], text, font_path)
    doc.save(output_path)
    doc.close()


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("証拠番号スタンプアプリ")
        self.resizable(False, False)
        self.font_path = find_font()
        self._build_ui()

    def _build_ui(self):
        pad = {"padx": 8, "pady": 4}

        # ── ファイルリスト ──
        frame_list = ttk.LabelFrame(self, text="PDFファイル（順番がそのまま番号になります）")
        frame_list.grid(row=0, column=0, columnspan=3, sticky="ew", **pad)

        self.listbox = tk.Listbox(frame_list, width=60, height=10, selectmode=tk.SINGLE)
        self.listbox.pack(side="left", fill="both", expand=True, padx=4, pady=4)

        sb = ttk.Scrollbar(frame_list, orient="vertical", command=self.listbox.yview)
        sb.pack(side="left", fill="y")
        self.listbox.configure(yscrollcommand=sb.set)

        btn_frame = ttk.Frame(frame_list)
        btn_frame.pack(side="left", padx=4)
        ttk.Button(btn_frame, text="追加", width=8, command=self._add_files).pack(pady=2)
        ttk.Button(btn_frame, text="削除", width=8, command=self._remove_file).pack(pady=2)
        ttk.Button(btn_frame, text="↑ 上へ", width=8, command=self._move_up).pack(pady=2)
        ttk.Button(btn_frame, text="↓ 下へ", width=8, command=self._move_down).pack(pady=2)
        ttk.Button(btn_frame, text="全削除", width=8, command=self._clear_files).pack(pady=2)

        # ── スタンプ設定 ──
        frame_cfg = ttk.LabelFrame(self, text="スタンプ設定")
        frame_cfg.grid(row=1, column=0, columnspan=3, sticky="ew", **pad)

        ttk.Label(frame_cfg, text="種別：").grid(row=0, column=0, sticky="w", padx=8, pady=6)
        self.prefix_var = tk.StringVar(value="甲")
        ttk.Radiobutton(frame_cfg, text="甲（原告側）", variable=self.prefix_var, value="甲").grid(row=0, column=1, sticky="w")
        ttk.Radiobutton(frame_cfg, text="乙（被告側）", variable=self.prefix_var, value="乙").grid(row=0, column=2, sticky="w")
        ttk.Radiobutton(frame_cfg, text="丙", variable=self.prefix_var, value="丙").grid(row=0, column=3, sticky="w")

        ttk.Label(frame_cfg, text="開始番号：").grid(row=1, column=0, sticky="w", padx=8, pady=6)
        self.start_var = tk.IntVar(value=1)
        ttk.Spinbox(frame_cfg, from_=1, to=999, width=6, textvariable=self.start_var).grid(row=1, column=1, sticky="w")

        # ── 出力先 ──
        frame_out = ttk.LabelFrame(self, text="出力先フォルダ")
        frame_out.grid(row=2, column=0, columnspan=3, sticky="ew", **pad)

        self.outdir_var = tk.StringVar(value=os.path.expanduser("~\\Desktop\\スタンプ済み"))
        ttk.Entry(frame_out, textvariable=self.outdir_var, width=50).pack(side="left", padx=4, pady=4)
        ttk.Button(frame_out, text="参照", command=self._browse_outdir).pack(side="left", pady=4)

        # ── プレビュー ──
        self.preview_var = tk.StringVar(value="（ファイルを追加するとプレビューが表示されます）")
        ttk.Label(self, textvariable=self.preview_var, foreground="gray").grid(
            row=3, column=0, columnspan=3, sticky="w", padx=10)

        self.listbox.bind("<<ListboxSelect>>", self._update_preview)
        self.prefix_var.trace_add("write", lambda *_: self._update_preview())
        self.start_var.trace_add("write", lambda *_: self._update_preview())

        # ── 実行ボタン ──
        ttk.Button(self, text="スタンプ実行", command=self._run,
                   style="Accent.TButton").grid(row=4, column=0, columnspan=3, pady=10)

        # ── ログ ──
        frame_log = ttk.LabelFrame(self, text="ログ")
        frame_log.grid(row=5, column=0, columnspan=3, sticky="ew", **pad)
        self.log = tk.Text(frame_log, height=6, width=70, state="disabled", bg="#f5f5f5")
        self.log.pack(fill="both", padx=4, pady=4)

    # ── ファイル操作 ──

    def _add_files(self):
        paths = filedialog.askopenfilenames(
            title="PDFファイルを選択", filetypes=[("PDF files", "*.pdf")])
        for p in paths:
            self.listbox.insert(tk.END, p)
        self._update_preview()

    def _remove_file(self):
        sel = self.listbox.curselection()
        if sel:
            self.listbox.delete(sel[0])
        self._update_preview()

    def _move_up(self):
        sel = self.listbox.curselection()
        if not sel or sel[0] == 0:
            return
        i = sel[0]
        val = self.listbox.get(i)
        self.listbox.delete(i)
        self.listbox.insert(i - 1, val)
        self.listbox.select_set(i - 1)
        self._update_preview()

    def _move_down(self):
        sel = self.listbox.curselection()
        if not sel or sel[0] == self.listbox.size() - 1:
            return
        i = sel[0]
        val = self.listbox.get(i)
        self.listbox.delete(i)
        self.listbox.insert(i + 1, val)
        self.listbox.select_set(i + 1)
        self._update_preview()

    def _clear_files(self):
        self.listbox.delete(0, tk.END)
        self._update_preview()

    def _browse_outdir(self):
        d = filedialog.askdirectory(title="出力先フォルダを選択")
        if d:
            self.outdir_var.set(d)

    # ── プレビュー更新 ──

    def _update_preview(self, *_):
        files = list(self.listbox.get(0, tk.END))
        if not files:
            self.preview_var.set("（ファイルを追加するとプレビューが表示されます）")
            return
        prefix = self.prefix_var.get()
        start = self.start_var.get()
        lines = [f"  {prefix}{start + i}  ←  {os.path.basename(f)}" for i, f in enumerate(files)]
        self.preview_var.set("スタンプ割り当てプレビュー：\n" + "\n".join(lines))

    # ── スタンプ実行 ──

    def _log(self, msg: str):
        self.log.configure(state="normal")
        self.log.insert(tk.END, msg + "\n")
        self.log.see(tk.END)
        self.log.configure(state="disabled")
        self.update_idletasks()

    def _run(self):
        files = list(self.listbox.get(0, tk.END))
        if not files:
            messagebox.showwarning("確認", "PDFファイルを1つ以上追加してください。")
            return

        prefix = self.prefix_var.get()
        start = self.start_var.get()
        outdir = self.outdir_var.get()
        os.makedirs(outdir, exist_ok=True)

        errors = []
        for i, path in enumerate(files):
            label = f"{prefix}{start + i}"
            basename = os.path.splitext(os.path.basename(path))[0]
            out_path = os.path.join(outdir, f"{label}_{basename}.pdf")
            try:
                stamp_pdf(path, out_path, label, self.font_path)
                self._log(f"[OK] {label} → {out_path}")
            except Exception as e:
                errors.append(path)
                self._log(f"[ERROR] {label} {path}: {e}")

        if errors:
            messagebox.showerror("エラー", f"{len(errors)} 件の処理に失敗しました。\nログを確認してください。")
        else:
            messagebox.showinfo("完了", f"{len(files)} 件のスタンプ押印が完了しました。\n\n保存先：{outdir}")


if __name__ == "__main__":
    app = App()
    app.mainloop()
