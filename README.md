# Planetensimulation mit Reinforced Learning
<p align="center">
  <img src="https://user-images.githubusercontent.com/44225863/120490838-07133f00-c3b9-11eb-9352-a7df5f518b6d.png" alt="1442401" width="60%" height="60%">
</p>

## TODO:
- `keras-rl` / `keras` / `tensorflow.keras` installieren (noch nicht ganz sicher, welches wir benötigen)

## kNN Research
https://hawhamburgde-my.sharepoint.com/:o:/g/personal/joseffa_steuernagel_haw-hamburg_de/Ek6hzA7c0ktCjPyQAAoxLhwBvw9r4ONEP8tcgwJBYmGDJw?e=JYx68c

https://realpython.com/knn-python/#fit-knn-in-python-using-scikit-learn

## Aktivierung der virtuellen Python Umgebung:
Windows:
```
.venv\Scripts\activate.bat
```
Unix / MacOS:
```
source .venv/Scripts/activate
```

## Visualisierung starten
```
python vis.py
```

oder

```
python3 vis.py
```

## Simulation starten
```
python sim.py
```

oder

```
python3 sim.py
```


## Visualisierung
| Key(s)    | Action(s)                                          |
|-----------|----------------------------------------------------|
| `SPACE`   | Pause/play simulation                              |
| `↑ ↓ ← ↑` | Move window view; pan about                        |
| `+/-`     | Zoom in and out respectively                       |
| `r`       | Reset zoom and position                            |
| `l`       | Toggle labels on the entities                      |
| `h`       | Toggle history paths on the entities               |
| `t`       | Toggle simulation space visualization              |
| `q`       | Quit the simulation                                |

## Inspiration
- https://github.com/ModMaamari/reinforcement-learning-using-python
- https://github.com/akuchling/50-examples/blob/master/gravity.rst
- https://www.youtube.com/watch?v=fML1KpvvQTc
