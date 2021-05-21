import tkinter as tk
from PIL import ImageTk, Image
canvas_w = 700
canvas_h = 700

def paint(event):
    color = 'red'
    print(event.x/canvas_w, event.y/canvas_h)
    file.write('{0:.4f} {1:.4f}\n'.format(event.x/canvas_w, event.y/canvas_h))
    x1, y1 = event.x-1, event.y-1
    x2, y2 = event.x+1, event.y+1
    c.create_oval(x1, y1, x2, y2, fill=color, outline=color)

def newline(event):
    print('\n:\n')
    file.write('\n')
    file.write(':\n')

file = open('./MakeUp_keypoints.txt', 'w')
file.write(':\n')
master = tk.Tk()
master.title = 'MakeUp Locator'
c = tk.Canvas(master, width=canvas_w, height=canvas_h, bg='white')
c.pack(expand=tk.YES, fill=tk.BOTH)
c.bind('<Button-1>', paint)
c.bind('<Button-3>', newline)
img = Image.open("Images/AF02.jpg")
img = img.resize((canvas_w, canvas_h))
img_tk = ImageTk.PhotoImage(img)
c.create_image(0, 0, anchor=tk.NW, image=img_tk)
message = tk.Label(master, text='Left click to print XY. Right click to start a new step.')
message.pack(side=tk.BOTTOM)
master.mainloop()

file.write('\n')
file.close()