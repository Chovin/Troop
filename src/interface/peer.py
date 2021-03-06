from __future__ import absolute_import

try:
    import Tkinter as Tk
except ImportError:
    import tkinter as Tk
    
from ..config import *
import colorsys

def rgb2hex(*rgb): 
    r = max(0, min(rgb[0], 255))
    g = max(0, min(rgb[1], 255))
    b = max(0, min(rgb[2], 255))
    return "#{0:02x}{1:02x}{2:02x}".format(r, g, b)

def int2rgb(i):
    h = (((i + 2) * 70) % 255) / 255.0
    return [int(n * 255) for n in colorsys.hsv_to_rgb(h, 1, 1)]

class PeerColourTest:
    def __init__(self):
        self.root=Tk.Tk()
        num = 20
        h = 30
        w = 100
        self.canvas =Tk.Canvas(self.root, width=300, height=num*h)
        self.canvas.pack()
        m = 0
        for n in range(num):
            rgb = int2rgb(n)
            m = 0
            self.canvas.create_rectangle(m * w, n * h, (m + 1) * w,  (n + 1) * h, fill=rgb2hex(*rgb))
            m = 1
            rgb = tuple(n - 30 for n in rgb)
            self.canvas.create_rectangle(m * w, n * h, (m + 1) * w,  (n + 1) * h, fill=rgb2hex(*rgb))
            m = 2
            self.canvas.create_rectangle(m * w, n * h, (m + 1) * w,  (n + 1) * h, fill="Black")
        self.root.mainloop()


def PeerFormattingOld(index):
    """
        Based on a number between 0 and 99, returns a tuple with
        three colours:

        colour[0] = Text colour
        colour[1] = Highlight text colour
        colour[2] = Colour for strings
        
    """
    rgb = int2rgb(index)
    
    a = rgb2hex(*rgb)
    b = COLOURS["Background"]
    c = rgb2hex(*tuple(n - 30 for n in rgb))
    
    return a, b, c

def PeerFormatting(index):
    i = index % len(COLOURS["Peers"])
    c = COLOURS["Peers"][i]
    return c, "Black"

class Peer:
    """ Class representing the connected performers within the Tk Widget
    """
    def __init__(self, id_num, widget, row=1, col=0):
        self.id = id_num
        self.root = widget # Text
        self.root_parent = widget.root

        self.name = Tk.StringVar()
        self.name.set("Peer")

        self.update_colours()
        
        self.label = Tk.Label(self.root,
                           textvariable=self.name,
                           bg=self.bg,
                           fg=self.fg,
                           font="Font")

        self.insert = Tk.Label(self.root,
                            bg=self.bg,
                            fg=self.fg,
                            bd=0,
                            height=2,
                            text="", font="Font" )

        self.text_tag = "text_" + str(self.id)
        self.code_tag = "code_" + str(self.id)
        self.sel_tag  = "sel_"  + str(self.id)
        self.str_tag  = "str_"  + str(self.id) 
        self.mark     = "mark_" + str(self.id)

        self.root.peer_tags.append(self.text_tag)

        # Stat graph

        self.count = 0
        self.graph = None

        self.configure_tags()
        
        # Tracks a peer's selection amount and location
        self.row = row
        self.col = col
        self.sel_start = "0.0"
        self.sel_end   = "0.0"

        # self.move(1,0) # create the peer

    def __str__(self):
        return str(self.name.get())

    def update_colours(self):
        self.bg, self.fg = PeerFormatting(self.id)
        return self.bg, self.fg

    def configure_tags(self):
        doing = True
        while doing:
            try:
                # Text tags
                self.root.tag_config(self.text_tag, foreground=self.bg)
                self.root.tag_config(self.str_tag,  foreground=self.fg)
                self.root.tag_config(self.code_tag, background=self.bg, foreground=self.fg)
                self.root.tag_config(self.sel_tag,  background=self.bg, foreground=self.fg)
                # Label
                self.label.config(bg=self.bg, fg=self.fg)
                self.insert.config(bg=self.bg, fg=self.fg)
                doing = False
            except TclError:
                pass
        return
        
    def move(self, row, col, raised = False):
        """ Updates the location of the Peer's label """

        try:

            row = int(row)
            col = int(col)

            index = "{}.{}".format(row, col)

            if index == self.root.index(Tk.END):

                self.row = row - 1
                end_index = self.root.index(str(self.row) + ".end")

                self.col = int(end_index.split(".")[1])

            else:

                self.row = row
                self.col = col

            index = "{}.{}".format(self.row, self.col)

            # Update the Tk text tag

            self.root.mark_set(self.mark, index)

            # Only move the cursor if we have a valid index

            bbox = self.root.bbox(index)

            if bbox is not None:

                x, y, width, height = bbox

                x_val = x - 2

                # Label can go on top of the cursor

                if raised:

                    y_val = (y - height, y - height)

                else:

                    y_val = (y + height, y)
                
                self.label.place(x=x_val, y=y_val[0], anchor="nw")
                self.insert.place(x=x_val, y=y_val[1], anchor="nw")

            else:

                # If we're not meant to see the peer, hide it
                
                self.label.place(x=-100, y=-100)
                self.insert.place(x=-100, y=-100)

        except Tk.TclError:

            pass
            
        return

    def select(self, start, end):
        """ Highlights text selected by this peer"""
        self.root.tag_remove(self.sel_tag, "1.0", Tk.END)
        start, end = self.root.sort_indices([start, end])
        self.sel_start = start
        self.sel_end   = end  
        if start != end:
            self.root.tag_add(self.sel_tag, self.sel_start, self.sel_end)
        return

    def remove(self):
        self.label.destroy()
        self.insert.destroy()
        self.root.root.graphs.delete(self.graph)
        return
    
    def hasSelection(self):
        return self.sel_start != self.sel_end != "0.0"
    
    def deleteSelection(self):
        self.root.tag_remove(self.sel_tag, self.sel_start, self.sel_end)
        self.root.delete(self.sel_start, self.sel_end)
        row, col = self.sel_start.split(".")
        self.move(row, col)
        self.sel_start = "0.0"
        self.sel_end   = "0.0"
        return

    def highlightBlock(self, lines):

        a, b = (int(x) for x in lines)

        if a == b: b += 1

        for line in range(a, b):
            start = "%d.0" % line
            end   = "%d.end" % line

            # Highlight text only to last character, not whole line

            self.highlight(start, end)
            
        # Unhighlight the line of text

        self.root.master.after(200, self.unhighlight)

        return

    def highlight(self, start, end):
        self.root.tag_add(self.code_tag, start, end)
        return

    def unhighlight(self):
        self.root.tag_remove(self.code_tag, "1.0", Tk.END)
        return

    def index(self):
        a = "{}.{}".format(self.row, self.col)
        b = self.root.index(self.mark)
        if a != b:
            stdout(a, b)
        return b
    
    def __eq__(self, other):
        return self.id == other
    def __ne__(self, other):
        return self.id != other

