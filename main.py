from tkinter import ttk
import tkinter as tk
from tkinter.filedialog import askopenfilename

import matplotlib
from matplotlib.figure import Figure 
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)

import numpy as np
import netCDF4 as nc

DEBUG = False

class App:
    def __init__(self, root):
        self.root = root
        self.root.geometry("800x800")
        self.root.title("Panopoly who?")

        self.frm = None
        self.frm2 = None
        self.curFrame = None

        self.filePath = ""
        self.data = None
        self.axis1 = tk.StringVar()
        self.axis2 = tk.StringVar()
        self.plotType = tk.StringVar()


        self.plotTypes = ["Line Plot", "Color Map"]

        self.create_plot_frame()
        # self.create_data_view_frame()
        self.set_main_menu()
        self.set_active(self.frm)

        if DEBUG:
            self.filePath = "/Users/grhuber/Downloads/2018_High_Vertical.geosgcm_gwd.20180201.nc4"
            self.load_data()
    
    def set_main_menu(self):
        self.menuBar = tk.Menu(self.root)
        self.fileMenu = tk.Menu(self.menuBar, tearoff=0)
        self.fileMenu.add_command(label="New", command=None)
        self.fileMenu.add_command(label="Open", command=self.select_file)
        self.fileMenu.add_command(label="Save", command=None)
        self.fileMenu.add_separator()
        self.fileMenu.add_command(label="Quit", command=self.root.quit)
        self.menuBar.add_cascade(label="File", menu=self.fileMenu)

        self.windowMenu = tk.Menu(self.menuBar, tearoff=0)
        self.windowMenu.add_command(label="Plot", command=lambda: self.set_active(self.frm))
        self.windowMenu.add_command(label="Data", command=lambda: self.set_active(self.frm2))
        self.menuBar.add_cascade(label="Window", menu=self.windowMenu)
        self.root.config(menu=self.menuBar)

    def create_plot_frame(self):
        self.frm = ttk.Frame(self.root)
        self.frm.grid(column=0, row=0,sticky ="nsew")
        ttk.Label(self.frm, text="Panopoly The Sequel", padding=10).grid(column=0, row=0)

        self.axis1Drop = ttk.OptionMenu(self.frm, self.axis1) 
        self.axis1Drop.grid(row=2, column=1)

        self.axis2Drop = ttk.OptionMenu(self.frm, self.axis2) 
        self.axis2Drop.grid(row=2, column=2)

        ttk.Button(self.frm, text="PLOT", command=self.plot).grid(column=0, row=2)
        self.plotTypeDrop = ttk.OptionMenu( self.frm, self.plotType, self.plotTypes[0], *self.plotTypes) 
        self.plotTypeDrop.grid(row=1, column=0)

    def create_data_view_frame(self):
        self.frm2 = ttk.Frame(self.root)
        self.frm2.grid(column=0, row=0,sticky ="nsew")
        ttk.Label(self.frm2, text="Data Properties", padding=10).grid(column=0, row=0)
        ttk.Label(self.frm2, text="Metadata").grid()
        if self.data:
            for property in self.data.ncattrs():
                ttk.Label(self.frm2, text=property).grid()
                ttk.Label(self.frm2, text=self.data.getncattr(property)).grid()
        ttk.Label(self.frm2, text="Variables").grid()
        if self.data:
            for variable in self.data.variables.keys():
                ttk.Label(self.frm2, text=variable).grid()
                try:
                    ttk.Label(self.frm2, text=self.data.variables[variable].long_name).grid()
                except:
                    pass

    def select_file(self):
        self.filePath = askopenfilename()
        if self.filePath:
            self.load_data()


    def load_data(self):
        try:
            self.data = nc.Dataset(self.filePath)
        except Exception as e:
            tk.messagebox.showerror("Error", f"Failed to load NetCDF file: {e}")
            return
        self.update_properties_dropdown()
        self.create_data_view_frame()
        self.set_active(self.curFrame)

    def update_properties_dropdown(self):
        if self.data:
            variables = self.data.variables.keys()
            self.axis1Drop['menu'].delete(0, 'end')
            for prop in variables:
                self.axis1Drop['menu'].add_command(label=prop, command=tk._setit(self.axis1, prop))
                self.axis2Drop['menu'].add_command(label=prop, command=tk._setit(self.axis2, prop))
            self.axis1.set(list(variables)[0]) # Set default property
            self.axis2.set(list(variables)[0]) # Set default property
    
    def plot(self):
        if not self.data:
            tk.messagebox.showerror("Error", "No NetCDF file loaded.")
            return
        fig = Figure(figsize = (8, 8), 
                 dpi = 100) 
        subplot = fig.add_subplot(111) 
        plotType = self.plotType.get()
        if plotType == "Line Plot":
            axis1Name = self.axis1.get()
            axis1Data = self.data.variables[axis1Name][:]
            subplot.set_xlabel(axis1Name)
            axis2Name = self.axis2.get()
            axis2Data = self.data.variables[axis2Name][:]
            subplot.set_ylabel(axis2Name)
            try:
                subplot.plot(axis1Data, axis2Data)
            except ValueError:
                tk.messagebox.showerror("Error", "Axis Dimensions do not match\naxis 1 with size: {}\naxis 2 with size:{}".format(axis1Data.shape, axis2Data.shape))
                return
            subplot.set_title("{} vs. {}".format(axis1Name, axis2Name))
        elif plotType == "Color Map":
            axis1Name = self.axis1.get()
            axis1Data = self.data.variables[axis1Name][:]
            mesh = subplot.pcolormesh(self.data.variables[axis1Name][0, 0, :, :])
            fig.colorbar(mesh, ax=subplot)
            subplot.set_title("{}".format(self.data.variables[axis1Name].long_name))

        canvas = FigureCanvasTkAgg(fig, master=self.frm)   
        canvas.draw()
        canvas.get_tk_widget().grid(row=3,column=0)
    
    def set_active(self, frm):
        frm.tkraise()
        self.curFrame = frm

def main():
    matplotlib.use('agg')  
    root = tk.Tk()
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()