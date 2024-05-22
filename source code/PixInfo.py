# PixInfo.py
# Program to start evaluating an image in python

from PIL import Image, ImageTk
import glob, os, math


# Pixel Info class.
class PixInfo:
    # Constructor.
    def __init__(self, master):
        self.master = master
        self.imageList = []
        self.thumbnailList = []
        self.intenCode = []
        self.x = 0
        self.y = 0

        files = os.listdir("frames/")
        image_files = [file for file in files if file.endswith(".jpg")]
        image_files = sorted(image_files, key=lambda x: int(x.split(".")[0]))

        # Add each image (for evaluation) into a list,
        # and a Photo from the image (for the GUI) in a list.
        for infile in image_files:
            full_path = os.path.join("frames/", infile)
            im = Image.open(full_path)

            # Resize the image for thumbnails.
            self.x = int(im.size[0] / 4)
            self.y = int(im.size[1] / 4)
            imResize = im.resize((self.x, self.y), Image.ANTIALIAS)
            photo = ImageTk.PhotoImage(imResize)

            # Add the images to the lists.
            self.imageList.append(im)
            self.thumbnailList.append(photo)

        # Create a list of pixel data for each image and add it to a list.
        for im in self.imageList[:]:
            pixList = list(im.getdata())
            InBins = self.encode(pixList)
            self.intenCode.append(InBins)

    # Bin function returns an array of bins for each image with Intensity methods.
    def encode(self, pixlist):
        # 2D array initilazation for bins, initialized to zero.
        InBins = [0] * 25

        for pix in pixlist:
            # Calculate intensity
            # Put in InBins with appropriate values
            # H1: [0, 10), H2: [10, 20),... H24: [230, 240), H25: [240, 255)
            intensity = 0.299 * pix[0] + 0.587 * pix[1] + 0.114 * pix[2]
            intensity = int(intensity)

            if intensity > 239:
                InBins[24] += 1
            else:
                InBins[int(intensity / 10)] += 1

        # Return the list of binary digits, one digit for each pixel.
        return InBins

    # Accessor functions:
    def get_imageList(self):
        return self.imageList

    def get_thumbnailList(self):
        return self.thumbnailList

    def get_intenCode(self):
        return self.intenCode

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def get_image(self, filename):
        try:
            # Open the image file using PIL
            img = Image.open(filename)

            # Convert the PIL Image to a PhotoImage object for tkinter
            photo_img = ImageTk.PhotoImage(img)
            return photo_img
        except IOError:
            print(f"Unable to load image: {filename}")
            return None
