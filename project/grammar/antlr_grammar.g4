grammar antlr_grammar;

prog : (EOL? WS? stmt SEMI EOL?)+ EOF;
WS : [ \t\r]+ -> skip ;
EOL : [\n]+ ;
SEMI : ';' WS?;

stmt : 'print' '(' expr ')'
      | var '=' expr
      ;

expr : my_graph
      | my_map
      | my_filter
      | var
      | val
      | labels
      | vertices
      | edges
      | 'not' expr
      | expr 'in' expr
      | expr '&' expr
      | expr '.' expr
      | expr '|' expr
      | expr '*'
      | '(' expr ')'
      ;

my_graph :
    var
    | 'load' '(' STRING ')'
    | 'set_start' '(' vertices ',' my_graph ')'
    | 'set_final' '(' vertices ',' my_graph ')'
    | 'add_start' '(' vertices ',' my_graph ')'
    | 'add_final' '(' vertices ',' my_graph ')'
    ;

NONZERO : [1-9] ;
DIGIT : [0-9] ;
INT : (NONZERO DIGIT*) | [0] ;

BOOL : 'true'
      | 'false'
      ;

CHAR : [a-z] | [A-Z] ;
STRING : '"' (CHAR | DIGIT | '_' | ' ')* '"' ;
PATH : '"' (CHAR | DIGIT | '_' | ' ' | '/' | '.')* '"' ;

IDENTIFIER : FIRST_SYMBOL (SYMBOL)* ;
FIRST_SYMBOL : '_' | CHAR ;
SYMBOL : FIRST_SYMBOL | DIGIT ;

vertex : var | INT ;

vertices :
    var
    | '{' (vertex ',')* (vertex)? '}'
    | 'range' '(' INT ',' INT ')'
    | 'get_start' '(' my_graph ')'
    | 'get_final' '(' my_graph ')'
    | 'get_vertices' '(' my_graph ')'
    | my_filter
    | my_map
    ;

edges : edge
       | '{' (edge ',')* (edge)? '}'
       | 'get_edges' '(' my_graph ')'
       ;

edge : '(' vertex ',' label ',' vertex ')'
      | '(' vertex ',' vertex ')'
      ;

label : STRING ;

labels : label
        | '{' (label ',')* (label)? '}'
        | 'get_labels' '(' my_graph ')'
        ;


my_lambda :  'fun' '[' (var ',')* var? ']' ':' expr
        | 'fun' ':' expr
        ;

my_filter : 'filter' '(' my_lambda ',' expr ')'
          | 'filter' '(' '(' my_lambda ')' ',' expr ')' ;
my_map : 'map' '(' my_lambda ',' expr ')'
       | 'map' '(' '(' my_lambda ')' ',' expr ')' ;

var : IDENTIFIER ;

val : STRING
     | INT
     | BOOL
     ;
