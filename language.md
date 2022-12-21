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
prog -> stmt ; prog
      | eps

stmt -> 'print' '(' expr ')' 
      | var '=' expr

expr -> graph
      | map
      | filter
      | var
      | val
      | 'not' expr
      | expr 'in' expr
      | expr '&' expr
      | expr '.' expr
      | expr '|' expr
      | expr '*'
      
graph ->
    var
    | 'load' '(' PATH ')'
    | 'set_start' '(' vertices ',' graph ')'
    | 'set_final' '(' vertices ',' graph ')'
    | 'add_start' '(' vertices ',' graph ')'
    | 'add_final' '(' vertices ',' graph ')'

NONZERO -> [1-9]
DIGIT -> [0-9]
INT -> (NONZERO DIGIT*) | 0

BOOL -> 'true'
      | 'false'

CHAR -> [a-z] | [A-Z]
STRING -> '"' (CHAR | DIGIT | '_' | ' ')* '"'
PATH -> '"' (CHAR | DIGIT | '_' | ' ' | '/' | '.')* '"'

IDENTIFIER -> INITIAL_LETTER LETTER*
FIRST_SYMBOL -> '_' | CHAR
SYMBOL -> INITIAL_LETTER | DIGIT

SET<X> -> '{' (X ',')* X? '}' | 'set()'
LIST<X> -> '[' (X ',')* X? ']' | 'list()'

vertex -> var | INT

vertices ->
    var
    | SET<vertex>
    | 'range' '(' INT ',' INT ')'
    | 'get_start' '(' graph ')'
    | 'get_final' '(' graph ')'
    | 'get_vertices' '(' graph ')'
    | filter
    | map

edges -> edge
       | SET<edge>
       | 'get_edges' '(' graph ')'

edge -> '(' vertex ',' label ',' vertex ')'
      | '(' vertex ',' vertex ')'

label -> STRING

labels -> label
        | SET<label>
        | 'get_labels' '(' graph ')'


lambda -> 'fun' LIST<var> ':' expr
        | 'fun' ':' expr

filter -> 'filter' '(' lambda ',' expr ')'
map -> 'map' '(' lambda ',' expr ')'

var -> IDENTIFIER

val -> STRING
     | INT
     | BOOL
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
