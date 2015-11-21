'''
Created on Nov 21, 2015

@author: Tommi Unruh
'''

import _constants
from _constants import TYPE_ASSIGN, TYPE_ENCAPS_LIST, TYPE_ASSIGN_OP

class AST2Gremlin(object):
    """
    Converts PHP ASTs to gremlin queries.
    """


    def __init__(self, ast):
        '''
        Constructor
        '''
        self.cleanAST(ast)
        self.ast = ast
        self.vars = set()
        
    def convertPHPAST(self):
        ast = self.ast
        # Print out AST (for debugging purposes).
        print ast
        
        query = self.prepareQuery() + "\n"
        
        # Get all nodes.
        query += "g.V"
        
        # Remove "NULL" nodes.
        query += self.filter("it.type != \"NULL\"")
        
        # The root node is a AST_STMT_LIST, therefore we skip it and 
        # analyse its children.
        first = True
        for child in ast.getChildren():
            query += self.convertNode(child, first=first)
            first = False
            
        query = self.prepareEndOfQuery(query)
                    
        return query
    
    def cleanAST(self, ast):
        for node in ast.iter_DFS():
            # Remove nodes of type "null".
            if node.getType() == "null":
                node.cutFromParent()
    
    def prepareQuery(self):
        """
        Add generic content we need to the gremlin query.
        """
        # Add a function to print any found results later on.
        query = "def printFoundCC(line_start, line_end, file_name) {\n"
        query += (
            "\"Found a code clone on lines \" + line_start + \" to \"" 
            " + line_end + \"\\n\" + \"File: \" + file_name"
            )
        query += "\n}\n\n"
        
        # Add global variable to track the childnumbers of parsed nodes.
        query += "childnumber = 0\n"
        
        return query
    
    def prepareEndOfQuery(self, query):
        # Remove last two lines from query, because they are 
        # ".parents()" and ".children().filter...", which we do not need
        # anymore.
        i = query.rfind("\n")
        query = query[0:i]
        
        i = query[0:i].rfind("\n")
        query = query[0:i]
        
        i = query[0:i].rfind("\n")
        query = query[0:i]

        # Save linenumber of last node.
        query += "\n" + self.sideEffect("end_linenumber = it.lineno")
        
        # Save filename/
        query += "\n.toFile()"
        query += self.sideEffect("filename = it.name")[1:]
        
        # Print result.
        query += self.transform(
                    "printFoundCC(start_linenumber, end_linenumber, filename)"
                    )

        return query
    
    def convertNode(self, ast, first=None):
        """
        Check the given AST for its type and build a gremlin query.
        """
        query = ""
        node_type = ast.getType()
        node_children = ast.getChildren()
        
        if first:
            # This is the first matched node, so save its linenumber
            query += self.sideEffect("start_linenumber = it.lineno")
        
        if node_type == TYPE_ASSIGN:
            # $var = whatever
            # AST_ASSIGN
            #     0: AST_VAR
            #         0: "string"
            #     1: AST_DIM | AST_VAR | AST_ENCAPS_LIST | string | int
            # Filter left side.
            query += self.filter("isAssignment(it)")
            
            # Filter right side.
            query += self.filter("it.rval().type.next() == \"%s\"" % (
                                                    node_children[1].getType()
                                                    ))
            
            # Remember the $var's name.
            query += self.rememberVarName(node_children)

            # Remember its position as a child.
            query += self.sideEffect("childnumber = %s" % (
                                "it.childnum" if first else "childnumber + 1"
                                ))
            
            # Recursively continue with the right side if necessary.
            if not node_children[1].isPrimitiveType():
                query += self.convertNode(node_children[1])
                
            # Go back in hierarchy.
            query += self.setupNextNode()
            
        elif node_type == TYPE_ENCAPS_LIST:
            # A string also containing variables ("example $list").
            # Each child should have the correct type, therefore add
            # filters for them.
            for i, child in enumerate(node_children):
                query += self.filter(
                        "it.rval().ithChildren(%d).type.next() == \"%s\"" % (
                                            i, child.getType()
                                            )
                        )
                
        elif node_type == TYPE_ASSIGN_OP:
            # $var .= whatever (similar to TYPE_ASSIGN)
            # Filter left side.
            query += self.filter("isConcatAssignment(it)")
            
            # Filter right side.
            query += self.filter("it.rval().type.next() == \"%s\"" % (
                                                    node_children[1].getType()
                                                    ))
            
            # Check if variable name is one of the already defined variables.
            # If yes, then add a filter which checks for equality of
            # their names.
            varname = node_children[0].getChildren()[0].getValue()
            
            if varname in self.vars:
                # Var is already known. Check for equality.
                query += self.filter(
                            "it.lval().varToName().next() == %s.next()" % (
                                                        varname
                                                        )
                            )
                
            else:
                # Remember variable name 
                query += self.rememberVarName(node_children)
                
            # Recursively continue with the right side if necessary.
            if not node_children[1].isPrimitiveType():
                query += self.convertNode(node_children[1])
        
            # Go back in hierarchy.
            query += self.setupNextNode()
        
        return query
    
    def rememberVarName(self, children_list):
        varname = children_list[0].getChildren()[0].getValue()
        self.vars.add(varname)
        
        return self.sideEffect("%s = it.lval().varToName()" % (varname))
        
    def setupNextNode(self):
        return "\n.parents()\n.children()" + self.filter("it.childnum == childnumber + 1")[1:] + "\n"
    
    def filter(self, _filter):
        return "\n.filter{ %s }" % (_filter)
    
    def sideEffect(self, sideeffect):
        return "\n.sideEffect{ %s }" % (sideeffect)
    
    def transform(self, transform):
        return "\n.transform{ %s }" % (transform)