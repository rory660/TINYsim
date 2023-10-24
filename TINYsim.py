class Trace:
    def __init__(self):
        self.memory = [0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0]
        self.registry = [0x0,0x0,0x0,0x0]
        self.action = ["", "", "", ""]
        self.inQueue, self.outQueue = [], []
        self.stop = False
        self.reason = ""
        
    def takeInitialInput(self):
        inpStr = input('Enter input queue (Format: x, x, x, x...) - ').replace(', ', "")
        for char in inpStr: self.inQueue.append(self.strToHex(char))
        
        inpStr = input('Enter TINY configuration (Format: x x x x xxxxxxxxxxxxxxx) - ').replace(" ", "")

        x = 0
        
        for char in inpStr:
            if x < 20:
                if x < 4:  self.registry[x] = self.strToHex(char)
                else: self.memory[x-4] = self.strToHex(char)
                
            x += 1
        
        print(self.memory)
        
    @staticmethod
    def hexToStr(hexIn) -> str:
        if hexIn > 9: hexOut = str(hex(hexIn))[-1].upper()
        else: hexOut = str(hexIn)
        print(hexOut)
        return hexOut

    @staticmethod
    def strToHex(stringIn:str) -> int:
        print(stringIn)
        
        if stringIn == 'A': return 10
        elif stringIn == 'B': return 11
        elif stringIn == 'C': return 12
        elif stringIn == 'D': return 13
        elif stringIn == 'E': return 14
        elif stringIn == 'F': return 15
        else: int(stringIn) 
        
        # match stringIn:
        #     case 'A': return 10
        #     case 'B': return 11
        #     case 'C': return 12
        #     case 'D': return 13
        #     case 'E': return 14
        #     case 'F': return 15
        #     case _: int(stringIn)
            
    def printState(self) -> None:
        printStr = ''
        
        for pos in self.registry: printStr += self.hexToStr(pos) + '  '
        for pos in self.memory: printStr += self.hexToStr(pos) + ' '
        for pos in self.action: printStr += ' ' + pos
        
        print(printStr)
        
    def incrementIP(self, amt:int) -> None:
        self.registry[0] += amt
        if self.registry[0] >= 16: self.registry[0] -= 16
        
    def setAction(self, actionList:list[str]) -> None:
        for i in range(len(actionList)): self.action[i] = actionList[i]
        
class Operators:
	def __init__(self, trace:Trace): self.trace = trace
    
	def HLT(self) -> None:
		self.setAction(["HLT","-","-","-"])
		self.printState()
		
		self.registry[2] = self.registry[2] or 0b1000
		self.incrementIP(1)
		
		self.setAction(["","","",""])
		self.printState()
		
		global stop
		stop = True
		global reason
		reason = "Halted Normally"

	def JMP(self) -> None:
		self.setAction(["JMP", self.hexToString(self.memory[self.registry[0]+1]), "-", "-"])
		self.printState()
  
		self.registry[0] = self.memory[self.registry[0]+1]

	def JZE(self) -> None:
		self.setAction(["JZE", self.hexToString(self.memory[self.registry[0]+1]), "-", "-"])
		self.printState()
  
		if self.registry[2] & 0b10 == 0b10: self.registry[0] = self.memory[self.registry[0]+1]
		else: self.incrementIP(2)

	def JNZ(self) -> None:
		self.setAction(["JNZ", self.hexToString(self.memory[self.registry[0]+1]), "-", "-"])
		self.printState()
  
		if self.registry[2] & 0b10 != 0b10: self.registry[0] = self.memory[self.registry[0]+1]
		else: self.incrementIP(2)

	def LDA(self) -> None:
		self.setAction(["LDA", self.hexToString(self.memory[self.registry[0]+1]),"-","-"])
		self.printState()
	
		self.registry[3] = self.memory[self.memory[self.registry[0]+1]]

		if self.registry[3] == 0: self.registry[2] = self.registry[2] or 0b10
		else: self.registry[2] = self.registry[2] & 0b1101
	
		self.incrementIP(2)

	def STA(self) -> None:
		self.setAction(["STA", self.hexToString(self.memory[self.registry[0]+1]), "-", "-"])
		self.printState()
	
		self.memory[self.memory[self.registry[0]+1]] = self.registry[3]
		self.incrementIP(2)

	def GET(self) -> None:
		if len(self.inQueue) != 0:
			self.setAction(["GET", "-", self.hexToString(self.inQueue[0]), "-"])
			self.printState()
	
			self.registry[3] = self.inQueue[0]
			del self.inQueue[0]
	
			if self.registry[3] == 0: self.registry[2] = self.registry[2] or 0b10
			else: self.registry[2] = self.registry[2] and 0b1101
		else:
			self.setAction(["GET","-","-","-"])
			self.printState()
	
			self.stop = True
			self.reason = "Starved For Input"
		self.incrementIP(1)

	def PUT(self) -> None:
		self.setAction(["PUT", "-", "-", self.hexToString(self.registry[3])])
		self.printState()
	
		self.outQueue.append(self.registry[3])
		self.incrementIP(1)

	def ROL(self) -> None:
		self.setAction(["ROL", "-", "-", "-"])
		self.printState()
	
		x = self.registry[3] and 0b1000
		self.registry[3] = self.registry[3] * 2 + (self.registry[2] and 0b1)
	
		if self.registry[3] >= 16:
			self.registry[3] -= 16
			self.registry[2] = self.registry[2] or 0b1
	
		else: self.registry[2] = self.registry[2] and 0b1110
	
		if self.registry[3] and 0b1000 != x: self.registry[2] = self.registry[2] or 0b100
		else: self.registry[2] = self.registry[2] and 0b011
	
		if self.registry[3] == 0: self.registry[2] = self.registry[2] or 0b10
		else: self.registry[2] = self.registry[2] and 0b1101
	
		self.incrementIP(1)

	def ROR(self) -> None:
		self.setAction(["ROR", "-", "-", "-"])
		self.printState()
  
		x = self.registry[3] and 0b1000
  
		if self.registry[3] % 2 == 0:
			self.registry[3] /= 2
			self.registry[2] = self.registry[2] and 0b1110
		else:
			self.registry[3] = (self.registry[3] - 1) / 2
			self.registry[2] = self.registry[2] or 0b1
		if self.registry[3] & 0b1000 != x:
			self.registry[2] = self.registry[2] or 0b100
		else:
			self.registry[2] = self.registry[2] and 0b011
		if self.registry[3] == 0:
			self.registry[2] = self.registry[2] or 0b10
		else:
			self.registry[2] = self.registry[2] and 0b1101
   
		self.incrementIP(1)

	def ADC(self) -> None:
		self.setAction(["ADC", self.hexToString(self.memory[self.registry[0]+1]), "-", "-"])
		self.printState()
		carry = 0
  
		if (self.registry[3] and 0b1) + (self.memory[self.memory[self.registry[0]+1]] and 0b1) + (self.registry[2] and 0b1) >= 2: carry = 1
		else: carry = 0
   
		if (self.registry[3] & 0b10) / 2 + (self.memory[self.memory[self.registry[0]+1]] and 0b10) / 2 + carry >= 2: carry = 1
		else: carry = 0
  
		if (self.registry[3] & 0b100) / 4 + (self.memory[self.memory[self.registry[0]+1]] and 0b100) / 4 + carry >= 2:carry = 1
		else: carry = 0
  
		if (self.registry[3] & 0b1000) / 8 + (self.memory[self.memory[self.registry[0]+1]] and 0b1000) / 8 + carry >= 2: carry2 = 1
		else: carry2 = 0
  
		if carry2 == carry: self.registry[2] = self.registry[2] and 0b1011
		else: self.registry[2] = self.registry[2] or 0b0100
  
		self.registry[3] = self.registry[3] + (self.registry[2] and 0b1) + self.memory[self.memory[self.registry[0]+1]]
  
		if self.registry[3] >= 16:
			self.registry[3] -= 16
			self.registry[2] = self.registry[2] or 0b1
   
		else: self.registry[2] = self.registry[2] and 0b1110
  
		if self.registry[3] == 0: self.registry[2] = self.registry[2] or 0b10
		else: self.registry[2] = self.registry[2] and 0b1101
		
		self.incrementIP(2)

	def CCF(self) -> None:
		self.setAction(["CCF", "-", "-", "-"])
		self.printState()
		
		self.registry[2] = self.registry[2] and 0b1110
		self.incrementIP(1)

	def SCF(self) -> None:
		self.setAction(["SCF","-","-","-"])
		self.printState()
  
		self.registry[2] = self.registry[2] or 0b0001
		self.incrementIP(1)

	def DEL(self) -> None:
		self.setAction(["DEL", "-", "-", "-"])
		self.printState()
  
		self.registry[1] -= 1
		if self.registry[1] < 0: self.registry[1] += 16
		if self.registry[1] == 0: self.registry[2] = self.registry[2] or 0b0010
  
		else: self.registry[2] = self.registry[2] & 0b1101
  
		self.incrementIP(1)

	def LDL(self) -> None:
		self.setAction(["LDL", self.hexToString(self.memory[self.registry[0]+1]), "-", "-"])
		self.printState()
  
		self.registry[1] = self.memory[self.memory[self.registry[0]+1]]
		if self.registry[1] == 0: self.registry[2] = self.registry[2] or 0b0010
		else: self.registry[2] = self.registry[2] and 0b1101

		self.incrementIP(2)

	def FLA(self) -> None:
		self.setAction(["FLA", "-", "-", "-"])
		self.printState()
	
		self.registry[3] = 15 - self.registry[3]
		if self.registry[3] < 0: self.registry[3] += 16
		if self.registry[3] == 0: self.registry[2] = self.registry[2] or 0b0010
		else: self.registry[2] = self.registry[2] and 0b1101

		self.incrementIP(1)
	
def main():
	trace = Trace()
	trace.takeInitialInput()
	newOp = Operators(trace)

	count = 0

	while not trace.stop:
		if count >= 500: 
			trace.stop = True
			trace.reason = 'Loops Henceforth'

		print(trace.memory)

		match trace.memory[trace.registry[0]]:
			case 0: newOp.HLT()
			case 1: newOp.JMP()
			case 2: newOp.JZE()
			case 3: newOp.JNZ()
			case 4: newOp.LDA()
			case 5: newOp.STA()
			case 6: newOp.GET()
			case 7: newOp.PUT()
			case 8: newOp.ROL()
			case 9: newOp.ROR()
			case 10: newOp.ADC()
			case 11: newOp.CCF()
			case 12: newOp.SCF()
			case 13: newOp.DEL()
			case 14: newOp.LDL()
			case 15: newOp.FLA()
			case _: print('Error')

		count += 1
  
	print(trace.reason)

main()