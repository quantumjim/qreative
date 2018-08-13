# coding: utf-8

from creative import *

def clear_screen():

    for _ in range(50):
        print("")

def get_percentage(stats,string):
    
    if string not in stats:
        percentage = "00.00%"
    else:
        percentage = str(round(stats[string]*100,2)) + "%"
        
    percentage = " "*(6-len(percentage)) + percentage
        
    return percentage

def get_neighbour(string,n):
    
    neighbour = ''
    for m in range(num):
        if n!=m:
            neighbour += string[m]
        else:
            neighbour += '0'*(string[m]=='1') + '1'*(string[m]=='0')
            
    return neighbour
    
def universe_and_neighbours(stats,universe,requested=False):
    
    neighbours = []
    for n in range(num):
        neighbour = get_neighbour(universe,n)
        neighbours.append(neighbour)
                
    circle = []
    circle.append('\n                     |  |   |  |                    ')
    circle.append('                     |. · ˙ · .|                    ')
    circle.append('                    ·           ·                   ')
    circle.append('                   ·             ·                  ')
    circle.append('                   ·    '+get_percentage(stats,neighbours[0])+'   ·                  ') 
    circle.append('                   ·             ·                  ')
    circle.append('----. · ˙ · .       ·           ·      . · ˙ · .----')
    circle.append('  ·           ·       ˙·  .  ·˙      ·           ·  ')
    circle.append('-·             ·          |         ·             ·-')
    circle.append(' ·    '+get_percentage(stats,neighbours[4])+'   ·         [1]        ·    '+get_percentage(stats,neighbours[1])+'   · ')
    circle.append('-·             ·\         |        /·             ·-')
    circle.append('  ·           · [5]   . · ˙ · .  [2] ·           ·  ')
    circle.append('----˙·  .  ·˙     \ ·           ·/     ˙·  .  ·˙----')
    circle.append('                   ·    Your     ·                  ')
    circle.append('                   ·   current   ·                  ') 
    circle.append('                   ·   universe  ·                  ')
    circle.append('                    ·           ·                   ')
    circle.append('                    / ˙·  .  ·˙  \                  ')
    circle.append('      . · ˙ · .   [4]            [3]  . · ˙ · .     ')
    circle.append('    ·           · /                \·           ·   ')
    circle.append('   ·             ·                 ·             ·  ')
    circle.append('   ·    '+get_percentage(stats,neighbours[3])+'   ·                 ·    '+get_percentage(stats,neighbours[2])+'   ·  ') 
    circle.append('   ·             ·                 ·             ·  ')
    circle.append('    ·           ·                   ·           ·   ')
    circle.append('     |˙·  .  ·˙|                     |˙·  .  ·˙|    ')
    circle.append('     |  |   |  |                     |  |   |  |    \n\n')

    for line in circle:
        print(line)
        
def calculate_distance(string1,string2):
    
    distance = 0
    for b1,b2 in zip (string1,string2):
        distance += (b1!=b2)
        
    return distance

def universe_descriptions():
    
    description = {}
    
    description['00000'] = "Your current universe has subspace and warp fields and Jean-Luc Picard."
    description['00001'] = "Your current universe is the dream of the Wind Fish."
    description['00010'] = "In your current universe, all emergency services are staffed by anthropomorphic dogs."
    description['00011'] = "Your current universe is host to an eternal war between butterflies and moths."
    description['00100'] = "In your current universe, 'Hello Quantum' was the top mobile game of 2018."
    description['00101'] = "In your curent universe, the ever changing nature of the Klingons makes complete sense."
    description['00110'] = "Your current universe was messed up by a idiot speedster who keeps messing things up."
    description['00111'] = "Your current universe is one where Ganondorf gets forever stuck in the Water Temple."
    description['01000'] = "Your current universe has a weird vibe."
    description['01001'] = "Your current universe is our universe! It has the best cosmic microwave backround in the multiverse!"
    description['01010'] = "Your current universe is the only one where QISKit is not the best way to program quantum computers."
    description['01011'] = "Your current universe is the crossover universe for Marvel, DC and the Beano."
    description['01100'] = "Your current universe has a faint but noticable smell of cheese."
    description['01101'] = "Your current universe is the one where musicals happen."
    description['01110'] = "Your current universe defies explantion."
    description['01111'] = "Your current universe has the weird kind of physics you often get in sci-fi."   
    description['10000'] = "Your current universe is the only one where my kids go to bed at a reasonable hour."
    description['10001'] = "Your current universe is the one where genocidal plumbers gain royal favour."
    description['10010'] = "Your current universe is one that my parents wouldn't let me go to."
    description['10011'] = "Your current universe is the ne where the 'Superman's Girl Friend, Lois Lane' comics were set."
    description['10100'] = "Your current universe is not on any maps, and seems to be full of dragons."
    description['10101'] = "In your current universe, Sega still makes consoles."
    description['10110'] = "Your current universe is cooler that you'll ever be."
    description['10111'] = "Your current universe is in need of a proper tidy."
    description['11000'] = "In your current universe, the Golden Gate Bridge is a nice shade of azure."
    description['11001'] = "Your current universe is one where Hylians evolve into fluffy pink rabbits."
    description['11010'] = "Your current universe is where giant reptiles prefer karting to kidnapping."
    description['11011'] = "Your current universe has Luigi as player one. It is better in every way."
    description['11100'] = "Your current universe is just a spare. It's where all the other universes keep their clutter."
    description['11101'] = "In your current universe, Monty Python's flying circus doesn't seem at all absurd."
    description['11110'] = "Your current universe is one where you didn't say that stupid thing."
    description['11111'] = "Your current universe has advanced technology and space wizards, but everyone still fights with swords for some reason." 
    
    return description

def get_distant (string):
    
    distance = 0
    while distance <3:
        distant_pos = ''
        for n in range(num):
            distant_pos += random.choice(['0','1'])
        distance = calculate_distance(distant_pos,string)
        
    return distant_pos

def intro():
    
    clear_screen()
    print("       ▄█    █▄    ███    █▄  ███▄▄▄▄       ███              ███        ▄█    █▄       ▄████████    ")
    print("      ███    ███   ███    ███ ███▀▀▀██▄ ▀█████████▄      ▀█████████▄   ███    ███     ███    ███   ")
    print("      ███    ███   ███    ███ ███   ███    ▀███▀▀██         ▀███▀▀██   ███    ███     ███    █▀    ")
    print("     ▄███▄▄▄▄███▄▄ ███    ███ ███   ███     ███   ▀          ███   ▀  ▄███▄▄▄▄███▄▄  ▄███▄▄▄       ")
    print("    ▀▀███▀▀▀▀███▀  ███    ███ ███   ███     ███              ███     ▀▀███▀▀▀▀███▀  ▀▀███▀▀▀       ")
    print("      ███    ███   ███    ███ ███   ███     ███              ███       ███    ███     ███    █▄    ")
    print("      ███    ███   ███    ███ ███   ███     ███              ███       ███    ███     ███    ███   ")
    print("      ███    █▀    ████████▀   ▀█   █▀     ▄████▀           ▄████▀     ███    █▀      ██████████   ")
    print("                                                                                                   ")
    print("    ████████▄   ███    █▄     ▄████████ ███▄▄▄▄       ███        ▄███████▄ ███    █▄     ▄████████ ")
    print("    ███    ███  ███    ███   ███    ███ ███▀▀▀██▄ ▀█████████▄   ███    ███ ███    ███   ███    ███ ")
    print("    ███    ███  ███    ███   ███    ███ ███   ███    ▀███▀▀██   ███    ███ ███    ███   ███    █▀  ")
    print("    ███    ███  ███    ███   ███    ███ ███   ███     ███   ▀   ███    ███ ███    ███   ███        ")
    print("    ███    ███  ███    ███ ▀███████████ ███   ███     ███     ▀█████████▀  ███    ███ ▀███████████ ")
    print("    ███    ███  ███    ███   ███    ███ ███   ███     ███       ███        ███    ███          ███ ")
    print("    ███  ▀ ███  ███    ███   ███    ███ ███   ███     ███       ███        ███    ███    ▄█    ███ ")
    print("     ▀██████▀▄█ ████████▀    ███    █▀   ▀█   █▀     ▄████▀    ▄████▀      ████████▀   ▄████████▀  ")
    print("    ")
    print("    ")
    print("                             AKA 'Running out of Hilbert space'")
    print("                      The 1st Ludum Dare game to run on a quantum computer")
    print("    ")
    print("                      By James Wootton, University of Basler and QISKitter")
    print("                        twitter.com/decodoku        github.com/quantumjim")
    print("    ")
    print("    ")
    input("Press any key to continue...\n")
    input("In the beginning, a quantum computer created the multiverse...")
    input("It was called the 'Quantum Production of Universes System', or 'Quantpus'...")
    input("Though it has lain dormant for eons, it has suddenly started to malfunction...")
    input("It is running the universe creation program backwards, causing the multiverse to collapse...")
    input("Your job is to find and fix it, before it is too late...")
    input("Use portals to move between universes, but be careful...")
    input("If you enter a universe with less than 0.5% strength, you might cease to exist...")
    input("There will become increasinly more of these as the multiverse collapses around you...")
    input("And beware of malfunctioning portals, which would also lead to your annihilation...")
    input("But if you find the universe where the quantpus is hidden, everything will be fine...")
    input("The quantpus' universe will typically have a high strength, and will get stronger as everything collapses into it...")
    input("That's the only clue we have as to where it is, so good luck!...")

def play_game():

    description = universe_descriptions()
    

    intro()
    

    # initialize the walk
    w = walker(length,device,samples=samples,method='load')
    full_stats = w.stats
    sample = random.choice(range(len( full_stats )))
    starts = w.starts
    
    target = starts[sample]
    
    # generate an initial starting pos
    pos = get_distant(target) 

    steps = length
    immunity = 3
    sample = random.choice(range(len( full_stats )))
    direction = 0

    while pos!=target and steps>=0:

        steps -= 1
        immunity -= 1
        
        stats = full_stats[sample][steps]
        
        if pos in stats:
            if stats[pos]<0.005:
                if immunity <=0:
                    if random.random()<0.5:
                        steps = -1
        else:
            steps = -1

        clear_screen()

        print("\n-----------> You have " + str(steps+1) + " moves until the multiverse is destroyed!")
        print("\n             " + description[pos])

        universe_and_neighbours(stats,pos)

        print("\nThe highest strength universes can be reached by the following routes (portals can be used in any order)\n")
        sorted_strings = sorted(stats,key=stats.get)[::-1]
        for j in range(min(len(sorted_strings),3)):
            portals = ""
            for n in range(num):
                if sorted_strings[j][n]!=pos[n]:
                    portals += str(n+1) + "--"

            if sorted_strings[j]!=pos:
                print("    * The route --" + portals + " leads to a universe with strength " + get_percentage(stats,sorted_strings[j]) )
        
        dodgy_portal = 0
        if random.random()<0.25:
            dodgy_portal = random.choice( range(1,num+1) )
            if dodgy_portal==direction:
                dodgy_portal = 0 

        unmoved = True
        while unmoved:
            
            if dodgy_portal!=0:
                print("\n\n-----> WARNING: Scans suggest that a nearby portal is malfunctioning (not the one you just used).")
            
            direction = input("\nInput the number for the portal you want to use (1, 2, 3, 4 or 5)...\n")
            print("")
            
            if direction==dodgy_portal:
                steps= - 1
                print('hi')

            try:
                pos = get_neighbour(pos,int(direction)-1)
                unmoved = False
            except Exception as e:
                print(e)
                print("That's not a valid direction. Try again")
                
        #print(steps)

    if pos==target:           
        print('-----------> You saved the multiverse :)\n\n\n')
    elif steps==-1:
        print('-----------> You ceased to exist :(\n\n\n')
    else:
        print('-----------> The multiverse has been destroyed :(\n\n\n')

        

length = 30
samples = 10

device = 'ibmqx4'
num = 5
        
play_game()