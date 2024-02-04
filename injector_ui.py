import tkinter as tk
from tkinter import filedialog, messagebox
import traceback
import os

class InjectorForm:
    def __init__(self, boxcount = 16, boxslotcount = 30, levelpath = "", savetoolspath = ""):
        self.root = tk.Tk()
        self.settings = self.SettingsInput(self.root, boxcount, boxslotcount, levelpath, savetoolspath)
        self.root.mainloop()

    def GetBoxCount(self):
        return self.settings.GetBoxCount()

    def GetBoxSlotCount(self):
        return self.settings.GetBoxSlotCount()

    def GetLevelPath(self):
        return self.settings.GetLevelPath()

    def GetSaveToolsPath(self):
        return self.settings.GetSaveToolsPath()

    def Result(self):
            return self.settings.result

    class SettingsInput:
        def __init__(self, root, boxcount = 16, boxslotcount = 30, levelpath = "", savetoolspath = ""):
            self.root = root

            self.boxcount = tk.IntVar()
            self.boxcount.set(boxcount)

            self.boxslotcount = tk.IntVar()
            self.boxslotcount.set(boxslotcount)

            self.levelpath = tk.StringVar()
            self.levelpath.set(levelpath)

            self.savetoolspath = tk.StringVar()
            self.savetoolspath.set(savetoolspath)

            self.statusText = tk.StringVar()
            self.statusText.set("")

            # Just default to false, success only ever occurs with a good ok press
            self.result = False

            self.ConstructForm()

        def ConstructForm(self):
            self.root.geometry("450x150")

            vcmdBoxSlotCount = (self.root.register(self.Validate_txbBoxSlotCount),  "%P", "%V")
            self.lblBoxSlotCount = tk.Label(self.root, text = "Box Slot Count:", width = 15)
            self.txbBoxSlotCount = tk.Entry(self.root, width = 10, textvariable=self.boxslotcount, validate="all", validatecommand=vcmdBoxSlotCount)

            vcmdBoxCount = (self.root.register(self.Validate_txbBoxCount),  "%P", "%V")
            self.lblBoxCount = tk.Label(self.root, text = "Box Count:", width = 15)
            self.txbBoxCount = tk.Entry(self.root, width = 10, textvariable=self.boxcount, validate="all", validatecommand=vcmdBoxCount)

            vcmdLevelPath = (self.root.register(self.Validate_txbLevelPath),  "%P", "%V")
            self.lblLevelPath = tk.Label(self.root, text = "Level.sav path:", width = 15)
            self.txbLevelPath = tk.Entry(self.root, width = 50, textvariable=self.levelpath, validate="focus", validatecommand=vcmdLevelPath)
            self.btnLevelPath = tk.Button(self.root, text = "...", command=self.btnLevelPath_Click)

            vcmdSaveToolsPath = (self.root.register(self.Validate_txbSaveToolsPath),  "%P", "%V")
            self.lblSaveToolsPath = tk.Label(self.root, text = "Save-Tools path:", width = 15)
            self.txbSaveToolsPath = tk.Entry(self.root, width = 50, textvariable=self.savetoolspath, validate="focus", validatecommand=vcmdSaveToolsPath)
            self.btnSaveToolsPath = tk.Button(self.root, text = "...", command=self.btnSaveToolsPath_Click)

            self.btnOk = tk.Button(self.root, text = "OK", command=self.btnOk_Click)
            self.btnCancel = tk.Button(self.root, text = "Cancel", command = self.root.destroy)

            self.btnOk = tk.Button(self.root, text = "OK", command=self.btnOk_Click)
            self.btnCancel = tk.Button(self.root, text = "Cancel", command = self.root.destroy)

            self.lblStatusbar = tk.Label(self.root, textvariable=self.statusText, relief=tk.SUNKEN)

            row = 0
            self.lblBoxCount.grid(column=0, row=row)
            self.txbBoxCount.grid(column=1, row=row, columnspan=2, sticky="we")

            row += 1
            self.lblBoxSlotCount.grid(column=0, row=row)
            self.txbBoxSlotCount.grid(column=1, row=row, columnspan=2, sticky="we")

            row += 1
            self.lblLevelPath.grid(column=0, row=row)
            self.txbLevelPath.grid(column=1, row=row, sticky="we")
            self.btnLevelPath.grid(column=2, row=row)

            row += 1
            self.lblSaveToolsPath.grid(column=0, row=row)
            self.txbSaveToolsPath.grid(column=1, row=row, sticky="we")
            self.btnSaveToolsPath.grid(column=2, row=row)

            row += 1
            self.btnOk.grid(column=0, row=row)
            self.btnCancel.grid(column=1, row=row)

            row += 1
            self.lblStatusbar.grid(row=row, columnspan=2, sticky="we")

        def OpenDialog(self):
            self.root.mainloop()

        def btnOk_Click(self):
            if (not self.ValidateAllFields()):
                return

            boxCount = 0
            boxSlotCount = 0
            try:
                # Just some extra validation that honestly isn't really needed
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
            self.result = True

        def btnLevelPath_Click(self):
            levelFileDialog = self.LevelFileDialog(parent=self.root)
            levelPath = levelFileDialog.GetPath()
            self.levelpath.set(levelPath)

        def btnSaveToolsPath_Click(self):
            savetoolsFileDialog = self.SaveToolsDialog(parent=self.root)
            savetoolsPath = savetoolsFileDialog.GetPath()
            self.savetoolspath.set(savetoolsPath)

        def ValidateAllFields(self):
            if (not self.Validate_txbBoxCount(self.boxcount.get(), "forced")):
                return False

            if (not self.Validate_txbBoxSlotCount(self.boxslotcount.get(), "forced")):
                return False

            if (not self.Validate_txbLevelPath(self.levelpath.get(), "forced")):
                return False

            if (not self.Validate_txbSaveToolsPath(self.savetoolspath.get(), "forced")):
                return False

            return True

        def Validate_txbBoxCount(self, P, V):
            self.statusText.set("")

            # Let the user wipe the field as they are typing
            if (P == "" and V == "key"):
                return True
            elif (P == "" and V in ["focusout", "focusin"]):
                self.boxcount.set(0)
                return True

            if (P == None or P == ""):
                if (V == "forced"):
                    self.statusText.set("Box Count can't be empty")
                return False
            elif (isinstance(P, int) or str.isdigit(P)):
                if (int(P) == 0 and V == "forced"):
                    self.statusText.set("Box Count can't be 0")
                    return False
                return True
            else:
                print("User trying to put in non-number into Box Count: {value}".format(value=P))
                message ="Must input a positive number"
                print(message)
                self.statusText.set(message)
                return False

        def Validate_txbBoxSlotCount(self, P, V):
            self.statusText.set("")

            # Let the user wipe the field as they are typing
            if (P == "" and V == "key"):
                return True
            elif (P == "" and V in ["focusout", "focusin"]):
                self.boxslotcount.set(0)
                return True

            if (P == ""):
                if (V == "forced"):
                    self.statusText.set("Box Slot Count can't be empty")
                return False
            elif (isinstance(P, int) or str.isdigit(P)):
                if (int(P) == 0 and V == "forced"):
                    self.statusText.set("Box Slot Count can't be 0")
                    return False
                return True
            else:
                print("User trying to put in non-number into Box Slot Count: {value}".format(value=P))
                message ="Must input a positive number"
                print(message)
                self.statusText.set(message)
                return False

        def Validate_txbLevelPath(self, P, V):
            self.statusText.set("")

            # Don't waste time validating empty field when changing focus
            if (P == "" and V in ["focusin", "focusout"]):
                return True

            if (P == None or P == ""):
                message = "Level path can't be blank"
                print(message)
                self.statusText.set(message)
                return False

            if (not os.path.exists(P)):
                message = "Level.sav path must exist"
                print(message)
                self.statusText.set(message)
                return False

            valueName, valueExtension = os.path.splitext(P)
            if (valueExtension.upper() not in [".sav".upper(), ".json".upper()]):
                message = "Level file must end in .sav or .json"
                print(message)
                self.statusText.set(message)
                return False

            return True

        def Validate_txbSaveToolsPath(self, P, V):
            self.statusText.set("")

            # Don't waste time validating empty field when changing focus
            if (P == "" and V in ["focusin", "focusout"]):
                return True

            if (P == None or P == ""):
                message = "Save-Tools path can't be blank"
                print(message)
                self.statusText.set(message)
                return False

            if (not os.path.exists(P)):
                message = "Save-Tools path doesn't exist"
                print(message)
                self.statusText.set(message)
                return False

            valueName, valueExtension = os.path.splitext(P)
            if (valueExtension.upper() not in [".cmd".upper(), ".py".upper()]):
                message = "Save-Tools must end in .cmd or .py"
                print(message)
                self.statusText.set(message)
                return False
                
            return True

        def GetBoxCount(self):
            return int(self.boxcount.get())

        def GetBoxSlotCount(self):
            return int(self.boxslotcount.get())

        def GetLevelPath(self):
            return self.levelpath.get()

        def GetSaveToolsPath(self):
            return self.savetoolspath.get()

        def Result(self):
            return self.result

        class LevelFileDialog:
            def __init__(self, parent):
                validFileTypes = (("Valid files", "*.sav *.sav.json"),(".sav", "*.sav"), (".sav.json", "*.sav.json"), ("All Files", "*.*"))
                self.path = filedialog.askopenfilename(filetypes=validFileTypes, title="Open Palworld Level.sav[.json] Save", parent=parent)

            def GetPath(self):
                return self.path

        class SaveToolsDialog:
            def __init__(self, parent):
                validFileTypes = (("Valid files", "*.cmd"),(".cmd", "*.cmd"), ("All Files", "*.*"))
                self.path = filedialog.askopenfilename(filetypes=validFileTypes, title="Open Palworld-Save-Tools convert.cmd", parent=parent)

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
