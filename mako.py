import cv2
import argparse
import os
import pathlib
import imghdr
import sys

###     Arguments

#load the arguments
arguments = argparse.ArgumentParser()

#file input
arguments.add_argument(
    '-i', '--input',
    type = str,
    dest = 'input_source',
    required = True,
    
    help = 'Source File or Directory of Files'
)

#output directory
arguments.add_argument(
    '-o', '--output',
    type = str,
    dest = 'output_folder',
    help = 'Output folder (If empty, it uses current directory)',
    required = False,
    default = 'CURRENTDIR'
)

#Manga or Comic
arguments.add_argument(
    '-t', '--type',
    type = str,
    dest = 'current_type',
    help = 'defind comic type ( [M]anga or [C]omic)',
    required = False,
    default = 'Manga'
)

###     File Loaders

#retuns a list of all images in the dir
def prase_dir(str_path):
    img_files = []
    files_in_dir = []

    #load all file in a dir
    for root, dirs, files in os.walk(str_path):
        for filename in files:
            files_in_dir.append( os.path.join( root, filename ) )
    
    #check if the file is image file (cant wait someone actualy passes GIF here!)
    for file_in_question in files_in_dir :
        if imghdr.what(file_in_question) is not None :
            
            img_files.append(file_in_question)
    
    return img_files

#configure if the input is a folder or just an image
def load_img(str_path):
    files = []

    #load the files into list
    if os.path.isdir(str_path) :
        files = prase_dir(str_path)
    else :
        files.append(str_path)

    return files

#set the output directory
def output_folder_check(str_folderpath):
    
    #using current dir!
    if str_folderpath is 'CURRENTDIR':
        return os.getcwd()
    
    #using input dir
    if os.path.isdir(str_folderpath) is False:
        #if its not a correct input then trow an error
        sys.exit('Error invalid OUTPUT folder name or path')

    return str_folderpath

#check if the input is valid
def input_type_check(str_input_path):

    if os.path.isdir(str_input_path):
        return ' (Folder)'

    elif os.path.isfile(str_input_path):
        return ' (File)'
    
    else :
        sys.exit('Error invalid File or folder for input')

###     Image processsing

#detect panels in a image
def panel_detector(cv2_img):
    #Convert it into grayscale and get the dimensions
    gray_img = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2GRAY)
    img_hight, img_width, img_colors = cv2_img.shape

    #defind the minium width and hight of a panel
    panel_minim_width = img_width // 16
    panel_minim_hight = img_hight // 16

    #color treshold for image
    tmin = 220
    tmax = 255

    #using the treashold we turn the image into binary the invert it (white -> black || black -> white)
    _ , threshed_img = cv2.threshold(gray_img, tmin, tmax, cv2.THRESH_BINARY_INV)

    #simple appromixmation to define the minium shape
    #RET_EXTERNAL for only the outer most contour
    #cv2.CHAIN_APPROX_SIMPLE removes all redundant points and compresses the contour
    contours, hierarchy = cv2.findContours(threshed_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    detected_panels = []    #holder for cv2.image crops

    #loop for every detected countours
    for contour in contours:

        #get the archlength (circumference of the countour) and get define how accurate (epsilon) it should be
        arclength = cv2.arcLength(contour, True)
        epsilon = 0.15 * arclength

        #get the appoximate shape of the countour
        approx = cv2.approxPolyDP(contour,epsilon,True)

        #convert contours into rectange then get then the 4 corners
        x,y,w,h = cv2.boundingRect(approx)

        #if its smaller than the minimum width then we dont care
        if (w < panel_minim_width) and (h < panel_minim_hight):
            continue
        
        #append the valid contours into the list
        detected_panels.append( [x, y, (x + w), (y + h)] )
    
    #return valid panels
    return detected_panels

#get the middle location of a square
def middle_location(input_coords = []):
    x_pos = ( (input_coords[0] + input_coords[2]) // 2 )
    y_pos = ( (input_coords[1] + input_coords[3]) // 2 )
    return [x_pos, y_pos]

#map a 2D point into a 1D line
def sorting_funct_manga(cords = []):
    middle_coords = middle_location(cords)
    x_coord = middle_coords[0] * -31
    y_coord = middle_coords[1] * 3
    return x_coord + y_coord


#write the output into a file!
def write_to_file(str_folderpath, str_filename, cv2_img, list_panels = []):
    filename = pathlib.PurePath(str_filename).stem  #get the filename
    counter = 0
    for panel in list_panels:
        counter = counter + 1
        
        #crop the image using cv2 array slicing
        cropped_img = cv2_img[ 
            panel[1] : panel[3],
            panel[0] : panel[2]
        ]

        #make a filename and generate the full path and then write it!
        panel_filename = filename + 'x' + str(counter) + '.jpg'
        panel_fullpath = os.path.join(str_folderpath, panel_filename)
        cv2.imwrite(panel_fullpath, cropped_img)



#main function 
if __name__ == "__main__":
    args = arguments.parse_args()

    fof_input = args.input_source
    output_foler = output_folder_check(args.output_folder)
    current_type = args.current_type

    print("Input  : ", fof_input, input_type_check(fof_input))
    print("Output : ", output_foler)
    print('Type   : ', current_type)

    #prase the input!
    files_or_folders = load_img(fof_input)
    print( "Files to processed : ", len(files_or_folders) )
    print('')

    #loop each object
    for img_file in files_or_folders:
        print('File : ', img_file)

        img_source = cv2.imread(img_file)           #load the image from file
        panels = panel_detector(img_source)         #get the panels
        panels.sort(key = sorting_funct_manga)      #sort the panels

        print('Detected Panels : ', len(panels) )

        write_to_file(output_foler, img_file, img_source, panels)
        print('')




    

