import pygame

pygame.init()

# Screen size
screen = pygame.display.set_mode((900,400))
# Player
player1 = pygame.image.load('pygame/newcar1.png')
X1, Y1 = 50, 50
player2 = pygame.image.load('pygame/newcar2.png')
X2, Y2 = 50, 150

stop = 650

def player(player, point):
    screen.blit(player, point)

running = True
while running:

    # RGB = R,G,B
    screen.fill((255,0,0))

    # X1 +=0.1
    # print()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            print('A key stroke')
            if event.key == pygame.K_LEFT:
                X1 += 15
                print('Left press')
            if event.key == pygame.K_RIGHT:
                X2 += 15
                print('Right press')
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                print('Key release')

    if X1 >= stop:
        X1 = stop
    if X2 >= stop:
        X2 = stop

    player(player1, (X1,Y1))
    player(player2, (X2,Y2))
    pygame.display.update()