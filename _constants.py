'''
Created on Nov 21, 2015

These types, flags etc. are copied and extended from python-joerns's 
php-addition's _constants.groovy file.

@author: Tommi Unruh
'''

# Node types
TYPE_STMT_LIST = 'AST_STMT_LIST' # ...; ...; ...;
TYPE_CALL = 'AST_CALL' # foo()
TYPE_STATIC_CALL = 'AST_STATIC_CALL' # bla::foo()
TYPE_METHOD_CALL = 'AST_METHOD_CALL' # $bla->foo()
TYPE_PROP = 'AST_PROP' # e.g., $bla->foo
TYPE_FUNC_DECL = 'AST_FUNC_DECL' # function foo() {}
TYPE_METHOD = 'AST_METHOD' # class bla { ... function foo() {} ... }0
TYPE_ARG_LIST = 'AST_ARG_LIST' # foo( $a1, $a2, $a3)
TYPE_PARAM_LIST = 'AST_PARAM_LIST' # function foo( $p1, $p2, $p3) {}
TYPE_PARAM = 'AST_PARAM' # $p1
TYPE_ASSIGN = 'AST_ASSIGN' # $buzz = true
TYPE_ASSIGN_REF = 'AST_ASSIGN_REF' # $b = &$a
TYPE_ASSIGN_OP = 'AST_ASSIGN_OP' # $x += 3
TYPE_NAME = 'AST_NAME' # names (e.g., name of a called function in call expressions)
TYPE_VAR = 'AST_VAR' # $v
TYPE_BINARY_OP = 'AST_BINARY_OP' # e.g., "foo"."bar" or 3+4
TYPE_ENCAPS_LIST = 'AST_ENCAPS_LIST' # e.g., "blah{$var1}buzz $var2 beep"
TYPE_INCLUDE_OR_EVAL = 'AST_INCLUDE_OR_EVAL' # eval, include, require
TYPE_SIMPLE_STRING = 'string'
TYPE_SIMPLE_INT = 'integer'
# Additions
TYPE_DIM = 'AST_DIM' # $_POST[], $_GET[]
TYPE_ISSET = 'AST_ISSET' # isset()
TYPE_IF = 'AST_IF' # if () {}
TYPE_IF_ELEM = 'AST_IF_ELEM' # a node for the if block or the else block.
TYPE_NULL = 'NULL'

# AST node flags
# of AST_ASSIGN.*
FLAG_ASSIGN_CONCAT = 'ASSIGN_CONCAT' # $v .= "foo"
# of AST_BINARY_OP
FLAG_BINARY_CONCAT = 'BINARY_CONCAT' # "foo"."bar"
# of AST_INCLUDE_OR_EVAL
FLAG_EXEC_EVAL = 'EXEC_EVAL' # eval("...")
FLAG_EXEC_INCLUDE = 'EXEC_INCLUDE' # include "..."
FLAG_EXEC_INCLUDE_ONCE = 'EXEC_INCLUDE_ONCE' # include_once "..."
FLAG_EXEC_REQUIRE = 'EXEC_REQUIRE' # require "..."
qFLAG_EXEC_REQUIRE_ONCE = 'EXEC_REQUIRE_ONCE' # require_once "..."