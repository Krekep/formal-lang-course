# Исполнитель запросов к графам
Это консольное приложение для выполнения запросов к графам.

## Как запустить приложение
Из корня проекта выполнить следующую команду в консоли:

```python -m project```

## Доступные команды
* create-graph --- Создать граф
    * two-cycles --- Создать граф из двух циклов с метками на рёбрах.
* save-to-dot --- Сохранить граф по указанному пути.
* print-graph-info --- Получить информацию о графе.
* quit --- Закончить исполнение программы.
* graph-to-nfa --- Построение по графу недетерминированного конечного автомата.

### Граф с двумя циклами
```bash
create-graph two-cycles [-h] name first-cycle-vertices second-cycle-first_cycle_vertices [--edge-labels L1 L2]
```
#### Пример
```bash
create-graph two-cycles test 10 5 --edge-labels a b
```

### Запись в файл
```bash
save-to-dot [-h] name folder-path
```

#### Пример
```bash
save-to-dot test tests/data
```

### Информация о графе
```bash
print-graph-info name
```

### Недетерминированный автомат по графу
```bash
graph-to-nfa graph-name [--start-vertices list] [--finish-vertices list]
```
#### Пример
```bash
graph-to-nfa test --start-vertices 1 2 3 --finish-vertices 10
```
