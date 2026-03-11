# Flow

A tiny language with no variables — only pipes and transformations.

Computation is a river. You never name the water; you only shape where it goes.

## Syntax

```
source |> transform |> transform |> ...
```

**Sources** — where data begins:
- Numbers: `42`, `3.14`, `-7`
- Strings: `"hello world"`
- Lists: `[1, 2, 3]`
- Ranges: `1..10`

**Transforms** — what shapes the flow:

| Transform | Example | Description |
|-----------|---------|-------------|
| `map`     | `map double` | Apply a function to each element |
| `filter`  | `filter even` | Keep elements matching a predicate |
| `fold`    | `fold + 0` | Reduce to a single value |
| `reduce`  | `reduce +` | Fold without initial value |
| `take`    | `take 3` | Keep first N elements |
| `drop`    | `drop 2` | Remove first N elements |
| `reverse` | `reverse` | Reverse order |
| `sort`    | `sort` | Sort ascending |
| `unique`  | `unique` | Remove duplicates |
| `split`   | `split " "` | Split string into list |
| `join`    | `join ", "` | Join list into string |
| `sum`     | `sum` | Sum all elements |
| `length`  | `length` | Count elements |
| `first`   | `first` | First element |
| `last`    | `last` | Last element |
| `flatten` | `flatten` | Flatten nested lists |

**Built-in functions** (for `map` / `filter`):
- Predicates: `even`, `odd`, `positive`, `negative`, `zero`
- Mappers: `uppercase`, `lowercase`, `trim`, `abs`, `neg`, `double`, `square`, `str`, `int`, `float`, `len`
- Operators: `+`, `-`, `*`, `/`, `%`

## Examples

```
[3, 1, 4, 1, 5, 9] |> unique |> sort |> reverse
"hello world" |> split " " |> map uppercase |> join ", "
1..10 |> filter even |> fold + 0
1..10 |> filter odd |> map square
```

## Usage

```bash
# REPL
python3 flow.py

# Run a file
python3 flow.py examples.flow

# Evaluate an expression
python3 flow.py -e '[1, 2, 3] |> map double'

# Run tests
python3 flow.py --test
```
