from tkinter import *
from tkinter.ttk import *
from time import strftime
from pynput.mouse import Controller as MouseController
from pynput.keyboard import Key, Controller as KeyboardController
import os

idle_timer = 0
mouse = MouseController()
keyboard = KeyboardController()

lastSavePosition = (0, 0)
awake_treshold = 90

is_snapped = False
prev_y = 0

LAST_STATE_FILE=".laststete"

def time(tolabel):
    string = strftime('%H:%M:%S %d-%b-%Y KW-%V').upper()
    tolabel.config(text=string)
    tolabel.after(1000, time, tolabel)

def execute_keep_awake_action():
    keyboard.press(Key.shift)
    keyboard.release(Key.shift)
    print(f"{strftime('%H:%M:%S')} - shift pressed")    

def counter(tolabel, counterval):
    global lastSavePosition
    currentPosition = mouse.position
    
    is_user_away = currentPosition == lastSavePosition
    if is_user_away:
        counterval += 1
        if(counterval > awake_treshold):
            execute_keep_awake_action()
            counterval = 0
        currentPosition = mouse.position
    else:
        counterval = 0
    
    lastSavePosition = currentPosition
    
    tolabel.config(text=f"S: {counterval:3d}s, A: {'?' if is_user_away else '\u2714'}")
    tolabel.after(1000, counter, tolabel, counterval)

def start_move(event):
    global window_pos_x, window_pos_y
    window_pos_x = event.x
    window_pos_y = event.y

def stop_move(event):
    global window_pos_x, window_pos_y
    window_pos_x = None
    window_pos_y = None

def do_move(event):
    global window_pos_x, window_pos_y, is_snapped, prev_y
    # Snap zóna meghatározása (pl. a képernyő alsó 50 pixel)
    snap_zone = 10

    # Képernyő méretének lekérdezése
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width, window_height, x, y = map(int, root.geometry().replace('x', '+').split('+'))
    
    # Ellenőrizzük, hogy az ablak az alsó snap zónában van-e
    deltax = event.x - window_pos_x
    deltay = event.y - window_pos_y
    x0 = root.winfo_x() + deltax
    y0 = root.winfo_y() + deltay
    
    #root.geometry(f"+{x0}+{y0}")
    #print(f"+{x0}+{y0}")

    # Ellenőrizzük, hogy az ablak az alsó snap zónában van-e és az egér felfelé mozog-e
    if screen_height - (y + window_height) <= snap_zone and not is_snapped:
        is_snapped = True
    elif is_snapped and event.y_root < prev_y:
        is_snapped = False  # Leválasztás, ha az egér felfelé mozog

    if is_snapped:
        # Ha snapelve van, az ablakot a képernyő aljára helyezzük
        root.geometry(f"{window_width}x{window_height}+{x}+{screen_height - window_height}")
    else:
        # Egyébként normál mozgatás
        root.geometry(f"{window_width}x{window_height}+{x0}+{y0}")

    # Az előző egér Y koordinátának frissítése
    prev_y = event.y_root


def on_closing(event=None):
    # Az ablak méretének és pozíciójának lekérdezése
    geometry = root.geometry()
    
    # Az adatok elmentése egy fájlba
    with open(LAST_STATE_FILE, "w") as file:
        file.write(geometry)
    
    root.destroy()

#############################################################

root=Tk()
if os.path.exists(LAST_STATE_FILE):
    with open(LAST_STATE_FILE, "r") as file:
        # Ablak pozíciójának és méretének beállítása
        root.geometry(file.read())
root.protocol("WM_DELETE_WINDOW", on_closing)
#root.title("Clock")

# Ablak fejlécének és keretének eltávolítása
root.overrideredirect(True)
# Ablak átméretezhetőségének letiltása
root.resizable(False, False)
# Ablak mindig legfelül beállítása
root.attributes('-topmost', True)



root.bind('<Button-1>', start_move)
root.bind('<ButtonRelease-1>', stop_move)
root.bind('<B1-Motion>', do_move)
# Stílus beállítása
style = Style()
style.configure('TFrame', background='black')
style.configure('TLabel', background='black', foreground='cyan')

# Ablakon belüli tartalom
content = Frame(root, style='TFrame')
content.pack(expand=YES, fill=BOTH)

time_label=Label(root,font=("ds-digital",14), style='TLabel', anchor='center', justify='center')
#label.pack(anchor='center')
time_label.pack(side=TOP, expand=YES, fill=BOTH)
# Eseménykezelő az ablak mozgatásához
#time_label.bind('<B1-Motion>', do_move)

# 'X' bezáró gomb
close_label = Label(content, text=" X ", font=("Arial", 6), style='TLabel')
close_label.pack(side=RIGHT, padx=5)
close_label.bind('<Button-1>', on_closing)

#counter test
counter_label = Label(content, font=("Arial", 6), style='TLabel')
counter_label.pack(side=LEFT, padx=5)
#close_label.bind('<Button-1>', close_window)
#root.geometry("250x50")

#############################################################

time(time_label)
counter(counter_label, idle_timer)
mainloop()