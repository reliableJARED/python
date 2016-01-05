'''
This code will put a video on a colored object (like a green ball)in the main
video stream.  It will resize the overlay video on the fly
based on big the tracked object is.  The code will not work without
the file: hist_for_tracking.png
that is the 'color calibration' image.  The program does allow you
to calibrate to any color.  press 'x' while an image is in the
green box shown on the screen and it will recalibrate to 
that and update the 'hist_for_tracking.png' .  You also need something to overlay. replace
'video1.mp4' with what ever video or image you want to overlay on the tracked object.
I can show you how to use this program if you're
looking for this type of application.  Its just a basic demo
'''
#need sys import to use any no python env files like common.py
import sys
sys.path.append('/home/jared/PythonWork/opencv')
import cv2 #NOTE: this is from OpenCV 
import numpy as np

#get video frame
frame = cv2.VideoCapture(0)

def read_overlay():
    vid = cv2.VideoCapture('video1.mp4')
    return vid


while (True):
    #get pic to be used as tracking histogram
    roi = cv2.imread('hist_for_tracking.png')
    search_hsv = cv2.cvtColor(roi,cv2.COLOR_BGR2HSV)
    
    #get next video frame
    check, img = frame.read()

    #this try/except if is used to start the overlay video, and keep looping it
    try:
        check2, track_img = vid.read()
    except:
        vid = read_overlay()
        check2, track_img = vid.read()
    if check2 == False:
        vid = read_overlay()
        check2, track_img = vid.read()

    #when check2 == False, the vid is over.
    find_hsv = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
    
    #calculate histogram of color to look for
    #calcHist([image],[channel],mask,[histogram bin count(256 full)],range(256 full))
    roihist = cv2.calcHist([search_hsv],[0,1], None, [50,256], [0,180,0,256] )
    #ORIGINAL:
    #roihist = cv2.calcHist([search_hsv],[0,1], None, [180,256], [0,180,0,256] )

    
    # normalize histogram and apply backprojection
    cv2.normalize(roihist,roihist,0,255,cv2.NORM_MINMAX)
    dst = cv2.calcBackProject([find_hsv],[0,1],roihist,[0,180,0,256],1)
    
    # Now convolute with circular disc
    #--not sure what that means
    disc = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))
    cv2.filter2D(dst,-1,disc,dst)

    #Find all the blobs that match tracked color
    #using dst as input will be looking for black and white as dst has no color
    contours, hier = cv2.findContours(dst,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)

    #determine which contour is the largest
    big_area = 0
    for shape in contours:
        check = cv2.contourArea(shape)
        if check > big_area:
            #set new biggest area
            big_area = cv2.contourArea(shape)
            #identify largest shape so that x,y is known
            big_shape = shape
            
    if big_shape.any():
        if 10<cv2.contourArea(big_shape):
            #determine shape of a rectangle that would enclose the obj
            (x,y,w,h) = cv2.boundingRect(big_shape)
            #read image to be displayed
            if check2==True:
                pic = track_img
                #resize image based on boundingRect() coordinates
                new_dimensions = (int(w),int(h))
                new_pic = cv2.resize(pic,new_dimensions,interpolation=cv2.INTER_AREA)
                img[y:y+h,x:x+w]=new_pic
            
        if check2 == False:
            vid.release()
        
           
       
    # threshold and binary AND
    ret,thresh = cv2.threshold(dst,50,255,0)
    thresh = cv2.merge((thresh,thresh,thresh))
    resb = cv2.bitwise_and(img, thresh)
    cv2.imshow('color_select',resb)
    
    
    #put rectangle on screen where screen shot will grab from
    cv2.rectangle(img,(250,200),(350,300),(0,255,0),2)
    cv2.imshow('live',img)
    
    ScreenShot = cv2.waitKey(25)& 0xFF
    if ScreenShot == ord('x'):
        #if 'x' is pressed
        #displays a screen shot of image in rectangle
        #saves it for use in histogram[y:y,x:x]
        cv2.imshow('Color2Track',img[200:300,250:350])
        cv2.imwrite('hist_for_tracking.png',img[200:300,250:350])
        
    if cv2.waitKey(25) &0xFF== ord('q'):
        #when everything done, release the capture
        frame.release()
        cv2.destroyAllWindows()
        break
