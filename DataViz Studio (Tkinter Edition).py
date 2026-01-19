import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class DataVizDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Visualization Dashboard")
        self.root.geometry("1000x600")

        # ----------- STATE -----------
        self.df = None            # current DataFrame
        self.canvas = None        # matplotlib canvas

        # ----------- LAYOUT -----------
        self.create_widgets()
        self.load_sample_data()   # start with sample data

    def create_widgets(self):
        # Main layout → Left (controls) | Right (chart)
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill="both", expand=True)

        # LEFT FRAME - Controls
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(side="left", fill="y")

        # RIGHT FRAME - Chart
        chart_frame = ttk.Frame(main_frame)
        chart_frame.pack(side="right", fill="both", expand=True)

        # Save chart_frame for later
        self.chart_frame = chart_frame

        # ---------- Controls ----------

        # Title
        ttk.Label(
            control_frame, text="Data Controls",
            font=("Segoe UI", 14, "bold")
        ).pack(pady=(0, 10))

        # Load CSV Button
        ttk.Button(
            control_frame,
            text="Load CSV File",
            command=self.load_csv
        ).pack(fill="x", pady=5)

        # Info label
        self.info_label = ttk.Label(
            control_frame,
            text="Using sample sales data",
            foreground="grey"
        )
        self.info_label.pack(pady=(0, 15))

        # X-axis column selector
        ttk.Label(control_frame, text="X-axis Column:").pack(anchor="w")
        self.x_column_cb = ttk.Combobox(control_frame, state="readonly")
        self.x_column_cb.pack(fill="x", pady=5)

        # Y-axis column selector
        ttk.Label(control_frame, text="Y-axis Column:").pack(anchor="w")
        self.y_column_cb = ttk.Combobox(control_frame, state="readonly")
        self.y_column_cb.pack(fill="x", pady=5)

        # Chart type
        ttk.Label(control_frame, text="Chart Type:").pack(anchor="w", pady=(10, 0))
        self.chart_type_cb = ttk.Combobox(
            control_frame,
            state="readonly",
            values=["Bar", "Line", "Pie"]
        )
        self.chart_type_cb.current(0)
        self.chart_type_cb.pack(fill="x", pady=5)

        # Plot button
        ttk.Button(
            control_frame,
            text="Plot Chart",
            command=self.plot_chart
        ).pack(fill="x", pady=(15, 5))

        # Quit button
        ttk.Button(
            control_frame,
            text="Exit",
            command=self.root.quit
        ).pack(fill="x", pady=(30, 5))

    # ---------- DATA HANDLING ----------

    def load_sample_data(self):
        """Load built-in sample sales data into DataFrame."""
        data = {
            "Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
            "Sales": [12000, 18000, 15000, 22000, 17000, 25000],
            "Profit": [3000, 5000, 4000, 7000, 4500, 8000]
        }
        self.df = pd.DataFrame(data)
        self.info_label.config(text="Using sample sales data")
        self.update_column_dropdowns()
        self.plot_chart(initial=True)

    def load_csv(self):
        """Open file dialog and load a CSV file."""
        file_path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if not file_path:
            return

        try:
            self.df = pd.read_csv(file_path)
        except Exception as e:
            messagebox.showerror("Error", f"Could not load file:\n{e}")
            return

        if self.df.empty:
            messagebox.showwarning("Warning", "The selected CSV file is empty.")
            return

        self.info_label.config(text=f"Loaded: {file_path.split('/')[-1]}")
        self.update_column_dropdowns()

    def update_column_dropdowns(self):
        """Update x/y column comboboxes based on DataFrame columns."""
        if self.df is None:
            return

        cols = list(self.df.columns)

        self.x_column_cb["values"] = cols
        self.y_column_cb["values"] = cols

        if cols:
            self.x_column_cb.current(0)
        if len(cols) > 1:
            self.y_column_cb.current(1)
        elif cols:
            self.y_column_cb.current(0)

    # ---------- PLOTTING ----------

    def clear_chart(self):
        """Remove existing matplotlib canvas if any."""
        if self.canvas is not None:
            self.canvas.get_tk_widget().destroy()
            self.canvas = None

    def plot_chart(self, initial=False):
        """Plot chart based on current selections."""
        if self.df is None or self.df.empty:
            messagebox.showwarning("No Data", "No data available to plot.")
            return

        chart_type = self.chart_type_cb.get() or "Bar"

        # For initial plot, use defaults
        if initial:
            x_col = self.df.columns[0]
            # pick first numeric column as y if possible
            numeric_cols = self.df.select_dtypes(include="number").columns
            y_col = numeric_cols[0] if len(numeric_cols) > 0 else self.df.columns[-1]
        else:
            x_col = self.x_column_cb.get()
            y_col = self.y_column_cb.get()

        if not x_col or not y_col:
            messagebox.showwarning("Select Columns", "Please select both X and Y columns.")
            return

        if x_col not in self.df.columns or y_col not in self.df.columns:
            messagebox.showerror("Error", "Selected columns not found in data.")
            return

        # For Pie chart, we use y_col as values and x_col as labels
        if chart_type == "Pie":
            try:
                values = self.df[y_col]
                labels = self.df[x_col]
            except Exception as e:
                messagebox.showerror("Error", f"Cannot plot pie chart:\n{e}")
                return
        else:
            x = self.df[x_col]
            y = self.df[y_col]

        # Clear previous chart
        self.clear_chart()

        # Create new Figure
        fig, ax = plt.subplots(figsize=(6, 4))

        # Draw chart
        try:
            if chart_type == "Bar":
                ax.bar(x, y)
                ax.set_xlabel(x_col)
                ax.set_ylabel(y_col)
                ax.set_title(f"{y_col} vs {x_col} (Bar Chart)")
            elif chart_type == "Line":
                ax.plot(x, y, marker="o")
                ax.set_xlabel(x_col)
                ax.set_ylabel(y_col)
                ax.set_title(f"{y_col} vs {x_col} (Line Chart)")
            elif chart_type == "Pie":
                ax.pie(values, labels=labels, autopct="%1.1f%%")
                ax.set_title(f"{y_col} distribution by {x_col}")
            else:
                messagebox.showerror("Error", "Unknown chart type.")
                return

            fig.tight_layout()

            # Embed in Tkinter
            self.canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(fill="both", expand=True)

        except Exception as e:
            messagebox.showerror("Plot Error", f"Could not create chart:\n{e}")
            self.clear_chart()


if __name__ == "__main__":
    root = tk.Tk()
    app = DataVizDashboard(root)
    root.mainloop()

