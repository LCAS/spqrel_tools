import os
from aiml.Kernel import Kernel

class DialogueManager:

	path = ''
	kernel = None
	
	def __init__(self):
		self.kernel = Kernel()

	def learn(self,path):
		print "Importing AIML KBs..."
		for root, directories, filenames in os.walk(path):
			for filename in filenames: 
				if filename.endswith('aiml'):
					self.kernel.learn(os.path.join(root,filename))
		print "...AIML KBs imported!"
		print 'Number of categories: ' + str(self.kernel.numCategories())
	
	def respond(self,sentence):
		return self.kernel.respond(sentence)