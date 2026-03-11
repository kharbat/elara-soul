# System Dynamics Simulator

A tool for seeing how feedback loops create behavior.

Stocks accumulate. Flows change stocks. Feedback loops connect them. Delays hide the truth. From these four elements, every pattern emerges: growth, oscillation, collapse, equilibrium.

## Usage

```
python sim.py list              # see available models
python sim.py run <model>       # run a simulation
python sim.py explain <model>   # understand the feedback structure
```

## Models

| Model | Pattern | Mechanism |
|---|---|---|
| `exponential_growth` | Accelerating curve | Unopposed positive feedback |
| `logistic_growth` | S-curve to plateau | Positive loop meets negative loop |
| `oscillation` | Predator-prey cycles | Two interlinked negative loops with delay |
| `overshoot` | Growth then crash | Delayed negative feedback arrives too late |
| `s_curve` | Adoption wave | Word-of-mouth meets market saturation |

## Adding Models

Models are defined declaratively in `models.json`. A model specifies:

- **stocks** — quantities that accumulate (with initial values)
- **flows** — rates of change (as expressions over stocks and parameters)
- **updates** — how stocks change each timestep
- **parameters** — constants

Expressions can use stocks, parameters, flows, `t`, `dt`, and basic math functions (`max`, `min`, `abs`, `sqrt`, `log`, `exp`, `sin`, `cos`).

## Philosophy

The point is not numerical precision. The point is seeing the shape of behavior and understanding *why* it has that shape. Structure determines behavior. If you want different behavior, change the structure.
