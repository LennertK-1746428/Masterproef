import tkinter as tk

window = tk.Tk()

# No parameters --> center, top-most available position
frame1 = tk.Frame(master=window, width=100, height=100, bg="red")
frame1.pack()

frame2 = tk.Frame(master=window, width=50, height=50, bg="yellow")
frame2.pack()

frame3 = tk.Frame(master=window, width=25, height=25, bg="blue")
frame3.pack()

# 'fill' parameter
# fill entire width/height of window with frame (tk.X, tk.Y)
# Notice that the width is not set on any of the Frame widgets. width is no longer necessary
# responsive to window resizing --> try resizing the window
label = tk.Label(master=window, text="fill")
label.pack()

frame1 = tk.Frame(master=window, height=100, bg="red")
frame1.pack(fill=tk.X)

frame2 = tk.Frame(master=window, height=50, bg="yellow")
frame2.pack(fill=tk.X)

frame3 = tk.Frame(master=window, height=25, bg="blue")
frame3.pack(fill=tk.X)

# 'side' parameter
#  specifies on which side of the window the widget should be placed
# label = tk.Label(master=window, text="side")
# label.pack()

# frame1 = tk.Frame(master=window, width=20, height=100, bg="red")
# frame1.pack(fill=tk.Y, side=tk.LEFT)

# frame2 = tk.Frame(master=window, width=10, bg="yellow")
# frame2.pack(fill=tk.Y, side=tk.RIGHT)

# frame3 = tk.Frame(master=window, width=50, bg="blue")
# frame3.pack(fill=tk.Y, side=tk.RIGHT)

# To make the layout truly responsive, you can set an initial size for your frames using the width and height attributes. 
# Then, set the fill keyword argument of .pack() to tk.BOTH and set the expand keyword argument to True:
label = tk.Label(master=window, text="fully responsive")
label.pack()

frame1 = tk.Frame(master=window, width=200, height=100, bg="red")
frame1.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)

frame2 = tk.Frame(master=window, width=100, bg="yellow")
frame2.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)

frame3 = tk.Frame(master=window, width=50, bg="blue")
frame3.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)

window.mainloop()