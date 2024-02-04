import tkinter as tk
from tkinter import filedialog, messagebox
import traceback

class SettingsInput:
    def __init__(self, boxcount = 30, boxslotcount = 30):
        self.root = tk.Tk()
        self.boxcount = tk.IntVar()
        self.boxcount.set(boxcount)
        self.boxslotcount = tk.IntVar()
        self.boxslotcount.set(boxslotcount)
        self.ConstructUI()

    def ConstructUI(self):
        self.root.geometry("200x80")

        vcmdBoxSlotCount = (self.root.register(self.Validate_txbBoxSlotCount),  "%P")
        self.lblBoxSlotCount = tk.Label(self.root, text = "Box Slot Count:", width = 15)
        self.txbBoxSlotCount = tk.Entry(self.root, width = 10, textvariable=self.boxslotcount, validate="key", validatecommand=vcmdBoxSlotCount)

        vcmdBoxCount = (self.root.register(self.Validate_txbBoxCount),  "%P")
        self.lblBoxCount = tk.Label(self.root, text = "Box Count:", width = 15)
        self.txbBoxCount = tk.Entry(self.root, width = 10, textvariable=self.boxcount, validate="key", validatecommand=vcmdBoxCount)

        self.btnOk = tk.Button(self.root, text = "OK", command=self.btnOk_Click)
        self.btnCancel = tk.Button(self.root, text = "Cancel", command = self.root.destroy)
        self.lblBoxCount.grid(column=0, row = 0)
        self.txbBoxCount.grid(column=1, row = 0)

        self.lblBoxSlotCount.grid(column=0, row = 1)
        self.txbBoxSlotCount.grid(column=1, row = 1)

        self.btnOk.grid(column=0, row = 2)
        self.btnCancel.grid(column=1, row = 2)

    def OpenDialog(self):
        self.root.mainloop()

    def btnOk_Click(self):
        boxCount = 0
        boxSlotCount = 0
        try:
            boxCount = int(self.txbBoxCount.get())
            boxSlotCount = int(self.txbBoxSlotCount.get())
        except Exception as ex:
            print("User broke setting input somehow")
            print("Box Count box value: {value}".format(value=self.txbBoxCount.get()))
            print("Box Slot Count box value: {value}".format(value=self.txbBoxSlotCount.get()))
            print(ex)
            print(traceback.print_exception(type(ex), ex, ex.__traceback__))

        print("Box Count box value: {value}".format(value=boxCount))
        print("Box Slot Count box value: {value}".format(value=boxSlotCount))
        self.root.destroy()

    def Validate_txbBoxCount(self, P):
        if (str.isdigit(P)):
            return True
        elif (P == ""):
            return False
        else:
            print("User trying to put in non-number into Box Count: {value}".format(value=P))
            return False

    def Validate_txbBoxSlotCount(self, P):
        if (str.isdigit(P)):
            return True
        elif (P == ""):
            return False
        else:
            print("User trying to put in non-number into Box Slot Count: {value}".format(value=P))
            return False

    def GetBoxCount(self):
        return int(self.boxcount.get())

    def GetBoxSlotCount(self):
        return int(self.boxslotcount.get())

class LevelFileDialog:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        validFileTypes = (("Valid files", "*.sav *.sav.json"),(".sav", "*.sav"), (".sav.json", "*.sav.json"), ("All Files", "*.*"))
        self.path = filedialog.askopenfilename(filetypes=validFileTypes, title="Open Palworld Level.sav[.json] Save")
        self.root.destroy()

    def GetPath(self):
        return self.path

class SaveToolsCmd:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        validFileTypes = (("Valid files", "*.cmd"),(".cmd", "*.cmd"), ("All Files", "*.*"))
        self.path = filedialog.askopenfilename(filetypes=validFileTypes, title="Open Palworld-Save-Tools convert.cmd")
        self.root.destroy()

    def GetPath(self):
        return self.path

class MessageBox:
    def ShowDialog(title, message):
        root = tk.Tk()
        root.withdraw()
        root.iconify()

        result = messagebox.askyesno(title, message)

        root.destroy()
        return result
