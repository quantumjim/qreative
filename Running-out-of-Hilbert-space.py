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
    circle.append('                   ·             ·                  ')
    circle.append('                   ·    '+get_percentage(stats,universe)+'   ·                  ') 
    circle.append('                   ·             ·                  ')
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

def universe_description(num):
    
    universes = ["".join(seq) for seq in itertools.product("01", repeat=num)]

    description = {}
    for universe in universes:
        description[universe] = ""
        
    return description




length = 30
samples = 1

device = 'ibmqx4'
num = 5

# generate an initial starting pos
pos = ''
for n in range(num):
    pos += random.choice(['0','1'])

# generate an initial pos for the target
distance = 0
while distance <3:
    target = ''
    for n in range(num):
        target += random.choice(['0','1'])
    distance = calculate_distance(target,pos)
    
# initialize the walk
w = walker(length,device,start=target,samples=samples,method='load')
target = w.start # only does somethng when data='load'
full_stats = w.stats
starts = w.starts

steps = length
score = 100
sample = random.choice(range(len( full_stats )))

while pos!=target and steps>=0:
    
    steps -= 1

    clear_screen()

    print("==== You have " + str(steps+1) + " moves until the end of the multiverse! ===\n\nScore = " + str(score) + "\n")
    
    stats = full_stats[sample][steps]
    target = starts[sample]
        
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

    unmoved = True
    while unmoved:

        direction = input("\nInput the number for the portal you want to use (1, 2, 3, 4 or 5)...\n")
        print("")

        try:
            pos = get_neighbour(pos,int(direction)-1)
            unmoved = False
        except Exception as e:
            print(e)
            print("That's not a valid direction. Try again")
            
    if pos in stats:
        score += np.log(stats[pos])/np.log(2)
    else:
        score = 0

if pos==target:           
    print('==== You saved the multiverse! ====')
    print('Final score: ' + str(score) + "\n\n")
else:
    print('==== The multiverse has been destroyed! ====')
    
