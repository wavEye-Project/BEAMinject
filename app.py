"""
BEAMinject GUI app

This code is experimental, check out our GitHub repository:
https://github.com/wavEye-Project/BEAMinject for more info
"""
import BEAMinjector
__version__ = BEAMinjector.__version__

import sys
import threading
import tkinter.font
import customtkinter

# Identifier for inject_buildstr.py
buildstr = "custombuild"

app = customtkinter.CTk()
app.geometry("480x360")
app.resizable(False, False)
app.title(f"BEAMinject {__version__}")
customtkinter.set_appearance_mode("system")
customtkinter.set_default_color_theme("green")

fixedfont = customtkinter.CTkFont(*[], **tkinter.font.nametofont("TkFixedFont").actual())
def convert_monospace(widget, **kwargs):
    if "size" not in kwargs:
        kwargs["size"] = widget.cget("font").actual()["size"]
    new_font = customtkinter.CTkFont(**fixedfont.actual())
    new_font.configure(**kwargs)
    widget.configure(font=new_font)

# Injection logic
def write_logs(widget, text):
    widget.configure(state=customtkinter.NORMAL)
    widget.insert(customtkinter.END, text)
    widget.configure(state=customtkinter.DISABLED)
    widget.see(customtkinter.END)

def start_inject():
    for widget in frame.winfo_children()[1:]:
        widget.destroy()
    logwidget = customtkinter.CTkTextbox(frame, state='disabled', width=500, height=220)
    convert_monospace(logwidget, size=14)
    logwidget.pack(padx=8, pady=8)
    titlelabel.set("Injecting...")
    BEAMinjector.launchmc = launchmc.get()
    BEAMinjector.preview_version = patchpreview.get()
    BEAMinjector.write_logs = lambda x: write_logs(logwidget, x)
    BEAMinjector.quitfunc = quit_button
    thread = threading.Thread(target=BEAMinjector.main, args=())
    thread.start()

def quit_button(return_code):
    if return_code:
        titlelabel.set("Failed")
    else:
        titlelabel.set("Success!")
    quitbtn = customtkinter.CTkButton(master=frame, command=lambda: sys.exit(app.destroy() is not None))
    quitbtn.pack()
    quitbtn.configure(text="Quit")



# UI components
###############

# Frame
frame = customtkinter.CTkFrame(master=app)
frame.pack(pady=20, padx=20, fill="both", expand=True)

title = customtkinter.CTkLabel(master=frame, justify=customtkinter.LEFT)
title.pack(pady=10)
titlelabel = customtkinter.StringVar()
titlelabel.set("BEAMinject")
title.configure(textvariable=titlelabel, font=("", 30))


# Injection start
startbutton = customtkinter.CTkButton(master=frame, command=start_inject)
startbutton.pack(pady=20)
startbutton.cget("font").configure(size=20, weight="bold")
startbutton.configure(text="Let's go!", width=180, height=60)

# Launch MC
launchmc = customtkinter.IntVar()
launchmc.set(1)
launchswitch = customtkinter.CTkSwitch(master=frame, variable=launchmc)
launchswitch.pack(pady=10)
launchswitch.configure(text="Launch Minecraft")

# Beta Minecraft
patchpreview = customtkinter.IntVar()
patchpreview.set(0)
previewswitch = customtkinter.CTkSwitch(master=frame, variable=patchpreview)
previewswitch.pack(pady=10)
previewswitch.configure(text="Patch Minecraft Preview")

# Theme Switch
currenttheme = customtkinter.IntVar()
if customtkinter.get_appearance_mode() == "Light":
    currenttheme.set(1)
def updatetheme():
    if currenttheme.get():
        customtkinter.set_appearance_mode("light")
    else:
        customtkinter.set_appearance_mode("dark")
themeswitch = customtkinter.CTkSwitch(master=frame, variable=currenttheme, command=updatetheme)
themeswitch.pack(padx=35, side=customtkinter.LEFT)
themeswitch.configure(text="Light Mode")


# Build string
title = customtkinter.CTkLabel(master=frame, justify=customtkinter.RIGHT)
title.pack(padx=35, side=customtkinter.RIGHT)
title.configure(text=f"version {__version__}\nbuild {buildstr}")

# Start app
app.mainloop()
