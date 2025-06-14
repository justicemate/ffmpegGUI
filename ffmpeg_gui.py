import os
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

# Drag-and-drop support via tkinterdnd2 (optional)
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False

class FFmpegApp(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title('FFmpeg GUI')
        self.master.geometry('900x650')
        # Configure resizing
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)

        # Determine ffmpeg executable path
        script_dir = os.path.dirname(os.path.abspath(__file__))
        local_ffmpeg = os.path.join(script_dir, 'ffmpeg.exe')
        self.ffmpeg_executable = local_ffmpeg if os.path.isfile(local_ffmpeg) else 'ffmpeg'

        self.create_widgets()

    def create_widgets(self):
        # Main frame grid
        self.grid(sticky='nsew')
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(2, weight=1)

        # Notebook
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)

        # Tabs
        self.tab_files   = ttk.Frame(self.notebook)
        self.tab_trim    = ttk.Frame(self.notebook)
        self.tab_filters = ttk.Frame(self.notebook)
        self.tab_rotate  = ttk.Frame(self.notebook)
        self.tab_speed   = ttk.Frame(self.notebook)
        self.tab_format  = ttk.Frame(self.notebook)
        self.tab_meta    = ttk.Frame(self.notebook)
        self.tab_stitch  = ttk.Frame(self.notebook)

        for frame, title in [
            (self.tab_files, 'Files'),
            (self.tab_trim, 'Trim'),
            (self.tab_filters, 'Filters'),
            (self.tab_rotate, 'Rotate/Flip'),
            (self.tab_speed, 'Speed'),
            (self.tab_format, 'Format'),
            (self.tab_meta, 'Metadata'),
            (self.tab_stitch, 'Stitch')
        ]:
            self.notebook.add(frame, text=title)

        # Build each tab
        self.build_files_tab()
        self.build_trim_tab()
        self.build_filters_tab()
        self.build_rotate_tab()
        self.build_speed_tab()
        self.build_format_tab()
        self.build_meta_tab()
        self.build_stitch_tab()

        # Run/Cancel frame
        run_frame = ttk.Frame(self)
        run_frame.grid(row=1, column=0, sticky='ew', padx=10, pady=(0,10))
        run_frame.columnconfigure(0, weight=1)

        self.run_button = ttk.Button(run_frame, text='Run', command=self.on_run)
        self.run_button.grid(row=0, column=1, padx=5)
        ttk.Button(run_frame, text='Cancel', command=self.master.quit).grid(row=0, column=2)

        # Log output
        self.log = scrolledtext.ScrolledText(self, state='disabled')
        self.log.grid(row=2, column=0, sticky='nsew', padx=10, pady=(0,10))

        # Tab change binding
        self.notebook.bind('<<NotebookTabChanged>>', self._on_tab_changed)
        self._on_tab_changed()

    def _on_tab_changed(self, event=None):
        current = self.notebook.tab(self.notebook.select(), 'text')
        if current == 'Files':
            self.run_button.state(['disabled'])
        else:
            self.run_button.state(['!disabled'])

    def build_files_tab(self):
        tab = self.tab_files
        tab.columnconfigure(1, weight=1)
        labels = ['Input File:', 'Second File (Stitch):', 'Output File:']
        for i, text in enumerate(labels):
            ttk.Label(tab, text=text).grid(row=i, column=0, sticky='e', pady=5)
            entry = ttk.Entry(tab)
            entry.grid(row=i, column=1, sticky='ew', padx=5)
            # Drag-and-drop
            if DND_AVAILABLE:
                entry.drop_target_register(DND_FILES)
                entry.dnd_bind('<<Drop>>', lambda e, ent=entry: (ent.delete(0, 'end'), ent.insert(0, e.data)))
            # Browse buttons
            if i < 2:
                btn = ttk.Button(tab, text='Browse', command=lambda e=entry: self.browse_file(e))
            else:
                btn = ttk.Button(tab, text='Save As', command=lambda e=entry: self.browse_save(e))
            btn.grid(row=i, column=2, padx=5)
            setattr(self, f'file_entry_{i}', entry)

    def build_trim_tab(self):
        tab = self.tab_trim
        tab.columnconfigure(1, weight=1)
        ttk.Label(tab, text='Start (s)').grid(row=0, column=0, sticky='e', pady=5)
        self.trim_start = ttk.Spinbox(tab, from_=0, to=9999, width=10)
        self.trim_start.grid(row=0, column=1, sticky='w')
        ttk.Label(tab, text='End (s)').grid(row=1, column=0, sticky='e', pady=5)
        self.trim_end = ttk.Spinbox(tab, from_=0, to=9999, width=10)
        self.trim_end.grid(row=1, column=1, sticky='w')

    def build_filters_tab(self):
        tab = self.tab_filters
        tab.columnconfigure(1, weight=1)
        ttk.Label(tab, text='Reverse').grid(row=0, column=0, sticky='w', pady=5)
        self.reverse_var = tk.BooleanVar()
        ttk.Checkbutton(tab, variable=self.reverse_var).grid(row=0, column=1, sticky='w')
        ttk.Label(tab, text='Ping-Pong').grid(row=1, column=0, sticky='w', pady=5)
        self.pingpong_var = tk.BooleanVar()
        ttk.Checkbutton(tab, variable=self.pingpong_var).grid(row=1, column=1, sticky='w')
        ttk.Label(tab, text='Custom Filter').grid(row=2, column=0, sticky='e', pady=5)
        self.custom_filter = ttk.Entry(tab)
        self.custom_filter.grid(row=2, column=1, columnspan=2, sticky='ew', padx=5)

    def build_rotate_tab(self):
        tab = self.tab_rotate
        frame = ttk.LabelFrame(tab, text='Rotate & Flip')
        frame.pack(fill='x', padx=10, pady=10)
        frame.columnconfigure(tuple(range(5)), weight=1)
        ttk.Label(frame, text='Preset:').grid(row=0, column=0, sticky='e')
        self.rotate_var = tk.IntVar(value=0)
        for idx, ang in enumerate((0, 90, 180, 270)):
            ttk.Radiobutton(frame, text=f'{ang}\u00B0', variable=self.rotate_var, value=ang).grid(row=0, column=idx+1)
        ttk.Label(frame, text='Custom Angle:').grid(row=1, column=0, sticky='e', pady=5)
        self.custom_rotate = ttk.Spinbox(frame, from_=0, to=360, width=5)
        self.custom_rotate.grid(row=1, column=1, sticky='w')
        self.flip_h_var = tk.BooleanVar()
        ttk.Checkbutton(frame, text='Flip H', variable=self.flip_h_var).grid(row=2, column=0, sticky='w')
        self.flip_v_var = tk.BooleanVar()
        ttk.Checkbutton(frame, text='Flip V', variable=self.flip_v_var).grid(row=2, column=1, sticky='w')

    def build_speed_tab(self):
        tab = self.tab_speed
        frame = ttk.LabelFrame(tab, text='Speed')
        frame.pack(fill='x', padx=10, pady=10)
        frame.columnconfigure(1, weight=1)
        ttk.Label(frame, text='Speed Factor').grid(row=0, column=0, sticky='e')
        self.speed_var = tk.DoubleVar(value=1.0)
        ttk.Spinbox(frame, from_=0.1, to=4.0, increment=0.1, textvariable=self.speed_var, width=5).grid(row=0, column=1, sticky='w')
        self.audio_speed_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame, text='Adjust Audio', variable=self.audio_speed_var).grid(row=1, column=0, columnspan=2, sticky='w')

    def build_format_tab(self):
        tab = self.tab_format
        frame = ttk.LabelFrame(tab, text='Format')
        frame.pack(fill='x', padx=10, pady=10)
        for i in range(4): frame.columnconfigure(i, weight=1)
        ttk.Label(frame, text='Container').grid(row=0, column=0, sticky='e')
        self.container_var = ttk.Combobox(frame, values=['mp4','mkv','mov','avi','webm'], width=6)
        self.container_var.set('mp4')
        self.container_var.grid(row=0, column=1, sticky='w')
        ttk.Label(frame, text='V Codec').grid(row=1, column=0, sticky='e')
        self.vcodec_var = ttk.Combobox(frame, values=['libx264','libx265','libvpx-vp9','copy'], width=10)
        self.vcodec_var.set('libx264')
        self.vcodec_var.grid(row=1, column=1, sticky='w')
        ttk.Label(frame, text='Preset').grid(row=1, column=2, sticky='e')
        self.preset_var = ttk.Combobox(frame, values=['ultrafast','superfast','veryfast','medium','slow'], width=10)
        self.preset_var.set('medium')
        self.preset_var.grid(row=1, column=3, sticky='w')
        ttk.Label(frame, text='CRF').grid(row=2, column=0, sticky='e', pady=5)
        self.crf_var = ttk.Spinbox(frame, from_=0, to=51, width=5)
        self.crf_var.set(23)
        self.crf_var.grid(row=2, column=1, sticky='w')
        ttk.Label(frame, text='V Bitrate').grid(row=2, column=2, sticky='e')
        self.vbitrate_var = ttk.Entry(frame)
        self.vbitrate_var.grid(row=2, column=3, sticky='w')
        ttk.Label(frame, text='A Codec').grid(row=3, column=0, sticky='e', pady=5)
        self.acodec_var = ttk.Combobox(frame, values=['aac','mp3','opus','copy'], width=10)
        self.acodec_var.set('aac')
        self.acodec_var.grid(row=3, column=1, sticky='w')
        ttk.Label(frame, text='A Bitrate').grid(row=3, column=2, sticky='e')
        self.abitrate_var = ttk.Entry(frame)
        self.abitrate_var.insert(0, '128k')
        self.abitrate_var.grid(row=3, column=3, sticky='w')

    def build_meta_tab(self):
        tab = self.tab_meta
        frame = ttk.LabelFrame(tab, text='Metadata')
        frame.pack(fill='x', padx=10, pady=10)
        for i in range(2): frame.columnconfigure(i, weight=1)
        fields = [('Title','title'), ('Artist','artist'), ('Album','album'), ('Genre','genre'), ('Year','date'), ('Track','track'), ('Comment','comment')]
        for i,(lbl,attr) in enumerate(fields):
            ttk.Label(frame, text=lbl).grid(row=i, column=0, sticky='e', pady=3)
            ent = ttk.Entry(frame)
            ent.grid(row=i, column=1, sticky='ew', pady=3)
            setattr(self, f'meta_{attr}', ent)
        # Cover art
        ttk.Label(frame, text='Cover Art').grid(row=len(fields), column=0, sticky='e')
        self.cover_entry = ttk.Entry(frame)
        self.cover_entry.grid(row=len(fields), column=1, sticky='ew')
        ttk.Button(frame, text='Browse', command=self.browse_cover).grid(row=len(fields), column=2, padx=5)
        if DND_AVAILABLE:
            self.cover_entry.drop_target_register(DND_FILES)
            self.cover_entry.dnd_bind('<<Drop>>', lambda e: (self.cover_entry.delete(0,'end'), self.cover_entry.insert(0, e.data)))

    def build_stitch_tab(self):
        ttk.Label(self.tab_stitch, text='Stitch using Files tab inputs', font=('Arial', 12)).pack(pady=20)

    def browse_file(self, entry):
        path = filedialog.askopenfilename(filetypes=[('Video','*.mp4;*.mkv;*.avi;*.mov')])
        if path:
            entry.delete('0', tk.END)
            entry.insert('0', path)

    def browse_save(self, entry):
        ext = f".{self.container_var.get()}"
        path = filedialog.asksaveasfilename(defaultextension=ext, filetypes=[('Video', f"*{ext}")])
        if path:
            entry.delete('0', tk.END)
            entry.insert('0', path)

    def browse_cover(self):
        path = filedialog.askopenfilename(filetypes=[('Image','*.jpg;*.png')])
        if path:
            self.cover_entry.delete('0', tk.END)
            self.cover_entry.insert('0', path)

    def on_run(self):
        infile = self.file_entry_0.get().strip()
        outfile = self.file_entry_2.get().strip()
        if not infile or not outfile:
            messagebox.showerror('Error', 'Specify input/output')
            return
        tab = self.notebook.tab(self.notebook.select(), 'text')
        cmd = [self.ffmpeg_executable, '-y']

        if tab == 'Trim':
            start = self.trim_start.get().strip()
            end   = self.trim_end.get().strip()
            if not start or not end:
                messagebox.showerror('Error', 'Specify start and end times')
                return
            cmd += ['-i', infile, '-ss', start, '-to', end, '-c', 'copy', outfile]

        elif tab == 'Rotate/Flip':
            angle = int(self.rotate_var.get())
            try:
                custom = int(self.custom_rotate.get())
            except ValueError:
                custom = 0
            if custom:
                angle = custom

            filters = []
            if angle:
                filters.append(f"rotate={angle}*PI/180:ow=rotw({angle}*PI/180):oh=roth({angle}*PI/180)")
            if self.flip_h_var.get():
                filters.append('hflip')
            if self.flip_v_var.get():
                filters.append('vflip')
            if not filters:
                messagebox.showerror('Error', 'No rotate/flip option selected')
                return
            vf = ','.join(filters)
            cmd += ['-i', infile, '-vf', vf, '-c:a', 'copy', outfile]

        elif tab == 'Filters':
            cmd += ['-i', infile]
            if self.pingpong_var.get():
                filter_complex = (
                    '[0:v]split=2[forward][tmp];'
                    '[tmp]reverse[reverse];'
                    '[forward][reverse]concat=n=2:v=1[outv]'
                )
            elif self.reverse_var.get():
                filter_complex = '[0:v]reverse[outv]'
            else:
                messagebox.showerror('Error', 'No filters selected')
                return
            cf = self.custom_filter.get().strip()
            if cf:
                filter_complex += f';[outv]{cf}[outv]'
            cmd += ['-filter_complex', filter_complex, '-map', '[outv]', '-c:v', 'libx264', outfile]

        elif tab == 'Speed':
            factor = float(self.speed_var.get())
            cmd += ['-i', infile]
            vf = f"setpts={1/factor}*PTS"
            cmd += ['-vf', vf]
            if self.audio_speed_var.get():
                rem = factor
                at_filters = []
                while rem < 0.5:
                    at_filters.append('atempo=0.5')
                    rem /= 0.5
                while rem > 2.0:
                    at_filters.append('atempo=2.0')
                    rem /= 2.0
                at_filters.append(f'atempo={rem}')
                af = ','.join(at_filters)
                cmd += ['-af', af]
            else:
                cmd += ['-c:a', 'copy']
            cmd += [outfile]

        elif tab == 'Format':
            cmd += ['-i', infile]
            container = self.container_var.get()
            vcodec = self.vcodec_var.get()
            preset = self.preset_var.get()
            crf = self.crf_var.get()
            vbitrate = self.vbitrate_var.get().strip()
            acodec = self.acodec_var.get()
            abitrate = self.abitrate_var.get().strip()
            if vcodec == 'copy':
                cmd += ['-c:v', 'copy']
            else:
                cmd += ['-c:v', vcodec, '-preset', preset, '-crf', crf]
            if vbitrate:
                cmd += ['-b:v', vbitrate]
            if acodec == 'copy':
                cmd += ['-c:a', 'copy']
            else:
                cmd += ['-c:a', acodec, '-b:a', abitrate]
            cmd += ['-f', container, outfile]

        elif tab == 'Metadata':
            # collect metadata tags
            metadata_args = []
            for key in ['title','artist','album','genre','date','track','comment']:
                val = getattr(self, f'meta_{key}').get().strip()
                if val:
                    metadata_args += ['-metadata', f"{key}={val}"]
            cover = self.cover_entry.get().strip()
            if cover:
                cmd += ['-i', infile, '-i', cover] + metadata_args + ['-map', '0', '-map', '1', '-c', 'copy', '-disposition:v:1', 'attached_pic',(outfile)]
            else:
                cmd += ['-i', infile] + metadata_args + ['-c', 'copy', outfile]

        elif tab == 'Stitch':
            import tempfile
            second = self.file_entry_1.get().strip()
            if not second:
                messagebox.showerror('Error', 'Specify second file for stitching')
                return

            # Create a temporary “list.txt” for FFmpeg’s concat demuxer
            list_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
            list_file.write(f"file '{infile}'\nfile '{second}'\n")
            list_file.flush()
            list_file.close()

            # Build the concat-demuxer command
            cmd = [
                self.ffmpeg_executable,
                '-y',
                '-f', 'concat',
                '-safe', '0',
                '-i', list_file.name,
                '-c', 'copy',
                outfile
            ]

        else:
            messagebox.showinfo('Info', f'Run logic for "{tab}" not implemented yet')
            return

        threading.Thread(target=self.run_process, args=(cmd,)).start()

    def run_process(self, cmd):
        self.log.config(state='normal')
        self.log.delete('1.0', tk.END)
        self.log.insert(tk.END, 'Running: ' + ' '.join(cmd) + '\n')
        self.log.config(state='disabled')
        try:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        except FileNotFoundError:
            messagebox.showerror('Error', f'FFmpeg not found at {self.ffmpeg_executable}')
            return
        for line in proc.stdout:
            self.log.config(state='normal')
            self.log.insert(tk.END, line)
            self.log.see(tk.END)
            self.log.config(state='disabled')
        proc.wait()
        messagebox.showinfo('Done', 'Success' if proc.returncode == 0 else 'Error')

if __name__ == '__main__':
    if DND_AVAILABLE:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()
    app = FFmpegApp(master=root)
    root.mainloop()
