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
      | NOT expr
      | expr IN expr
      | expr AND expr
      | expr DOT expr
      | expr OR expr
      | expr KLEENE
      | LP expr RP
      ;

AND : '&' ;
OR : '|' ;
NOT : 'not' ;
IN : 'in' ;
KLEENE : '*' ;
DOT : '.' ;
LP : '(' ;
RP : ')' ;

my_graph :
    var
    | load_graph
    | set_start
    | set_final
    | add_start
    | add_final
    ;

load_graph : 'load' '(' string ')' ;
set_start : 'set_start' '(' vertices ',' my_graph ')' ;
set_final : 'set_final' '(' vertices ',' my_graph ')' ;
add_start : 'add_start' '(' vertices ',' my_graph ')' ;
add_final : 'add_final' '(' vertices ',' my_graph ')' ;

NONZERO : [1-9] ;
DIGIT : [0-9] ;
INT : (NONZERO DIGIT*) | [0] ;

TRUE : 'true' ;
FALSE : 'false' ;

CHAR : [a-z] | [A-Z] ;
STRING : '"' (CHAR | DIGIT | '_' | ' ')* '"' ;
PATH : '"' (CHAR | DIGIT | '_' | ' ' | '/' | '.')* '"' ;


MY_IDENTIFIER : (FIRST_SYMBOL) (MY_SYMBOL*) ;
FIRST_SYMBOL : '_' | CHAR ;
MY_SYMBOL : FIRST_SYMBOL | DIGIT ;

vertex : var | INT ;

vertices :
    vertex
    | vertices_set
    | my_range
    | get_start
    | get_final
    | get_vertices
    | get_reachable
    | my_filter
    | my_map
    ;

get_start : 'get_start' '(' my_graph ')' ;
get_final : 'get_final' '(' my_graph ')' ;
get_vertices : 'get_vertices' '(' my_graph ')' ;
get_reachable : 'get_reachable' '(' my_graph ')' ;
my_range : 'range' '(' INT ',' INT ')' ;

vertices_set : '{' (vertex ',')* (vertex)? '}'
                | '{' (vertices_set ',')* (vertices_set)? '}' ;

edges : edge
       | edges_set
       | get_edges
       ;

get_edges : 'get_edges' '(' my_graph ')' ;

edge : '(' vertex ',' label ',' vertex ')'
      | '(' vertex ',' vertex ')'
      ;

edges_set : '{' (edge ',')* (edge)? '}' ;

label : string ;

labels : label
        | labels_set
        | get_labels
        ;

get_labels : 'get_labels' '(' my_graph ')' ;

labels_set : '{' (label ',')* (label)? '}' ;

my_lambda :  'fun' '[' (var ',')* var? ']' ':' expr
        | 'fun' ':' expr
        ;

my_filter : 'filter' '(' my_lambda ',' expr ')'
          | 'filter' '(' '(' my_lambda ')' ',' expr ')' ;
my_map : 'map' '(' my_lambda ',' expr ')'
       | 'map' '(' '(' my_lambda ')' ',' expr ')' ;

var : MY_IDENTIFIER ;

val : labels
     | vertices
     | edges
     | bool
     ;

bool : TRUE
      | FALSE
      ;

string : STRING ;

int : INT ;
