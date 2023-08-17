from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
import cv2
import os


class svgTopng():
    """
    Represents a selectable options to convert svg files to png.
    png images are directly as black and white. 
    if the blackness is more than 50% for each pixel, it is considered as black.
    
    Attributes
    ----------
    
    Input_path::class:`str`
        the path of svgs folder
    
    Output_Folder: :class:`str` 
        the name of output folder name
        
        default = OutputPngs
    
    width: :class:`int`
        width of png
        
        default  = 10000
    
    height: :class:`int`
        height of png
        
        default  = 10000
    

    """
    def __init__(self, Input_path:str, Output_Folder:str = "OutputPngs", width:int = 10000, height:int = 10000) -> None:
        self.path = Input_path
        self.dim = (width,height)
        self.Output_Folder = Output_Folder
        self.__create_outputFolder()
        self.__Create_png()
        

    def __create_outputFolder(self) -> None:
        """Create output folder at your directory"""
        cwd = os.getcwd()
        self.dir_sep = os.path.sep
        try :
            os.mkdir(cwd + self.dir_sep + self.Output_Folder)
        except FileExistsError:
            print("Folder is already exist.")
        self.outputFolder_path  = cwd + self.dir_sep + self.Output_Folder

    def __Create_png(self) -> None:
        """Takes all svg files and convert each to png files"""
        AllSvgs = os.listdir(self.path)
        for svg in AllSvgs:
           
            self.pngFileName = svg.strip(".svg")
            self.svgpath = self.path + self.dir_sep + self.pngFileName
            self.output_path = self.outputFolder_path + self.dir_sep + self.pngFileName + ".png"
            self.fmt_png(self.path+self.dir_sep+svg)
            self._cnvrtTobinary()

    def fmt_png(self,img_path, fmt="PNG", dpi=72, bg=0xffffff) -> None:
        """Convert SVG to ReportLab drawing.""" 
        png_image = svg2rlg(img_path)
        renderPM.drawToFile(png_image,self.output_path, fmt=fmt, dpi=dpi, bg=bg)

        
    def _cnvrtTobinary(self) -> None:
        """Apply Thres binary each png files and write specified folder"""
        img=cv2.imread(self.output_path) #read image
        img = cv2.resize(img, self.dim)
        retval,b_img = cv2.threshold(img, 125, 255, cv2.THRESH_BINARY)
        os.remove(self.output_path)
        cv2.imwrite(self.output_path, b_img)



    

    
    

