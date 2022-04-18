import math
import cvzone
import cv2
import numpy as np
from cvzone.HandTrackingModule import HandDetector
from numpy import random


cam=cv2.VideoCapture(0)
cam.set(3,1280)
cam.set(4,720)

detector=HandDetector(detectionCon=0.8,maxHands=1)

class SnakeGameClass:
    def __init__(self,pathFood) :
        #snake attributes
        self.points = [] 
        self.lengths = []
        self.currentLength = 0
        self.allowedLength = 150
        self.previousHead = 0 , 0
        #food attributes
        self.imgFood=cv2.imread(pathFood,cv2.IMREAD_UNCHANGED)
        self.hFood,self.wFood, _ =self.imgFood.shape
        self.foodPoint= 0 , 0
        self.randomFoodLocation()
        # score attributes
        self.score=0
        self.GameOver=False
    def randomFoodLocation(self):
        self.foodPoint=random.randint(100,1000),random.randint(100,600)

    #draw line
    def update(self,imgMain,currentHead):
        if self.GameOver:
            cvzone.putTextRect(imgMain,"Game Over!!!",[300,400],scale=7,thickness=5,offset=20)
            cvzone.putTextRect(imgMain,f'Score:{self.score}',[450,500],scale=7,thickness=7,offset=20)
        else:
            cvzone.putTextRect(imgMain,f'Score:{self.score}',[30,80],scale=3,thickness=3,offset=10)
            px , py = self.previousHead
            cx , cy = currentHead


            self.points.append([ cx , cy ])
            distance=math.hypot( cx - px , cy - py )
            self.lengths.append( distance )
            self.currentLength += distance
            self.previousHead= cx , cy

            #length control
            if self.currentLength>self.allowedLength:
                for i,length in enumerate(self.lengths):
                    self.currentLength-=length
                    self.lengths.pop(i)
                    self.points.pop(i)
                    if self.currentLength<self.allowedLength:
                        break
            #check eat condition
            rx , ry =self.foodPoint
            if (rx-self.wFood//2<cx<rx+self.wFood//2 and ry-self.hFood//2<cy<ry+self.hFood//2):
                self.randomFoodLocation()
                self.allowedLength+=50
                self.score+=1
                print(self.score)

        #Draw snake function
            if self.points:
                for i,point in enumerate(self.points):
                    if i!=0:
                        cv2.line(imgMain,self.points[i-1],self.points[i],(0,0,200),20)
                cv2.circle( imgMain , self.points[-1] , 20 , ( 0,200,0) , cv2.FILLED )
            #Draw Food
            rx,ry=self.foodPoint
            imgMain=cvzone.overlayPNG(imgMain,self.imgFood,(rx-self.wFood//2,ry-self.hFood//2),)
        
            #check for collision
            pts=np.array(self.points[:-2],np.int32)
            pts=pts.reshape((-1,1,2))
            cv2.polylines(imgMain,[pts],False,(0,200,0),3)
            minDist=cv2.pointPolygonTest(pts,(cx,cy),True)
            if(-0.5<=minDist<=0.5):
                print("Hit!!!")
                #reset attributes
                self.GameOver=True
                self.points = [] 
                self.lengths = []
                self.currentLength = 0
                self.allowedLength = 150
                self.previousHead = 0 , 0
                
            print(minDist)
       
        return imgMain

game=SnakeGameClass("Donut (1).png")


while True:
    success , img = cam.read()
    img = cv2.flip( img , 1 )
    hands , img=detector.findHands( img , flipType=False )
    if hands:
        lmlist=hands[0]['lmList']
        pointIndex=lmlist[ 8 ][ 0 : 2 ]
        img=game.update(img,pointIndex)

    cv2.imshow( "image" , img )
    key=cv2.waitKey(1)
    if key==ord('r'):
        game.GameOver=False
        game.score=0
