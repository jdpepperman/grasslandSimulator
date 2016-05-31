from scene import *
from random import uniform
A = Action

NUM_RABBITS = 20
RABBIT_AGE = 30

NUM_TIGERS = 3
TIGER_AGE = 100

SIGHT = 600

class Actor(SpriteNode):
	def __init__(self, img, max_x, max_y, *args, **kwargs):
		SpriteNode.__init__(self, img, *args, **kwargs)
		self.scale = 0.6
		self.max_x = max_x
		self.max_y = max_y
		#angle
		a = uniform(0, math.pi*2)
		self.position = (uniform(0, max_x), uniform(0, max_y))
		#unit vector for the angle
		self.v = Vector2(math.cos(a), math.sin(a))
		#reproductionTimer
		self.reproductionTimer = uniform(0,10)
		#age
		self.age = uniform(0,5)
		#fullness
		self.fullness = uniform(45, 55)
		#how high they are on the food chain
		self.foodChain = 0
		
	def update(self, neighbors):
		self.stayOnScreen(neighbors)
		self.collide(neighbors)
		self.updateStats()
		if self.canMate():
			self.tryToMate(neighbors)
		elif self.isHungry():
			self.tryToEat(neighbors)
		else:
			self.wander(neighbors)
		
	def updateStats(self):
		#reproduction
		if uniform(0,80) > 79:
			self.reproductionTimer -= 1
		#age
		if uniform(0,60) > 59:
			self.age += 1
		
	def stayOnScreen(self, neighbors):
		if self.position.x <= 0 or self.position.x >= self.max_x:
			self.v.x = self.v.x - self.v.x * 2
		if self.position.y <= 0 or self.position.y >= self.max_y:
			self.v.y = self.v.y - self.v.y * 2
		
	def collide(self, neighbors):
		# Don't crowd neighbors
		if not neighbors:
			return Vector2(0, 0)
		c = Vector2()
		for n in neighbors:
			#if we're touching another actor
			if abs(n.position - self.position) < 30:
				c += (self.position - n.position)
		self.v += c * 0.01
		
	def wander(self, neighbors):
		#turn sometimes
		turnChance = uniform(0,100)
		if turnChance > 99:
			angle = uniform(0, math.pi * 2)
			self.turn(angle)
			
	def tryToMate(self, neighbors):
		#if actor can mate
		if self.canMate():
			for n in neighbors:
				if type(self) == type(n):
					if abs(n.position - self.position) < SIGHT:
						self.v = self.getVectorToward(n)
						
	def tryToEat(self, neighbors):
		if self.isHungry():
			for n in neighbors:
				if n.foodChain < self.foodChain:
					if abs(n.position - self.position) < SIGHT:
						#makes them go too fast
						self.v = self.getVectorToward(n) * 1.001
		
	def isHungry(self):
		return self.fullness < 50
		
	def turn(self, angle):
		if angle <= 0 or angle >= math.pi * 2:
			raise ValueError("Angle less than 0 or greater than 2pi")
			
		currentX = self.v.x
		currentY = self.v.y
		
		self.v.x = currentX * math.cos(angle) - currentY * math.sin(angle)
		self.v.y = currentX * math.sin(angle) + currentY * math.cos(angle)
		
	def die(self):
		self.parent.actors.remove(self)
		self.run_action(A.remove())
		
	def depleteFullness(self):
		#take away fullness from actor
		if uniform(0, 60) > 59: 
			self.fullness -= 1
		#if actor starves, kill it
		if self.fullness < 0:
			self.die()
			
	def canMate(self):
		return self.reproductionTimer <= 0 and self.fullness >= 50
		
	def getVectorToward(self, other):
		newVector = other.position - self.position
		#speed currently
		speed = math.sqrt(self.v.x*self.v.x + self.v.y*self.v.y)
		#normalize newVector
		magnitude = math.sqrt(newVector.x*newVector.x + newVector.y*newVector.y)
		newVector.x = newVector.x/magnitude
		newVector.y = newVector.y/magnitude
		
		return newVector * speed
		
	def distanceTo(self, other):
		#return math.sqrt(math.pow(other.position.x - self.position.x, 2) + math.pow(other.position.y - self.position.y, 2))
		return abs(other.position - self.position)

class Rabbit(Actor):
	def __init__(self, max_x, max_y, *args, **kwargs):
		img = 'emj:Rabbit_Face'
		Actor.__init__(self, img, max_x, max_y, *args, **kwargs)
		self.foodChain = 2
		
	def update(self, neighbors):
		Actor.update(self, neighbors)
		self.runAway(neighbors)
		if self.age >= uniform(RABBIT_AGE,RABBIT_AGE+10):
			self.die()
		
	def collide(self, neighbors):
		for n in neighbors:
			#if we're touching another actor
			if abs(n.position - self.position) < 30:
				if isinstance(n, Rabbit) and self.reproductionTimer <= 0:
					babyRabbit = Rabbit(self.max_x, self.max_y, parent=self.parent)
					self.parent.actors.append(babyRabbit)
					self.reproductionTimer = 10
					
		Actor.collide(self, neighbors)
		
	def runAway(self, neighbors):
		for n in neighbors:
			if self.distanceTo(n) < 100 and isinstance(n, Tiger):
				self.v = self.getVectorToward(n) * -1.01
		
class Tiger(Actor):
	def __init__(self, max_x, max_y, *args, **kwargs):
		img = 'emj:Tiger_Face'
		Actor.__init__(self, img, max_x, max_y, *args, **kwargs)
		self.foodChain = 5
		
	def update(self, neighbors):
		Actor.update(self, neighbors)
		self.depleteFullness()
		if self.age >= uniform(TIGER_AGE,TIGER_AGE+20):
			self.die()
			
	def chase(self, neighbors):
		for n in neighbors:
			if self.distanceTo(n) < 100 and isinstance(n, Rabbit):
				self.v = self.getVectorToward(n) * -1.02
		
	def collide(self, neighbors):
		for n in neighbors:
			#if we're touching another actor
			if abs(n.position - self.position) < 30:
				if isinstance(n, Tiger) and self.reproductionTimer <= 0 and self.fullness > 50:
					babyTiger = Tiger(self.max_x, self.max_y, parent=self.parent)
					self.parent.actors.append(babyTiger)
					self.reproductionTimer = 30
				elif isinstance(n, Rabbit):
					n.die()
					self.fullness += 10
					
		Actor.collide(self, neighbors)

class MyScene(Scene):
	def setup(self):
		self.actors = []
		rabbits = [Rabbit(self.size.w, self.size.h, parent=self) for i in xrange(NUM_RABBITS)]
		tigers = [Tiger(self.size.w, self.size.h, parent=self) for i in xrange(NUM_TIGERS)]
		self.actors.extend(rabbits)
		self.actors.extend(tigers)
		self.background_color = "green"
		
	def update(self):
		for actor in self.actors:
			neighbor_distance = min(self.size)/3
			neighbors = [actr for actr in self.actors if actr != actor and abs(actr.position - actor.position) < neighbor_distance]
			actor.update(neighbors)
		for actor in self.actors:
			actor.position += actor.v
			#orient the graphic to the direction its going
			actor.rotation = math.atan2(*reversed(actor.v)) + math.pi
		
	def touch_began(self, touch):
		x, y = touch.location
		move_action = Action.move_to(x, y, 0.7, TIMING_SINODIAL)
		for a in self.actors:
			a.run_action(move_action)
		
if __name__ == '__main__':
	run(MyScene(), show_fps=True)