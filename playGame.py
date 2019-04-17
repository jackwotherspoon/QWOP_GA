#Author: Jack Wotherspoon

from PIL import Image
import pytesseract
from selenium import webdriver
import keyboard
import _thread as thread
import random
import re
import time

class GeneticAlg(object):
    def __init__(self):
        self.driver = webdriver.Chrome() #initialize chrome to be able to create game window
        self.driver.set_window_size(638, 515)   #create chrome game window
        self.keyboard = keyboard
        self.population = []            #initialize population to empty set
        self.alive = True
        self.population_size = 10       #initialize population size
        self.mutation_rate = 10         #initialize mutation rate of 10%
        self.score = 0.0                #initialize score to 0
        self.time_limit = 120  # Seconds
        self.delta = 1
        self.iteration=0
        self.generation=0

    def generate_dna(self):    #different keypress combos are the DNA
        chromosomes = [
            "q",
            "w",
            "o",
            "p",
            "qw",
            "qo",
            "qp",
            "qo",
            "wp",
            "op",
            "qwo",
            "wop",
            "qop"
            "qwp",
            "qwop"
        ]
        self.start_time = time.time()
        dna = []

        for chromosome in range(10):  #make chain of 10 pieces of dna and generate a time pressed for each
            dna.append(
                (random.choice(chromosomes), self.generate_time())
            )
        return dna

    def generate_time(self):
        return random.randint(50, 3000) / 1000 #generate random time between .005 and 3 seconds

    def generate_population(self):
        self.population = []
        for x in range(self.population_size):
            dna = self.generate_dna()
            self.population.append(dna)

    def reproduce(self, org1, org2):    #mate function for reproduction and to create children
        visited = {}
        population = []
        for x in range(self.population_size): #for each organism in population
            position = random.randint(0, len(org1)) #grab crossover position randomly
            print("Position :",position)
            if not visited.get(position):
                visited[position] = True
                if random.randint(0, 100) > 50: #random integer between 0 and 100 and check if greater than 50, this randomly chooses order to crossover parents
                    child = org1[0:position] + org2[position:]  #implement crossover
                    print("Child :",child)
                    if random.randint(0, 100) <= self.mutation_rate: #if random integer between 0 and 100 is less than mutation rate than mutation occurs, ie mututation rate of 10 gives 10% chance of mutation
                        print("MUTATED")
                        index = random.randint(0, len(child) - 1) #grab random index within size of child to mutate
                        child[index] = self.generate_dna()[0]   #generate new piece of dna for the chosen index
                        print("Child after mutation: ",child)
                    population.append(child)
                else:           #if random int was not > 50 crossover parents in different order, rest is same as above
                    child = org2[0:position] + org1[position:]
                    if random.randint(0, 100) < self.mutation_rate:
                        print("MUTATED")
                        index = random.randint(0, len(child) - 1)
                        child[index] = self.generate_dna()[0]
                    population.append(child)
            else:
                population.append(self.generate_dna())

        print("Offspring: ", population)
        self.population = population

    def restart_game(self): #restart function to reset score and get runner off game over screen
        self.score = 0.0
        self.keyboard.press_and_release('space')

    def check_done(self):   #function to check if game is won
        self.driver.get_screenshot_as_file('qwop.png') #screenshot the QWOP screen
        img = Image.open('qwop.png').convert('LA')     #greyscale the image to perform better with tesseract
        img.save('grey.png')    #save greyscale
        text_on_screen = pytesseract.image_to_string(img)   #use tesseract on image
        is_done = 'everyone is a winner' in text_on_screen or 'PARTICI PANT' in text_on_screen or 'PARTICIPANT' in text_on_screen\
                  or 'NATIONAL' in text_on_screen or 'HERO' in text_on_screen           #check if winning phrases are on screen to show that you have won

        score_filtered = re.findall("(\-?[0-9]+\.[0-9]+) metres", text_on_screen)    #grabs distance ran from screen
        print(score_filtered)   #print distance ran
        if score_filtered:
            self.score = float(score_filtered[0])/self.delta  #calculate fitness score
        if "NATIONAL" in text_on_screen or "HERO" in text_on_screen and self.score < 100: #if won
            self.score = 100    #score is 100 if you have won game
        return is_done

    def main(self):

        self.openGame()             #open QWOP game screen
        input("Tap to start")       #prompt user to press a button to start
        print("Starting...")
        time.sleep(5) #5 seconds to get back to chrome game window
        self.generate_population()  #generate initial population
        parent1 = parent2 = None    #initialize parents to none
        while True:                 #infinite loop to keep game running until program is halted
            print("Mom:", parent1)
            print("Dad:", parent2)
            for org in self.population: #for each organism within population
                print(org)
                is_done = self.check_done() #continuously check if won
                thread.start_new_thread(self.run, (org,))
                self.start_time = time.time()
                while not is_done:  #while not won
                    print("ELAPSED TIME:", time.time() - self.start_time) #grab current runs time
                    is_done = self.check_done()         #check if won
                self.delta = time.time() - self.start_time      #grab current runs time and save it to delta

                print("Last run: ", self.score, self.delta)     #print last runs score and time
                print("Mom: ", parent1)
                print("Dad: ", parent2)

                if not parent1:
                    parent1 = (org, self.score, self.delta) #if there is no parent1 then first run is parent1
                elif not parent2:
                    parent2 = (org, self.score, self.delta) #if there is no parent2 then second run is parent2
                elif parent1[1] >= 100 and self.score >= 100: #if winning time is better
                    if parent1[2] > self.delta and self.delta >= 60:
                        print("Better time for Mom")
                        parent2 = parent1
                        parent1 = (org, self.score, self.delta)
                elif parent2[1] >= 100 and self.score >= 100: #if winning time is better
                    if parent2[2] > self.delta and self.delta >= 60:
                        print("Better time for Dad")
                        parent2 = (org, self.score, self.delta)
                elif self.score > 0 and parent1[1] < self.score: #if current runs score is better than parent1 score make it new parent1 and make parent2 old parent1
                    print("New Mom Found")
                    parent2 = parent1
                    parent1 = (org, self.score, self.delta)
                elif self.score > 0 and parent2[1] < self.score: #if current run is better than parent2 but less than parent 1 update current run to new parent2
                    print("New Dad Found")
                    parent2 = (org, self.score, self.delta)
                self.alive = False #if runner falls over he is no longer alive
                self.restart_game() #call function to restart game
                self.alive = True   #set runner to back alive
                print("Restarting...")
                self.iteration += 1     #update iteration count
                print("Epoch: ",self.iteration)
            print("Reproducing...")
            self.reproduce(parent1[0], parent2[0]) #after each organism in population has run, reproduce to make new generation
            self.generation+=1 #update generation count
            print("Generation: ", self.generation)

    def run(self, dna):
        print("DNA:")
        while self.alive: #while runner is running
            for keys in dna:    #for the chromosomes in the DNA
                if not self.alive:  #if runner has fallen break
                    break
                for key in keys[0]: #grab combination of keyboard keys in DNA
                    self.keyboard.press(key)    #press the grabbed keyboard keys
                time.sleep(keys[1])       #hold keyboard press for generated time in dna
                for key in keys[0]:  #release pressed keys
                    self.keyboard.release(key)

    def openGame(self): #open game function that pops up game window
        self.driver.get("http://www.foddy.net/Athletics.html")  #get url for game window


if __name__ == "__main__":
    GeneticAlg().main()
