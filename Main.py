from customtkinter import *
import customtkinter
from tkinter import *
import PackingUnpacking as AnimTools
from AnimStruct import AnimSlot
from AnimStruct import Pivot
from AnimStruct import CarName
from tkinter import ttk
import tkinter
import os
from tkinter import filedialog
from DialogBox import InputDialog
import shutil
import PivotNames
import shutil
from tkinter import messagebox
import json
import EulerHexTools
import FrameTools

customtkinter.set_appearance_mode("dark")

PartAnimPath = ''

def UpdateStates(event=None):
    # Get selected item
    selected_items = Hierarchy.selection()
    
    if selected_items:
        # Get the parent of selected item
        selected_item = selected_items[0]  # Get the first selected item
        parent = Hierarchy.parent(selected_item)
        
        # Check if the parent is 'AnimSlots'
        if parent == 'AnimSlots':
            # Enable buttons
            rename_button.configure(state="normal")
            #delete_button.configure(state="normal")
        else:
            # Disable buttons
            rename_button.configure(state="disabled")
            #delete_button.configure(state="disabled")
         
        if parent == 'CarXName':
            # Enable buttons
            rename_button.configure(state="normal")

        if parent == 'PivotData':
            for item  in EntryList:
                item.configure(state="normal")
                item.delete(0, customtkinter.END)
            pivot = Pivot(selected_item)
            XEntry.insert(0, pivot.GetValues()[0])
            YEntry.insert(0, pivot.GetValues()[1])
            ZEntry.insert(0, pivot.GetValues()[2])
            WEntry.insert(0, pivot.GetValues()[3])
        elif Hierarchy.parent(parent) == 'AnimSlots':
            for item in EntryList:
                item.configure(state="normal")
                item.delete(0, customtkinter.END)
            WEntry.configure(state="disabled")
            with open('TEMP\Frames.json', 'r') as FramesJson:
                FramesInfo = json.load(FramesJson)
            frame = FramesInfo[parent][0][f"FRAME{(int(selected_items[0][21:])):02d}"]
            x = frame["x"]
            y = frame["y"]
            z = frame["z"]
            XEntry.insert(0, x)
            YEntry.insert(0, y)
            ZEntry.insert(0, z)
        else:
            for item in EntryList:
                item.delete(0, customtkinter.END)
                item.configure(state="disabled")

    else:
        # No selection, disable buttons
        rename_button.configure(state="disabled")
        #delete_button.configure(state="disabled")

def UpdateCoords(a):
    selected_items = Hierarchy.selection()
    selected_item = selected_items[0]
    parent = Hierarchy.parent(selected_item)
    if parent == 'PivotData':
        pivot = Pivot(selected_item)
        pivot.UpdateValues(float(XEntry.get()), float(YEntry.get()), float(ZEntry.get()), float(WEntry.get()))
    elif Hierarchy.parent(parent) == 'AnimSlots':
        with open('TEMP\Frames.json', 'r') as FramesJson:
            FramesInfo = json.load(FramesJson)
        frame = FramesInfo[parent][0][f"FRAME{(int(selected_items[0][21:])):02d}"]
        frame.update({
            "x": float(XEntry.get()),
            "y": float(YEntry.get()),
            "z": float(ZEntry.get())
        })
        with open('TEMP\Frames.json', 'w') as FramesJson:
            json.dump(FramesInfo, FramesJson, indent=4)

def InterpolateSlot():
    selected_items = Hierarchy.selection()
    if selected_items:
        if Hierarchy.parent(selected_items[0]) == 'AnimSlots':
            with open("TEMP\Frames.json", "r") as file:
                FrameList = json.load(file)
            Interpolated = FrameTools.Interpolate(FrameList, selected_items[0])
            try:
                with open("TEMP\Frames.json", "w") as file:
                    json.dump(Interpolated, file, indent=4)
            except Exception as e:
                messagebox.showerror("Error", e)
                return
            messagebox.showinfo("Success", f"Interpolated {Hierarchy.item(selected_items[0], 'text')}")

        else:
            messagebox.showerror("Error", "To interpolate you should select Anim Slot first!")
    else:
        messagebox.showerror("Error", "To interpolate you should select Anim Slot first!")



def FindAndReplace():
    Find = InputDialog.show(
    app, title="Editor", prompt="Enter string to search for", default_text='')
    if Find:
        Replace = InputDialog.show(
        app, title="Editor", prompt="Enter string to replace with", default_text='')
        for id in Hierarchy.get_children('AnimSlots'):
            slot = AnimSlot(id, '')
            name = slot.GetName()
            NewName = name.replace(Find, Replace)
            if slot.Rename(NewName):
                Hierarchy.item(id, text=NewName)

    else:
        pass


def rename_item():
    selected_item = Hierarchy.selection()
    selected_id = selected_item[0]
    if selected_item:
        if Hierarchy.parent(selected_item) == 'AnimSlots':
            SelectedSlot = AnimSlot(selected_id, '')
            input = InputDialog.show(
                app, title="Editor", prompt="Enter new AnimationSlot name", default_text=SelectedSlot.GetName())
            if input:
                if SelectedSlot.Rename(input):
                    Hierarchy.item(selected_id, text=input)
        elif Hierarchy.parent(selected_item) == 'CarXName':
            CarNameHash = CarName('TEMP/CarHashString.bin')
            input = InputDialog.show(
            app, title="Editor", prompt="Enter new CarXName", default_text=CarNameHash.GetName())
            if input:
                if CarNameHash.Rename(input):
                    Hierarchy.item(selected_id, text=input)


def PopulateHierarchy(FilePath):
        global Pivots
        global Hierarchy
        global AnimSlots
        for item in Hierarchy.get_children():
            Hierarchy.delete(item)
        Hierarchy.insert('', '0', 'i1', text=os.path.basename(FilePath))
        Hierarchy.insert('i1', 'end', iid='CarXName', text='CarXName')
        Hierarchy.insert('i1', 'end', iid='AnimSlots', text='AnimSlots')
        Hierarchy.insert('i1', 'end', iid='PivotData', text='PivotPositions')
        with open('TEMP/Frames.json', 'r') as json_file:
            frames_data = json.load(json_file)

        
        # Loop through and print each frame
        animlist = os.listdir('TEMP/AnimSlots/')
        pivotlist = os.listdir('TEMP/PivotData/')
        for item in animlist:
            fullpath = 'TEMP/AnimSlots/' + item
            Slot = AnimSlot(fullpath, '')
            Hierarchy.insert('AnimSlots', 'end', iid=fullpath, text=Slot.GetName())
            frames = frames_data[fullpath][0].items()
            print(f"Frames in {fullpath}:")
            for i, frame in enumerate(frames, 1):
                Hierarchy.insert(fullpath, 'end', iid=item+f'\FRAME{i}', text=f'FRAME{i:02d}')
        for item, pivot_name in zip(pivotlist, PivotNames.PivotNamesList):
            fullpath = 'TEMP/PivotData/' + item
            Hierarchy.insert('PivotData', 'end', iid=fullpath, text=pivot_name)
        CarNameHash = CarName('TEMP/CarHashString.bin')
        Hierarchy.insert('CarXName', 'end', iid='CARNAME', text=CarNameHash.GetName())

def Open():
    global PartAnimPath
    PartAnimPath = filedialog.askopenfilename()
    if PartAnimPath:
        CleanUp()
        if AnimTools.Unpack(PartAnimPath, "TEMP/"):
            PopulateHierarchy(PartAnimPath)
            Log.configure(text=f"Loaded: {PartAnimPath}")
        else:
            global Hierarchy
            for item in Hierarchy.get_children():
                Hierarchy.delete(item)
            Log.configure(text=f"Ready")


def Save():

    global PartAnimPath
    if PartAnimPath:
        if AnimTools.Pack(PartAnimPath, "TEMP/"):
            Log.configure(text=f"Saved: {PartAnimPath}")
        else:
            Log.configure(text=f"ERROR: Couldn't save the file. Please check if game is closed.")

        

def CleanUp():
    for filename in os.listdir('TEMP/'):
        file_path = os.path.join('TEMP/', filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
    

def Exit():
    for filename in os.listdir('TEMP/'):
        file_path = os.path.join('TEMP/', filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
    app.destroy()


app = CTk()  
app.title("PartAnimatorulator 0.0.4b | December 31, 2024") 
current_directory = os.path.dirname(os.path.abspath(__file__))
app.iconbitmap(os.path.join(current_directory, "icon.ico"))
app.protocol("WM_DELETE_WINDOW", Exit)
CleanUp()

window_width = 906
window_height = 466

# Get screen width and height
screen_width = app.winfo_screenwidth()
screen_height = app.winfo_screenheight()

# Calculate position coordinates
x = (screen_width // 2) - (window_width // 2)
y = (screen_height // 2) - (window_height // 2)

# Set the geometry with the position
app.geometry(f"{window_width}x{window_height}+{x}+{y}")

bg_color = app._apply_appearance_mode(customtkinter.ThemeManager.theme["CTkFrame"]["fg_color"])
text_color = app._apply_appearance_mode(customtkinter.ThemeManager.theme["CTkLabel"]["text_color"])
selected_color = app._apply_appearance_mode(customtkinter.ThemeManager.theme["CTkButton"]["fg_color"])
menu_bg_color = "#505050"
menu_fg_color = "white"

# Configure Treeview Style
treestyle = ttk.Style()
treestyle.theme_use('default')
treestyle.configure("Treeview", background=bg_color, foreground=text_color, fieldbackground=bg_color, borderwidth=0)
treestyle.map('Treeview', background=[('selected', bg_color)], foreground=[('selected', '#33FF53')])

# Configure Scrollbar Style
scrollbar_style = ttk.Style()
scrollbar_style.theme_use('default')
scrollbar_style.configure(
    "Vertical.TScrollbar",
    gripcount=0,
    background="gray",
    darkcolor="gray",
    lightcolor="gray",
    troughcolor="#1F1F1F",
    bordercolor=bg_color,
    arrowcolor="white",
    borderwidth=0,
    relief="flat"
)


# Configure grid layout for the main window
app.columnconfigure(0, weight=1)
app.rowconfigure(1, weight=1) # Changed to row 1 to accommodate menu bar
app.rowconfigure(2, weight=0)

# Create Menu Bar Frame
MenuFrame = CTkFrame(master=app)
MenuFrame.grid(row=0, column=0, sticky = "ew")

# Create menu in the MenuFrame
style = {'bg': "#2B2B2B", 'fg': "white", 
                 'activebackground': "#3D3D3D", 'activeforeground': "white",
                 'borderwidth': 0}

FileButton = tkinter.Menubutton(MenuFrame, text = "   File   ", **style)
FileButton.grid(row = 0, column = 0)

FileMenu = tkinter.Menu(FileButton, tearoff = 0, bg = bg_color, 
activebackground= selected_color, fg = "white",borderwidth = 1, activeborderwidth= 1)

FileMenu.add_command(label = "Open", command=Open)
FileMenu.add_command(label = "Save", command=Save)
FileMenu.add_command(label = "Exit", command=app.destroy)

FileButton.configure(menu = FileMenu)

ToolsButton = tkinter.Menubutton(MenuFrame, text = "  Tools  ", **style)
ToolsButton.grid(row = 0, column = 1)

ToolsMenu = tkinter.Menu(ToolsButton, tearoff = 0, bg = bg_color, 
activebackground= selected_color, fg = "white",borderwidth = 1, activeborderwidth= 1)

ToolsMenu.add_command(label = "Find and Replace (AnimSlot Only)", command=FindAndReplace)
ToolsMenu.add_command(label = 'Interpolate AnimSlot', command=InterpolateSlot)

ToolsButton.configure(menu = ToolsMenu)



# Create Main Content Frame
MainFrame = CTkFrame(master=app)
MainFrame.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
MainFrame.columnconfigure(0, weight=1)
MainFrame.columnconfigure(1, weight=3)
MainFrame.columnconfigure(2, weight=3)
MainFrame.rowconfigure(0, weight=1)

# Create main left frame to contain both top frame and hierarchy
LeftMainFrame = CTkFrame(master=MainFrame)
LeftMainFrame.grid(padx=5, pady=5, column=0, sticky='nsew')
LeftMainFrame.columnconfigure(0, weight=1)
LeftMainFrame.rowconfigure(1, weight=1)

# Create top frame
TopFrame = CTkFrame(master=LeftMainFrame)
TopFrame.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
TopFrame.columnconfigure((0), weight=1)

rename_button = CTkButton(master=TopFrame, text="Rename", command=rename_item, state="disabled", width=50,
                         fg_color="#1F1F1F", hover_color="#262626")
rename_button.grid(row=0, column=0, padx=2, sticky='ew')


# Create Hierarchy Frame
HierarchyFrame = CTkFrame(master=LeftMainFrame)
HierarchyFrame.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)

# Add a customized scrollbar
scrollbar = ttk.Scrollbar(HierarchyFrame, orient='vertical', style="Vertical.TScrollbar")
scrollbar.pack(side=RIGHT, fill=Y)

# Create Treeview
Hierarchy = ttk.Treeview(HierarchyFrame, yscrollcommand=scrollbar.set, show="tree", selectmode="browse")
Hierarchy.pack(fill="both", expand=True)

# Bind selection event
Hierarchy.bind('<<TreeviewSelect>>', UpdateStates)

# Configure scrollbar to control Treeview
scrollbar.config(command=Hierarchy.yview)

# Properties Frame
PropertiesFrame = CTkFrame(master=MainFrame)
PropertiesFrame.grid(padx=0, pady=5, row=0, column=1, sticky='nsew')

XLabel = CTkLabel(PropertiesFrame, text = 'X Coordinates')
XLabel.grid(row=0, column=0, sticky="w", padx=10, pady=1)
separator = ttk.Separator(PropertiesFrame)
separator.grid(row=1, column=0, sticky="ew", pady=1)

YLabel = CTkLabel(PropertiesFrame, text = 'Y Coordinates')
YLabel.grid(row=2, column=0, sticky="w", padx=10, pady=1)
separator1 = ttk.Separator(PropertiesFrame)
separator1.grid(row=3, column=0, sticky="ew", pady=1)

ZLabel = CTkLabel(PropertiesFrame, text = 'Z Coordinates')
ZLabel.grid(row=4, column=0, sticky="w", padx=10, pady=1)
separator2 = ttk.Separator(PropertiesFrame)
separator2.grid(row=5, column=0, sticky="ew", pady=1)

WLabel = CTkLabel(PropertiesFrame, text = 'W - Size')
WLabel.grid(row=6, column=0, sticky="w", padx=10, pady=1)
separator3 = ttk.Separator(PropertiesFrame)
separator3.grid(row=7, column=0, sticky="ew", pady=1)




PropertiesFrame.columnconfigure(0, weight=1)
ValuesFrame = CTkFrame(master=MainFrame)
ValuesFrame.grid(padx=5, pady=5, row=0, column=2, sticky='nsew')
ValuesFrame.columnconfigure(0, weight=1)



XEntry = CTkEntry(ValuesFrame, width=50, state="disabled")
XEntry.grid(row=0, column=0, sticky="nsew", pady=1)
separator4 = ttk.Separator(ValuesFrame)
separator4.grid(row=1, column=0, sticky="ew", pady=1)

YEntry = CTkEntry(ValuesFrame, width=50, state="disabled")
YEntry.grid(row=2, column=0, sticky="nsew", pady=1)
separator5 = ttk.Separator(ValuesFrame)
separator5.grid(row=3, column=0, sticky="ew", pady=1)

ZEntry = CTkEntry(ValuesFrame, width=50, state="disabled")
ZEntry.grid(row=4, column=0, sticky="nsew", pady=1)
separator6 = ttk.Separator(ValuesFrame)
separator6.grid(row=5, column=0, sticky="ew", pady=1)

WEntry = CTkEntry(ValuesFrame, width=50, state="disabled")
WEntry.grid(row=6, column=0, sticky="nsew", pady=1)
separator7 = ttk.Separator(ValuesFrame)
separator7.grid(row=7, column=0, sticky="ew", pady=1)

EntryList = [XEntry,YEntry,ZEntry,WEntry]

for item in EntryList:
    item.bind("<KeyRelease>", UpdateCoords)

LogFrame = CTkFrame(master=app)
LogFrame.grid(row=2, column=0, sticky = "ew")
Log = CTkLabel(LogFrame, text = 'Ready')
Log.grid(row=0, column=0, sticky="w", padx=10, pady=1)

app.mainloop()