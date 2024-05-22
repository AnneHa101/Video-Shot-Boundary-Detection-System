# ImageViewer.py
# Program to start evaluating an image in python

# Define Constants
START_FRAME = 1000
END_FRAME = 4999

from tkinter import *
import math, os, sys
import cv2, time
import numpy as np
from PixInfo import PixInfo


def read_video(filename):
    cap = cv2.VideoCapture(filename)
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    if not cap.isOpened():
        print("Error opening video stream or file")
        exit(0)
    print("Wait a minute to capture frames from 1000 to 4999...")

    cap.set(cv2.CAP_PROP_POS_FRAMES, START_FRAME)
    index = START_FRAME

    while cap.isOpened():
        cap.set(cv2.CAP_PROP_POS_FRAMES, index)
        ret, img = cap.read()  # Read the video frame by frame: status, frame data

        if not ret:
            print("Error: Unable to read frame.")
            break
        if index <= END_FRAME:
            cv2.imwrite(f"frames/{index}.jpg", img)  # Save frames 1000 to 4999
        else:
            break
        index += 1

    print("Video processing done!")
    cap.release()
    cv2.destroyAllWindows()


# Main app.
class ImageViewer(Frame):
    # Constructor.
    def __init__(self, master, pixInfo, resultWin):
        Frame.__init__(self, master)
        self.master = master
        self.pixInfo = pixInfo
        self.resultWin = resultWin
        self.intenCode = pixInfo.get_intenCode()
        self.imageList = pixInfo.get_imageList()  # Full-sized images.
        self.thumbnailList = pixInfo.get_thumbnailList()
        self.x = pixInfo.get_x()
        self.y = pixInfo.get_y()
        self.SDs = []
        self.Tb = 0
        self.Ts = 0
        self.Tor = 2
        self.CSet = set()
        self.FSet = set()
        self.firstFrames = []
        self.shotList = []

        # Create Main frame.
        mainFrame = Frame(master)
        mainFrame.pack()

        # Create Picture chooser frame.
        listFrame = Frame(mainFrame)
        listFrame.pack(side=LEFT)

        # Create Control frame.
        controlFrame = Frame(mainFrame)
        controlFrame.pack(side=RIGHT)

        # Create Preview frame.
        previewFrame = Frame(mainFrame, width=self.x + 45, height=self.y)
        previewFrame.pack_propagate(0)
        previewFrame.pack(side=RIGHT)

        # Create Results frame.
        resultsFrame = Frame(self.resultWin)
        resultsFrame.pack(side=BOTTOM)
        self.canvas = Canvas(resultsFrame)
        self.resultsScrollbar = Scrollbar(resultsFrame)
        self.resultsScrollbar.pack(side=RIGHT, fill=Y)

        # Layout Picture Listbox.
        self.listScrollbar = Scrollbar(listFrame)
        self.listScrollbar.pack(side=RIGHT, fill=Y)
        self.list = Listbox(
            listFrame,
            yscrollcommand=self.listScrollbar.set,
            selectmode=BROWSE,
            height=10,
        )
        for i in range(len(self.imageList)):
            self.list.insert(i, self.imageList[i].filename)
        self.list.pack(side=LEFT, fill=BOTH)
        self.list.activate(1)
        self.list.bind("<<ListboxSelect>>", self.update_preview)
        self.listScrollbar.config(command=self.list.yview)

        # Layout Controls.
        b1 = Button(
            controlFrame,
            text="Intensity",
            padx=10,
            width=10,
            command=lambda: self.find_distance(),
        )
        b1.grid(row=2, sticky=E)

        self.resultLbl = Label(controlFrame, text="Results:")
        self.resultLbl.grid(row=3, sticky=W)

        # Layout Preview.
        self.selectImg = Label(previewFrame, image=self.thumbnailList[0])
        self.selectImg.pack()

    # Event "listener" for listbox change.
    def update_preview(self, event):
        i = self.list.curselection()[0]
        self.selectImg.configure(image=self.thumbnailList[int(i)])

    # Get frame-to-frame difference
    # by calculating Manhattan distance between an image and the next image
    # and building SDs
    def find_distance(self):
        binList = self.intenCode

        for i in range(len(self.imageList) - 1):
            sum = 0

            for j in range(len(binList[i])):
                imgi = float(binList[i][j])
                imgk = float(binList[i + 1][j])
                sum += math.fabs(imgi - imgk)

            self.SDs.append((i + START_FRAME, sum))

        self.check_thresholds()
        self.update_shotList()
        self.update_results()

    # Check thresholds for the SDs
    def check_thresholds(self):
        differences = [tuple[1] for tuple in self.SDs]
        mean = np.mean(differences)
        std = np.std(differences, ddof=1)
        self.Tb = mean + 11 * std
        self.Ts = mean * 2
        print("SDs", self.SDs)

        # Loop through the SDs and compare them to the thresholds
        # to determine the type of change
        i = 0
        while i in range(len(self.SDs)):
            if self.SDs[i][1] >= self.Tb:
                self.CSet.add((START_FRAME + i, START_FRAME + i + 1))
                i += 1
            elif self.SDs[i][1] >= self.Ts and self.SDs[i][1] < self.Tb:
                Fs_candidate = i
                total_sum = self.SDs[i][1]
                count = 0  # count consecutive frames with SD < Tb
                isRealFs = False

                for j in range(i + 1, len(self.SDs)):
                    if self.SDs[j][1] < self.Ts:
                        count += 1
                        total_sum += self.SDs[j][1]

                        if count == self.Tor:
                            total_sum = self.get_sum_to_check(j, total_sum, count)
                            if total_sum >= self.Tb:
                                isRealFs = True
                                self.FSet.add(
                                    (
                                        START_FRAME + Fs_candidate,
                                        START_FRAME + j - count,
                                    )
                                )
                            break
                    elif self.SDs[j][1] >= self.Tb:
                        count = 0  # reset count
                        if total_sum >= self.Tb:
                            isRealFs = True
                            self.FSet.add(
                                (START_FRAME + Fs_candidate, START_FRAME + j - 1)
                            )
                        if not self.frame_included(START_FRAME + j):
                            self.CSet.add((START_FRAME + j, START_FRAME + j + 1))
                        break
                    else:
                        count = 0  # reset count
                        total_sum += self.SDs[j][1]

                if count < self.Tor and count != 0:
                    total_sum = self.get_sum_to_check(j, total_sum, count)
                    if total_sum >= self.Tb:
                        isRealFs = True
                        self.FSet.add(
                            (START_FRAME + Fs_candidate, START_FRAME + j - count)
                        )

                if isRealFs:
                    i = j + 1
                else:
                    i += 1
            else:
                i += 1

        self.CSet = sorted(self.CSet, key=lambda x: x[0])
        self.FSet = sorted(self.FSet, key=lambda x: x[0])
        print("CSet: ", self.CSet)
        print("FSet: ", self.FSet)

    # Recalculate the sum of SDs for (Fs_candidate, Fe_candidate)
    def get_sum_to_check(self, cur_idx, total_sum, count):
        new_idx = max(cur_idx - count, 0)
        for k in range(cur_idx, new_idx, -1):
            total_sum -= self.SDs[k][1]
        return total_sum

    # Check if the frame is in the CSet/FSet
    def frame_included(self, frame):
        return any(start <= frame <= end for start, end in self.CSet) or any(
            start <= frame <= end for start, end in self.FSet
        )

    # Update the shotList
    def update_shotList(self):
        # Get the first frames of each shot, Ce and Fs + 1
        self.firstFrames = [tuple[1] for tuple in self.CSet] + [
            tuple[0] + 1 for tuple in self.FSet
        ]

        # Sort the first frames
        self.firstFrames.sort()
        print("firstFrames: ", self.firstFrames)

        # Store the shots in shotList
        for i in range(len(self.firstFrames) - 1):
            self.shotList.append((self.firstFrames[i], self.firstFrames[i + 1] - 1))
        self.shotList.append((self.firstFrames[-1], END_FRAME))
        print("shotList: ", self.shotList)

    # Update the results window with the sorted results
    def update_results(self):
        cols = int(math.ceil(math.sqrt(len(self.firstFrames))))
        fullsize = (0, 0, (self.x * cols), (self.y * cols))

        # Initialize the canvas with dimensions equal to the number of results.
        self.canvas.delete(ALL)
        self.canvas.config(
            width=self.x * cols + 50,
            height=self.y * cols / 2 + 50,
            yscrollcommand=self.resultsScrollbar.set,
            scrollregion=fullsize,
        )
        self.canvas.pack()
        self.resultsScrollbar.config(command=self.canvas.yview)

        # Append images to the list ordered by Manhattan distance DES
        photoRemain = []
        for img in self.firstFrames:
            i = img - START_FRAME
            photoRemain.append((img, self.imageList[i].filename, self.thumbnailList[i]))

        # Place first images on buttons, then on the canvas in the sequence order.
        # Buttons envoke the play_shot(f) method.
        rowPos = 0
        while photoRemain:
            photoRow = photoRemain[:cols]
            photoRemain = photoRemain[cols:]
            colPos = 0
            for firstFrame, filename, img in photoRow:
                link = Button(self.canvas, image=img)
                handler = lambda f=firstFrame: self.play_shot(f)
                link.config(command=handler)
                link.pack(side=LEFT, expand=YES)
                self.canvas.create_window(
                    colPos,
                    rowPos,
                    anchor=NW,
                    window=link,
                    width=self.x + 10,
                    height=self.y + 10,
                )
                colPos += self.x

            rowPos += self.y

    # Play the shot when the button is clicked
    def play_shot(self, firstFrame):
        start = firstFrame
        for i in range(len(self.shotList)):
            if self.shotList[i][0] == firstFrame:
                end = self.shotList[i][1]
                break

        for i in range(start, end + 1):
            filename = f"frames/{i}.jpg"
            if not os.path.isfile(filename):
                print(f"File {filename} does not exist.")
                continue

            frame = cv2.imread(filename)
            cv2.imshow("Frame", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
            time.sleep(0.01)

        cv2.destroyAllWindows()


# Executable section.
if __name__ == "__main__":
    # Read video file
    read_video("videos/20020924_juve_dk_02a.mpg")

    root = Tk()
    root.title("Video Analysis Tool")

    resultWin = Toplevel(root)
    resultWin.title("Result Viewer")
    resultWin.protocol("WM_DELETE_WINDOW", lambda: None)

    pixInfo = PixInfo(root)

    imageViewer = ImageViewer(root, pixInfo, resultWin)

    root.mainloop()
