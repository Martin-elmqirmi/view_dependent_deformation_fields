import tkinter as tk


""" Numeric Input Widget with Slider Only """
class NumericInput(tk.Frame):
    def __init__(self, parent, callback_value, update_callback, label, min_val=0, max_val=100, step=1, initial=50,
                 *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.update_callback = update_callback
        self.min_val = min_val
        self.max_val = max_val
        self.step = step
        self.callback_value = callback_value

        self.value = tk.DoubleVar(value=initial)
        self.configure(bg="#333", padx=3, pady=1)

        # Label
        self.label = tk.Label(self, text=label, bg="#333", fg="white", font=("Arial", 9))
        self.label.pack(side="top", anchor="w", padx=2)

        # Control Frame: buttons + slider
        control_frame = tk.Frame(self, bg="#333")
        control_frame.pack(fill="x", padx=2, pady=1)

        # Decrement Button
        self.btn_down = tk.Button(control_frame, text="➖", command=self.decrement,
                                  width=2, bg="#444", fg="white")
        self.btn_down.pack(side="left")

        # Slider
        self.slider = tk.Scale(control_frame,
                               from_=min_val,
                               to=max_val,
                               resolution=step,
                               orient="horizontal",
                               variable=self.value,
                               command=self.on_slider_change,
                               bg="#333",
                               fg="white",
                               highlightthickness=0,
                               troughcolor="#555",
                               sliderrelief="flat",
                               showvalue=False)
        self.slider.pack(side="left", fill="x", expand=True, padx=4)

        # Increment Button
        self.btn_up = tk.Button(control_frame, text="➕", command=self.increment,
                                width=2, bg="#444", fg="white")
        self.btn_up.pack(side="right")

    def increment(self):
        val = self.value.get() + self.step
        if val <= self.max_val:
            self.value.set(val)
            self.callback_value(val)
        self.update_callback()

    def decrement(self):
        val = self.value.get() - self.step
        if val >= self.min_val:
            self.value.set(val)
            self.callback_value(val)
        self.update_callback()

    def on_slider_change(self, val):
        try:
            self.callback_value(float(val))
            self.update_callback()
        except ValueError:
            pass
