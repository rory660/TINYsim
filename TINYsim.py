registry = [0x0,0x0,0x0,0x0]
memory = [0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0]
action = ["","","",""]
inQueue = []
outQueue = []
stop = False
reason = ""

def hexToString(hexIn):
	if hexIn>9:
		hexOut = str(hex(hexIn))[-1].upper()
	else:
		hexOut = str(hexIn)
	return hexOut

def stringToHex(stringIn):
	if stringIn == "A":
		return 10
	if stringIn == "B":
		return 11
	if stringIn == "C":
		return 12
	if stringIn == "D":
		return 13
	if stringIn == "E":
		return 14
	if stringIn == "F":
		return 15
	return int(stringIn)

def incrementIP(amount):
	registry[0]+=amount
	if registry[0]>=16:
		registry[0]-=16

def setAction(newAction):
	for i in range(len(newAction)):\
		action[i] = newAction[i]

def printState():
	printString = ""
	for i in registry:
		printString+=hexToString(i) + " "
	printString+= " "
	for i in memory:
		printString+=hexToString(i)
	printString+= " "
	for i in action:
		printString+= " " + i
	print printString

def HLT():
	setAction(["HLT","-","-","-"])
	printState()
	registry[2] = registry[2] | 0b1000
	incrementIP(1)
	setAction(["","","",""])
	printState()
	global stop
	stop = True
	global reason
	reason = "Halted Normally"

def JMP():
	setAction(["JMP",hexToString(memory[registry[0]+1]),"-","-"])
	printState()
	registry[0] = memory[registry[0]+1]
	

def JZE():
	setAction(["JZE",hexToString(memory[registry[0]+1]),"-","-"])
	printState()
	if registry[2] & 0b10 == 0b10:
		registry[0] = memory[registry[0]+1]
	else:
		incrementIP(2)
	

def JNZ():
	setAction(["JNZ",hexToString(memory[registry[0]+1]),"-","-"])
	printState()
	if registry[2] & 0b10 != 0b10:
		registry[0] = memory[registry[0]+1]
	else:
		incrementIP(2)
	

def LDA():
	setAction(["LDA",hexToString(memory[registry[0]+1]),"-","-"])
	printState()
	registry[3] = memory[memory[registry[0]+1]]
	if registry[3] == 0:
		registry[2] = registry[2] | 0b10
	else:
		registry[2] = registry[2] & 0b1101
	incrementIP(2)

def STA():
	setAction(["STA",hexToString(memory[registry[0]+1]),"-","-"])
	printState()
	memory[memory[registry[0]+1]] = registry[3]
	incrementIP(2)

def GET():
	if len(inQueue) != 0:
		setAction(["GET","-",hexToString(inQueue[0]),"-"])
		printState()
		registry[3] = inQueue[0]
		del inQueue[0]
		if registry[3] == 0:
			registry[2] = registry[2] | 0b10
		else:
			registry[2] = registry[2] & 0b1101
	else:
		setAction(["GET","-","-","-"])
		printState()
		global stop
		stop = True
		global reason
		reason = "Starved For Input"
	incrementIP(1)

def PUT():
	setAction(["PUT","-","-",hexToString(registry[3])])
	printState()
	outQueue.append(registry[3])
	incrementIP(1)

def ROL():
	setAction(["ROL","-","-","-"])
	printState()
	x = registry[3] & 0b1000
	registry[3] = registry[3]*2 + (registry[2] & 0b1)
	if registry[3] >=16:
		registry[3] -= 16
		registry[2] = registry[2] | 0b1
	else:
		registry[2] = registry[2] & 0b1110
	if registry[3] & 0b1000 != x:
		registry[2] = registry[2] | 0b100
	else:
		registry[2] = registry[2] & 0b011
	if registry[3] == 0:
		registry[2] = registry[2] | 0b10
	else:
		registry[2] = registry[2] & 0b1101
	incrementIP(1)

def ROR():
	setAction(["ROR","-","-","-"])
	printState()
	x = registry[3] & 0b1000
	if registry[3] % 2 == 0:
		registry[3]/=2
		registry[2] = registry[2] & 0b1110
	else:
		registry[3] = (registry[3]-1) / 2
		registry[2] = registry[2] | 0b1
	if registry[3] & 0b1000 != x:
		registry[2] = registry[2] | 0b100
	else:
		registry[2] = registry[2] & 0b011
	if registry[3] == 0:
		registry[2] = registry[2] | 0b10
	else:
		registry[2] = registry[2] & 0b1101
	incrementIP(1)

def ADC():
	setAction(["ADC",hexToString(memory[registry[0]+1]),"-","-"])
	printState()
	carry = 0
	if (registry[3] & 0b1) + (memory[memory[registry[0]+1]] & 0b1) + (registry[2] & 0b1) >= 2:
		carry = 1
	else:
		carry = 0
	if (registry[3] & 0b10)/2 + (memory[memory[registry[0]+1]] & 0b10)/2 + carry >= 2:
		carry = 1
	else:
		carry = 0
	if (registry[3] & 0b100)/4 + (memory[memory[registry[0]+1]] & 0b100)/4 + carry >= 2:
		carry = 1
	else:
		carry = 0
	if (registry[3] & 0b1000)/8 + (memory[memory[registry[0]+1]] & 0b1000)/8 + carry >= 2:
		carry2 = 1
	else:
		carry2 = 0
	if carry2 == carry:
		registry[2] = registry[2] & 0b1011
	else:
		registry[2] = registry[2] | 0b0100
	registry[3] = registry[3] + (registry[2] & 0b1) + memory[memory[registry[0]+1]]
	if registry[3] >=16:
		registry[3] -= 16
		registry[2] = registry[2] | 0b1
	else:
		registry[2] = registry[2] & 0b1110
	if registry[3] == 0:
		registry[2] = registry[2] | 0b10
	else:
		registry[2] = registry[2] & 0b1101
	incrementIP(2)

def CCF():
	setAction(["CCF","-","-","-"])
	printState()
	registry[2] = registry[2] & 0b1110
	incrementIP(1)

def SCF():
	setAction(["SCF","-","-","-"])
	printState()
	registry[2] = registry[2] | 0b0001
	incrementIP(1)

def DEL():
	setAction(["DEL","-","-","-"])
	printState()
	registry[1]-=1
	if registry[1]<0:
		registry[1]+=16
	if registry[1] == 0:
		registry[2] = registry[2] | 0b0010
	else:
		registry[2] = registry[2] & 0b1101
	incrementIP(1)

def LDL():
	setAction(["LDL",hexToString(memory[registry[0]+1]),"-","-"])
	printState()
	registry[1] = memory[memory[registry[0]+1]]
	if registry[1] == 0:
		registry[2] = registry[2] | 0b0010
	else:
		registry[2] = registry[2] & 0b1101
	incrementIP(2)

def FLA():
	setAction(["FLA","-","-","-"])
	printState()
	registry[3] = 15 - registry[3]
	if registry[3]<0:
		registry[3]+=16
	if registry[3] == 0:
		registry[2] = registry[2] | 0b0010
	else:
		registry[2] = registry[2] & 0b1101
	incrementIP(1)
inputString = raw_input("Enter input queue (Format: x, x, x, x...): ")
inputString = inputString.replace(", ","")
for char in inputString:
	inQueue.append(stringToHex(char))
inputString = raw_input("Enter TINY configuration (Format: x x x x  xxxxxxxxxxxxxxx): ")
inputString = inputString.replace(" ","")
inputNumList = []
x = 0
for char in inputString:
	if x<20:
		if x<4:
			registry[x] = stringToHex(char)
		else:
			memory[x-4] = stringToHex(char)
	x+=1

count = 0
while not stop:
	if count >=500:
		stop = True
		reason = "Loops Henceforth"
	if memory[registry[0]] == 0:
		HLT()
	elif memory[registry[0]] == 1:
		JMP()
	elif memory[registry[0]] == 2:
		JZE()
	elif memory[registry[0]] == 3:
		JNZ()
	elif memory[registry[0]] == 4:
		LDA()
	elif memory[registry[0]] == 5:
		STA()
	elif memory[registry[0]] == 6:
		GET()
	elif memory[registry[0]] == 7:
		PUT()
	elif memory[registry[0]] == 8:
		ROL()
	elif memory[registry[0]] == 9:
		ROR()
	elif memory[registry[0]] == 10:
		ADC()
	elif memory[registry[0]] == 11:
		CCF()
	elif memory[registry[0]] == 12:
		SCF()
	elif memory[registry[0]] == 13:
		DEL()
	elif memory[registry[0]] == 14:
		LDL()
	elif memory[registry[0]] == 15:
		FLA()
	count+=1
print reason