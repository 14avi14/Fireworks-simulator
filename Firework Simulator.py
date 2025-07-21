# July 4 firework simulator 
import pygame, sys
import random
import numpy as np
from copy import deepcopy

pygame.init()
screen = pygame.display.set_mode((700, 700))
clock = pygame.time.Clock()

# create trasnperent glwoing circle surf
def circle_surf(radius, color):
    surf = pygame.Surface((radius * 2, radius * 2))
    pygame.draw.circle(surf, color, (radius, radius), radius)
    surf.set_colorkey((0, 0, 0))
    return surf

def draw_text(text, text_size, color, surf, pos):
    font=pygame.font.SysFont(None, text_size, bold=True)
    text_obj = font.render(text, 1, color)
    text_rect = text_obj.get_rect()
    text_rect.center = pos[0], pos[1]

    surf.blit(text_obj, text_rect)



class Firework:
    def __init__(self, start_loc, explosion_time, color, vel):
        self.timer = explosion_time
        self.pos = start_loc
        self.color = color
        self.trail_prtcls = []
        self.vel = vel
        self.slowdown = self.vel[1] / self.timer
        self.explosion = []
    
        
    def move_firework(self):
        self.pos[0] += self.vel[0]
        self.pos[1] -= self.vel[1]
        self.vel[1] -= self.slowdown
    def draw(self, surf):
        radius = 5
        pygame.draw.circle(surf, self.color, self.pos, radius)
        # transparent circle
        color = self.color[0]//15, self.color[1]//15, self.color[2]//15
        for _ in range(10):
            new_r = radius + random.randint(-radius, radius)
            circle = circle_surf(2 * new_r, color)
            pos = self.pos[0] - circle.get_width() / 2, self.pos[1] - circle.get_height() / 2
            surf.blit(circle, pos, special_flags=1)
    
    def create_explosion(self):
        for i in range(80):
            speed = random.randint(4, 10)
            angle = random.uniform(0, 2 * np.pi)
            size = speed / 3 # make the size proportional to the distance it goes out
            self.explosion.append([deepcopy(self.pos), [speed, angle], size])
    
    def update_explosion(self, surf):
        alive = []
        for i, prtcl in enumerate(self.explosion):
            # only start decreasing the size after the speed of the prtcl is less than 1
            if prtcl[1][0] > 1:
                # update speed
                self.explosion[i][1][0] /= 1.05
                
                x_vel = np.cos(self.explosion[i][1][1]) * self.explosion[i][1][0]
                y_vel = np.sin(self.explosion[i][1][1]) * self.explosion[i][1][0]
            
                # update prtcl x, y
                self.explosion[i][0][0] += x_vel
                self.explosion[i][0][1] -= y_vel
                # add it to alive prtcls
                alive.append(self.explosion[i])
                
            else:
                self.explosion[i][2] -= 0.15
                if self.explosion[i][2] > 1:
                    alive.append(self.explosion[i])
            # draw
            pygame.draw.circle(surf, self.color, self.explosion[i][0], self.explosion[i][2])
            for _ in range(5):
                color = self.color[0]//15, self.color[1]//15, self.color[2]//15
                circle = circle_surf(round(self.explosion[i][2] * random.uniform(0.8, 3)), color)
                pos = self.explosion[i][0][0] - circle.get_width() / 2, self.explosion[i][0][1] - circle.get_height() / 2
                surf.blit(circle, pos, special_flags=1)
        self.explosion = alive
                
    def draw_prtcls(self, surf):
        # add one particle every fram
        self.trail_prtcls.append([deepcopy(self.pos), [random.uniform(-0.5, 0.5), random.randint(-2, 0)], random.randint(1, 4)])
        # draw prtcls
        alive = []
        for i, prtcl in enumerate(self.trail_prtcls):
            self.trail_prtcls[i][2] -= 0.1
            if self.trail_prtcls[i][2] >= 1:
                self.trail_prtcls[i][0][0] += self.trail_prtcls[i][1][0]
                self.trail_prtcls[i][0][1] -= self.trail_prtcls[i][1][1]
                pygame.draw.circle(surf, self.color, self.trail_prtcls[i][0], self.trail_prtcls[i][2])
                alive.append(self.trail_prtcls[i])
        self.trail_prtcls = alive
        
class Slider:
    def __init__(self, x, y, width, height, slider_size):
        self.bar = pygame.Rect(x, y, width, height)
        self.slider_nob = pygame.Rect((x, y), slider_size)
        self.slider_nob.center = self.slider_nob.center[0], self.bar.center[1]
        
        
        self.nob_clicked = False
    
    def nob_held(self): # check if the person is still holding the mouse on the nob
        mx, my = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        if mouse_pressed:
            if self.nob_clicked:
                self.nob_clicked = True
            elif self.slider_nob.collidepoint((mx, my)) and mouse_pressed:
                self.nob_clicked = True
        else:
            self.nob_clicked = False
            
    def slider_value(self):
        return self.slider_nob.x - self.bar.x
    def set_slider_value(self, value):
        if value < 0:
            self.slider_nob.left = self.bar.left
        elif value > self.bar.right:
            self.slider_nob.right = self.bar.right
        else:
            self.slider_nob.x = value
    
    def move_slider(self):
        mx, my = pygame.mouse.get_pos()
        if self.nob_clicked:
            if mx > self.bar.right:
                self.slider_nob.x = self.bar.right
            elif mx < self.bar.left:
                self.slider_nob.x = self.bar.left
            else:
                self.slider_nob.x = mx
    def draw(self, surf, bar_color=(100, 100, 100), nob_color=(255, 255, 255)):
        pygame.draw.rect(surf, bar_color, self.bar)
        pygame.draw.rect(surf, nob_color, self.slider_nob)

class Colors:
    def __init__(self, pos, bar_length, bar_height, start_colors):
        self.max_width = 20
        self.pos = pos
        self.size = [bar_length, bar_height]
        self.colors = []
        for color in start_colors:
            self.add_color(color)
            self.clicked_color = 0
    
    def add_color(self, new_color):
        new_width = self.size[0] / (len(self.colors) + 1)
        if new_width > self.max_width:
            new_width = self.max_width
        self.colors.append([new_color, pygame.Rect(self.pos, (new_width, self.size[1]))])
        for i, color in enumerate(self.colors):
            self.colors[i][1].width = new_width
            self.colors[i][1].x = i * new_width + self.pos[0]
    
    def del_color(self):
        new_width = self.size[0] / len(self.colors)
        if new_width > self.max_width:
            new_width = self.max_width
        if len(self.colors) > 1:
            self.colors.pop(self.clicked_color)
            if self.clicked_color == 0:
                self.clicked_color = 0
            else:
                self.clicked_color -= 1
            for i, color in enumerate(self.colors):
                self.colors[i][1].width = new_width
                self.colors[i][1].x = i * new_width + self.pos[0]            
    
    def set_clicked_color(self, clicked):
        for i, color in enumerate(self.colors):
            if button_clicked(color[1], clicked):
                self.clicked_color = i
        
    def draw(self, surf):
        pygame.draw.rect(surf, (70, 70, 70), (self.pos, self.size))
        for i, color in enumerate(self.colors):
            pygame.draw.rect(surf, color[0], color[1])
        clicked_rect = self.colors[self.clicked_color][1]
        pygame.draw.rect(surf, (20, 20, 20), clicked_rect, width=2)
        
def button_clicked(button, clicked):
    if button.collidepoint(pygame.mouse.get_pos()) and clicked:
        return True


# navbar
navbar = pygame.Rect(0, screen.get_height() - 120, screen.get_width(), 120)
# create background starry night
#stars
stars = []
for i in range(45):
    # star = [x, y, width, width] as pygame Rect(it will be a square)
    x = random.randint(15, screen.get_width() - 15)
    y = random.randint(20, screen.get_height() - navbar.height - 90)
    width = random.randint(2, 5)
    stars.append(pygame.Rect(x, y, width, width))
comets = []

fireworks = []

# color chooser
red = Slider(100, 600, 255, 10, [10, 20])
green = Slider(100, 625, 255, 10, [10, 20])
blue = Slider(100, 650, 255, 10, [10, 20])
# colors list
color_change_delay = 0
del_timer = 0
colors_list = Colors([410, 600], 200, 20, [(255, 0, 0), (255, 255, 255), (0, 0, 255), (0, 255, 0)])

while True:
    # mouse clicked
    clicked = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            clicked = True
   
    # spawn fireworks
    if clicked and pygame.mouse.get_pos()[1] < navbar.y - 30:
        color = colors_list.colors[colors_list.clicked_color][0]
        fireworks.append(Firework(list(pygame.mouse.get_pos()), 60, color, [0, 12]))

    screen.fill((20, 50, 120))

    # create random comets falling down
    if random.random() <= 0.02 and len(comets) == 0:
        lowest_y = 100
        spawning_locs = [[0, random.randint(0, lowest_y)], [random.randint(0, screen.get_width()), 0], [screen.get_width(), random.randint(0, lowest_y)]]
        # get velocity
        spawn_index = random.randint(0, 2)
        spawn_pos = spawning_locs[spawn_index]
        y_vel = random.randint(-8, -5)
        if spawn_index == 2:
            x_vel = random.randint(-10, -8)
        elif spawn_index == 0:
            x_vel = random.randint(8, 10)
        else:
            x_vel = random.randint(-5, 5)
            y_vel = random.randint(-10, -7)
        
        size = random.randint(2, 3)
        comets.append({'pos':spawn_pos, 'vel':[x_vel, y_vel], 'size':size, 'prtcls':[]})
        
        
    alive = []
    for i, comet in enumerate(comets):
        comets[i]['size'] -= 0.008
        if comets[i]['size'] > 0.6:
            
            comets[i]['pos'][0] += comet['vel'][0]
            comets[i]['pos'][1] -= comet['vel'][1]
            # drawing
            # comet
            pygame.draw.circle(screen, (255, 255, 255), comet['pos'], comet['size'])
            # glowing affect
            color = random.choice([(77, 255, 248), (231, 68, 255)])
            color = 182/10, 0, 152/10

            
            # particles
            good_prtcls = []
            comets[i]['prtcls'].append([deepcopy(comet['pos']), [random.randint(-1, 1), random.randint(0, 5)], random.randint(2, 4)])
            for j, prtcl in enumerate(comets[i]['prtcls']):
                comets[i]['prtcls'][j][2] -= 0.5
                
                if comets[i]['prtcls'][j][2] >= 1:
                    comets[i]['prtcls'][j][0][0] += comet['prtcls'][j][1][0]
                    comets[i]['prtcls'][j][0][1] -= comet['prtcls'][j][1][1]
                    pygame.draw.circle(screen, (255, 255, 255), comets[i]['prtcls'][j][0], comets[i]['prtcls'][j][2])
                    
                    circle = circle_surf(comets[i]['prtcls'][j][2] * 4, (20, 20, 60))
                    pos = comets[i]['prtcls'][j][0][0] - circle.get_width() / 2,comets[i]['prtcls'][j][0][1] - circle.get_height() / 2
                    screen.blit(circle, pos, special_flags=1)
                    good_prtcls.append(comets[i]['prtcls'][j])
            
            comets[i]['prtcls'] = good_prtcls
            alive.append(comet)
    comets = alive
    
    # draw stars
    star_colors = [(77, 255, 248), (231, 68, 255)]
    for i, star in enumerate(stars):
        col = random.choice(star_colors)
        pygame.draw.rect(screen, col, star)
        for i in range(10):
            scale = 1
            radius = scale*star.width + round(random.uniform(scale*-star.width / 2, scale*star.width / 2))
            glowing_surf = circle_surf(radius, (col[0] // 15, col[1] // 15, col[2] // 15))
            x, y = star.center[0] - glowing_surf.get_width() / 2, star.center[1] - glowing_surf.get_height() / 2
            screen.blit(glowing_surf, (x, y), special_flags=1)
            
    # update fireworks    
    alive = []
    for i, firework in enumerate(fireworks):
        fireworks[i].timer -= 1
        if fireworks[i].timer > -8:
            fireworks[i].move_firework()
            fireworks[i].draw(screen)
            fireworks[i].draw_prtcls(screen)
            alive.append(fireworks[i])
        elif fireworks[i].timer == -8:
            fireworks[i].create_explosion()
            alive.append(fireworks[i])
        else:
            fireworks[i].update_explosion(screen)
            if fireworks[i].explosion != []:
                alive.append(fireworks[i])
        
    fireworks = alive
            
    # draw nav bar
    pygame.draw.rect(screen, (0, 0, 0), navbar)
    
    # choose a color
    red.nob_held()
    red.move_slider()
    red.draw(screen, bar_color=(255, 0, 0))
    green.nob_held()
    green.move_slider()
    green.draw(screen, bar_color=(0, 255, 0))            
    blue.nob_held()
    blue.move_slider()
    blue.draw(screen, bar_color=(0, 0, 255)) 
    color = red.slider_value(), green.slider_value(), blue.slider_value()
    pygame.draw.rect(screen, color, (10, 590, 80, 50))
    # colors list
    colors_list.set_clicked_color(clicked)
    colors_list.draw(screen)
    # loop through colors
    keys = pygame.key.get_pressed()
    color_change_delay -= 1
    if keys[pygame.K_LEFT] and color_change_delay <= 0:
        color_change_delay = 4
        colors_list.clicked_color -= 1
        if colors_list.clicked_color < 0:
            colors_list.clicked_color = len(colors_list.colors) - 1
    elif keys[pygame.K_RIGHT] and color_change_delay <= 0:
        color_change_delay = 4
        colors_list.clicked_color += 1
        if colors_list.clicked_color > len(colors_list.colors) - 1:
            colors_list.clicked_color = 0
    
    # delete colors
    elif keys[pygame.K_BACKSPACE] and del_timer <= 0:
        del_timer = 5
        colors_list.del_color()
    del_timer -= 1
    
    add_color_button = pygame.Rect(10, 650, 80, 30)
    
    # check if hovereing
    if button_clicked(add_color_button, clicked):
        color = red.slider_value(), green.slider_value(), blue.slider_value()
        colors_list.add_color(color)
    pygame.draw.rect(screen, (0, 92, 181), add_color_button, border_radius=12)
    if button_clicked(add_color_button, True):
        pygame.draw.rect(screen, (255, 143, 219), add_color_button, width=3, border_radius=12)
    draw_text('add color', 15, (200, 200, 200), screen, add_color_button.center) 
    
    pygame.display.update()
    clock.tick(30)
