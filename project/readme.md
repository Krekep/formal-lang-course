# Как использовать приложение
Из корня проекта выполнить следующую команду в консоли:

```python -m project```

## Доступные команды
* create-graph --- Создать граф
    * two-cycles --- Создать граф из двух циклов с метками на рёбрах.
* save-to-dot --- Сохранить граф по указанному пути.
* print-graph-info --- Получить информацию о графе.
* quit --- Закончить исполнение программы.

### Граф с двумя циклами
```bash
create-graph two-cycles [-h] name [--folder_path path] first-cycle-vertices second-cycle-first_cycle_vertices [--edge-labels L1 L2]
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
