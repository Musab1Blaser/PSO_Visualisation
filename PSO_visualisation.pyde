import random
from math import atan2, radians

W = 800
H = 800
MENU_W = 200

# Control variables
num_particles = 10
inertia = 90
inertia_lim = 1
pbest = 50
pbest_lim = 4
gbest = 25
gbest_lim = 4
lbest = 50
lbest_lim = 4
ring_topology = 1
show_pbest = False
show_gbest = False
show_lbest = False
update_freq = 5

# New: Food spawn delay
food_spawn_delay = 3500  # In milliseconds (2.5 seconds)
food_spawn_delay_lim = 5 * 1000  # 5 seconds in milliseconds

class Particle():
    def __init__(self):
        self.pos = [random.randint(10, W-10), random.randint(10, H-10)]
        self.speed = [random.randint(-3, 3), random.randint(-3,3)]
        self.col = (255, 0, 0)
        self.pfit_pos = () # dist, pos
    
    def display(self):
        x, y = self.pos
        sx, sy = self.speed
        angle = atan2(-sy, sx)
        
        pushMatrix()
        translate(x, y)
        rotate(radians(90) - angle)
        
        fill(*self.col)
        stroke(0)
        
        beginShape()
        vertex(-10, 10)
        vertex(0, -5)
        vertex(10, 10)
        vertex(0, 5)
        endShape(CLOSE)
        
        popMatrix()
        
        # show personal best
        if show_pbest:
            fill(120, 80, 30)
            if len(self.pfit_pos):
                circle(self.pfit_pos[1][0], self.pfit_pos[1][1], 12)
        
    def move(self):
        self.pos = [self.pos[i] + self.speed[i] for i in range(2)]
        if self.pos[0] < 0 or self.pos[0] > W:
            self.speed[0] = -self.speed[0]
        if self.pos[1] < 0 or self.pos[1] > H:
            self.speed[1] = -self.speed[1]
        
        self.pos[0] = min(max(self.pos[0], 0), W)
        self.pos[1] = min(max(self.pos[1], 0), H)
        
    def check_consume(self, food, delta=20):
        if food.valid:
            dist_to_food = sqrt((self.pos[0] - food.pos[0])**2 + (self.pos[1] - food.pos[1])**2)
            x = dist_to_food / sqrt(2*((W//2)**2))
            if not len(self.pfit_pos) or dist_to_food < self.pfit_pos[0]:
                self.pfit_pos = (dist_to_food, self.pos)
            self.col = (255*(1-x), 0, 255*x)
            if dist_to_food < delta:
                food.consume()
            return dist_to_food
        else:
            self.pfit_pos = ()
        return -1

    def update_vel(self, gbest_pos, lbest_pos):
        global inertia, pbest, gbest, lbest, inertia_lim, pbest_lim, gbest_lim, lbest_lim, ring_topology, food
        inertia_val = float(inertia)/(100/inertia_lim)
        pbest_val = float(pbest)/(100/pbest_lim)
        gbest_val = float(gbest)/(100/gbest_lim)
        lbest_val = float(lbest)/(100/lbest_lim)
        speed_lim = 6
        for i in range(2):
            v = self.speed[i]
            inert = inertia_val * v
            pers = pbest_val*random.random()*max(-3, min(3, ((self.pfit_pos[1][i] - self.pos[i])/(W/20)))) # ranges from -pbest to pbest
            glob = gbest_val*random.random()*max(-3, min(3, ((gbest_pos[i] - self.pos[i])/(W/4)))) # ranges from -gbest to gbest
            if ring_topology:
                loc = lbest_val*random.random()*max(-3, min(3, ((lbest_pos[i] - self.pos[i])/(W/4)))) # ranges from -lbest to lbest
            else:
                loc = 0
            v = inert + pers + glob + loc

            self.speed[i] = v
        magnt = sqrt(self.speed[0]**2 + self.speed[1]**2)
        if magnt > speed_lim:
            self.speed[0] = speed_lim*self.speed[0]/magnt
            self.speed[1] = speed_lim*self.speed[1]/magnt
            
        # print(self.speed)
        
class Food():
    def __init__(self):
        self.pos = [random.randint(10, W-10), random.randint(10, H-10)]
        self.radius = 20
        self.time_of_spawn = millis()
        self.valid = True
        self.time_of_cons = 0

        self.cons_history = []
        self.history_lim = 10
        
    def display(self):
        global food_spawn_delay
        if not self.valid and food_spawn_delay < millis() - self.time_of_cons:
            self.pos = [random.randint(10, W-10), random.randint(10, H-10)]
            self.valid = True
            self.time_of_spawn = millis()
            
        if self.valid:
            fill(255, 0, 0)
            circle(self.pos[0], self.pos[1], self.radius)
        
    def consume(self):
        self.valid = False
        self.time_of_cons = millis()
        self.cons_history.append(float(self.time_of_cons - self.time_of_spawn) / 1000)
        if len(self.cons_history) > self.history_lim:
            self.cons_history.pop(0)
            
    def get_hist(self):
        if len(self.cons_history):
            return sum(self.cons_history) / len(self.cons_history)
        else:
            return 0
        
        
def setup():
    global particles, food, counter, lbest_lst
    size(W + MENU_W, H)
    particles = [Particle() for _ in range(num_particles)]
    food = Food()
    counter = 0
    lbest_lst = []

def draw():
    global particles, food, ring_topology, food_spawn_delay, gbest_pos, counter, lbest_lst
    
    background(0)
    
    # Simulation area
    fill(0)
    rect(0, 0, W, H)
    
    # Right-side menu (light blue)
    fill('#ADD8E6')
    rect(W, 0, MENU_W, H)
    
    fill(255)
    textSize(16)
    
    # Particle controls
    text("Particles", W + 20, 30)
    fill(180)
    rect(W + 20, 40, 30, 30)
    fill(0)
    text("-", W + 30, 60)
    
    fill(255)
    text(str(num_particles), W + 60, 60)
    
    fill(180)
    rect(W + 100, 40, 30, 30)
    fill(0)
    text("+", W + 110, 60)
    
    # Sliders for inertia, pBest, gBest, lBest
    fill(255)
    text("Inertia: " + str(float(inertia)/(100/inertia_lim)), W + 20, 100)
    fill(180)
    rect(W + 20, 110, 150, 10)
    fill(255, 0, 0)
    rect(W + 20, 110, map(inertia, 0, 100, 0, 150), 10)
    
    fill(255)
    text("pBest: " + str(float(pbest)/(100/pbest_lim)), W + 20, 140)
    fill(180)
    rect(W + 20, 150, 150, 10)
    fill(0, 255, 0)
    rect(W + 20, 150, map(pbest, 0, 100, 0, 150), 10)
    
    fill(255)
    text("gBest: " + str(float(gbest)/(100/gbest_lim)), W + 20, 180)
    fill(180)
    rect(W + 20, 190, 150, 10)
    fill(0, 0, 255)
    rect(W + 20, 190, map(gbest, 0, 100, 0, 150), 10)
    
    fill(255)
    text("lBest: " + str(float(lbest)/(100/lbest_lim)), W + 20, 220)
    fill(180)
    rect(W + 20, 230, 150, 10)
    fill(255, 0, 255)
    rect(W + 20, 230, map(lbest, 0, 100, 0, 150), 10)
    
    # Ring Topology checkbox
    fill(255)
    text("Ring Topology", W + 20, 270)
    fill(180)
    rect(W + 150, 255, 15, 15)
    if ring_topology == 1:
        line(W + 150, 255, W + 165, 270)
        line(W + 165, 255, W + 150, 270)
    elif ring_topology == 2:
        fill(50)
        rect(W+150, 255, 15, 15)
    # Show pbest checkbox
    fill(255)
    text("Show pbest", W + 20, 440)
    fill(180)
    rect(W + 150, 425, 15, 15)
    if show_pbest:
        line(W + 150, 425, W + 165, 440)
        line(W + 165, 425, W + 150, 440)
    fill(120, 80, 30)
    circle (W+120, 435, 15)
        
    # Show gbest checkbox
    fill(255)
    text("Show gbest", W + 20, 480)
    fill(180)
    rect(W + 150, 465, 15, 15)
    if show_gbest:
        line(W + 150, 465, W + 165, 480)
        line(W + 165, 465, W + 150, 480)
    fill(0, 150, 150)
    circle (W+120, 475, 15)
    
        
    # Show lbest checkbox
    fill(255)
    text("Show lbest", W + 20, 520)
    fill(180)
    rect(W + 150, 505, 15, 15)
    if show_lbest:
        line(W + 150, 505, W + 165, 520)
        line(W + 165, 505, W + 150, 520)
    fill(0, 255, 150)
    circle (W+120, 515, 15)
    
    # Food spawn delay slider
    fill(255)
    text("Food Spawn Delay: " + str(round(float(food_spawn_delay) / 1000, 2)) + " s", W + 20, 320)
    fill(180)
    rect(W + 20, 330, 150, 10)
    fill(255, 165, 0)
    rect(W + 20, 330, map(food_spawn_delay, 0, food_spawn_delay_lim, 0, 150), 10)
    
    # Average time
    fill(255)
    text("Avg Consumption time:\n                  " + str(round(food.get_hist(), 3)) + " s", W + 20, 380)
    
    # Draw ring topology if enabled
    if ring_topology == 2 and len(particles) > 1:
        stroke(255)
        strokeWeight(1)
        for i in range(len(particles)):
            x1, y1 = particles[i].pos
            x2, y2 = particles[(i + 1) % len(particles)].pos
            
            dist_val = dist(x1, y1, x2, y2)
            num_dashes = max(1, int(dist_val / 20))
            for j in range(num_dashes):
                x_start = lerp(x1, x2, float(j) / num_dashes)
                y_start = lerp(y1, y2, float(j) / num_dashes)
                x_end = lerp(x1, x2, (j + 0.5) / num_dashes)
                y_end = lerp(y1, y2, (j + 0.5) / num_dashes)
                line(x_start, y_start, x_end, y_end)
    
    # Display and move particles
    fit_pos = []
    for particle in particles:
        particle.move()
        fit_pos.append((particle.check_consume(food), particle.pos))
        particle.display()

    _, gbest_pos = min(fit_pos)
    # show global best point
    if show_gbest:
        fill(0, 150, 150)
        circle (gbest_pos[0], gbest_pos[1], 15)
        
    counter = (counter + 1) % update_freq
    if food.valid and counter % update_freq == 0:
        lbest_lst = []
        for i in range(len(particles)):
            _, lbest_pos = min(fit_pos[i-1], fit_pos[i], fit_pos[(i+1)%len(particles)])
            lbest_lst.append(lbest_pos)
            # fill(0, 255, 150)
            # circle (lbest_pos[0], lbest_pos[1], 10)
            particles[i].update_vel(gbest_pos, lbest_pos)
            
    # show local best points
    if show_lbest:
        if len(lbest_lst):
            for lb in lbest_lst:
                fill(0, 255, 150)
                circle (lb[0], lb[1], 10)

    # print(particles[0].speed)
    # Display food
    food.display()
    
def mousePressed():
    global num_particles, particles, ring_topology, inertia, pbest, gbest, lbest, food_spawn_delay, show_pbest, show_gbest, show_lbest
    
    # Decrease particles
    if W + 20 <= mouseX <= W + 50 and 40 <= mouseY <= 70:
        if num_particles > 1:
            num_particles -= 1
            particles.pop()
    
    # Increase particles
    if W + 100 <= mouseX <= W + 130 and 40 <= mouseY <= 70:
        num_particles += 1
        particles.append(Particle())
    
    # Adjust sliders
    if W + 20 <= mouseX <= W + 170:
        if 110 <= mouseY <= 120:
            inertia = int(map(mouseX, W + 20, W + 170, 0, 100))
        if 150 <= mouseY <= 160:
            pbest = int(map(mouseX, W + 20, W + 170, 0, 100))
        if 190 <= mouseY <= 200:
            gbest = int(map(mouseX, W + 20, W + 170, 0, 100))
        if 230 <= mouseY <= 240:
            lbest = int(map(mouseX, W + 20, W + 170, 0, 100))
        if 330 <= mouseY <= 340:
            food_spawn_delay = int(map(mouseX, W + 20, W + 170, 0, food_spawn_delay_lim))

    # Toggle ring topology
    if W + 150 <= mouseX <= W + 165:
        if 255 <= mouseY <= 270:
            ring_topology = (ring_topology + 1) % 3
        if 425 <= mouseY <= 440:
            show_pbest = not show_pbest
        if 465 <= mouseY <= 480:
            show_gbest = not show_gbest
        if 505 <= mouseY <= 520:
            show_lbest = not show_lbest
        
