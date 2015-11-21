'''
Created on Nov 20, 2015

@author: Tommi Unruh
'''
import sys
from ast_parser import ASTParser
from ast2gremlin import AST2Gremlin

def main(args):
    results_path  = "../ccdetection/AST_parser/parse_results"
    parser_script = "../ccdetection/AST_parser/parser"
    phpjoern_path = "/opt/phpjoern"
    parser = ASTParser(results_path, parser_script, phpjoern_path)
    ast_root = parser.runPHPParser(args[1])
    
    converter = AST2Gremlin(ast_root)
    query = converter.convertPHPAST()
    print query

if __name__ == '__main__':
    main(sys.argv)