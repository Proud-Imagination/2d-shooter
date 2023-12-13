import pygame as p
import math as m
import random as r

def num_to_range(num, inMin, inMax, outMin, outMax):
    return outMin + (float(num - inMin) / float(inMax - inMin) * (outMax - outMin))

p.init()
screen = p.display.set_mode((1280, 720))
clock = p.time.Clock()
dt = 0

running = True
gameTimer = 0
difficulty = 1
notificationText = ""
notificationTextCoolDown = 3
lastNotification = 0

enemies = []
lastEnemy = 0
enemyCooldown = 0.5
enemySpeed = 200

guns = ["pistol"]
currentGun = 0
lastGunChange = 0
bullets = []
lastShot = 0
shotCooldown = 0.5
bulletSpeed = 1000
bulletStrength = 30

playerPos = p.Vector2(screen.get_width()/2, screen.get_height()/2)
playerRot = 0
playerHealth = 100
playerSpeed = 400
playerRadius = 60
killCount = 0

lastMedkit = [20, True]
medkitCooldown = 15
medkitPos = p.Vector2()
medkitRadius = 10

class bullet:
    def __init__(self, position, angle):
        self.position = p.Vector2(position)
        self.velocity = p.Vector2(bulletSpeed * m.cos(angle), bulletSpeed * m.sin(angle))
        self.radius = 5
        self.hit = False
    def update(self, dt):
        self.position += self.velocity*dt

class enemy:
    def __init__(self, position, angle):
        self.position = p.Vector2(position)
        self.velocity = p.Vector2(enemySpeed * m.cos(angle), enemySpeed * m.sin(angle))
        self.health = 100
        self.strength = 10
        self.lastHit = 0
        self.radius = 30
    def update(self, damage, dt):
        self.position += self.velocity*dt
        self.health -= damage    

while running:
    for event in p.event.get():
        if event.type == p.QUIT:
            running = False

    keys = p.key.get_pressed()

    # player movement
    if keys[p.K_w]:
        if playerPos.y-playerSpeed*dt > playerRadius/2:
            playerPos.y -= playerSpeed*dt
    if keys[p.K_s]:
        if playerPos.y+playerSpeed*dt < screen.get_height()-playerRadius/2:
            playerPos.y += playerSpeed*dt
    if keys[p.K_a]:
        if playerPos.x-playerSpeed*dt > playerRadius/2:
            playerPos.x -= playerSpeed*dt
    if keys[p.K_d]:
        if playerPos.x+playerSpeed*dt < screen.get_width()-playerRadius/2:
            playerPos.x += playerSpeed*dt
    
    
    # player rotation
    mousePos = p.Vector2(p.mouse.get_pos()[0], p.mouse.get_pos()[1])
    playerRot = -m.atan2(mousePos.y - playerPos.y, mousePos.x - playerPos.x)

    # player shooting
    mousePress = p.mouse.get_pressed()
    if mousePress[0] is True and lastShot >= shotCooldown:
        if currentGun == 1 or currentGun == 3: # shotgun or minigun
            for i in range(10):
                variance = r.random()
                variance = num_to_range(variance, 0, 1, -m.pi/8, m.pi/8)
                bullets.append(bullet(playerPos, -playerRot+variance))
        else:
            bullets.append(bullet(playerPos, -playerRot))
        lastShot = 0
    for i in bullets:
        i.update(dt)
    lastShot += dt

    # enemy spawning
    if lastEnemy >= enemyCooldown:
        side = r.choice(["left", "right", "top", "bottom"])
        if side == "left":
            random_x = 0
            random_y = r.randint(0, screen.get_height())
        elif side == "right":
            random_x = screen.get_width()
            random_y = r.randint(0, screen.get_height())
        elif side == "top":
            random_x = r.randint(0, screen.get_width())
            random_y = 0
        elif side == "bottom":
            random_x = r.randint(0, screen.get_width())
            random_y = screen.get_height()
        angle = -m.atan2(playerPos.y - random_y, playerPos.x - random_x)
        enemies.append(enemy((random_x, random_y), -angle))
        lastEnemy = 0
    #enemy updates
    for i in enemies:
        damage = 0
        for j in bullets:
            if p.Vector2(i.position).distance_to(j.position) <= i.radius+j.radius:
                damage = bulletStrength
                j.hit = True
        angle_to_player = m.atan2(playerPos.y - i.position.y, playerPos.x - i.position.x)
        i.velocity = p.Vector2(enemySpeed * m.cos(angle_to_player), enemySpeed * m.sin(angle_to_player))   
        if p.Vector2(i.position).distance_to(playerPos) <= i.radius + playerRadius and i.lastHit > 1:
            # i.velocity = p.Vector2(0,0)
            playerHealth -= i.strength
            i.lastHit = 0
        i.lastHit += dt
        i.update(damage, dt)
    lastEnemy += dt
    # enemy difficulty
    if killCount < 20:
        difficulty = 1
        enemyCooldown = 2
        enemySpeed = 150
    if killCount >= 20 and killCount < 40:
        difficulty = 2
        enemyCooldown = 1 
        enemySpeed = 175
    if killCount >= 40 and killCount < 70:
        difficulty = 3
        enemyCooldown = 0.75 
        enemySpeed = 200
    if killCount >= 70 and killCount < 110:
        difficulty = 4
        enemyCooldown = 0.5
        enemySpeed = 250
    if killCount >= 110 and killCount < 170:
        difficulty = 5
        enemyCooldown = 0.3
        enemySpeed = 250
    if killCount >= 170:
        difficulty = 6
        enemyCooldown = 0.1
        enemySpeed = 300

    # medkit spawning
    if lastMedkit[0] > medkitCooldown and lastMedkit[1] is True:
        medkitPos.x = r.randint(0, screen.get_width())
        medkitPos.y = r. randint(0, screen.get_height())
        lastMedkit = [0, False]
    # medkit updates
    if p.Vector2(medkitPos).distance_to(playerPos) <= medkitRadius+playerRadius:
        playerHealth = 100
        lastMedkit = [0, True]
    lastMedkit[0] += dt

    # guns
    if keys[p.K_e] and lastGunChange > 0.5:
        currentGun += 1
        currentGun %= len(guns)
        lastGunChange = 0
    lastGunChange += dt
    # pistol
    if killCount < 10:
        pass
    # shotgun
    if killCount >= 10 and killCount < 100 and len(guns) < 2:
        notificationText = "shotgun equipped, press E to change weapon"
        guns.append("shotgun")
    # AR
    if killCount >= 100 and killCount < 170 and len(guns) < 3:
        notificationText = "AR equipped, press E to change weapon"
        guns.append("AR")
    # minigun
    if killCount >= 170 and len(guns) < 4:
        notificationText = "minigun equipped, press E to change weapon"
        guns.append("minigun")
    if currentGun == 0:
        shotCooldown = 0.5
        bulletSpeed = 1000
        bulletStrength = 30
    elif currentGun == 1:
        shotCooldown = 1
        bulletSpeed = 800
        bulletStrength = 50    
    elif currentGun == 2:
        shotCooldown = 0.05
        bulletSpeed = 1200
        bulletStrength = 40 
    elif currentGun == 3:
        shotCooldown = 0.05
        bulletSpeed = 1300
        bulletStrength = 50 

    if playerHealth <= 0:
        running = False

    bullets = [i for i in bullets if 0 <= i.position.x < screen.get_width() and 0 <= i.position.y < screen.get_height() and i.hit == False]
    temp = len(enemies)
    enemies = [i for i in enemies if i.health > 0]
    killCount += temp - len(enemies)

    # background
    screen.fill("black")
    # player
    p.draw.circle(screen, "white", playerPos, 30)
    p.draw.arc(screen, "red", (playerPos.x-playerRadius/2, playerPos.y-playerRadius/2, playerRadius, playerRadius), -m.pi*1/3+playerRot, m.pi*1/3+playerRot, 10)
    # bullets
    for i in bullets:
        p.draw.circle(screen, "red", (int(i.position.x), int(i.position.y)), i.radius)
    # enemies
    for i in enemies:
        p.draw.circle(screen, "blue", (int(i.position.x), int(i.position.y)), i.radius)
        p.draw.rect(screen, "red", (int(i.position.x)-i.radius*2/3, int(i.position.y)-i.radius, 4/3*i.radius*i.health/100, 1/4*i.radius))
        p.draw.rect(screen, "grey", (int(i.position.x)-i.radius*2/3, int(i.position.y)-i.radius, 4/3*i.radius, 1/4*i.radius), 2)
    # medkit
    if lastMedkit[1] is False:
        p.draw.circle(screen, "green", medkitPos, medkitRadius)
    # player health bar
    p.draw.rect(screen, "green", (20, 20, 100*playerHealth/100, 20))
    p.draw.rect(screen, "grey", (20, 20, 100, 20), 2)
    # kill count
    font = p.font.Font(None, 36)  
    text = font.render(f"{killCount}", True, "white")
    text_rect = text.get_rect()
    text_rect.topright = (screen.get_width() - 20, 20)
    screen.blit(text, text_rect)
    # timer
    text = font.render("{:02d}:{:02d}".format(int(gameTimer // 60), int(gameTimer % 60)), True, "white")
    text_rect = text.get_rect()
    text_rect.midtop = (screen.get_width()//2, 20)
    screen.blit(text, text_rect)
    # gun info
    text = font.render(f"<{guns[currentGun]}>", True, "white")
    text_rect = text.get_rect()
    text_rect.bottomleft = (20, screen.get_height() - 20)
    screen.blit(text, text_rect)
    # difficulty level
    text = font.render(f"Level:{difficulty}", True, "white")
    text_rect = text.get_rect()
    text_rect.midbottom = (screen.get_width()//2, screen.get_height() - 20)
    screen.blit(text, text_rect)
    # notification text
    if notificationText!="":
        lastNotification += dt
    if lastNotification < notificationTextCoolDown:
        text = font.render(notificationText, True, "white")
        text_rect = text.get_rect()
        text_rect.bottomright = (screen.get_width() - 20, screen.get_height() - 20)
        screen.blit(text, text_rect)
    else:
        notificationText = ""
    # mouse cursor
    p.draw.circle(screen, "grey", mousePos, 20, 2)

    p.display.flip()

    # print(playerHealth) 
    gameTimer += dt
    dt = clock.tick(60)/1000
print(killCount)
p.quit()