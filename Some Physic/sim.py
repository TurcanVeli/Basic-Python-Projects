

import time

import pygame 
import math
import random

pygame.init()  
size = (WIDTH,WEIGHT) = (500,500)
screen = pygame.display.set_mode(size)
pygame.display.set_caption('Engine')
FPS = pygame.time.Clock()

GRAVITY = (math.pi, 0.02)
drag = 0.99
# f = m*a
# potenial energy = m.g.h  = 1/2*m*v^2
# gravity = pygame.math.Vector2(0,1)


def addVectors(v1 : tuple, v2: tuple):
    x  = math.sin(v1[0]) * v1[1]  + math.sin(v2[0]) * v2[1]
    y  = math.cos(v1[0]) * v1[1]  + math.cos(v2[0]) * v2[1]
    angle = 0.5 * math.pi - math.atan2(y, x)
    length  = math.hypot(x, y)

    return (angle, length)

def collide(p1:object, p2: object):
    dx = abs(p2.x - p1.x)    
    dy = abs(p2.y - p1.y)
    pygame.draw.line(screen,(0,0,255), (p1.x,p1.y),(p1.x+ dx, p1.y+ dy) )
    distance  = math.hypot(dx,dy)
    
    if distance  <= p2.size + p1.size:
        tangent = math.atan2(dy, dx)
        p1.angle = 2 * tangent - p1.angle
        p2.angle = 2 * tangent - p2.angle
        (p1.speed, p2.speed) = (p2.speed, p1.speed)
        p1.speed *= p1.elasticy
        p2.speed *= p2.elasticy
        angle = 0.5 * math.pi + tangent
        p1.x += math.sin(angle)
        p1.y += math.cos(angle)
        p2.x += math.sin(angle)
        p2.y += math.cos(angle)


def hold( pos1: tuple, particle_list ):
    pass




class particles():
    def __init__(self):
        self.size     = random.randint(5,32)
        self.x        = random.randint(self.size, 500-self.size)
        self.y        = random.randint(self.size, 500-self.size)
        self.elasticy = 0.75
        self.color    = (255,255,255) # White
        #these two varables presents vector of particles
        self.speed    = random.random() #Velocity of Particle
        self.angle    = random.uniform(0, math.pi*2) #Direction of particle
    
    def _display(self,screen):
        pygame.draw.circle(screen, self.color, (self.x,self.y), self.size)

    def _move(self):
        #print("Radians ", self.angle, " Hız ", self.speed)
        (self.angle,self.speed) = addVectors((self.angle,self.speed), GRAVITY)
        
        dx = math.sin(self.angle) * self.speed
        dy = math.cos(self.angle) * self.speed

        self.x += dx
        self.y -= dy   


    def bounce(self):
        
        if self.x > 500 - self.size:
            self.x = 2*(500 - self.size) - self.x
            self.angle = - self.angle
            self.speed *= self.elasticy
        
        elif self.x < self.size:
            self.x = 2*self.size - self.x
            self.angle = - self.angle
            self.speed *= self.elasticy

        if self.y > 500 - self.size:
            self.y = 2*(500 - self.size) - self.y
            self.angle = math.pi - self.angle
            self.speed *= self.elasticy

        elif self.y < self.size:
            self.y = 2*self.size - self.y
            self.angle = math.pi - self.angle
            self.speed *= self.elasticy
        


done = False
particle_list = list()
particle_numbers = 3
for i in range(particle_numbers):
    particle_list.append(particles())

selected_p = None
while not done:
    
    screen.fill((0,0,0))  
    for event in pygame.event.get():  
        if event.type == pygame.QUIT:  
            done = True  
        if event.type == pygame.MOUSEBUTTONDOWN:
            (mouseX, mouseY) = pygame.mouse.get_pos()
            print((mouseX,mouseY))

    for index,i in enumerate(particle_list):
        if selected_p != i:
            i._move()
            i.bounce()
            i._display(screen)
        
        for j in particle_list[index+1:]:
            collide(i,j)

    pygame.display.update()

FPS.tick(60)
pygame.display.flip()  
pygame.quit()