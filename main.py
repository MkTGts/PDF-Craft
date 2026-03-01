"""
PDF Splitter, Joiner & Compressor - A GUI application for PDF operations
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

try:
    from pypdf import PdfReader, PdfWriter
except ImportError:
    messagebox.showerror(
        "Missing Dependency",
        "Please install pypdf: pip install pypdf"
    )
    raise


class PDFCraftApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PDF Craft v0.0.1")
        self.root.geometry("560x520")
        self.root.resizable(True, True)

        self.pdf_path = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.split_mode = tk.StringVar(value="each_page")
        self.pages_per_file = tk.StringVar(value="1")
        self.split_at_pages = tk.StringVar(value="1, 2, 5")
        self.join_output_path = tk.StringVar()
        self.join_files = []  # List of paths for join
        self.compress_input_path = tk.StringVar()
        self.compress_output_path = tk.StringVar()
        self.compress_streams = tk.BooleanVar(value=True)
        self.compress_duplicates = tk.BooleanVar(value=False)

        self._build_ui()

    def _build_ui(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # === Split tab ===
        split_tab = ttk.Frame(notebook, padding=15)
        notebook.add(split_tab, text="Split PDF")

        ttk.Label(split_tab, text="PDF File:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        file_frame = ttk.Frame(split_tab)
        file_frame.grid(row=1, column=0, columnspan=2, sticky=tk.EW, pady=(0, 15))
        split_tab.columnconfigure(0, weight=1)
        file_frame.columnconfigure(0, weight=1)

        ttk.Entry(file_frame, textvariable=self.pdf_path).grid(row=0, column=0, sticky=tk.EW, padx=(0, 5))
        ttk.Button(file_frame, text="Browse...", command=self._browse_pdf).grid(row=0, column=1)

        ttk.Label(split_tab, text="Output Folder:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        out_frame = ttk.Frame(split_tab)
        out_frame.grid(row=3, column=0, columnspan=2, sticky=tk.EW, pady=(0, 15))
        out_frame.columnconfigure(0, weight=1)

        ttk.Entry(out_frame, textvariable=self.output_dir).grid(row=0, column=0, sticky=tk.EW, padx=(0, 5))
        ttk.Button(out_frame, text="Browse...", command=self._browse_output).grid(row=0, column=1)

        ttk.Label(split_tab, text="Split Mode:").grid(row=4, column=0, sticky=tk.W, pady=(10, 5))
        mode_frame = ttk.Frame(split_tab)
        mode_frame.grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))

        ttk.Radiobutton(
            mode_frame, text="Each page → separate PDF",
            variable=self.split_mode, value="each_page"
        ).pack(anchor=tk.W)
        ttk.Radiobutton(
            mode_frame, text="Every N pages → one PDF",
            variable=self.split_mode, value="every_n"
        ).pack(anchor=tk.W)

        pages_frame = ttk.Frame(mode_frame)
        pages_frame.pack(anchor=tk.W, padx=(20, 0))
        ttk.Label(pages_frame, text="Pages per file:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Entry(pages_frame, textvariable=self.pages_per_file, width=6).pack(side=tk.LEFT)

        ttk.Radiobutton(
            mode_frame, text="Extract only specific pages (e.g. 1, 2, 5)",
            variable=self.split_mode, value="at_pages"
        ).pack(anchor=tk.W)
        split_frame = ttk.Frame(mode_frame)
        split_frame.pack(anchor=tk.W, padx=(20, 0))
        ttk.Label(split_frame, text="Page numbers:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Entry(split_frame, textvariable=self.split_at_pages, width=25).pack(side=tk.LEFT)

        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(split_tab, textvariable=self.status_var, foreground="gray").grid(
            row=6, column=0, columnspan=2, sticky=tk.W, pady=(15, 5)
        )

        ttk.Button(split_tab, text="Split PDF", command=self._split_pdf).grid(
            row=7, column=0, columnspan=2, pady=(10, 0)
        )

        # === Join tab ===
        join_tab = ttk.Frame(notebook, padding=15)
        notebook.add(join_tab, text="Join PDF")

        ttk.Label(join_tab, text="PDF files (order matters):").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        list_frame = ttk.Frame(join_tab)
        list_frame.grid(row=1, column=0, columnspan=2, sticky=tk.NSEW, pady=(0, 10))
        join_tab.columnconfigure(0, weight=1)
        join_tab.rowconfigure(1, weight=1)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        self.join_listbox = tk.Listbox(list_frame, height=10, selectmode=tk.EXTENDED)
        self.join_listbox.grid(row=0, column=0, sticky=tk.NSEW, padx=(0, 5))
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.join_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky=tk.NS)
        self.join_listbox.config(yscrollcommand=scrollbar.set)

        btn_frame = ttk.Frame(join_tab)
        btn_frame.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(0, 15))
        ttk.Button(btn_frame, text="Add PDFs...", command=self._join_add_files).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Remove selected", command=self._join_remove).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Clear all", command=self._join_clear).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Move up", command=self._join_move_up).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Move down", command=self._join_move_down).pack(side=tk.LEFT)

        ttk.Label(join_tab, text="Output file:").grid(row=3, column=0, sticky=tk.W, pady=(0, 5))
        out_file_frame = ttk.Frame(join_tab)
        out_file_frame.grid(row=4, column=0, columnspan=2, sticky=tk.EW, pady=(0, 15))
        out_file_frame.columnconfigure(0, weight=1)

        ttk.Entry(out_file_frame, textvariable=self.join_output_path).grid(row=0, column=0, sticky=tk.EW, padx=(0, 5))
        ttk.Button(out_file_frame, text="Save as...", command=self._join_browse_output).grid(row=0, column=1)

        self.join_status_var = tk.StringVar(value="Add PDF files to merge")
        ttk.Label(join_tab, textvariable=self.join_status_var, foreground="gray").grid(
            row=5, column=0, columnspan=2, sticky=tk.W, pady=(5, 5)
        )

        ttk.Button(join_tab, text="Join PDFs", command=self._join_pdfs).grid(
            row=6, column=0, columnspan=2, pady=(10, 0)
        )

        # === Compress tab ===
        compress_tab = ttk.Frame(notebook, padding=15)
        notebook.add(compress_tab, text="Compress PDF")

        ttk.Label(compress_tab, text="PDF File:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        comp_in_frame = ttk.Frame(compress_tab)
        comp_in_frame.grid(row=1, column=0, columnspan=2, sticky=tk.EW, pady=(0, 15))
        compress_tab.columnconfigure(0, weight=1)
        comp_in_frame.columnconfigure(0, weight=1)

        ttk.Entry(comp_in_frame, textvariable=self.compress_input_path).grid(row=0, column=0, sticky=tk.EW, padx=(0, 5))
        ttk.Button(comp_in_frame, text="Browse...", command=self._compress_browse_input).grid(row=0, column=1)

        ttk.Label(compress_tab, text="Output file:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        comp_out_frame = ttk.Frame(compress_tab)
        comp_out_frame.grid(row=3, column=0, columnspan=2, sticky=tk.EW, pady=(0, 15))
        comp_out_frame.columnconfigure(0, weight=1)

        ttk.Entry(comp_out_frame, textvariable=self.compress_output_path).grid(row=0, column=0, sticky=tk.EW, padx=(0, 5))
        ttk.Button(comp_out_frame, text="Save as...", command=self._compress_browse_output).grid(row=0, column=1)

        ttk.Label(compress_tab, text="Compression options:").grid(row=4, column=0, sticky=tk.W, pady=(10, 5))
        opt_frame = ttk.Frame(compress_tab)
        opt_frame.grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        ttk.Checkbutton(
            opt_frame, text="Lossless content stream compression (FlateDecode)",
            variable=self.compress_streams
        ).pack(anchor=tk.W)
        ttk.Checkbutton(
            opt_frame, text="Remove duplicate & unused objects",
            variable=self.compress_duplicates
        ).pack(anchor=tk.W)

        self.compress_status_var = tk.StringVar(value="Select a PDF to compress")
        ttk.Label(compress_tab, textvariable=self.compress_status_var, foreground="gray").grid(
            row=6, column=0, columnspan=2, sticky=tk.W, pady=(10, 5)
        )

        ttk.Button(compress_tab, text="Compress PDF", command=self._compress_pdf).grid(
            row=7, column=0, columnspan=2, pady=(10, 0)
        )

    def _browse_pdf(self):
        path = filedialog.askopenfilename(
            title="Select PDF",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if path:
            self.pdf_path.set(path)
            if not self.output_dir.get():
                self.output_dir.set(str(Path(path).parent))

    def _browse_output(self):
        path = filedialog.askdirectory(title="Select Output Folder")
        if path:
            self.output_dir.set(path)

    def _join_add_files(self):
        paths = filedialog.askopenfilenames(
            title="Select PDF files to join",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if paths:
            for p in paths:
                self.join_files.append(p)
                self.join_listbox.insert(tk.END, Path(p).name)
            self.join_status_var.set(f"{len(self.join_files)} file(s) selected")
            if not self.join_output_path.get():
                self.join_output_path.set(str(Path(paths[0]).parent / "merged.pdf"))

    def _join_remove(self):
        indices = list(self.join_listbox.curselection())
        if not indices:
            return
        for i in reversed(indices):
            self.join_listbox.delete(i)
            del self.join_files[i]
        self.join_status_var.set(f"{len(self.join_files)} file(s) selected")

    def _join_clear(self):
        self.join_listbox.delete(0, tk.END)
        self.join_files.clear()
        self.join_status_var.set("Add PDF files to merge")

    def _join_move_up(self):
        idx = self.join_listbox.curselection()
        if not idx or idx[0] == 0:
            return
        i = idx[0]
        self.join_files[i], self.join_files[i - 1] = self.join_files[i - 1], self.join_files[i]
        self.join_listbox.delete(i)
        self.join_listbox.insert(i - 1, Path(self.join_files[i - 1]).name)
        self.join_listbox.selection_set(i - 1)

    def _join_move_down(self):
        idx = self.join_listbox.curselection()
        if not idx or idx[0] >= len(self.join_files) - 1:
            return
        i = idx[0]
        self.join_files[i], self.join_files[i + 1] = self.join_files[i + 1], self.join_files[i]
        self.join_listbox.delete(i)
        self.join_listbox.insert(i + 1, Path(self.join_files[i + 1]).name)
        self.join_listbox.selection_set(i + 1)

    def _join_browse_output(self):
        path = filedialog.asksaveasfilename(
            title="Save merged PDF as",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if path:
            self.join_output_path.set(path)

    def _compress_browse_input(self):
        path = filedialog.askopenfilename(
            title="Select PDF to compress",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if path:
            self.compress_input_path.set(path)
            if not self.compress_output_path.get():
                self.compress_output_path.set(str(Path(path).with_stem(Path(path).stem + "_compressed")))

    def _compress_browse_output(self):
        path = filedialog.asksaveasfilename(
            title="Save compressed PDF as",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if path:
            self.compress_output_path.set(path)

    def _compress_pdf(self):
        in_path = self.compress_input_path.get().strip()
        out_path = self.compress_output_path.get().strip()

        if not in_path:
            messagebox.showerror("Error", "Please select a PDF file.")
            return
        if not Path(in_path).exists():
            messagebox.showerror("Error", f"File not found: {in_path}")
            return
        if not out_path:
            messagebox.showerror("Error", "Please specify an output file.")
            return
        if not (self.compress_streams.get() or self.compress_duplicates.get()):
            messagebox.showerror("Error", "Select at least one compression option.")
            return

        try:
            self.compress_status_var.set("Loading PDF...")
            self.root.update_idletasks()

            writer = PdfWriter(clone_from=in_path)

            if self.compress_streams.get():
                self.compress_status_var.set("Compressing content streams...")
                self.root.update_idletasks()
                for page in writer.pages:
                    page.compress_content_streams()

            if self.compress_duplicates.get():
                self.compress_status_var.set("Removing duplicates...")
                self.root.update_idletasks()
                writer.compress_identical_objects(remove_identicals=True, remove_orphans=True)

            self.compress_status_var.set("Writing file...")
            self.root.update_idletasks()
            with open(out_path, "wb") as f:
                writer.write(f)

            orig_size = Path(in_path).stat().st_size
            new_size = Path(out_path).stat().st_size
            reduction = (1 - new_size / orig_size) * 100 if orig_size > 0 else 0

            messagebox.showinfo(
                "Success",
                f"PDF compressed successfully!\n\n"
                f"Original: {orig_size / 1024:.1f} KB\n"
                f"Compressed: {new_size / 1024:.1f} KB\n"
                f"Reduction: {reduction:.1f}%"
            )
            self.compress_status_var.set("Done")
        except Exception as e:
            messagebox.showerror("Error", f"Compression failed: {e}")

    def _join_pdfs(self):
        if len(self.join_files) < 2:
            messagebox.showerror("Error", "Please add at least 2 PDF files to join.")
            return
        out_path = self.join_output_path.get().strip()
        if not out_path:
            messagebox.showerror("Error", "Please specify an output file.")
            return

        try:
            writer = PdfWriter()
            for i, pdf_path in enumerate(self.join_files):
                if not Path(pdf_path).exists():
                    messagebox.showerror("Error", f"File not found: {pdf_path}")
                    return
                self.join_status_var.set(f"Merging {i + 1}/{len(self.join_files)}...")
                self.root.update_idletasks()
                reader = PdfReader(pdf_path)
                for page in reader.pages:
                    writer.add_page(page)
            with open(out_path, "wb") as f:
                writer.write(f)
            messagebox.showinfo("Success", f"PDFs joined successfully!\nOutput: {out_path}")
            self.join_status_var.set("Done")
        except Exception as e:
            messagebox.showerror("Error", f"Join failed: {e}")

    def _split_pdf(self):
        pdf_path = self.pdf_path.get().strip()
        output_dir = self.output_dir.get().strip()

        if not pdf_path:
            messagebox.showerror("Error", "Please select a PDF file.")
            return
        if not Path(pdf_path).exists():
            messagebox.showerror("Error", f"File not found: {pdf_path}")
            return
        if not output_dir:
            messagebox.showerror("Error", "Please select an output folder.")
            return

        Path(output_dir).mkdir(parents=True, exist_ok=True)
        base_name = Path(pdf_path).stem

        try:
            reader = PdfReader(pdf_path)
            total_pages = len(reader.pages)
        except Exception as e:
            messagebox.showerror("Error", f"Could not read PDF: {e}")
            return

        mode = self.split_mode.get()

        try:
            if mode == "each_page":
                self._split_each_page(reader, output_dir, base_name, total_pages)
            elif mode == "every_n":
                n = int(self.pages_per_file.get())
                if n < 1:
                    raise ValueError("Pages per file must be at least 1")
                self._split_every_n(reader, output_dir, base_name, total_pages, n)
            elif mode == "at_pages":
                parts = [int(x.strip()) for x in self.split_at_pages.get().split(",") if x.strip()]
                page_nums = sorted(set(p for p in parts if 1 <= p <= total_pages))
                if not page_nums:
                    raise ValueError(f"Enter at least one valid page number (1–{total_pages})")
                self._extract_specific_pages(reader, output_dir, base_name, total_pages, page_nums)
            else:
                raise ValueError("Unknown split mode")
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return
        except Exception as e:
            messagebox.showerror("Error", f"Split failed: {e}")
            return

        messagebox.showinfo("Success", f"PDF split successfully!\nOutput: {output_dir}")
        self.status_var.set(f"Done. Split into files in {output_dir}")

    def _split_each_page(self, reader, output_dir, base_name, total_pages):
        for i in range(total_pages):
            writer = PdfWriter()
            writer.add_page(reader.pages[i])
            out_path = Path(output_dir) / f"{base_name}_page_{i + 1:03d}.pdf"
            with open(out_path, "wb") as f:
                writer.write(f)
            self.status_var.set(f"Writing page {i + 1}/{total_pages}...")
            self.root.update_idletasks()

    def _split_every_n(self, reader, output_dir, base_name, total_pages, n):
        file_num = 1
        for start in range(0, total_pages, n):
            end = min(start + n, total_pages)
            writer = PdfWriter()
            for j in range(start, end):
                writer.add_page(reader.pages[j])
            out_path = Path(output_dir) / f"{base_name}_part_{file_num:03d}.pdf"
            with open(out_path, "wb") as f:
                writer.write(f)
            self.status_var.set(f"Writing part {file_num} (pages {start + 1}-{end})...")
            self.root.update_idletasks()
            file_num += n
    def _extract_specific_pages(self, reader, output_dir, base_name, total_pages, page_nums):
        """Extract only the specified pages, each as its own PDF file."""
        for i, page_num in enumerate(page_nums):
            writer = PdfWriter()
            writer.add_page(reader.pages[page_num - 1])  # 0-based index
            out_path = Path(output_dir) / f"{base_name}_page_{page_num}.pdf"
            with open(out_path, "wb") as f:
                writer.write(f)
            self.status_var.set(f"Extracting page {page_num} ({i + 1}/{len(page_nums)})...")
            self.root.update_idletasks()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = PDFCraftApp()
    app.run()
