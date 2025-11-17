import tkinter as tk
from tkinter import ttk, messagebox
import winsound
import datetime

class EyeReminderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("EyeCare♒")
        self.work_time = 40 * 60  # 40 minutes in seconds
        self.rest_time = 10 * 60  # 10 minutes in seconds
        self.timer_id = None
        self.is_working = False
        self.is_running = False
        self.is_paused = False
        self.remaining_time = 0
        self.work_cycle = 0
        self.last_date = datetime.date.today()
        
        # Soothing green color scheme (eye-friendly)
        self.colors = {
            "dark_green": "#1e6f5c",
            "light_green": "#d8f3dc",  # Very light green for main background
            "panel_green": "#e8f5e9",  # Lighter green for time display panel
            "medium_green": "#52b788",  # For progress bars
            "dark_blue": "#1d4e89",
            "light_blue": "#00b4d8",
            "text_dark": "#212529",
            "text_light": "#f8f9fa"
        }
        
        # Configure root window with light green background
        self.root.configure(bg=self.colors["light_green"])
        self.root.geometry("360x360")
        self.root.resizable(False, False)
        
        # Create custom styles
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Progress bar styles
        self.style.configure("green.Horizontal.TProgressbar",
                           troughcolor=self.colors["panel_green"],
                           background=self.colors["medium_green"],
                           thickness=10)
        self.style.configure("blue.Horizontal.TProgressbar",
                           troughcolor=self.colors["panel_green"],
                           background=self.colors["light_blue"],
                           thickness=10)
        
        # Button styles
        self.style.configure("Green.TButton",
                           foreground=self.colors["text_light"],
                           background=self.colors["dark_green"],
                           font=("Arial", 11, "bold"),
                           padding=8,
                           width=10)
        self.style.configure("Blue.TButton",
                           foreground=self.colors["text_light"],
                           background=self.colors["dark_blue"],
                           font=("Arial", 11, "bold"),
                           padding=8,
                           width=10)
        
        # Main container frame with light green background
        main_frame = tk.Frame(root, bg=self.colors["light_green"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Card frame for timer display (lighter green)
        card_frame = tk.Frame(main_frame, bg=self.colors["panel_green"],
                            bd=0, highlightthickness=0,
                            relief=tk.RAISED)
        card_frame.pack(fill=tk.X, pady=(0, 20), ipady=10, ipadx=10)
        
        # Timer label
        self.label = tk.Label(card_frame,
                            font=("Arial", 38, "bold"),
                            fg=self.colors["dark_green"],
                            bg=self.colors["panel_green"])
        self.label.pack(pady=(10, 5))
        
        # Status label
        self.status_label = tk.Label(card_frame,
                                   font=("Arial", 12),
                                   fg=self.colors["text_dark"],
                                   bg=self.colors["panel_green"])
        self.status_label.pack(pady=(0, 15))
        
        # Progress bar
        self.progress = ttk.Progressbar(card_frame,
                                      orient="horizontal",
                                      length=300,
                                      mode="determinate",
                                      style="green.Horizontal.TProgressbar")
        self.progress.pack(pady=(0, 15))
        
        # Button container - using grid for equal sizing
        btn_frame = tk.Frame(main_frame, bg=self.colors["light_green"])
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Configure grid for equal button sizes
        btn_frame.columnconfigure(0, weight=1, uniform="btn")
        btn_frame.columnconfigure(1, weight=1, uniform="btn")
        btn_frame.columnconfigure(2, weight=1, uniform="btn")
        
        # Start button (also works as resume)
        self.start_btn = ttk.Button(btn_frame, text="▶ Start", 
                                  command=self.start_timer,
                                  style="Green.TButton")
        self.start_btn.grid(row=0, column=0, padx=5, sticky="ew")
        
        # Pause button (only pauses, doesn't resume)
        self.pause_btn = ttk.Button(btn_frame, text="⏸ Pause", 
                                   command=self.pause_timer,
                                   style="Blue.TButton")
        self.pause_btn.grid(row=0, column=1, padx=5, sticky="ew")
        
        # Reset button
        self.reset_btn = ttk.Button(btn_frame, text="↻ Reset", 
                                   command=self.reset_timer,
                                   style="Blue.TButton")
        self.reset_btn.grid(row=0, column=2, padx=5, sticky="ew")
        
        # Stats card (lighter green)
        stats_card = tk.Frame(main_frame, bg=self.colors["panel_green"],
                            bd=0, highlightthickness=0,
                            relief=tk.RAISED)
        stats_card.pack(fill=tk.X, pady=(10, 0), ipady=5, ipadx=10)
        
        # Stats label
        self.stats_label = tk.Label(stats_card,
                                  font=("Arial", 14),
                                  fg=self.colors["dark_blue"],
                                  bg=self.colors["panel_green"])
        self.stats_label.pack(pady=5)
        
        # Initialize
        self.reset_timer()

    def reset_progress(self):
        """Reset progress bar to full length."""
        if self.is_working:
            self.progress["maximum"] = self.work_time
            self.progress["value"] = self.work_time
            self.progress.configure(style="green.Horizontal.TProgressbar")
        else:
            self.progress["maximum"] = self.rest_time
            self.progress["value"] = self.rest_time
            self.progress.configure(style="blue.Horizontal.TProgressbar")

    def update_progress(self, remaining):
        """Update progress bar during countdown."""
        self.progress["value"] = remaining

    def update_display(self, seconds):
        """Update timer label and progress bar."""
        mins, secs = divmod(seconds, 60)
        self.label.config(text=f"{mins:02d}:{secs:02d}")
        self.update_progress(seconds)

    def update_stats(self):
        """Update work cycle count."""
        current_date = datetime.date.today()
        if current_date != self.last_date:
            self.work_cycle = 0
            self.last_date = current_date
        stats_text = f"Completed: {self.work_cycle} work cycles today"
        self.stats_label.config(text=stats_text)

    def start_timer(self):
        """Start or resume the timer."""
        if not self.is_running:
            if self.is_paused:
                # Resume from paused state
                self.is_paused = False
                self.is_running = True
                self.status_label.config(text="Resumed" + (" (Working)" if self.is_working else " (Break)"))
                self.update_timer(self.remaining_time)
            else:
                # Start fresh
                self.is_running = True
                self.is_working = True
                self.start_work_period()

    def pause_timer(self):
        """Pause the current timer."""
        if self.is_running:
            self.is_paused = True
            self.is_running = False
            self.stop_timer()
            self.status_label.config(text="Paused")

    def reset_timer(self):
        """Reset timer to initial state."""
        self.stop_timer()
        self.is_working = False
        self.is_running = False
        self.is_paused = False
        self.remaining_time = self.work_time
        self.update_display(self.work_time)
        self.root.title("EyeCare")
        self.label.config(fg=self.colors["dark_green"])
        self.status_label.config(text="Ready to start")
        self.reset_progress()

    def stop_timer(self):
        """Stop the current timer."""
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None

    def update_timer(self, remaining):
        """Handle countdown logic."""
        self.remaining_time = remaining
        self.update_display(remaining)
        
        if remaining > 0:
            self.timer_id = self.root.after(1000, self.update_timer, remaining - 1)
        else:
            self.switch_mode()

    def switch_mode(self):
        """Switch between work/rest modes."""
        winsound.PlaySound("sound.wav", winsound.SND_ASYNC)
        
        if self.is_working:
            self.work_cycle += 1
            self.update_stats()
            messagebox.showinfo("Break Time", "Time to rest your eyes! Look away for 10 minutes.")
            self.start_rest_period()
        else:
            messagebox.showinfo("Work Time", "Time to focus! Start working.")
            self.start_work_period()

    def start_work_period(self):
        """Begin work countdown."""
        self.stop_timer()
        self.is_working = True
        self.is_running = True
        self.is_paused = False
        self.label.config(fg=self.colors["dark_green"])
        self.root.title("Working - EyeCare")
        self.status_label.config(text="Working - Focus time!")
        self.progress.configure(style="green.Horizontal.TProgressbar")
        self.progress["maximum"] = self.work_time
        self.progress["value"] = self.work_time
        self.update_timer(self.work_time)

    def start_rest_period(self):
        """Begin rest countdown."""
        self.stop_timer()
        self.is_working = False
        self.is_running = True
        self.is_paused = False
        self.label.config(fg=self.colors["dark_blue"])
        self.root.title("On Break - EyeCare")
        self.status_label.config(text="On Break - Relax your eyes!")
        self.progress.configure(style="blue.Horizontal.TProgressbar")
        self.progress["maximum"] = self.rest_time
        self.progress["value"] = self.rest_time
        self.update_timer(self.rest_time)

    def save_stats(self):
        """Save work cycles to a file."""
        with open("work_stats.txt", "a") as f:
            f.write(f"{datetime.date.today()}: {self.work_cycle}\n")


if __name__ == "__main__":
    root = tk.Tk()
    app = EyeReminderApp(root)
    
    def on_closing():
        app.save_stats()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
