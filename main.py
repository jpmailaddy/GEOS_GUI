from tkinter import ttk
import tkinter as tk
from tkinter.filedialog import askopenfilename

import matplotlib
from matplotlib.figure import Figure 
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)

import numpy as np
import netCDF4 as nc

DEBUG = True
class App:
    def __init__(self, root):
        self.root = root
        self.root.geometry("600x600")
        self.root.title("Panopoly who?")

        self.file_path = ""
        self.axis1 = tk.StringVar()
        self.axis2 = tk.StringVar()

        self.set_menu()
        self.create_widgets()
    
    def set_menu(self):
        self.menubar = tk.Menu(self.root)
        self.filemenu = tk.Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="New", command=None)
        self.filemenu.add_command(label="Open", command=self.select_file)
        self.filemenu.add_command(label="Save", command=None)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Quit", command=self.root.quit)
        self.menubar.add_cascade(label="File", menu=self.filemenu)
        self.root.config(menu=self.menubar)

    def create_widgets(self):
        self.frm = ttk.Frame(self.root)
        self.frm.grid()
        ttk.Label(self.frm, text="Panopoly The Sequel", padding=10).grid(column=0, row=0)

        self.axisdrop1 = ttk.OptionMenu( self.frm, self.axis1 ) 
        self.axisdrop1.grid(row=1, column=1)

        self.axisdrop2 = ttk.OptionMenu( self.frm, self.axis2 ) 
        self.axisdrop2.grid(row=1, column=2)

        ttk.Button(self.frm, text="New Plot discovered click HERE (not a scam)", command=self.plot).grid(column=0, row=1)
    def select_file(self):
        self.file_path = askopenfilename()
        if self.file_path:
            self.load_data()


    def load_data(self):
        try:
            self.data = nc.Dataset(self.file_path)
            self.update_properties_dropdown()
        except Exception as e:
            tk.messagebox.showerror("Error", f"Failed to load NetCDF file: {e}")
            self.file_path = ""
            self.data = None

    def update_properties_dropdown(self):
        if self.data:
            variables = self.data.variables.keys()
            self.axisdrop1['menu'].delete(0, 'end')
            for prop in variables:
                self.axisdrop1['menu'].add_command(label=prop, command=tk._setit(self.axis1, prop))
                self.axisdrop2['menu'].add_command(label=prop, command=tk._setit(self.axis2, prop))
            self.axis1.set(list(variables)[0]) # Set default property
            self.axis2.set(list(variables)[0]) # Set default property
    
    def plot(self):
        if not self.data or not self.axis1.get() or not self.axis2.get():
            ttk.messagebox.showerror("Error", "No NetCDF file loaded.")
            return
        fig = Figure(figsize = (5, 5), 
                 dpi = 100) 
        subplot = fig.add_subplot(111) 
        axis1name = self.axis1.get()
        propdata1 = self.data.variables[axis1name][:]
        subplot.set_xlabel(axis1name)
        if not DEBUG:
            axis2name = self.axis2.get()
            propdata2 = self.data.variables[axis2name][:]
            subplot.set_ylabel(axis2name)
        subplot.plot(*([propdata1] if DEBUG else [propdata1, propdata2]))
        subplot.set_title(f"{axis1name} vs. {axis2name if not DEBUG else "Index..."}")
        canvas = FigureCanvasTkAgg(fig, master=self.frm)   
        canvas.draw() 
        canvas.get_tk_widget().grid(row=2,column=0)

def main():
    matplotlib.use('agg')  
    root = tk.Tk()
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()