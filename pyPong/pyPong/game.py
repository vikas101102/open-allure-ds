"""
game.py
a component of pyPong.py

Defines the ball and paddle sprites, arena and event loop for pyPong.

Copyright (c) 2010 John Graves
MIT License: see LICENSE.txt
"""
# Adapted from http://wiki.showmedo.com/index.php/PythonArellanoPyGameSeries
#
# scriptedfun.com
#
# Screencast #4
# Arinoid - The Ball
#

class Game(object):
    """
    This class encapsulates the functionality of a game like Pong(R)
    with two paddles bouncing a ball from one side to the other.

    TODO: Scoring and sound
    """
    import pygame

    class Spritesheet:
        """
        Gets a small image from a larger bitmap containing an inventory of images.
        """
        def __init__(self, filename):
            import pygame, os
            self.sheet = pygame.image.load(os.path.join('data', filename)).convert()
        def imgat(self, rect, colorkey = None):
            """
            Returns an image at the location and size specified by a rectangle (top x1, left y1, x2 width, y2 height).
            """
            import pygame
            rect = pygame.rect.Rect(rect)
            image = pygame.Surface(rect.size).convert()
            image.blit(self.sheet, (0, 0), rect)
            if colorkey is not None:
                if colorkey is -1:
                    colorkey = image.get_at((0, 0))
                image.set_colorkey(colorkey, pygame.RLEACCEL)
            return image
        def imgsat(self, rects, colorkey = None):
            """
            Returns image sequence at the locations and sizes specified by a list of rectangles (top x1, left y1, x2 width, y2 height).
            """
            return [self.imgat(rect, colorkey) for rect in rects]

    class Arena:
        """
        Defines the playing area of the game.
        """
        import pygame

##        tileside = 31
##        numxtiles = 12
##        numytiles = 14
        #topx = (SCREENRECT.width - SCREENRECT.width/tileside*tileside)/2
        #topy = (SCREENRECT.height - SCREENRECT.height/tileside*tileside)/2
        #rect = Rect(topx + tileside, topy + tileside, tileside*numxtiles, tileside*numytiles)
        topx=640
        topy=480
        rect=pygame.rect.Rect(0,0,640,480)
        def __init__(self):
            import pygame
            self.background = pygame.Surface(self.rect.size).convert()
##        def drawtile(self, tile, x, y):
##            self.background.blit(tile, (self.topx + self.tileside*x,    \
##                                        self.topy + self.tileside*y))
##        def makebg(self, tilenum):
##            for x in range(self.numxtiles):
##                for y in range(self.numytiles):
##                    self.drawtile(self.tiles[tilenum], x + 1, y + 1)

    class Paddle(pygame.sprite.Sprite):
        """
        Defines the left paddle
        """
        def __init__(self):
            import pygame
            pygame.sprite.Sprite.__init__(self, self.containers)
            self.rect  = self.image.get_rect()
            #self.rect.bottom = self.arena.rect.bottom - self.arena.tileside
        def update(self):
            """
            Locks the left paddle center to column 7 while the row is determined by a signal from the webcam
            """
            import pygame
            self.rect.centerx = 7
##            self.rect.centery = pygame.mouse.get_pos()[1]
            self.rect.centery = signal[0]
            self.rect.clamp_ip(self.arena.rect)

    class Paddle2(pygame.sprite.Sprite):
        """
        Defines the right paddle
        """
        def __init__(self):
            import pygame
            pygame.sprite.Sprite.__init__(self, self.containers)
            self.rect  = self.image.get_rect()
            #self.rect.bottom = self.arena.rect.bottom - self.arena.tileside
        def update(self):
            """
            Locks the left paddle center a column close to right edge of arena while the row is determined by a signal from the webcam
            """
            import pygame
            self.rect.centerx = self.arena.rect.right - self.rect.width
##            self.rect.centery = pygame.mouse.get_pos()[1]
            self.rect.centery = signal[1]
            self.rect.clamp_ip(self.arena.rect)

    class Ball(pygame.sprite.Sprite):
        """
        Defines the ball
        """
        speed = 6
    ##    angleleft = 135
    ##    angleright = 45
        angleup = 45
        angledown = -45
        def __init__(self):
            import pygame
            pygame.sprite.Sprite.__init__(self, self.containers)
            self.rect  = self.image.get_rect()
            self.update = self.start
        def start(self):
            """
            Starts the ball adjacent to the center of the left paddle
            """
            import pygame
            #TODO: Start a different place depending on which side serves next
            self.rect.centery = self.paddle.rect.centery
            self.rect.left = self.paddle.rect.right
##            if pygame.mouse.get_pressed()[0] == 1:
            if True:
                self.setfp()
                self.dx = 6
                self.dy = 0
                self.update = self.move
        def setfp(self):
            """
            Set floating point location
            """
            self.fpx = float(self.rect.centerx)
            self.fpy = float(self.rect.centery)
        def setint(self):
            """
            Set integer location
            """
            self.rect.centerx = int(self.fpx)
            self.rect.centery = int(self.fpy)
        def move(self):
            """
            Calculate movement of ball, based on collisions with paddles and sides of arena.
            """
            import math
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
                #print "hit1", self.paddle.rect, self.rect
                angle = math.radians(x)
                #print m, offset, x, angle, math.cos(angle), math.sin(angle)
                self.dx = self.speed*math.cos(angle)
                self.dy = -self.speed*math.sin(angle)
                #print self.dx, self.dy
                # TODO: Add sound effect here

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
                #print "hit2", self.paddle2.rect, self.rect
                angle = math.radians(x)
                #print m, offset, x, angle, math.cos(angle), math.sin(angle)
                self.dx = -self.speed*math.cos(angle)
                self.dy = -self.speed*math.sin(angle)
                #print self.dx, self.dy
                # TODO: Add sound effect here

            self.fpx = self.fpx + self.dx
            self.fpy = self.fpy + self.dy
            self.setint()
            #print self.paddle.rect.centery - self.rect.centery

            if not self.arena.rect.contains(self.rect):
                if self.rect.left < self.arena.rect.left or \
                   self.rect.right > self.arena.rect.right:
                    #print "die", self.paddle.rect, self.paddle2.rect, self.rect
                    self.kill()
                    # TODO: Add score keeping and change of serve here
                else:
                    if self.rect.top < self.arena.rect.top:
                        self.dy = -self.dy
                        # TODO: Add sound effect here
                    if self.rect.bottom > self.arena.rect.bottom:
                        self.dy = -self.dy
                        # TODO: Add sound effect here
                    self.rect.clamp_ip(self.arena.rect)
                    self.setfp()

    def __init__(self):
        import pygame
        import video
        import gesture

        global signal

        SCREENRECT = pygame.rect.Rect(0, 0, 640, 480)

        pygame.init()

        screen = pygame.display.set_mode(SCREENRECT.size)

        spritesheet = self.Spritesheet('arinoid_master.bmp')

##        Arena.tiles = spritesheet.imgsat([(129, 321, 31, 31),   # purple - 0
##                                          (161, 321, 31, 31),   # dark blue - 1
##                                          (129, 353, 31, 31),   # red - 2
##                                          (161, 353, 31, 31),   # green - 3
##                                          (129, 385, 31, 31)])  # blue - 4
        def paddleimage(spritesheet):
            paddle = pygame.Surface((12, 61)).convert()
            #paddle = pygame.Surface((27, 11)).convert()
            # left half
            #paddle.blit(spritesheet.imgat((261, 143, 27, 11)), (0, 0))
            # right half
            #paddle.blit(spritesheet.imgat((289, 143, 28, 11)), (27, 0))
            paddle.blit(spritesheet.imgat((312, 413, 12, 61)), (0, 0))
            paddle.set_colorkey(paddle.get_at((0, 0)), pygame.RLEACCEL)
            return paddle

        self.Paddle.image = self.Paddle2.image = paddleimage(spritesheet)
        self.Ball.image = spritesheet.imgat((483, 420, 27, 25), -1)

        # make background
        arena = self.Arena()
##        arena.makebg(0) # you may change the background color here
        screen.blit(arena.background, (0, 0))
        pygame.display.update()

        self.Paddle.arena = self.Paddle2.arena = arena
        self.Ball.arena = arena

        # keep track of sprites
        balls = pygame.sprite.Group()
        all = pygame.sprite.RenderUpdates()

        self.Paddle.containers = self.Paddle2.containers = all
        self.Ball.containers = all, balls

        # keep track of time
        clock = pygame.time.Clock()

        paddle = self.Paddle()
        paddle2 = self.Paddle2()

        self.Ball.paddle = paddle
        self.Ball.paddle2 = paddle2

        greenScreen = video.GreenScreen()
        vcp         = video.VideoCapturePlayer(processFunction=greenScreen.process)
        gesture     = gesture.Gesture()
        showFlag    = True
        signal      = lastSignal = (0,0)

        # game loop
        while 1:

            # get input
            for event in pygame.event.get():
                if event.type == pygame.QUIT   \
                   or (event.type == pygame.KEYDOWN and    \
                       event.key == pygame.K_ESCAPE):
                    return
                if event.type == pygame.KEYDOWN and \
                   event.key == pygame.K_b: self.Ball()
                if event.type == pygame.KEYDOWN and \
                   event.key == pygame.K_s:
                        screen.blit(arena.background, (0, 0))
                        pygame.display.update()
                        showFlag = not showFlag
                if event.type == pygame.KEYDOWN and \
                   event.key == pygame.K_r:
                        greenScreen.calibrated = False

            # check webcam
            processedImage = vcp.get_and_flip(show=showFlag)
            lastSignal = signal
            signal = gesture.countWhitePixels(processedImage)
##            if abs(signal[0] - lastSignal[0]) > 20 or \
##               abs(signal[1] - lastSignal[0]) > 20: signal=lastSignal
            #print signal

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

#    if __name__ == '__main__': main()