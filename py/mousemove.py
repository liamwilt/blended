DEBUG_MESSAGES = True

CONFIG =
# MouseMove Core Properties
mmc{
	### Enable/Disable Base Features ###
	(bool) mouselook = true
	
	### Display Mouse Cursor ###
	(bool) cursor = none
	
	# Set to "none" to avoid interfering with
	# other scripts that render the cursor
}

# Mouselook Properties
ml{
	### Basic Properties ###
	(num) sensitivity = 2
	(bool) invert = false
	(bool) inherit = true
	
	# inherit: parent object inherits left/right rotation
	
	### Up/Down Rotation Cap ###
	(bool) cap = true
	(num) capupper = 80
	(num) caplower = -80
	(num) caporigin = 90
	
	# caporigin: the forward facing rotation of the object
	# 	on the X axis, in degrees.
}



from bge import logic, render, events
from mathutils import Vector
import math

# MouseMove Core
class Core:
	def __init__(self, object):
		self.own = object
		self.cont = None
		
		if isCont(object):
			self.cont = object
			self.own = object.owner
		
		self.features = {}
		
		cfg = self.getConfig()
		self.config = cfg[0]
		self.configTypes = cfg[1]
		
		self.props = self.getProperties('mmc')
		self.controls = Controls(self)
	
	def module(self):
		self.main()
		
		### Mouselook System ###
		if self.props['mouselook']:
			if not self.features.get('mouselook', None):
				self.addMouselook()
	
	def main(self):
		# Refresh properties
		self.props = self.getProperties('mmc')
		self.controls.main()
		
		cursor = self.props['cursor']
		if cursor in [True, False]:
			render.showMouse(cursor)
		
		for i in self.features:
			if self.props[i] == True:
				self.features[i].main()
			elif self.features[i].ready == True:
				self.features[i].deactivate()
	
	def create(self, key, object):
		features = {'mouselook':Mouselook}
		
		if key in self.features:
			msg('Core Feature "', key, '" already created! Returning None')
			return None
		
		newFeature = features[key](self, object)
		self.features[key] = newFeature
		
		return newFeature
		
	def addMouselook(self, object=None):
		self.setProp('mmc.mouselook', True)
		return self.create('mouselook', object)
	
	# Decode CONFIG properties
	def getConfig(self):
		props = {'mmc':{},
				 'ml':{},
				 'sm':{},
				 'dm':{}
				}
		dTypes = {'mmc':{},
				 'ml':{},
				 'sm':{},
				 'dm':{}
				}
				 
		key = None
		
		for i in CONFIG.splitlines():
			i = i.strip()
			i = i.replace('\t', '')
			
			fullLine = i
			
			if '{' in i:
				i = i.split('{')[0].lower().strip()
				if '#' not in i:
					key = i
					props[key] = {}
					dTypes[key] = {}
			elif i.startswith('}'):
				key = None
			elif i.startswith('#'):
				continue
			else:
				if key != None and i != '':
					i = i.split('#', 1)[0].strip() # Remove trailing comments
					
					dataType = None
					if i.startswith('(') and ')' in i:
						dataType = i[1:].split(')', 1)[0].strip().lower() # Extract data type
					
					if dataType == None:
						msg('Config: Property missing Data Type; "', fullLine, '"')
						continue
					
					i = i.split(')', 1)[1]
					
					if '=' not in i:
						msg('Config: Undefined Property; "', fullLine, '"')
						continue
					
					# Property names are all stored in lower case
					propName = i.split('=', 1)[0].strip().lower()
					propValue = i.split('=', 1)[1].strip()
					
					# Remove trailing comments
					propValue = propValue.split('#', 1)[0].strip()
					
					if propValue == '':
						msg('Config: Empty Property; "', fullLine, '"')
						continue
					
					# Convert Properties to data types
					if dataType == 'bool':
						if propValue.lower() in ['true', '1']:
							propValue = True
						elif propValue.lower() in ['false', '0']:
							propValue = False
						elif propValue.lower() == 'none':
							propValue = None
						else:
							msg('Config: Property doesn\'t match Data Type; "', fullLine, '"')
							continue
						nonetype = None
						dataType = [bool().__class__, int().__class__, nonetype.__class__]
					elif dataType == 'int':
						try:
							propValue = int(propValue)
							dataType = [int().__class__]
						except:
							msg('Config: Property doesn\'t match Data Type; "', fullLine, '"')
							continue
					elif dataType in ['float', 'num']:
						try:
							propValue = float(propValue)
							dataType = [float().__class__, int().__class__]
						except:
							msg('Config: Property doesn\'t match Data Type; "', fullLine, '"')
							continue
					elif dataType == 'str':
						dataType = [str().__class__]
					else:
						msg('Config: Invalid Data Type; "', fullLine, '"')
						continue
					
					props[key][propName] = propValue
					dTypes[key][propName] = dataType
					
		return [props, dTypes]
	
	# Get Properties
	def getProperties(self, prefix):
		props = {}
		objProps = {}
		
		# Organize properties and remove prefixes
		for i in self.own.getPropertyNames():
			if i.lower().startswith(prefix + '.'):
				objProps[i.lower()[len(prefix)+1:]] = self.own[i]
		
		for i in self.config[prefix]:
			props[i] = self.config[prefix][i]
			types = self.configTypes[prefix][i]
			
			if i in objProps and objProps[i].__class__ in types:
				props[i] = objProps[i]
		
		return props
	
	# Set Property
	def setProp(self, propName, value=None):
		propName = propName.lower()
		prefix = propName.split('.', 1)[0]
		suffix = propName.split('.', 1)[1]
		
		if suffix in self.config[prefix]:
			for i in self.own.getPropertyNames():
				if i.lower() == propName:
					if value == None and self.own[i] in [True, False]:
						self.own[i] = not self.own[i]
					elif value.__class__ in self.configTypes[prefix][suffix]:
						self.own[i] = value
					return
			
			if value.__class__ in self.getTypes(propName):
				self.own[propName] = value
	
	# Get Property
	def getProp(self, propName):
		propName = propName.lower()
		prefix = propName.split('.', 1)[0]
		suffix = propName.split('.', 1)[1]
		
		if suffix in self.config[prefix]:
			if suffix in self.config[prefix]:
				return self.config[prefix][suffix]
		
		return None
			
	def getTypes(self, propName):
		prefix = propName.split('.', 1)[0]
		suffix = propName.split('.', 1)[1]
		
		if suffix in self.configTypes[prefix]:
			return self.configTypes[prefix][suffix]
		
		
class Mouselook:
	def __init__(self, core, object=None):
		self.core = core
		
		if object == None:
			object = self.core.own
				
		if isCont(object):
			object = object.owner
			
		self.own = object

		self.props = self.core.getProperties('ml')
		self.ready = False
		
		# Mouselook Attributes
		self.size = self.getWindowSize()
		self.move = self.getMovement()
		self.verticalRotation = self.own.localOrientation.to_euler().x * (270 / math.pi)
		
	def main(self):
		self.props = self.core.getProperties('ml')
		self.size = self.getWindowSize()
		self.move = self.getMovement()
		
		if self.ready:
			self.run()
		else:
			self.activate()
		
	def run(self):
		invert = -1 if self.props['invert'] else 1
		sensitivity = self.props['sensitivity'] * 0.025
		
		horizontal = self.move[0] * sensitivity * invert
		vertical = self.move[1] * sensitivity * invert
		
		### Set vertical rotation (X) and apply capping ###
		self.verticalRotation += vertical
		self.applyCap()
		
		ori = self.own.localOrientation.to_euler()
		ori.x = self.verticalRotation / (180 / math.pi)
		
		if (self.props['inherit'] == False) or (self.own.parent == None):
			ori.z += horizontal / (180 / math.pi)
			
		elif self.props['inherit'] and self.own.parent:
			parentOri = self.own.parent.localOrientation.to_euler()
			parentOri.z += horizontal / (180 / math.pi)
			self.own.parent.localOrientation = parentOri.to_matrix()
		
		self.own.localOrientation = ori.to_matrix()
		
		self.setCenter()
		
	### "Get Property" Functions ###
	def getWindowSize(self):
		return (render.getWindowWidth(), render.getWindowHeight())
		
	def getMovement(self):
		pos = logic.mouse.position
		realCenter = self.getCenter()
		move = [realCenter[0] - pos[0], realCenter[1] - pos[1]]
		
		xMove = int(self.size[0] * move[0])
		yMove = int(self.size[1] * move[1])
		
		return (xMove, yMove)
		
	def getCenter(self):
		size = self.getWindowSize()
		screenCenter = (size[0]//2, size[1]//2)
		
		return (screenCenter[0] * (1.0/size[0]), screenCenter[1] * (1.0/size[1]))
		
	def setCenter(self):
		render.setMousePosition(self.size[0]//2, self.size[1]//2)
	
	def applyCap(self):
		if self.props['cap']:
			upper = self.props['capupper']
			lower = self.props['caplower']
			origin = self.props['caporigin']
			
			if upper < lower:
				return
			
			if self.verticalRotation > origin + upper:
				self.verticalRotation = origin + upper
				
			elif self.verticalRotation < origin + lower:
				self.verticalRotation = origin + lower
	
	### Activation/Deactivation ###
	def activate(self):
		self.setCenter()
		self.ready = True
		
	def deactivate(self):
		self.ready = False
		
		
def isCont(object):
	if str(object.__class__) == "<class 'SCA_PythonController'>":
		return True
	return False

def msg(*args):
	message = ""
	for i in args:
		message += str(i)
		
	if DEBUG_MESSAGES:
		print('[MouseMove] ' + message)
	
#################################

# Module Execution entry point
def main():
	cont = logic.getCurrentController()
	own = cont.owner
	
	if 'mmc.core' not in own:
		own['mmc.core'] = Core(cont)
	else:
		own['mmc.core'].module()
	
# Non-Module Execution entry point (Script)
if logic.getCurrentController().mode == 0:
	main()