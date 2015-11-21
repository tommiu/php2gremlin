'''
Created on Nov 20, 2015

@author: Tommi Unruh
'''

from _constants import TYPE_SIMPLE_STRING, TYPE_SIMPLE_INT

class ASTNode(object):
    '''
    classdocs
    '''


    def __init__(self, parent=None, level=0, _type=None, value=None):
        '''
        Constructor
        '''
        self.level = level
        self._type = _type
        self.parent   = parent
        self.children = []
        
        self.name  = None
        self.flags = None
        self.value = value
        self.doc_comment = None
    
    def addChild(self, ast_node):
        ast_node.setLevel(self.level + 1)
        self.children.append(ast_node)
        ast_node.setParent(self)
        
    def setType(self, _type):    
        self._type = _type
        
    def getType(self):    
        return self._type
    
    def getChildren(self):
        return self.children
        
    def setLevel(self, level):
        self.level = level
        
    def getLevel(self):
        return self.level
    
    def setParent(self, node):
        self.parent = node
        
    def getParent(self):
        return self.parent
    
    def setFlags(self, flags):
        self.flags = flags
        
    def getFlags(self):
        return self.flags
    
    def setName(self, name):
        self.name = name
        
    def getName(self):
        return self.name
    
    def setDocComment(self, comment):
        self.doc_comment = comment
        
    def getDocComment(self):
        return self.doc_comment
    
    def setValue(self, val):
        self.value = val
        
    def getValue(self):
        return self.value
    
    def __str__(self, *args, **kwargs):
        indentation = " " * self.level * 4
        result = str(self._type) + "\n"
        if self.flags:
            result += indentation + "flags: " + self.flags + "\n"
        
        for i, child in enumerate(self.children):
            result += indentation + str(i) + ": " + str(child)
        
        return result
    
    def isPrimitiveType(self):
        # Strings and integers are primitive types.
        if self._type == TYPE_SIMPLE_STRING or self._type == TYPE_SIMPLE_INT:
            return True
        
        return False
    
    def nodeOnlyRepresentation(self):
        result = str(self._type)
        if self.flags:
            result += "\n" + "flags: " + self.flags
        
        return result
    
    def iter_DFS(self):
        """
        Yield all nodes in DFS order.
        """
        yield self
        if self.getChildren():
            for child in self.children:
                for child in child.iter_DFS():
                    yield child
    
    def cutFromParent(self):
        for i, child in enumerate(self.getParent().getChildren()):
            if child == self:
                self.getParent().getChildren().pop(i)
                
            