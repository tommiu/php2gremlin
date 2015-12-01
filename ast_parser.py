'''
Created on Nov 20, 2015

@author: Tommi Unruh
'''
import pexpect
from ast_node import ASTNode
from _constants import *

class ASTParser(object):
    """
    Translates the output of the php parser (which is given as a string)
    into a python list.
    """

    def __init__(self, results_path, parser_script, phpjoern_path):
        '''
        Constructor
        '''
        self.results_path  = results_path
        self.parser_script = parser_script + " %s %s %d %s"
        self.phpjoern_path = phpjoern_path
    
    def runPHPParser(self, path):
        """
        Start php parser
        """
        process = pexpect.spawn(self.parser_script % (
                                            path, self.results_path,
                                            1, self.phpjoern_path
                                ))
        
        # Wait until child finishes.
#         process.expect(pexpect.EOF)
        output = self.cleanOutput(process.read())
        root = self.string2pythonAST(None, iter(output.splitlines()))
        return root
        
    
    def string2pythonAST(self, node_before, php_ast_string_generator):
        # A child is indented by 4 spaces.
        indentation = " " * 4
        
        try:
            while True:
                next_line = php_ast_string_generator.next()
                parsed_node_level = len(next_line)
                parsed_node_level -= len(next_line.lstrip())
                parsed_node_level /= 4
                parsed_node = self.line2AST(node_before, next_line)
                
                if not parsed_node:
                    # Parsed line was just an addition for 'node_before' (
                    # like flags, name, comments
                    # ). Therefore, we can skip it here.
                    continue

                if not node_before:
                    # parsed_node is the first node (== root node).
                    self.string2pythonAST(parsed_node, php_ast_string_generator)
                    return parsed_node
                
                if node_before.getLevel() == parsed_node_level:
                    # Node is on same level with node_before.
                    
                    parent_node = node_before.getParent()
                    
                    if parent_node:
                        parent_node.addChild(parsed_node)
                    
                    self.string2pythonAST(parsed_node, php_ast_string_generator)
                    
                    # No need to continue with this node_before, since 
                    # we encountered its next sibling.
                    return
                
                elif node_before.getLevel() + 1 == parsed_node_level:
                    # Node in next_line is a child node.
                    node_before.addChild(parsed_node)
                    self.string2pythonAST(parsed_node, php_ast_string_generator)
                    
                elif node_before.getLevel() > parsed_node_level:
                    # We are up some levels again, so we will not meet children
                    # of the node_before anymore.
                    
                    # Go back in the hierarchy, until we find the parent
                    # of the currently parsed node.
                    ancestor = node_before.getParent()
                    for i in xrange(node_before.getLevel() - parsed_node_level):
                        ancestor = ancestor.getParent()
                    
                    if ancestor == None:
                        raise Exception("Could not parse file")
                    ancestor.addChild(parsed_node)
                    self.string2pythonAST(parsed_node, php_ast_string_generator)

                    # We traversed back in the hierarchy, so there is nothing
                    # left to do for this 'node_before'.                    
                    return
        
        except StopIteration:
            # Done
            pass
        
    def cleanOutput(self, output):
        """
        Clean the output file, 
        by removing anything than the AST from the string.
        """
        
        # Cut out first line ("Parsing file ...").
        first_line_end = output.find("\n")
        output = output[first_line_end + 1:]
        
        # Cut out last line ("Done.")
        last_line_start = output.rfind("\nDone.")
        output = output[:last_line_start]
        
        return output
    
    def line2AST(self, parent, _line):
        # A child is indented by 4 spaces.
        child_number = _line.count(" " * 4)
        
        # Check if line is of format "%d: string"
        explode = _line.split(":", 1)
        
        if len(explode) > 1:
            # Format did include a colon.
            try:
#                 print explode
                child_num = int(explode[0].strip())
                _type = explode[1].strip()
                
                node = None
                
                if _type[0] == '"':
                    # Create string node, but remove its quote-characters.
#                     print "Stringnode:", _type[1:-1], child_num
                    node = ASTNode(_type="string", value=_type[1:-1],
                                   _childnum=child_num)
                
                else:
                    # Check if node is just an integer.
                    try: 
                        val = int(_type)
                        node = ASTNode(_type=TYPE_SIMPLE_INT, value=val,
                                       _childnum=child_num)
                        
                    except:
                        # Node is not just an integer
                        if _type == "null":
                            _type = TYPE_NULL
                        node = ASTNode(_type=_type, _childnum=child_num)
                        
                return node
            
            except ValueError:
                # Value before colon is not a number.
                # This means, the string started with "flags", "name" or
                # "docComment"
                key = explode[0].strip()
                val = explode[1].strip()
                
                if key == "flags":
                    parent.setFlags(val)
                    
                elif key == "name":
                    parent.setName(val)
                    
                elif key == "docComment":
                    parent.setDocComment(val)
                    
                return None
                
        else:
            return ASTNode(_type=_line)
                    