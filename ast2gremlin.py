'''
Created on Nov 21, 2015

@author: Tommi Unruh
'''

from _constants import *
import sys

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
    
    
    def removeNullNodes(self):
        query = self.addComment("Remove \"NULL\"-nodes")
        query += (
            "\ng.V.filter{ it.type == \"NULL\" }"
            ".each{ g.removeVertex(it) }.iterate();\n\n"
            )
        
        return query
    
    
    def convertPHPAST(self, debug=False):
        ast = self.ast
        # Print out AST (for debugging purposes).
        if debug:
            print ast
        
        # Remove "NULL" nodes.
#         query += self.removeNullNodes()
        
        query = self.addComment("Start query.") + "\n"
        # Get all nodes.
        query += "g.V"
        
        # The root node is a AST_STMT_LIST, therefore we skip it and 
        # analyse its children.
        first = True
        # This is the first matched node, so save its linenumber
        query += self.sideEffect("start_linenumber = it.lineno")
        
        ast_children = ast.getChildren()
        
        if ast_children[-1].getType() == TYPE_NULL:
            # If the code ends in e.g. '?>', it will produce a NULL node.
            # However if we search for the given code snippet in real code,
            # the '?>' will not be part of the code.
            # Therefore, we need to ignore it while producing the gremlin
            # query.
            itr = self.ignoreLastElement(ast_children)
        else:
            itr = ast_children
            
        itr = self.ignoreLastElement(itr)
        i = 0
        for child in itr:
            # All children except the last
            query += self.addComment("Parent #%d" % i)
            query += self.convertNode(child, first=first)
            query += self.setupNextNode()
            first = False
            i += 1
                
        try:
            # Handle last child here
            child = (
                ast_children[-2] if ast_children[-1].getType() == TYPE_NULL
                                    else ast_children[-1]
                )
            query += self.addComment("Parent #%d" % (i))
            query += self.convertNode(child)
            
            # Filter out path to last node here,
            # because we need to traverse it.
#             i_begin = query.rfind("\n")
#             last_filter_line = query[i_begin:]
#             child_traversal = self.extractChildFromFilter(last_filter_line)
#             query += self.addComment(
#                             "Traverse to last children to get its linenumber."
#                             )
#             query += child_traversal
            
        except:
            # Iterator was empty
            pass
            sys.exit()

        query = self.prepareQuery() + query        
        query = self.prepareEndOfQuery(query)
                    
        return query
    
    def cleanAST(self, ast):
        for node in ast.iter_DFS():
            # Remove nodes of type "null".
            if node.getType() == "null":
#                 node.cutFromParent()
                pass
    
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
        query += "childnumber = 0"
        
        # Initialize each variable that has been seen in the query.
        query += self.addComment("Initialize variables of query")
        for var in self.vars:
            query += "\n%s = \"\"" % var
        
        return query
    
    def extractChildFromFilter(self, _str):
        """
        In a string of format ".filter{ isType(it.....next(), "whatever") }"
        filter out the 'it....' part.
        """
        string_start = len(".filter{ isType(it") # Remove this part from string.
        i_end = _str.find(".next()")
        
        if i_end != -1:
            # Found ".next()"
            child_traversal = _str[string_start:i_end]
            
        else:
            # Did not find ".next()", because the string looks like this:
            # ".filter{ isType(it, "whatever") }".
            i_end = _str.find("it")
            child_traversal = _str[string_start, i_end+2]
            
        return child_traversal
    
    def prepareEndOfQuery(self, query):
        # Remove last six from query, because they are 
        # generalized gremlin-steps, that are only needed to traverse to the
        # next node. However, we are at the end of the query.
#         i = query.rfind("\n")
#         query = self.removeLastLines(query, 0)
# 
#         i = query[0:i].rfind("\n")
#         query = query[0:i]

        query = query + self.addComment("Prepare end of query.")

        # Save linenumber of last node.
        query += "\n" + self.sideEffect("end_linenumber = it.lineno")
        
        # Save filename/
        query += "\n.toFile()"
        query += self.sideEffect("filename = it.name")[1:]
        
        # Print result.
        query += self.addComment("Print all found results.")
        query += self.transform(
                    "printFoundCC(start_linenumber, end_linenumber, filename)"
                    )

        return query
    
    def convertNode_old(self, ast, first=None):
        """
        Check the given AST for its type and build a gremlin query.
        """
        query = ""
        node_type = ast.getType()
        node_children = ast.getChildren()
        
        if first:
            # This is the first matched node, so save its linenumber
            query += self.sideEffect("start_linenumber = it.lineno")
        
        query += self.addComment("Node: %s" % (node_type))
        
        # Filter node.
        query += self.filter(self.isType(node_type))
        
        if node_type == TYPE_ASSIGN:
            # $var = whatever
            # AST_ASSIGN
            #     0: AST_VAR
            #         0: "string"
            #     1: AST_DIM | AST_VAR | AST_ENCAPS_LIST | string | int
            
            # Filter children.
#             query += self.filterChildren(node_children)
            
            # Remember the $var's name.
            query += self.rememberVarName(node_children)

            # Remember its position as a child.
            query += self.sideEffect("childnumber = %s" % (
                                "it.childnum" if first else "childnumber + 1"
                                ))
            
        elif node_type == TYPE_ENCAPS_LIST:
            # A string also containing variables ("example $list").
            # Each child should have the correct type, therefore add
            # filters for them.
            pass
                
        elif node_type == TYPE_ASSIGN_OP:
            # $var .= whatever (similar to TYPE_ASSIGN)
            
            # Filter left and right child.
            query += self.filterChildren(node_children)
            
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
                
        elif node_type == TYPE_IF or node_type == TYPE_IF_ELEM:
            # if (...) {...} else {...}
            # AST_IF
            #     0: AST_IF_ELEM
            #         0: any node (if_condition)
            #         1: AST_STMT_LIST (code of if-block)
            #     1: AST_IF_ELEM
            #         same as child 0.
            
            pass
                
        elif node_type == TYPE_ISSET:
            # Call to isset()
            # AST_ISSET
            #     0: whatever
            pass
        
        query += self.traverseChildren(node_children)
            
        return query
    
    def ignoreLastElement(self, itr):
        """
        Iterate 'itr', but ignore its last element, so that we can treat
        it differently.
        """
        itr = iter(itr)
        prev = itr.next()
        
        for elem in itr:
            # Yield the PREVIOUS item. 
            # This will lead to ignoring the last item in 'itr'.
            # The last item will not hit the yield statement, since
            # the for-loop would need to iterate 'itr' one time more than
            # it has elements.
            yield prev
            prev = elem
    

    def addSeenVariableFilter(self, traversal, var_name):
        return self.filter("%s.varToName()%s == %s" % (
                                        traversal,
                                        ".next()" if traversal != "it" else "",
                                        var_name
                                        ))
    
    
    def convertNode(self, ast, first=None):
        """
        Check the given AST for its type and build a gremlin query.my
        """
        query = ""
        for traversal, node in self.recursiveFilter("it", ast):
            node_type = node.getType()
            if traversal == "it":
                result = "isType(%s, \"%s\")"
            else:
                result = "isType(%s.next(), \"%s\")"
            query += self.filter(result % (traversal, node_type))
            
            # Check if node is of type AST_VAR and its parent
            # is not of type AST_DIM.
            if node_type == TYPE_VAR and node.getParent().getType() != TYPE_DIM:
                # If yes, check if this variable has been seen before.
                var_name = node.getChild(0).getValue()
                
                if var_name in self.vars:
                    # Variable has been seen before
                    query += self.addSeenVariableFilter(traversal, var_name)
                
                else:
                    # Variable occured the first time - remember it.
                    query += self.rememberVarName(var_name, traversal)
            # Add sideEffect to remember the last matched linenumber.
            # self.sideEffect("current_ln = %s.lineno.next(); if( current_ln > 
            # end_linenumber) {end_linenumber = current_ln;}" % (query))

        return query
    
    def isType(self, _type):
        """
        Add the custom gremlin step "isType(node, type)", which returns true
        if a given node is of the given type.
        """
        query = "isType(it, \"%s\")" % (_type)
        return query
    
    def recursiveFilter(self, query, node):
        """
        Check the subtree of every node recursively and yield the traversal to
        each node.
        This approach does not actually traverse any child - the query stays 
        at the highest level in the AST and only checks if every child node
        is of the right type.
        """
        yield (query, node)
        
        for i, child in enumerate(node.getChildren()):
#             if child.getType() != "null":
            next_query = query + ".ithChildren(%d)" % i
            for resulting_query in self.recursiveFilter(next_query, child):
                yield resulting_query

        
    def traverseChildren(self, children_list):
        """
        Legacy code - add the traversal for each child in children_list
        to the query. After traversing the child, go back to its parent
        (== go up one level in tree).
        
        This code is obsolete, because actually traversing each child in 
        a even small ASTs will lead to stack overflows in the neo4j graph
        database.
        The new approach is in 'recursiveFilter'. 
        """
        query = ""
        for i, child in enumerate(children_list):
            query += self.goToChild(i)
            query += self.convertNode(child)
            query += self.goToParent()
            
        return query
            
    def goToParent(self):
        query  = "\n\n// Go up one level."
        query += "\n.parents()"
        return query
    
    def goToChild(self, i):
        query  = "\n\n// Traverse child #%d" % i
        query += "\n.ithChildren(%d)" % i
        return query 
    
    def rememberVarName(self, var_name, traversal):
        self.vars.add(var_name)
        
        return (
            self.addComment("Remember variable %s" % (var_name)) + 
            self.sideEffect("%s = %s.varToName().next()" % (
                                                            var_name, traversal
                                                            ))
            )
        
    def setupNextNode(self):
        return (
            self.sideEffect("childnumber = it.childnum") + 
            self.sideEffect("childnumber = childnumber + 1") +
            self.goToParent() + "\n.children()" +
            self.addComment("Check next AST-node (similar to next line of code)") +
            self.filter("it.childnum == childnumber")
            )
            
    def filter(self, _filter, no_end=False):
        query = "\n.filter{ %s }" % (_filter)
        
        if no_end:
            return query[:-2]
        
        return query
        
    def filterChildren(self, children_list):
        query = self.addComment("Filter node children.")
        for i, child in enumerate(children_list):
            query += self.filter("it.ithChildren(%d).type.next() == \"%s\"" % (
                                            i, child.getType()
                                            ))
            
        return query
    
    def sideEffect(self, sideeffect):
        return "\n.sideEffect{ %s }" % (sideeffect)
    
    def transform(self, transform):
        return "\n.transform{ %s }" % (transform)
    
    def addComment(self, comment):
        return "\n\n// " + comment
    
    def removeLastLines(self, _str, lines=1):
        i = _str.rfind("\n")
        _str = _str[0:i]
        
        if lines > 1:
            for _ in xrange(lines-1):
                i = _str[0:i].rfind("\n")
                _str = _str[0:i]
        
        return _str