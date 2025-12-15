import os
import pytesseract
import glob
from PIL import Image
from pdf2image import convert_from_path
import cv2


#This class checks if two images match using ORB. 
#All pages from the .pdf is saved as .jpg
#Then we use this ORB class to check if the new map matches with previous maps saved as .jpg
class ORB_maps:
    def __init__(self,  nfeatures, ratio, min_good):
        self.nfeatures= nfeatures
        self.ratio= ratio
        self.min_good= min_good

    def preprocess_image(self, image_path):
        img =  cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        return img 

    def matches(self, img1_path, img2_path) -> bool:
        img1 = self.preprocess_image(img1_path)
        img2 = self.preprocess_image(img2_path)
        
        
        orb =  cv2.ORB_create(nfeatures=self.nfeatures)
        kp1, des1=orb.detectAndCompute(img1,  None)
        kp2, des2=orb.detectAndCompute(img2, None)

        if des1 is None:
            return  False
        if des2 is None:
            return False
        if len(des1) < 2:
            return False
        if len(des2) < 2:
            return False

        bf =cv2.BFMatcher(cv2.NORM_HAMMING,  crossCheck=False)
        raw =bf.knnMatch(des1,  des2, k=2)

        good = [m for pair in  raw if len(pair)  == 2 for m, n in [pair]
                if m.distance < self.ratio * n.distance]

        return len(good)  >= self.min_good


#This class saves all pages from the .pdf as .jpg
#Then we use OCR to check if there is text on the image of the page
#If there is a lot of text in the image, we exclude it
#If not, we save it as a new map and then uses the ORB class to check if the new map matches with previous maps saved as .jpg
class MapExtractor:
    def __init__(self, orb_matcher, output_dir):
        self.orb=orb_matcher
        self.output_dir=output_dir
        
    
    def check_text_in_pdf(self, image_path):
        img = Image.open(image_path)
        text =pytesseract.image_to_string(img)
        total_chars = len(text)
        if total_chars  > 500:
            return True
        return False

    
    def check_mach_old_map(self, image_path, old_map_path):
        if not os.path.isdir(old_map_path):
            return False

        patterns = [
            os.path.join(old_map_path, "*.jpg"),
        ]
        candidates = []
        for p in patterns:
            candidates.extend(glob.glob(p))

        for old_map in candidates:
            if os.path.abspath(old_map) ==  os.path.abspath(image_path):
                continue
            
            if self.orb.matches(image_path, old_map):
                    
                return True
             

        return False
    
    def pdf_To_image(self, pdf_path):
        pages = convert_from_path(pdf_path, dpi=300)
        for i, page in enumerate(pages, start=1):
            out_path = f"{self.output_dir}/page_{i}.jpg"
            page.save(out_path, "JPEG")

            #Excludes if there is text on the pdf page
            if self.check_text_in_pdf(out_path):
                os.remove(out_path)
                continue

            #Excludes if it match with old maps  
            old_map_dir =self.output_dir  
            if self.check_mach_old_map(out_path, old_map_dir):
                os.remove(out_path)
            
                continue

            
                      
            