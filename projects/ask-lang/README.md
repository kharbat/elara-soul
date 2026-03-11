# Ask

A prototype language where **types are questions** and **values are answers**.

Instead of `x: Int`, you write `x: "how many?"`. A function signature reads like a conversation.

## Quick Start

```bash
# Run the REPL
python3 ask.py

# Run a file
python3 ask.py examples.ask

# Run the test suite (25 tests)
python3 ask.py --test
```

## The Idea

Every value knows what question it answers:

```
ask> 42
  => 42  (answers "how many?")

ask> "hello"
  => 'hello'  (answers "what?")

ask> true
  => True  (answers "true or false?")
```

Functions declare what questions their arguments answer and what question the return value answers:

```
define greet(who: "what?", times: "how many?") -> "what?":
  repeat(times, "Hello, " + who + "! ")
```

Type errors read naturally:

```
ask> greet(42, 3)
  !! Expected an answer to 'what?' but got an answer to 'how many?' (in argument 'who' of greet())
```

## Built-in Question Types

| Question | Corresponds to |
|---|---|
| `"how many?"` | integers |
| `"how much?"` | floats |
| `"what?"` | strings |
| `"true or false?"` | booleans |
| `"what list?"` | lists |

## Custom Questions

```
question "how old?" = number
define can_vote(age: "how old?") -> "true or false?": age >= 18
```

## Features

- Arithmetic, comparison, string, boolean, and list operations
- Conditionals (`if ... : ... else: ...`)
- `repeat(n, expr)` for repetition
- `len()`, `head()`, `tail()`, `append()`, `str()` builtins
- Custom question types via `question`
- Inference: the system figures out what question a value answers

## Where the Metaphor Works

- Error messages become conversations: "I expected an answer to X but got an answer to Y"
- Function signatures read as dialogues
- Forces you to think about *why* a value exists, not just its shape

## Where It Gets Tricky

- Compound types (`"what list of how many?"`) get awkward fast
- Generic functions need questions about questions
- The mapping between question and base type is sometimes arbitrary
- Some values answer multiple questions equally well
