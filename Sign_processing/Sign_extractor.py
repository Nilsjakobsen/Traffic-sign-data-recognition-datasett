import cv2
import numpy as np
from pathlib import Path

#Class for handling color detection, it detcts red, yellow and white. 
#Then it it takes the HSV image and generates it into two black and white masks.
#It creates one for red border and one for yellow or white center.
class HSVColorMask:
    def __init__(self):
        self.red1=(np.array([0, 90, 90]), np.array([10, 255, 255]))
        self.red2=(np.array([170, 90, 90]), np.array([179, 255, 255]))
        self.yellow=(np.array([15, 80, 100]), np.array([40,  255, 255])) 
        self.white= (np.array([0,0,180]),np.array([179,60,255]))
        self.subsign_yellow=(np.array([25, 150, 150]), np.array([35, 255, 255]))


    def get_masks(self, hsv):
        red = cv2.inRange(hsv, *self.red1) |  cv2.inRange(hsv, *self.red2)
        yellow = cv2.inRange(hsv, *self.yellow)
        white= cv2.inRange(hsv, *self.white)

        k =cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        
        red  = cv2.morphologyEx(red, cv2.MORPH_CLOSE, k, iterations=2)
        yellow = cv2.morphologyEx(yellow, cv2.MORPH_CLOSE,  k, iterations=1)
        white= cv2.morphologyEx(white,  cv2.MORPH_CLOSE, k, iterations=1)
        
        red_edge= cv2.bitwise_and(red, cv2.bitwise_not(yellow))
        red_edge= cv2.bitwise_and(red, cv2.bitwise_not(white))
        red_edge =cv2.morphologyEx(red_edge, cv2.MORPH_ERODE, k, iterations=1)

        center_of_sign= cv2.bitwise_or(yellow, white)
        return red_edge, center_of_sign

#CLass for filtering logical sign shapes based on apect ratio and area.
class Geometry_finder:
    def __init__(self, minimum_area=80*80, max_aspect_ratio=2.0): # størrelsen på utkippene 
        self.min_area = minimum_area
        self.max_aspect_ratio = max_aspect_ratio

    def plausible(self,Shape_edge):
        x, y, w, h = cv2.boundingRect(Shape_edge)
        if w * h <  self.min_area:
            return False
        ar = max(w, h) / max(1, min(w, h))
        return ar  <= self.max_aspect_ratio
    
    def is_rectangular(self, Shape_edge, min_area=700):
        area = cv2.contourArea(Shape_edge)
        if area < min_area:
            return False
        
        rect = cv2.minAreaRect(Shape_edge)
        w, h = rect[1]
        if w == 0 or h == 0:
            return False
        
        ar = max(w, h) / max(1, min(w, h))
        if not (2.3 <= ar <= 6.0):
            return False
        
        rect_area = w * h
        fill_ratio = area / rect_area if rect_area > 0 else 0
        return fill_ratio > 0.72
    
#Class for extracting signs from start to  finish.
class Sign_extractor_class:
    def __init__(self, image_path, output_dir, padding=6):
        self.image_path= Path(image_path)
        self.output_dir =  Path(output_dir)
        self.padding =  padding
        self.color_mask = HSVColorMask( )
        self.geometry =Geometry_finder()

    def save_crop(self, img, bbox, idx):
        image_height, image_width =  img.shape[:2]
        left, top, width  ,height = bbox

        crop_left =max(0,  left-self.padding)
        crop_top=max(0, top-self.padding)
        crop_right=min(image_width, left+width+self.padding)
        crop_bottom= min(image_height, top+height+self.padding)
        cropped_img= img[crop_top:crop_bottom,  crop_left:crop_right]


        d =self.output_dir
        base = f"{self.image_path.stem}_{idx:03d}"
        cv2.imwrite(str (d/f"{base}.png"), cropped_img)
        return 1



    def extract_signs(self, min_center_frac=0.05, 
                      min_redrim_frac=0.05):
        
        
        img=cv2.imread(str(self.image_path))
        hsv=cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        red_edge, center = self.color_mask.get_masks(hsv)
        Shape_edge, _ = cv2.findContours(red_edge, cv2.RETR_EXTERNAL,  cv2.CHAIN_APPROX_SIMPLE)
        saved = []

        
        for i, c in enumerate(Shape_edge):
            if not self.geometry.plausible(c):
                continue
            x, y, w, h =cv2.boundingRect(cv2.convexHull(c))
            r=red_edge[y:y+h, x:x+w]
            c= center[y:y+h, x:x+w]

            if (c > 0).mean() < min_center_frac or (r > 0).mean()  < min_redrim_frac:
                continue
            
            saved.append(self.save_crop(img,  (x, y, w, h), i))
        
        saved.extend(self.extract_subsigns(img, hsv))
        return saved

    def extract_subsigns(self, img, hsv):
        subsign_yellow = cv2.inRange(hsv, *self.color_mask.subsign_yellow)
        k = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        subsign_yellow = cv2.morphologyEx(subsign_yellow, cv2.MORPH_CLOSE, k, iterations=3)
        contours, _ = cv2.findContours(subsign_yellow, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        saved = []
        
        for i, c in enumerate(contours):
            if self.geometry.is_rectangular(c):
                rect = cv2.minAreaRect(c)
                box = cv2.boxPoints(rect)
                box = np.intp(box)
                
                mask = np.zeros(subsign_yellow.shape, dtype=np.uint8)
                cv2.drawContours(mask, [box], 0, 255, -1)
                
                masked_yellow = cv2.bitwise_and(subsign_yellow, mask)
                yellow_pixels = np.sum(masked_yellow > 0)
                total_pixels = np.sum(mask > 0)
                yellow_ratio = yellow_pixels / total_pixels if total_pixels > 0 else 0
                
                if yellow_ratio > 0.40:
                    x, y, w, h = cv2.boundingRect(c)
                    saved.append(self.save_crop(img, (x, y, w, h), 900 + i))
        return saved
     
