import tkinter as tk
from tkinter import ttk, filedialog
import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import time
from .streams import simulation_stream, com_stream
from .storage import history, latest, handle_record
from .alarms import active_alarms, alarm_rules


class Print2PanelApp(tk.Tk):
    def __init__(self, mode: str, config: dict):
        super().__init__()
        self.title("SCADALite")
        self.geometry("1600x900")  # change here default window size

        self.config_data = config
        self.graph_tags = set(config.get("graph_tags", []))
        self.mode = mode
        self.stop_event = threading.Event()
        self.paused = False

        self._build_layout()
        self._start_backend()
        self._schedule_updates()

    # ---------- Layout ----------

    def _build_layout(self):
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=1)

        # Plot frame
        plot_frame = ttk.Frame(self)
        plot_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Plot
        self.fig, self.ax = plt.subplots(figsize=(7, 5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Controls under plot
        control_frame = ttk.Frame(plot_frame)
        control_frame.pack(fill=tk.X, pady=5)

        # Pause/Resume
        self.btn_pause = ttk.Button(control_frame, text="Pause", command=self.toggle_pause)
        self.btn_pause.pack(side=tk.LEFT, padx=5)

        # Load Log
        self.btn_load = ttk.Button(control_frame, text="Load Log", command=self.load_log)
        self.btn_load.pack(side=tk.LEFT, padx=5)

        # Right panel
        right_frame = ttk.Frame(self)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        right_frame.rowconfigure(1, weight=1)
        right_frame.columnconfigure(0, weight=1)

        # Tag table
        title = ttk.Label(right_frame, text="Tags", font=("Segoe UI", 12, "bold"))
        title.grid(row=0, column=0, sticky="w")

        columns = ("tag", "type", "pv", "sp", "unit", "ts")
        self.tree = ttk.Treeview(right_frame, columns=columns, show="headings", height=20)
        for col in columns:
            self.tree.heading(col, text=col.upper())
            self.tree.column(col, width=100, anchor="center")
        self.tree.grid(row=1, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=1, column=1, sticky="ns")

        # Alarms panel
        alarm_frame = ttk.LabelFrame(right_frame, text="Alarms")
        alarm_frame.grid(row=2, column=0, sticky="nsew", pady=10)

        self.alarm_list = tk.Listbox(alarm_frame, height=6, fg="red", font=("Segoe UI", 11, "bold"))
        self.alarm_list.pack(fill=tk.BOTH, expand=True)

        config_alarm_frame = ttk.LabelFrame(right_frame, text="Configured Alarms")
        config_alarm_frame.grid(row=3, column=0, sticky="nsew", pady=10)

        self.config_alarm_list = tk.Listbox(config_alarm_frame, height=6, font=("Segoe UI", 10))
        self.config_alarm_list.pack(fill=tk.BOTH, expand=True)

        # Status bar
        self.status_var = tk.StringVar(value=f"Mode: {self.mode}")
        status_bar = ttk.Label(self, textvariable=self.status_var, anchor="w")
        status_bar.grid(row=1, column=0, columnspan=2, sticky="ew")

    # ---------- Controls ----------

    def toggle_pause(self):
        self.paused = not self.paused
        self.btn_pause.config(text="Resume" if self.paused else "Pause")

    def load_log(self):
        path = filedialog.askopenfilename(
            title="Select log file",
            filetypes=[("CSV Files", "*.csv")]
        )
        if not path:
            return

        history.clear()

        import csv
        with open(path, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                tag = row["tag"]
                pv = float(row["pv"])
                ts = time.time()
                history[tag].append((ts, pv))

        self.graph_tags = set(history.keys())

    # ---------- Backend ----------

    def _start_backend(self):
        if self.mode == "SIMULATION":
            t = threading.Thread(target=simulation_stream, args=(self.stop_event, handle_record), daemon=True)
            t.start()

        elif self.mode == "COM":
            port = self.config_data.get("com_port", "COM5")
            baud = self.config_data.get("baud", 115200)
            t = threading.Thread(target=com_stream, args=(self.stop_event, handle_record, port, baud), daemon=True)
            t.start()

        if "constants" in self.config_data:
            consts = self.config_data["constants"]
            from .parser import TagRecord

            def constant_stream():
                while not self.stop_event.is_set():
                    ts = datetime.datetime.utcnow().isoformat()
                    for tag, pv in consts.items():
                        rec = TagRecord(
                            tag=tag,
                            type="CONST",
                            pv=float(pv),
                            sp=None,
                            unit="",
                            ts=ts
                        )
                        handle_record(rec)
                    time.sleep(1)

            threading.Thread(target=constant_stream, daemon=True).start()


    # ---------- Periodic GUI updates ----------

    def _schedule_updates(self):
        self._update_plot()
        self._update_table()
        self._update_alarms()
        self.after(500, self._schedule_updates)
        self._update_configured_alarms()
        self.graph_tags.update(self.config_data.get("constants", {}).keys()) # auto add constants to graph

    def _update_alarms(self):
        self.alarm_list.delete(0, tk.END)
        for msg in active_alarms.values():
            self.alarm_list.insert(tk.END, msg)

    def _update_configured_alarms(self):
        self.config_alarm_list.delete(0, tk.END)
        for tag, rules in alarm_rules.items():
            hi = rules.get("hi")
            lo = rules.get("lo")
            msg = f"{tag}: HI={hi}, LO={lo}"
            self.config_alarm_list.insert(tk.END, msg)

    def _update_plot(self):
        if self.paused:
            return

        self.ax.clear()

        for tag, points in history.items():
            if self.graph_tags and tag not in self.graph_tags:
                continue
            if not points:
                continue

            xs, ys = zip(*points)
            xs = [x - xs[0] for x in xs]
            self.ax.plot(xs, ys, label=tag)

        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("PV")
        if self.ax.lines:
            self.ax.legend(loc="upper right")
        self.ax.grid(True)
        self.fig.tight_layout()
        self.canvas.draw_idle()

    def _update_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for tag, rec in sorted(latest.items()):
            self.tree.insert("", "end", values=(
                rec.tag,
                rec.type,
                f"{rec.pv:.2f}",
                "" if rec.sp is None else f"{rec.sp:.2f}",
                rec.unit,
                rec.ts.split("T")[-1],
            ))

    # ---------- Cleanup ----------

    def on_close(self):
        self.stop_event.set()
        self.destroy()
