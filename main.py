'''
Created on Nov 20, 2015

@author: Tommi Unruh
'''
import sys
from ast_parser import ASTParser
from ast2gremlin import AST2Gremlin
from args_parser import ModeArgsParser

ARGS_CONVERT = "convert"

def main(args):
    results_path  = "../ccdetection/AST_parser/parse_results"
    parser_script = "../ccdetection/AST_parser/parser"
    phpjoern_path = "/opt/phpjoern"

    # Setup command line arguments.
    parser = ModeArgsParser()
    setupArgs(parser)
    
    try:
        flow = parser.parseArgs(args[1], args[2:])
        
    except:
        parser.printHelp(args[0])
        sys.exit()

    if flow[parser.KEY_MODE] == ARGS_CONVERT:
        parser = ASTParser(results_path, parser_script, phpjoern_path)
        ast_root = parser.runPHPParser(getArg(flow, "p", "path"))
        
        if not ast_root:
            print "Could not parse given path! Exit."
            sys.exit()
        
        converter = AST2Gremlin(ast_root)
        
        try:
            getArg(flow, "d", "debug")
            query = converter.convertPHPAST(debug=True)
            
        except:
            query = converter.convertPHPAST()
            
        print query

def setupArgs(parser):
    """
    Setup command line arguments combinations.
    """
    # Search code clones: search -c file -in dir/file (-r)
    explanation = (
                ""
                )
    parser.addArgumentsCombination(
                                ARGS_CONVERT,
                                [
                            ["p=", "path"],
                            ],
                                [
                            ["d", "debug"]
                            ],
                                explanation=explanation
                                )

def getArg(_list, key1, key2=None):
    result = ""
    try:
        result = _list[key1]
    except:
        if key2:
            try:
                result = _list[key2]
            
            except:
                raise ArgException()
        
        else:
            raise ArgException()
        
    return result

if __name__ == '__main__':
    main(sys.argv)