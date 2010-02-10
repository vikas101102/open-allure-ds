# Adapted from http://wiki.showmedo.com/index.php/PythonArellanoPyGameSeries
#
# scriptedfun.com
#
# Screencast #4
# Arinoid - The Ball
#

import math, os, pygame
from pygame.locals import *

SCREENRECT = Rect(0, 0, 640, 480)

def paddleimage(spritesheet):
    paddle = pygame.Surface((6, 31)).convert()
    #paddle = pygame.Surface((27, 11)).convert()
    # left half
    #paddle.blit(spritesheet.imgat((261, 143, 27, 11)), (0, 0))
    # right half
    #paddle.blit(spritesheet.imgat((289, 143, 28, 11)), (27, 0))
    paddle.blit(spritesheet.imgat((319, 417, 6, 31)), (0, 0))
    paddle.set_colorkey(paddle.get_at((0, 0)), RLEACCEL)
    return paddle

class Spritesheet:
    def __init__(self, filename):
        self.sheet = pygame.image.load(os.path.join('data', filename)).convert()
    def imgat(self, rect, colorkey = None):
        rect = Rect(rect)
        image = pygame.Surface(rect.size).convert()
        image.blit(self.sheet, (0, 0), rect)
        if colorkey is not None:
            if colorkey is -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, RLEACCEL)
        return image
    def imgsat(self, rects, colorkey = None):
        return [self.imgat(rect, colorkey) for rect in rects]

class Arena:
    tileside = 31
    numxtiles = 12
    numytiles = 14
    #topx = (SCREENRECT.width - SCREENRECT.width/tileside*tileside)/2
    #topy = (SCREENRECT.height - SCREENRECT.height/tileside*tileside)/2
    #rect = Rect(topx + tileside, topy + tileside, tileside*numxtiles, tileside*numytiles)
    topx=640
    topy=480
    rect=Rect(0,0,640,480)
    def __init__(self):
        self.background = pygame.Surface(SCREENRECT.size).convert()
    def drawtile(self, tile, x, y):
        self.background.blit(tile, (self.topx + self.tileside*x,    \
                                    self.topy + self.tileside*y))
    def makebg(self, tilenum):
        for x in range(self.numxtiles):
            for y in range(self.numytiles):
                self.drawtile(self.tiles[tilenum], x + 1, y + 1)

class Paddle(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.rect = self.image.get_rect()
        #self.rect.bottom = self.arena.rect.bottom - self.arena.tileside
    def update(self):
        self.rect.centerx = 7
        self.rect.centery = pygame.mouse.get_pos()[1]
        self.rect.clamp_ip(self.arena.rect)

class Paddle2(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.rect = self.image.get_rect()
        #self.rect.bottom = self.arena.rect.bottom - self.arena.tileside
    def update(self):
        self.rect.centerx = self.arena.rect.right - self.rect.width
        self.rect.centery = pygame.mouse.get_pos()[1]
        self.rect.clamp_ip(self.arena.rect)

class Ball(pygame.sprite.Sprite):
    speed = 6
##    angleleft = 135
##    angleright = 45
    angleup = 45
    angledown = -45
    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.rect = self.image.get_rect()
        self.update = self.start
    def start(self):
        self.rect.centery = self.paddle.rect.centery
        self.rect.left = self.paddle.rect.right
        if pygame.mouse.get_pressed()[0] == 1:
            self.setfp()
            self.dx = 6
            self.dy = 0
            self.update = self.move
    def setfp(self):
        self.fpx = float(self.rect.centerx)
        self.fpy = float(self.rect.centery)
    def setint(self):
        self.rect.centerx = int(self.fpx)
        self.rect.centery = int(self.fpy)
    def move(self):
        #
        # Ball-Paddle Physics
        # - there are 2 extreme ball-paddle
        #   collision scenarios:
        #
        #
        # Scenario 1 - right edge
        #
        #            bbb
        #   pppppppppp
        #
        # - in this scenario, the left edge
        #   of the ball is at paddle.rect.right
        #
        #
        # Scenario 2 - left edge
        #
        # bbb
        #   pppppppppp
        #
        # - here, the left edge of the ball is
        #   (ball.rect.width - 1) units away from
        #   the paddle.rect.left, which means that
        #   the left edge of the ball is at
        #   (paddle.rect.left - (ball.rect.width - 1))
        #
        #
        # Hence, we want the linear function that
        # will determine the ball angle to contain
        # (paddle.rect.right, angler) and
        # (paddle.rect.left - (ball.rect.width - 1), anglel).
        #
        if self.rect.colliderect(self.paddle.rect): # and self.dx > 0:
            x1 = self.paddle.rect.top
            y1 = self.angleup
            x2 = self.paddle.rect.bottom # - (self.rect.height - 1)
            y2 = self.angledown
            y = self.rect.centery
            offset = self.paddle.rect.centery - y
            m = float(y1 - y2)/(x2 - x1) # degrees per pixel of paddle
            x = m*offset
            #print self.__dict__.items()
            print "hit1", self.paddle.rect, self.rect
            angle = math.radians(x)
            #print m, offset, x, angle, math.cos(angle), math.sin(angle)
            self.dx = self.speed*math.cos(angle)
            self.dy = -self.speed*math.sin(angle)
            print self.dx, self.dy

        if self.rect.colliderect(self.paddle2.rect): # and self.dx > 0:
            x1 = self.paddle2.rect.top
            y1 = self.angleup
            x2 = self.paddle2.rect.bottom # - (self.rect.height - 1)
            y2 = self.angledown
            y = self.rect.centery
            offset = self.paddle2.rect.centery - y
            m = float(y1 - y2)/(x2 - x1) # degrees per pixel of paddle
            x = m*offset
            #print self.__dict__.items()
            print "hit2", self.paddle2.rect, self.rect
            angle = math.radians(x)
            print m, offset, x, angle, math.cos(angle), math.sin(angle)
            self.dx = -self.speed*math.cos(angle)
            self.dy = -self.speed*math.sin(angle)
            print self.dx, self.dy

        self.fpx = self.fpx + self.dx
        self.fpy = self.fpy + self.dy
        self.setint()
        #print self.paddle.rect.centery - self.rect.centery

        if not self.arena.rect.contains(self.rect):
            if self.rect.left < self.arena.rect.left or \
               self.rect.right > self.arena.rect.right:
                print "die", self.paddle.rect, self.paddle2.rect, self.rect
                self.kill()
            else:
                if self.rect.top < self.arena.rect.top:
                    self.dy = -self.dy
                if self.rect.bottom > self.arena.rect.bottom:
                    self.dy = -self.dy
                self.rect.clamp_ip(self.arena.rect)
                self.setfp()

def main():
    pygame.init()

    screen = pygame.display.set_mode(SCREENRECT.size)

    spritesheet = Spritesheet('arinoid_master.bmp')

    Arena.tiles = spritesheet.imgsat([(129, 321, 31, 31),   # purple - 0
                                      (161, 321, 31, 31),   # dark blue - 1
                                      (129, 353, 31, 31),   # red - 2
                                      (161, 353, 31, 31),   # green - 3
                                      (129, 385, 31, 31)])  # blue - 4

    Paddle.image = Paddle2.image = paddleimage(spritesheet)
    Ball.image = spritesheet.imgat((428, 300, 11, 11), -1)

    # make background
    arena = Arena()
    arena.makebg(0) # you may change the background color here
    screen.blit(arena.background, (0, 0))
    pygame.display.update()

    Paddle.arena = Paddle2.arena = arena
    Ball.arena = arena

    # keep track of sprites
    balls = pygame.sprite.Group()
    all = pygame.sprite.RenderUpdates()

    Paddle.containers = Paddle2.containers = all
    Ball.containers = all, balls
    print dir(Paddle)

    # keep track of time
    clock = pygame.time.Clock()

    paddle = Paddle()
    paddle2 = Paddle2()
    print all

    Ball.paddle = paddle
    Ball.paddle2 = paddle2
    # game loop
    while 1:

        # get input
        for event in pygame.event.get():
            if event.type == QUIT   \
               or (event.type == KEYDOWN and    \
                   event.key == K_ESCAPE):
                return
            if event.type == KEYDOWN and event.key == K_b: Ball()

        # clear sprites
        all.clear(screen, arena.background)

        # update sprites
        all.update()

        #if not balls:
        #    Ball()

        # redraw sprites
        dirty = all.draw(screen)
        pygame.display.update(dirty)

        # maintain frame rate
        clock.tick(60)

if __name__ == '__main__': main()