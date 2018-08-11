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
    
def universe_and_neighbours(universe,requested=False):
    
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
    circle.append(' ·    '+get_percentage(stats,neighbours[4])+'   ·         [1]         ·    '+get_percentage(stats,neighbours[1])+'   · ')
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






length = 30
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
w = walker(length,num,target)

steps = length
score = 100
while pos!=target and steps>=0:
    
    steps -= 1

    clear_screen()
    print("==== You have " + str(steps+1) + " moves until the end of the multiverse! ===\n\nScore = " + str(score) + "\n")
    
    stats = w.get_step(steps)
    
    universe_and_neighbours(pos)

    unmoved = True
    while unmoved:

        direction = input("Input the number for the direction you want to move (1, 2, 3, 4 or 5)\n")
        print("")

        try:
            pos = get_neighbour(pos,int(direction)-1)
            unmoved = False
        except Exception as e:
            print(e)
            print("That's not a valid direction. Try again")
            
    score += np.log(stats[pos])/np.log(2)

if pos==target:           
    print('==== You saved the multiverse! ====')
    print('Final score: ' + str(score))
else:
    print('==== The multiverse has been destroyed! ====')
    
