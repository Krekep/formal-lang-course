# Язык запросов к графам

### Описание абстрактного синтаксиса языка

```
prog = List<stmt>

stmt =
    bind of var * expr
  | print of expr

val =
    String of string
  | Int of int
  | Bool of bool

expr =
    Var of var                   // переменные
  | Val of val                   // константы
  | Set_start of Set<val> * expr // задать множество стартовых состояний
  | Set_final of Set<val> * expr // задать множество финальных состояний
  | Add_start of Set<val> * expr // добавить состояния в множество стартовых
  | Add_final of Set<val> * expr // добавить состояния в множество финальных
  | Get_start of expr            // получить множество стартовых состояний
  | Get_final of expr            // получить множество финальных состояний
  | Get_reachable of expr        // получить все пары достижимых вершин
  | Get_vertices of expr         // получить все вершины
  | Get_edges of expr            // получить все рёбра
  | Get_labels of expr           // получить все метки
  | Map of lambda * expr         // классический map
  | Filter of lambda * expr      // классический filter
  | Load of path                 // загрузка графа
  | Intersect of expr * expr     // пересечение языков
  | Concat of expr * expr        // конкатенация языков
  | Union of expr * expr         // объединение языков
  | Star of expr                 // замыкание языков (звезда Клини)
  | Smb of expr                  // единичный переход

lambda = Lambda of List<var> * expr
```


### Описание конкретного синтаксиса языка

```
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

IDENTIFIER : FIRST_SYMBOL (SYMBOL)* ;
FIRST_SYMBOL : '_' | CHAR ;
SYMBOL : FIRST_SYMBOL | DIGIT ;

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

vertices_set : '{' (vertex ',')* (vertex)? '}' ;

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

var : IDENTIFIER ;

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
```

### Пример программы

Данный скрипт загружает граф "bzip", задаёт вершины с номерами от 1 до 100 в качестве стартовых вершин и в качестве финальных вершин все вершины графа. Создаёт запрос к графу, выполняет пересечение и выводит результат.
```
g = load("bzip");
g1 = set_final(get_vertices(g), set_start(range(1, 100), g));

q = ("l" . "r"*)*
res = g1 & q;
print(res)

```
