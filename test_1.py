import tkinter as tk
import time

# === Themes ===
LIGHT_THEME = {
    "bg": "#ffffff",
    "btn_bg": "#e0e0e0",
    "btn_fg": "#000000",
    "entry_bg": "#ffffff",
    "entry_fg": "#000000",
    "accent": "#f0f0f0",
    "text": "#000000",
    "countdown": "#555555",
    "icon": "🌙"
}

DARK_THEME = {
    "bg": "#1e1e1e",
    "btn_bg": "#2d2d2d",
    "btn_fg": "#f5f5f5",
    "entry_bg": "#3e3e3e",
    "entry_fg": "#f5f5f5",
    "accent": "#3e3e3e",
    "text": "#f5f5f5",
    "countdown": "#888888",
    "icon": "☀️"
}

current_theme = DARK_THEME
countdown_time = 20 * 60  # 20 mins
theme_transition_steps = 20
history_window = None  # Global to track the history tab

# === Utility ===
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb):
    return '#%02x%02x%02x' % rgb

def blend_colors(c1, c2, t):
    r1, g1, b1 = hex_to_rgb(c1)
    r2, g2, b2 = hex_to_rgb(c2)
    return rgb_to_hex((
        int(r1 + (r2 - r1) * t),
        int(g1 + (g2 - g1) * t),
        int(b1 + (b2 - b1) * t)
    ))

def smooth_switch(start_theme, end_theme, step=0):
    t = step / theme_transition_steps
    blended = {
        key: blend_colors(start_theme[key], end_theme[key], t)
        for key in ["bg", "btn_bg", "btn_fg", "entry_bg", "entry_fg", "accent", "text", "countdown"]
    }

    apply_theme(blended)
    if step < theme_transition_steps:
        window.after(20, lambda: smooth_switch(start_theme, end_theme, step + 1))
    else:
        apply_theme(end_theme)
        global current_theme
        current_theme = end_theme
        theme_btn.config(text=end_theme["icon"])

# === Theme Logic ===
def apply_theme(theme):
    window.configure(bg=theme["bg"])
    entry.configure(bg=theme["entry_bg"], fg=theme["entry_fg"], insertbackground=theme["entry_fg"])
    countdown_label.configure(bg=theme["bg"], fg=theme["countdown"])
    theme_btn.configure(bg=theme["btn_bg"], fg=theme["btn_fg"], activebackground=theme["accent"])
    
    for btn in buttons:
        btn.configure(bg=theme["btn_bg"], fg=theme["btn_fg"], activebackground=theme["accent"])
    clear_btn.configure(bg=theme["btn_bg"], fg=theme["btn_fg"], activebackground=theme["accent"])
    history_btn.configure(bg=theme["btn_bg"], fg=theme["btn_fg"], activebackground=theme["accent"])
    clear_hist_btn.configure(bg=theme["btn_bg"], fg=theme["btn_fg"], activebackground=theme["accent"])

def switch_theme():
    new_theme = LIGHT_THEME if current_theme == DARK_THEME else DARK_THEME
    smooth_switch(current_theme, new_theme)

# === Calculator Logic ===
def on_click(value):
    if value == "=":
        try:
            result = str(eval(entry.get()))
            log = entry.get() + " = " + result + "\n"
            with open("history.txt", "a") as file:
                file.write(log)
            entry.delete(0, tk.END)
            entry.insert(tk.END, result)
        except:
            entry.delete(0, tk.END)
            entry.insert(tk.END, "Error")
    else:
        entry.insert(tk.END, value)

def clear_entry():
    entry.delete(0, tk.END)

def show_history():
    global history_window

    # If already open, destroy it first
    if history_window and tk.Toplevel.winfo_exists(history_window):
        history_window.destroy()

    try:
        with open("history.txt", "r") as file:
            history = file.read()
    except FileNotFoundError:
        history = "No history yet."

    history_window = tk.Toplevel(window)
    history_window.title("Calculation History")
    history_window.geometry("300x400")
    history_window.configure(bg=current_theme["bg"])

    text_box = tk.Text(history_window, wrap="word", font=("Courier", 12),
                       bg=current_theme["accent"], fg=current_theme["text"])
    text_box.insert(tk.END, history)
    text_box.config(state="disabled")
    text_box.pack(expand=True, fill="both", padx=10, pady=10)


def clear_history():
    with open("history.txt", "w") as file:
        file.write("")

def auto_clear_history():
    global countdown_time
    with open("history.txt", "w") as file:
        file.write("")
    countdown_time = 20 * 60
    update_countdown()

def update_countdown():
    global countdown_time
    mins, secs = divmod(countdown_time, 60)
    countdown_label.config(text=f"Auto-clear in: {mins:02}:{secs:02}")
    
    if countdown_time > 0:
        countdown_time -= 1
        window.after(1000, update_countdown)
    else:
        auto_clear_history()

# === GUI Setup ===
window = tk.Tk()
window.title("Smart Calculator")
window.geometry("320x540")

entry = tk.Entry(window, font=("Arial", 20), justify="right", bd=0)
entry.grid(row=0, column=0, columnspan=4, pady=10, padx=10, sticky="nsew")

buttons = []
btn_values = [
    ["7", "8", "9", "/"],
    ["4", "5", "6", "*"],
    ["1", "2", "3", "-"],
    ["0", ".", "=", "+"]
]

for r, row in enumerate(btn_values):
    for c, char in enumerate(row):
        btn = tk.Button(window, text=char, font=("Arial", 18),
                        command=lambda val=char: on_click(val))
        btn.grid(row=r+1, column=c, sticky="nsew", padx=2, pady=2)
        buttons.append(btn)

clear_btn = tk.Button(window, text="C", font=("Arial", 14), command=clear_entry)
clear_btn.grid(row=5, column=0, sticky="nsew", padx=2, pady=2)

history_btn = tk.Button(window, text="History", font=("Arial", 14), command=show_history)
history_btn.grid(row=5, column=1, columnspan=2, sticky="nsew", padx=2, pady=2)

clear_hist_btn = tk.Button(window, text="Clear History", font=("Arial", 14), command=clear_history)
clear_hist_btn.grid(row=5, column=3, sticky="nsew", padx=2, pady=2)

countdown_label = tk.Label(window, text="", font=("Arial", 12))
countdown_label.grid(row=6, column=0, columnspan=4, sticky="nsew", pady=(5, 10))

theme_btn = tk.Button(window, text=current_theme["icon"], font=("Arial", 14), command=switch_theme)
theme_btn.grid(row=7, column=0, columnspan=4, sticky="nsew", padx=5, pady=5)

for i in range(4):
    window.columnconfigure(i, weight=1)
for i in range(8):
    window.rowconfigure(i, weight=1)

# === Start App ===
apply_theme(current_theme)
update_countdown()
window.mainloop()
