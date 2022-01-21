# https://realpython.com/python-gui-tkinter/

import tkinter as tk

# init window
window = tk.Tk()

# Label widget
greeting = tk.Label(
    text="Hello, Tkinter", 
    foreground="white",  # Set the text color to white
    background="black",  # Set the background color to black)
    # width and height are in text units --> 1 width = the width of '0', 1 height = the height of '0' 
    # --> width and height both 10 won't be a square
    width=10,            
    height=10
)
greeting.pack()

# Button widget
button = tk.Button(
    text="Click me!",
    width=25,
    height=5,
    bg="blue",      # background and bg are the same
    fg="yellow",    # idem
)
button.pack()

# Entry widget
# Retrieving text with .get()
# Deleting text with .delete()
# Inserting text with .insert()
entrylabel = tk.Label(text="Name")
entry = tk.Entry(width=50)
entry.insert(0, "lennert")
# entry.delete(0, tk.END)  # delete whole entry text
entrylabel.pack()
entry.pack()

# Text widget
# Similar to Entry widget, but text --> multiple paragraphs <--> entry --> one line 
text = tk.Text()
text.pack()

# keep window running and listening for events
window.mainloop()