"""Cimpl (Carleton Image Manipulation Python Library).

Copyright (c) 2013 - 2014, D.L. Bailey,
Department of Systems and Computer Engineering,
Carleton University

Cimpl provides a collection of functions for manipulating digital images.

Programmers should use the procedural interface to Cimpl; i.e., call the
"global" Colour and Image functions.

Do not call the methods provided by the underlying Image and Color
classes. These classes may be modified or replaced in future releases of
this module, and backwards compatibility is not guaranteed. Specifically,
class names and method names may be renamed, and classes and methods may be
replaced or deleted.

This version of Cimpl works with Python 3.x and Pillow 2.5.3/2.6.0.
"""

import os
import math

from tkinter import *
import tkinter.filedialog
import PIL.Image
import PIL.ImageTk

release = "Cimpl 1.00 Release Candidate 3"

IMAGE_FILE_FORMATS = ['.bmp', '.gif', '.jpg', '.jpeg', '.png', '.tif', '.tiff']

#-----------------------------------------------------------------

def _adjust_component(comp):
    """Return comp as an integer between 0 and 255, inclusive, returning 0
    if comp is negative and capping values >= 256 at 255.
    """
    comp = int(comp)
    return max(0, min(255, comp))

class Color(tuple):
    """An RGB color.

    When an instance is created, the RGB component values are quietly adjusted,
    as required, to ensure that they are ints in the range 0..255, inclusive.

    Examples:
      Color(120, 60, 200) yields the color (120, 60, 200)
      Color(-120, 60, 280) yields the color (0, 60, 255)
      Color(120.0, 60.5, 200.2) yields the color (120, 60, 200)

    Because Color is a subclass of tuple, Color objects can be treated as
    tuples. For example, to retrieve the rgb components stored in a Color
    object, it can be subscripted (indexed):

      col = Color(120, 60, 200)
      ...
      r = col[0]  # r is bound to 120
      g = col[1]  # g is bound to 60
      b = col[2]  # b is bound to 200

    Or, we can unpack a Color object, the same way we can unpack a tuple:

      r, g, b = col  # r is bound to 120, g is bound to 60, b is bound to 200

    To convert a Color object col to a tuple, do this:

      tuple(col)  # Returns the tuple (120, 60, 200)
    """

    __slots__ = () # Binding __slots__ to an empty tuple prevents instance
                   # dictionaries from being created, reducing memory
                   # requirements

    def __new__(_cls, red, green, blue):
        """Return a new instance of Color(red, green, blue)."""

        return tuple.__new__(_cls, (_adjust_component(red),
                                    _adjust_component(green),
                                    _adjust_component(blue)))

    @classmethod
    def _make(cls, t):
        # Make a new Color object from (r, g, b) tuple t.
        # This method assumes that t is a 3-tuple of ints, each in the
        # range 0 to 255, inclusive. THIS IS NOT CHECKED.
        #
        # The preferred way for application code to convert a tuple t to a
        # Color object is:
        #
        #     col = Color(t[0], [t1], t[2])
        #
        # or:
        #
        #     r, g, b = t
        #     col = Color(r, g, b)
        #
        # This way ensures that the rgb components will be converted, if
        # necessary, to integers in the range 0..255 when the Color object is
        # initialized.

        # Originally, I was going to have this function verify that it
        # was passed a 3-tuple.
        #
        # if not isinstance(t, tuple):
        #     raise TypeError('Argument is not a tuple')
        # if len(t) != 3:
        #     raise TypeError('Expected 3 values in tuple, got %d' % len(t))

        return tuple.__new__(cls, t)

    def __repr__(self):
        """Return the "official" string representation of the Color.

        This string is a valid expression that will yield a Color object with
        the same value when passed to eval().
        """

        return 'Color(red={0[0]}, green={0[1]}, blue={0[2]})'.format(self)


class Image(object):
    """
    A Image is a wrapper for an instance of PIL's Image class.
    Supported image formats include: JPEG, GIF, TIFF, PNG and BMP.

    To load an image from a file:

       image = Image(a_filename)

    To create a blank image with specified dimensions:

        image = Image(width=width_in_pixels, height=height_in_pixels)

    By default, the blank image's color is white. A different image color can be
    specified with a Color object:

        image = Image(width=width_in_pixels, height=height_in_pixels
                      color=Cimpl.Color(red, green, blue))

    To duplicate an image:

        original = Image(...)
        duplicate = Image(image=original)
    """

    def __init__(self, filename=None, image=None,
                 width=None, height=None, color=Color(255, 255, 255)):

        if filename is not None: # load image from file
            self.pil_image = PIL.Image.open(filename).convert("RGB")
            self.filename = filename

        elif image is not None:  # copy an image
            # To make a deep copy of the Image we're duplicating, we need to
            # copy its PIL Image.
            self.pil_image = image.pil_image.copy()
            self.filename = None

        elif width is None and height is None and color is None:
            raise TypeError('Image(): called with no arguments?')
        elif width is None or height is None:
            raise TypeError('Image(): missing width or height argument')
        elif width > 0 and height  > 0:  # create a blank image
            self.pil_image = PIL.Image.new(mode="RGB", size=(width, height),
                                           color=tuple(color))
            self.filename = None
        else:
            raise ValueError('Image(): width and height must be > 0')

        self.zoomfactor = 1 # By default, display images at their
                            # original size.
        self.pixels = self.pil_image.load() # The pixel access object for the
                                            # PIL Image; essentially a 2-D array
                                            # of (r, g, b) tuples.

    def copy(self):
        """Return a deep copy of this Image.
        """
        dup = Image(image=self)
        return dup

    def set_zoom(self, factor):
        '''Specify the amount that the image should be expanded when it is
        displayed; e.g., if factor is 3 the image is displayed at
        3 times its original size.
        '''
        if isinstance(factor, int) and factor > 0:
            self.zoomfactor = factor
        else:
            raise ValueError("factor must be a positive integer")

    def get_width(self):
        """Return the width of this Image, in pixels.
        """

        return self.pil_image.size[0]

    def get_height(self):
        """Return the height of this Image, in pixels.
        """

        return self.pil_image.size[1]

    def get_filename(self):
        """Return the name of the file where this Image is stored.
        """

        return self.filename

    def __iter__(self):
        """Return a generator object that iterates over this Image's pixels
        from left to right, top to bottom. The values when iterating are
        Color objects, each containing the RGB color of one pixel.
        """

        width = self.get_width()
        height = self.get_height()

        for y in range(0, height):
            for x in range(0, width):
                col = Color._make(self.pixels[x, y])
                yield x, y, col

    def get_color(self, x, y):
        """Return a Color containing the RGB components of the pixel at
        location (x, y) in this Image.
        """

        return Color._make(self.pixels[x, y])

    def set_color(self, x, y, color):
        """Set the color of the pixel at location (x, y) in this Image,
        to the RGB values stored in Color object, color.
        """

        # Ensure that color is bound to a Color object before we update the
        # pixel access object. Calling isinstance is frowned upon in some
        # circles, but we need to ensure that color is not bound to an
        # arbitrary sequence containing values outside the range 0..255.

        if not isinstance(color, Color):
            raise TypeError('Parameter color is not a Color object')
        
        #self.pixels[x, y] = (color[0], color[1], color[2])
        self.pixels[x, y] = tuple(color)

    def write_to(self, filename):
        """Save this Image to filename, overwriting the existing file.

        Raise a ValueError if
         - filename is None;
         - if filename has no extension.
         - if the filename's extension doesn't specify an image file format
           supported by this module.

        FIXME: reset the image's filename.
        """

        if filename:
            ext = os.path.splitext(filename)[-1]
            if ext == '':
                raise ValueError('Filename has no extension')

            # Extensions must be entirely lower-case or upper-case, but not
            # mixed case.
            if ext in IMAGE_FILE_FORMATS or \
                   (ext.isupper() and ext.lower() in IMAGE_FILE_FORMATS):
                self.pil_image.save(filename)
                #self.set_filename_and_title(filename)
            else:
                raise ValueError("%s is not a supported image file format." \
                                  % ext)
        else:
            raise ValueError("Parameter filename is None.")

    def _zoom_image(self):
        '''Return a copy of this Image, expanding it by the image's
        zoom factor (see set_zoom).
        '''
        copy = Image(width=self.get_width() * self.zoomfactor,
                       height=self.get_height() * self.zoomfactor,
                       color=Color(255, 255, 255))

        for x, y, col in self:
            scaled_x = x * self.zoomfactor
            scaled_y = y * self.zoomfactor
            for j in range(self.zoomfactor):
                for i in range(self.zoomfactor):
                    copy.set_color(scaled_x + i, scaled_y + j, col)
        return copy

    def show(self):
        root = Tk()

        # By default, display this image's PIL image access object.
        pil_image = self.pil_image

        if self.zoomfactor != 1:
            # Make an enlarged copy of this image and display its
            # PIL image access object.
            pil_image = self._zoom_image().pil_image

        if self.filename is None:
            view = ImageViewer(root, pil_image)
        else:

            # Use the name of the image file, without the drive/directory part
            # of its pathname, as the window's title.
            title = os.path.basename(self.filename)
            view = ImageViewer(root, pil_image, title)

        root.mainloop()

#---------------------------------------------------
# ImageViewer


class ImageViewer(object):
    def __init__(self, master, pil_image, title = "New Image"):
        """Initialize an image viewer (a Tk window) with parent widget master.
        pil_image is bound to the instance of PIL.Image.Image that contains
        the image to be displayed.
        """

        master.title(title)

        image_width = pil_image.size[0]
        image_height = pil_image.size[1]

        # Build a canvas big enough to display the image
        self.canvas = Canvas(master,
                             width=image_width,
                             height=image_height)

        self.photo_image = PIL.ImageTk.PhotoImage(pil_image)
        # The PhotoImage object must be bound to an instance variable
        # (which exists for the lifetime of the ImageViewer object) instead
        # of a local variable. If we don't do this, the PhotoImage object
        # might be garbage collected after __init__ returns, but before
        # we run the Tk/Tcl event loop, and the image won't appear in the
        # canvas. This is a bug in PIL...

        # Place the image in the canvas.
        self.canvas.create_image(image_width // 2,
                                 image_height // 2,
                                 image = self.photo_image)

        self.canvas.pack()

        master.resizable(0, 0) # Don't allow the window to be resized

#---------------------------------------------------
# "Global" Colour functions

def create_color(red, green, blue):
    """Return a Color object with the specified RGB components.

    When the Color object is created, non-integer component values are
    converted, if possible, to ints; negative values are converted to 0,
    and values > 255 are capped at 255.
    """

    return Color(red, green, blue)

def distance(color1, color2):
    """Return the Euclidean distance between two Color objects.
    """

    r1, g1, b1 = color1
    r2, g2, b2 = color2

    return math.sqrt((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2)

#---------------------------------------------------------------------------
# "Global" Image functions

def load_image(filename):
    """Return a Image loaded from the specified file.
    """
    return Image(filename)

def create_image(width, height, color=Color(255, 255, 255)):
    """Return a blank Image with the specified dimensions, in pixels.
    """

    return Image(width=width, height=height, color=color)

def copy(pict):
    """Return a deep copy of Image pict.
    """

    return pict.copy()

def get_width(pict):
    """Return the width of Image pict, in pixels.
    """

    return pict.get_width()

def get_height(pict):
    """Return the height of Image pict, in pixels."""

    return pict.get_height()

def get_color(pict, x, y):
    """
    Return a Color containing the RGB components of the pixel at
    location (x, y) in Image pict.
    """

    return pict.get_color(x, y)

def set_color(pict, x, y, color):
    """Set the color of the pixel at location (x, y) in Image pict,
    to the RGB values stored in Color object, color.
    """
    pict.set_color(x, y, color)

def save_as(pict, filename=None):
    """Save this Image to the specified file. If no filename is supplied,
    first prompt the user to interactively choose a directory and
    filename.

    Examples:
      save_as(pict, 'mypicture.jpg') saves pict to mypicture.jpg
      save_as(pict) asks the user to choose the directory and filename
    """

    if not filename:
        # The suggested name for the file is the image's current filename,
        # if it has one; otherwise, use 'untitled'.
        if pict.get_filename():
            base = os.path.basename(pict.get_filename())
            initial = os.path.splitext(base)[0]
        else:
            initial = 'untitled'
        filename = choose_save_filename(initial)

    if filename:
        pict.write_to(filename)

def save(pict):
    """Save this Image to its file, overwriting the existing file.

    If this Image doesn't have a corresponding filename; i.e., this
    instance has not yet been written to a file, the user will be prompted
    to provide a filename. See save_as(pict, filename).
    """

    name = pict.get_filename()
    if name:
        pict.write_to(name)
    else:
        save_as(pict)

def set_zoom(pict, factor):
    '''Specify the amount that the image should be expanded when it is
    displayed; e.g., if factor is 3 the image is displayed at
    3 times its original size.
    '''
    pict.set_zoom(factor)

def show(pict):
    """Display image pict in a window. The user must close the window to
    return control to the caller.
    """
    pict.show()

#---------------------------------
# File Dialogues

IMAGE_FILE_TYPES = [('All files', '.*'),
                    ('BMP', '.bmp'),
                    ('GIF', '.gif'),
                    ('PNG', '.png'),
                    ('TIFF', '.tif'),
                    ('TIFF', '.tiff'),
                    ('JPEG', '.jpg'),
                    ('JPEG', '.jpeg')]

def choose_save_filename(initial=''):
    """Display a Save As dialogue box. Return the complete path to 
    the new file.
    """

    root = Tk()
    # Hide the top-level window. (We only want the Save As dialogue box
    # to appear.)
    root.withdraw()

    path = tkinter.filedialog.asksaveasfilename(filetypes=IMAGE_FILE_TYPES,
                                          initialfile=initial,
                                          defaultextension='.jpg')

    # Things I've discovered about the dialogue box displayed by
    # asksaveasfilename():
    #
    # If the name we type in the "File name" field has no extension,
    # the extension corresponding to the selected "Save as type" is appended
    # to the name returned by the function.
    # An exception to this occurs when "All files" is selected as the
    # "Save as type" and we type a name without an extension. In this case,
    # defaultextension is appended to the name.

    # We can also type a name with an extension. If the extension is listed
    # in the IMAGE_FILE_TYPES list, that name is returned as typed, with no
    # changes to the extension; in other words, the extension implied by the
    # selected "Save as type" isn't used.

    # All bets are off if we type a name with an extension that isn't listed
    # in the IMAGE_FILE_TYPES list. Sometimes an additional extension
    # (corresponding to the selected "Save as type") is appended, but sometimes
    # this doesn't happen. I haven't found an explanation for this behaviour
    # in any of the online documentation or examples for Tkinter.

    root.destroy() # Do we need to do this?
    return path

def choose_file():
    """Display an Open dialog box. Return the complete path to the
    selected file.
    """

    root = Tk()
    # Hide the top-level window. (We only want the Open dialogue box
    # to appear.)
    root.withdraw()

    path = tkinter.filedialog.askopenfilename(filetypes=IMAGE_FILE_TYPES)

    root.destroy() # Do we need to do this?
    return path

print(release)
