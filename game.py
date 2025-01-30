import pygame
import os
import random as rd

pygame.init() # Initialize pygame module for use

''' COLOR '''
red = (255, 0, 0)
blue = (0, 0 , 255)
yellow = (255, 255, 0)
black = (0, 0, 0)
white = (255, 255, 255)
purple = (128, 0, 128)
magenta = (255, 0, 255)
green = (0, 255, 0)
grey = (169, 169, 169)


''' FONT '''
smallSize = 30
mediumSize = 40
largeSize = 110

# FOR CREATOR'S COMPUTER
pixelFontPath_myComp = 'C:/Users/Marc Neil/pyjourn/midnight_motorist/assets/Pixel Digivolve.otf'

# FOR USERS' COMPUTER
base_dir = os.path.dirname(os.path.abspath(__file__)) # Get the current directory where the script is located
pixelFontPath = os.path.join(base_dir, 'assets', 'Pixel Digivolve.otf') # Define the path to the font file relative to the script's directory

smallFont = pygame.font.Font(pixelFontPath, smallSize) # 
mediumFont = pygame.font.Font(pixelFontPath, mediumSize) # 
largeFont = pygame.font.Font(pixelFontPath, largeSize) # 

''' WINDOW DIMENSIONS '''
windowWidth = 1300
windowHeight = 750
window = pygame.display.set_mode((windowWidth, windowHeight))
# add pygame.RESIZABLE as argument for resizable window

''' WINDOW NAME '''
pygame.display.set_caption('Midnight Motorist') 

''' ELEMENT PROPERTIES '''
carWidth = 100
carHeight = 50
carX = 100
carY = 600
carVel = 1.5
powerUpWidth = 30
powerUpHeight = 30
powerUpSpeed = 1

''' DEFAULT DIFFICULTY '''
selectedDifficulty = 'Normal'

''' HIGH SCORE FILE DIRECTORY '''
scriptDir = os.path.dirname(os.path.realpath(__file__)) # Get the current directory of the script
highscoreFilePath = os.path.join(scriptDir, "high_scores.txt") # Absolute path for the highScores.txt file in the same directory as the script

class Car:
    def __init__(self, x, y, width, height, speed, color):
        self.rect = pygame.Rect (x, y, width, height)
        self.speed = speed
        self.lives = 3
        self.color = color
        self.carFlashing = False # Track whether the car is flashing
        self.carFlashTimer = 0 # Timer to control flash duration

    def movePlayer(self, keys):
        ''' MOVE PLAYER CAR BASED ON KEY PRESSED '''
        if keys[pygame.K_d]:
            if self.rect.x + self.rect.width < windowWidth:  # Check if the car is not going off the right edge
                self.rect.x += self.speed
        if keys[pygame.K_a]:
            if self.rect.x > 0:  # Check if the car is not going off the left edge
                self.rect.x -= self.speed
        if keys[pygame.K_w]:
            if self.rect.y > 0:  # Check if the car is not going off the top edge
                self.rect.y -= self.speed
        if keys[pygame.K_s]:
            if self.rect.y + self.rect.height < windowHeight:  # Check if the car is not going off the bottom edge
                self.rect.y += self.speed
    
    def moveEnemy(self):
        ''' MOVE ENEMY CARS TO THE LEFT '''
        self.rect.x -= self.speed

    def draw(self, window, color):
        ''' DRAW THE CAR ON THE SURFACE '''
        pygame.draw.rect(window, self.color, self.rect)

    def collide(self, otherCar):
        ''' CHECK FOR COLLISION WITH ANOTHER CAR '''
        return self.rect.colliderect(otherCar.rect)
    
    def startFlashingCar(self):
        self.carFlashing = True # Set car flashing state active
        self.carFlashTimer = 0 # Reset flash timer
        self.color = red # Flash player car red

    def updateCarFlash(self):
        if self.carFlashing:
            self.carFlashTimer += 1 # While flashing, flash timer counts up
            if self.carFlashTimer > 30: # Flash duration (in frames)
                self.carFlashing = False # If flash timer exceeds 30 frames, flashing stops
                self.carFlashTimer = 0 # Reset flash timer
                self.color = yellow # Return player car color to yellow

class PowerUp:
    def __init__(self, x, y, width, height, speed, color, type):
        self.rect = pygame.Rect(x, y, width, height)  # Rect for the power-up
        self.speed = speed  # Power-up speed (towards the player)
        self.color = color  # Color of the power-up (green as requested)
        self.type = type
        self.isBoosted = False # Track boosted state of player car
        self.boostTimer = 0 # Timer to control boost duration

    def move(self):
        """ MOVE POWER-UPS TO THE LEFT """
        self.rect.x -= self.speed # Move power-ups to the left

    def draw(self, window, color):
        ''' DRAW POWER-UPS ON THE SURFACE '''
        pygame.draw.rect(window, self.color, self.rect)

    def collide(self, playerCar):
        ''' CHECK FOR COLLISIONS WITH POWER-UPS '''
        return self.rect.colliderect(playerCar.rect)

class Game:
    def __init__(self, difficulty = 'Normal'):
        self.difficulty = difficulty # Set initial difficulty
        self.setDifficulty(self.difficulty) # Set the difficulty when initializing the game
        self.offset = 0
        self.playerCar = Car(carX, carY, carWidth, carHeight, carVel, yellow) # Create car instance as player car
        self.enemyCars = [] # List to store enemy cars
        self.enemySpawnTimer = 0 # Timer to control spawining interval of enemy cars
        self.powerUps = [] # List to store power-ups
        self.powerUpSpawnTimer = 0 # Timer to control the spawning interval of power-ups

        self.currentScore = 0 # Start current score at zero
        self.highScore = self.loadHighScore() # Access the value in the text file

        self.livesColor = yellow # Set initial lives color as yellow
        self.livesFlashing = False  # Track if lives should flash
        self.livesFlashTimer = 0  # Timer to control flash duration

        self.isBoosted = False # Track boosted state of player car
        self.boostTimer = 0 # Timer to control boost duration

        self.isSlowed = False # Track slowed state of enemy cars
        self.slowedTimer = 0 # Timer to control slowed duration

    ''' SET DIFFICULTY '''
    def setDifficulty(self, difficulty):
        self.difficulty = difficulty
        if self.difficulty == 'Easy':
            self.enemyCarSpeedRange = (1, 2) # Adjust enemy car speeds accordingly
        elif self.difficulty == 'Normal':
            self.enemyCarSpeedRange = (2, 3)
        elif self.difficulty == 'Hard':
            self.enemyCarSpeedRange = (3, 5)
        elif self.difficulty == 'Superhighway':          # EXPERIMENTAL hahahahhhhha
            self.enemyCarSpeedRange = (6, 8)
        print(f"Difficulty set to {self.difficulty}") # PRINT TO CONSOLE

    ''' LOAD HIGH SCORE FROM TEXT FILE'''
    def loadHighScore(self):
        try:
            with open(highscoreFilePath, "r") as file:
                return int(file.read())
        except FileNotFoundError:
            return 0

    ''' SAVE HIGH SCORE TO TEXT FILE '''
    def saveHighScore(self):
        global highScore
        with open(highscoreFilePath, "w") as file:
            file.write(str(self.highScore))

    ''' CREATE MULTIPLE ENEMY CARS '''
    def generateEnemyCars(self):     
        self.randomSpeed = rd.randint(self.enemyCarSpeedRange[0], self.enemyCarSpeedRange[1]) # Use the speed range based on difficulty  
        self.spawnArea = rd.choice(['top', 'bottom', 'middle']) # Choose random spawn area
        self.randomY = self.getRandomY(self.spawnArea)
        self.enemySpeed = self.randomSpeed
        self.newEnemyCar = Car(windowWidth, self.randomY, carWidth, carHeight, self.enemySpeed, red) # Create new car instance as enemy car
        return self.newEnemyCar # Return new enemy car

    ''' CREATE RANDOM POWER-UPS '''
    def generatePowerUps(self):
        self.spawnArea = rd.choice(['top', 'bottom', 'middle'])  # Choose random spawn area
        self.randomY = self.getRandomY(self.spawnArea)  # Get Y position based on spawn area
        self.type = rd.choice(['heal', 'speed', 'slowdown']) # Choose random power-up type
        self.randomType, self.color = self.randomPowerUp(self.type) # Assign type and color
        self.powerUpSpeed = powerUpSpeed  # Power-ups speed
        self.newPowerUp = PowerUp(windowWidth, self.randomY, powerUpWidth, powerUpHeight, self.powerUpSpeed, self.color, self.randomType)  # Create new power-up instance
        return self.newPowerUp # Return new power-up
    
    ''' DETERMINE RANDOM POSITION '''
    def getRandomY(self, spawnArea):
        # Define spawn boundaries
        if spawnArea == 'top': # Avoid top edge and the middle line
            return rd.randint(50, windowHeight // 2 - carHeight - 50)
        elif spawnArea == 'bottom': # Avoid bottom edge and the middle line
            return rd.randint(windowHeight // 2 + 50, windowHeight - carHeight - 50)
        else: # Spawn close to the middle line (narrow band)
            return rd.randint(windowHeight // 2 - carHeight // 2, windowHeight // 2 + carHeight // 2)

    ''' DETERMINE RANDOM POWER-UP TYPE '''
    def randomPowerUp(self, type): # Return type and color
        if type == 'heal':
            return  'heal', green
        elif type == 'speed':
            return 'speed', magenta
        elif type == 'slowdown':
            return 'slowdown', blue

    ''' DISPLAY SCORE AND LIVES '''
    def displayScore(self):
        # Display current score
        self.scoreText = smallFont.render(f"Current Score: {self.currentScore}", True, red)
        window.blit(self.scoreText, (10, 10)) # Place current score at top-left corner

        # Display high score
        self.highScoreText = smallFont.render(f"High Score: {self.highScore}", True, blue)
        window.blit(self.highScoreText, (10, 40)) # Place high score below current score

        # Display lives
        self.livesText = smallFont.render(f"Lives: {self.lives}", True, self.livesColor)
        window.blit(self.livesText, (windowWidth - 130, 10))  # Place lives at top-right corner

    ''' START FLASHING LIVES TIMER '''
    def startFlashingLives(self, color):
        self.livesFlashing = True # Start flashing the lives when a collision happens
        self.livesFlashTimer = 0  # Reset flash timer
        self.livesColor = color

    ''' LIMIT AND UPDATE FLASHING STATE '''
    def updateLivesFlash(self):
        if self.livesFlashing:
            self.livesFlashTimer += 1  # Increment flash timer while flashing state active
            if self.livesFlashTimer > 30:  # Stop flashing after 30 frames
                self.livesFlashing = False
                self.livesFlashTimer = 0 # Reset flash timer
                self.livesColor = yellow # Return lives color to yellow

    ''' DISPLAY ROAD AND LINE MARKINGS '''
    def drawRoad(self):
        pygame.draw.rect(window, black, (0, 0, windowWidth, windowHeight))  # Draw road

        ''' LANE/DASHED LINES '''
        self.laneWidth = 20
        self.laneSpacing = 40

        # Calculate how many lines need to be drawn to fill the entire width of the screen
        self.numLines = (windowWidth + self.laneSpacing) // self.laneSpacing  # Number of lines to cover screen width
        
        # Adjust the x-coordinate for the dashed lines to scroll from right to left
        for i in range(self.numLines):
            # Calculate the x position of the dashed line
            lineX = (self.offset + i * self.laneSpacing) % (windowWidth + self.laneSpacing)
                # (self.offset + i * self.laneSpacing): moves dashed lines along x-axis 
                # i provides necessary offset for each subsquent line
                # % (windowWidth + self.laneSpacing): dashed lines wrap around when edge is reached

            # Draw top dashed lines at the correct x position
            pygame.draw.line(window, white, (lineX, windowHeight // 4),
            (lineX + 20, windowHeight // 4), self.laneWidth)

            # Draw bottom dashed line at the correct x position
            pygame.draw.line(window, white, (lineX, 3 * windowHeight // 4),
            (lineX + 20, 3 * windowHeight // 4), self.laneWidth)

        ''' CENTRAL ROAD DIVIDER (SOLID WHITE LINE) '''
        pygame.draw.line(window, white, (0, windowHeight // 2), (windowWidth, windowHeight // 2), 5)

    def gameLoop(self):
        self.gameRun = True # Run game loop
        self.powerUpChance = 0.5 # Chance of power-up to spawn (50%)
        self.boostLimit = 300
        #self.setDifficulty(self.difficulty) # Ensure the difficulty is set at the start of the loop
        self.collideEC = 0
        self.collidePU = 0

        ''' RESET GAME '''
        self.resetGame()  # Reset game states at the start of the game loop
        
        ''' GAME LOOP '''
        while self.gameRun:
            self.enemySpawnTimer += 1 # Increment enemy car spawn timer each frame
            self.powerUpSpawnTimer += 1  # Increment the power-up spawn timer each frame

            ''' EVENT HANDLER'''
            for event in pygame.event.get():
                if event.type == pygame.QUIT: # Exits window when close button is pressed
                    self.quitGame()
                    return

            ''' SUPERHIGHWAY MODE '''
            if self.difficulty == 'Superhighway':
                #self.lives = 99999
                self.playerCar.speed = carVel + 3 # Faster player speed
                self.scrollSpeed = self.playerCar.speed # Faster road scrolling
                self.boostLimit = 600 # Longer boost

            ''' PLAYER CAR MOVEMENT and FLASHING '''
            keys = pygame.key.get_pressed() # Get key states to move the car
            self.playerCar.movePlayer(keys) # Move the car
            self.playerCar.updateCarFlash()  # Update car flashing effect
            self.updateLivesFlash() # Update lives flashing 

            ''' SPAWN ENEMY CARS '''
            if self.enemySpawnTimer >= 120: # Periodically spawn enemy cars every 120 frames (2 seconds)
                enemyCar = self.generateEnemyCars() # Generate enemy car
                self.enemyCars.append(enemyCar) # Add new enemy car to list of enemy cars on screen
                self.enemySpawnTimer = 0 # Reset spawn timer after every spawn

            ''' REMOVE OFF-SCREEN ENEMY CARS '''
            self.enemyCars = [enemyCar for enemyCar in self.enemyCars if enemyCar.rect.x + carWidth > 0]

            ''' MOVE ENEMY CARS '''
            for enemyCar in self.enemyCars:
                enemyCar.moveEnemy() # Enemy cars move to the left

                ''' CHECK ENEMY CAR COLLISIONS '''
                if self.playerCar.collide(enemyCar):
                    if not self.isBoosted: # Life deduction disabled when player is in boosted state
                        self.lives -= 1 # Deduct a life when collision happens
                    self.enemyCars.remove(enemyCar) # Remove enemy car hit
                    self.playerCar.startFlashingCar() # Flash player's car red
                    self.startFlashingLives(red) # Flash lives red
                    self.collideEC += 1
                    
                    if self.lives <= 0:
                        self.gameRun = False # Game over when lives run out

            ''' SPAWN POWER-UPS AT RANDOM CHANCE '''
            # if self.difficulty != 'Easy':
            if self.powerUpSpawnTimer >= 360:
                self.powerUpSpawnTimer = 0  # Reset the spawn timer every 360 frames (6 seconds)
                if rd.random() < self.powerUpChance: # Power-ups have 50% chance to spawn every 360 frames (6 seconds)
                    powerUp = self.generatePowerUps()  # Generate a new power-up
                    self.powerUps.append(powerUp)  # Add to the list of active power-ups

            ''' REMOVE OFF-SCREEN POWER-UPS '''
            self.powerUps = [powerUp for powerUp in self.powerUps if powerUp.rect.x + 30 > 0]

            ''' MOVE POWER-UPS '''
            for powerUp in self.powerUps:
                powerUp.move()  # Power-ups move to the left

                ''' CHECK POWER-UP COLLISION AND ACTIVATE POWER-UP STATES '''
                if powerUp.collide(self.playerCar):
                    if powerUp.type == 'heal':
                        if self.lives < 6: # Maximum lives at six
                            if self.difficulty != 'Superhighway':
                                self.lives += 1  # Increase player's lives
                            else:
                                self.lives = 6 # FOR SUPERHIGHWAY MODE
                        self.startFlashingLives(green)  # Flash lives in green color
                    if powerUp.type == 'speed':
                        self.isBoosted = True # Activate boosted state of player car
                        self.boostTimer = 0 # Ensure boost timer start at zero
                    elif powerUp.type == 'slowdown':
                        self.isSlowed = True # Activate slowed state of enemy cars
                        self.slowedTimer = 0 # Ensure boost timer start at zero
                    self.powerUps.remove(powerUp)  # Remove the power-up after collision
                    self.collidePU += 1

            ''' APPLY SPEED BOOST EFFECTS and UPDATE TIMER '''
            if self.isBoosted:
                self.boostTimer += 1 # Boost timer counts up while boosted state is active
                if self.difficulty != 'Superhighway':
                    self.playerCar.speed = 4 # Player car becomes faster
                else:
                    self.playerCar.speed = 10 # FOR SUPERHIGHWAY MODE
                self.playerCar.color = magenta # Flash player car in magenta color
                self.startFlashingLives(magenta)  # Flash lives in magenta color
                if self.boostTimer >= self.boostLimit: # After 300 frames (5 seconds):
                    self.isBoosted = False # Deactivate boosted state
                    self.boostTimer = 0 # Reset boost timer
                    self.playerCar.speed = carVel # Return original player car speed
                    self.playerCar.color = yellow # Return original player car color
            
            ''' APPLY SLOWED ENEMIES EFFECTS and UPDATE TIMER'''
            if self.isSlowed:
                self.slowedTimer += 1 # Slowed timer counts up while slowed state is active
                for enemyCar in self.enemyCars: 
                    enemyCar.speed = 1 # Slow down every enemy car
                    enemyCar.color = blue # Flash enemy cars in blue color
                if self.slowedTimer >= 300: # After 300 frames (5 seconds):
                    self.isSlowed = False # Deactivate slowed state
                    self.slowedTimer = 0 # Reset slowed timer
                    for enemyCar in self.enemyCars:
                        enemyCar.speed = self.randomSpeed # Return each enemy car's original speed
                        enemyCar.color = red # Return each enemy car's original color

            ''' SCROLLING ROAD LOGIC '''
            self.offset -= self.scrollSpeed # Scroll road lines continuously by updating the 'offset'
            if self.offset < -40:  # If the offset is less than the lane width, reset to 0 to keep it looping
                self.offset = 0
            
            ''' DRAW ELEMENTS  '''
            window.fill(black)  # Fill background with color black            
            self.drawRoad() # Draw the road with lines and divider

            self.playerCar.draw(window, self.playerCar.color) # Draw player car in its current color

            for enemyCar in self.enemyCars:
                enemyCar.draw(window, enemyCar.color) # Draw enemy car in its current color

            for powerUp in self.powerUps:
                powerUp.draw(window, powerUp.color) # Draw power-ups in their color based on type
           
            self.displayScore()  # Display current score and high score

            pygame.display.flip() # Update whole screen

            ''' INCREASE CURRENT SCORE '''
            self.currentScore += 1 # Increase current score per frame    

        ''' CONSOLE SUMMARY '''

        print ("\n----------- ROUND SUMMARY -----------")   

        print (f"Difficulty: {self.difficulty}") 

        ''' CHECK HIGH SCORE '''
        if self.currentScore > self.highScore: # After game ends, check if a new high score was achieved
            self.newHighScore = True
            self.highScore = self.currentScore  # Update high score if the player surpassed it
            self.saveHighScore()  # Save the new high score to text file
            print (f"New High Score: {self.highScore}! Congratulations!") # PRINT TO CONSOLE
        else:
            print (f"Final Score: {self.currentScore}") # PRINT TO CONSOLE
        
        print (f"Enemy cars hit: {self.collideEC}") # PRINT TO CONSOLE
        print (f"Power-ups consumed: {self.collidePU}") # PRINT TO CONSOLE

        print ("-------------------------------------\n") 


        self.gameOver() # End game, direct player to game over screen
        self.resetGame()

    ''' RESET GAME STATES WHEN STARTING NEW GAME OR AFTER GAME OVER '''
    def resetGame(self):     
        self.lives = 3 # Start at 3 lives
        self.offset = 0 # Start offset at zero
        self.scrollSpeed = carVel # Scroll speed = car speed
        self.playerCar = Car(carX, carY, carWidth, carHeight, carVel, yellow)
        self.enemyCars = [] # Clear enemy cars at start
        self.powerUps = [] # Clear power-ups at start

        self.enemySpawnTimer = 0
        self.powerUpSpawnTimer = 0

        self.currentScore = 0 # Start current score at zero
        self.newHighScore = False # FLag to check if a new high score is set at the start of the loop
        self.currentHighScore = self.highScore # Store the high score at the start of the game loop and don't modify it during gameplay

        ''' RESET PLAYER CAR POSITION and FLASHING STATE'''
        self.playerCar.rect.x = carX 
        self.playerCar.rect.y = carY
        self.playerCar.carFlashing = False
        self.playerCar.carFlashTimer = 0

        ''' RESET POWER-UP STATES AND TIMERS '''
        self.isBoosted = False
        self.boostTimer = 0
        self.isSlowed = False
        self.slowedTimer = 0

    ''' GAME OVER SCREEN '''
    def gameOver(self):
        self.saveHighScore() # save high score
        
        gameOverRun = True
        while gameOverRun:
            window.fill(black) # Fill screen black
        
            ''' CHECK IF CURRENT SCORE IS A NEW HIGH SCORE '''
            if self.newHighScore:
                self.gameOverText = largeFont.render("CONGRATULATIONS!", True, blue)
                self.finalScoreText = mediumFont.render(f"NEW HIGH SCORE: {self.currentScore}", True, yellow)
            else:
                self.gameOverText = largeFont.render("GAME OVER", True, red)
                self.finalScoreText = mediumFont.render(f"Final Score: {self.currentScore}", True, yellow)
            
            ''' DISPLAY FINAL SCORE '''
            window.blit(self.gameOverText, (windowWidth // 2 - self.gameOverText.get_width() // 2, windowHeight // 3 - 30))
            window.blit(self.finalScoreText, (windowWidth // 2 - self.finalScoreText.get_width() // 2, windowHeight // 2 - 40))

            ''' OPTION TO RETRY '''
            self.retryText = mediumFont.render(f"[Enter] to Retry", True, white)
            window.blit(self.retryText, (windowWidth // 2 - self.retryText.get_width() // 2, windowHeight // 2 + 50))

            ''' OPTION TO RETURN TO START MENU '''
            returnToMenuText = mediumFont.render("[Esc] to Return to Start Menu", True, white)
            window.blit(returnToMenuText, (windowWidth // 2 - returnToMenuText.get_width() // 2, windowHeight // 2 + 100))

            pygame.display.flip() # Update whole screen

            ''' WAIT FOR USER INPUT TO RETRY OR RETURN '''
            inputWait = True
            while inputWait:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT: # Exits window when close button is pressed
                        self.quitGame()
                        return
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN: # Restart the game when enter is pressed
                            self.game = Game(self.difficulty)  # Create a new game instance to restart the game, passes current difficulty 
                            self.game.gameLoop()
                            gameOverRun = False  # Exit game over loop
                        elif event.key == pygame.K_ESCAPE: # Return to start menu when backspace is pressed
                            gameOverRun = False  # Exit game over loop
                            self.returnStart()  # Call start menu function

        self.saveHighScore() # Save high score again for security
        self.resetGame()  # Reset all game states

    def returnStart(self):
        startMenu = StartMenu(self) # Create new start menu instance
        startMenu.display() # Display the start menu

    def quitGame(self):
        pygame.quit()
        quit()

class StartMenu:
    def __init__(self, game):
        self.game = game # Helps in accessing game's current state (difficulty in particular)
        self.difficulty = self.game.difficulty  # Initialize with the game's current difficulty

    ''' DISLAY START MENU SCREEN '''
    def display(self):
        self.difficultyColor = None

        window.fill(black) # Fill screen in black

        ''' TITLE TEXT (centered) '''
        titleText = largeFont.render("MIDNIGHT MOTORIST", True, white)
        window.blit(titleText, (windowWidth // 2 - titleText.get_width() // 2, windowHeight // 4 - 100 ) )

        ''' START TEXT (centered) '''
        startText = mediumFont.render("[Enter] to Start", True, blue)
        window.blit(startText, (windowWidth // 2 - startText.get_width() // 2, windowHeight // 3 - 50))

        ''' HIGH SCORE DISPLAY (centered) '''
        highScoreText = mediumFont.render(f"High Score: {self.game.highScore}", True, yellow)
        window.blit(highScoreText, (windowWidth // 2 - highScoreText.get_width() // 2, windowHeight // 2 - 80))

        '''  RESET HIGH SCORE OPTION (centered) '''
        resetText = mediumFont.render("[R] to Reset High Score", True, yellow)
        resetTextX = (windowWidth // 2) - (resetText.get_width() // 2)
        resetTextY = (windowHeight // 2 - 40)
        window.blit(resetText, (resetTextX, resetTextY))

        ''' DIFFICULTY CHOICE TEXT '''
        if self.difficulty == 'Easy':
            self.difficultyColor = white
        elif self.difficulty == 'Normal':
            self.difficultyColor = green
        elif self.difficulty == 'Hard':
            self.difficultyColor = red
        elif self.difficulty == 'Superhighway':
            self.difficultyColor = magenta
        
        difficultyText = mediumFont.render(f"Difficulty: {self.difficulty}", True, self.difficultyColor)
        window.blit(difficultyText, (windowWidth // 2 - difficultyText.get_width() // 2, windowHeight // 2 + 60))

        ''' DIFFICULTY SELECTION TEXT '''
        easyText = mediumFont.render("1 - Easy", True, white)
        window.blit(easyText, (windowWidth // 3 + 105, windowHeight // 2 + 110))

        mediumText = mediumFont.render("2 - Normal", True, white)
        window.blit(mediumText, (windowWidth // 3 + 100, windowHeight // 2 + 160))

        hardText = mediumFont.render("3 - Hard", True, white)
        window.blit(hardText, (windowWidth // 3 + 100, windowHeight // 2 + 210))

        pygame.display.flip() # Update whole screen

        ''' WAIT FOR USER INPUT '''
        waitforStart = True
        while waitforStart:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game.quitGame() # Exit game if close button is pressed
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN: # Start game when enter is pressed
                        self.game = Game(self.difficulty)  # Create a new game instance to start the game, passes current difficulty 
                        self.game.gameLoop()  # Restart game loop
                        waitforStart = False # Exit start menu loop
                    
                    elif event.key == pygame.K_r:
                        self.confirmReset() # Reset high score when 'R' is pressed

                    elif event.key == pygame.K_1:
                        self.difficulty = 'Easy'
                        self.game.setDifficulty(self.difficulty)  # Set difficulty to easy
                        self.display()

                    elif event.key == pygame.K_2:
                        self.difficulty = 'Normal'
                        self.game.setDifficulty(self.difficulty)  # Set difficulty to normal
                        self.display()

                    elif event.key == pygame.K_3:
                        self.difficulty = 'Hard'
                        self.game.setDifficulty(self.difficulty)  # Set difficulty to hard
                        self.display()

                    elif event.key == pygame.K_4:
                        self.difficulty = 'Superhighway'
                        self.game.setDifficulty(self.difficulty)  # Set difficulty to ...
                        self.display()

    def resetHighScore(self):
        self.game.highScore = 0 # Set high score to zero, effectively resetting it
        self.game.saveHighScore() # Save the new high score (0) to the file
        print ("High score has been reset to 0.") # PRINT TO CONSOLE

    '''DISPLAY RESET HIGH SCORE CONFIRMATION '''
    def confirmReset(self):
        confirmTextSize = pygame.font.Font(pixelFontPath, 35)
        confirmText = confirmTextSize.render("Are you sure you want to reset your high score? (Y/N)", True, white)
        window.fill(black) # CLear the window
        window.blit(confirmText, (windowWidth // 2 - confirmText.get_width() // 2, windowHeight // 2 - confirmText.get_height() // 2))

        pygame.display.flip() # Update whole screen

        ''' WAIT FOR USER INPUT TO CONFIRM OR CANCEL '''
        confirmWait = True
        while confirmWait:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: # Exit game when close button is pressed
                    self.game.quitGame()
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_y:  # Confirm reset when 'Y' is pressed
                        self.resetHighScore()
                        confirmWait = False  # Exit confirmation loop
                        self.display() # Return to start menu display
                    elif event.key == pygame.K_n:  # Cancel reset when 'N' is pressed
                        confirmWait = False  # Exit confirmation loop
                        self.display() # Return to start menu display

''' START THE GAME :)'''
if __name__ == "__main__": # Check if current script is run as main program
    gameInstance = Game() # Create instance of entire game class
    startMenu = StartMenu(gameInstance) # Allows start menu to access current game difficulty
    startMenu.display() # Show start menu upon opening the program

# Entry point for running the program