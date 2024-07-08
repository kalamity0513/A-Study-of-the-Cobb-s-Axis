#!/bin/python3.12

import os
from os.path import isdir, isfile
from os import listdir
import sys
from tkinter import Tk

from DICOMViewer import DICOMLoader

""" MAIN APPLICATION ENTRY POINT
    This is where the application does a few checks at the folder given to it. """

def main():

    folder_path: str

    root = Tk()

    if len(sys.argv) == 2:
        if isdir(sys.argv[1]):
            folder_path = sys.argv[1]

            for fname in listdir(folder_path):
                if fname.endswith('.dcm'):
                    # do stuff on the file
                    break

            else:
                # do stuff if a file .true doesn't exist.
                print("APP ERROR: Invalid argument - folder does not contain dicom files (.dcm)")
                return

        else:
            print("APP ERROR: Invalid argument - folder not found")
            return


    else:
        print("APP ERROR: Please provide app one argument - the path to the dicom folder")
        return


    DICOMLoader(root, folder_path)
    root.mainloop()


if __name__ == "__main__":
    main()
