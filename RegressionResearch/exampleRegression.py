# Beispiel nach https://www.pluralsight.com/guides/regression-keras

#----------Step 1:----------#

# Import required libraries
import pandas as pd
# Pandas scheint wirklich geiler scheiß zu sein
import numpy as np
import matplotlib.pyplot as plt
import sklearn

# Import necessary modules
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from math import sqrt

# Keras specific
import keras
from keras.models import Sequential
from keras.layers import Dense

#----------Step 2:----------#
# liest die Daten als Pandas Dataframe ein
df = pd.read_csv('regressionexample.csv')
print(df.shape)  # Gibt Form aus
df.describe()  # erzeugt zusammenfassende Statistik der numerischen Variablen

# Output: X Beobachtungen von Y Variablen

#----------Step 3:----------#
target_column = ['unemploy']  # erstellt ein Objekt der Zielvariablen
# Liefert Liste aller Merkmale mit Ausnahme der Zielvariablen
predictors = list(set(list(df.columns))-set(target_column))
# normalisiert die Prädiktoren
df[predictors] = df[predictors]/df[predictors].max()
# Wichtig, weil sich die Einheiten der Variablen erheblich unterscheiden und den Modellierungsprozess beeinflussen können.
# Um dies zu verhindern, wird die Normalisierung über eine Skalierung der Prädiktoren zwischen 0 und 1 vorgenommen.
df.describe()  # Zusammenfassung der normalisierten Daten
# alle unabhängigen Variablen werden zwischen 0 und 1 skaliert.
# Die Zielvariable bleibt unverändert.

#----------Step 4:----------#
X = df[predictors].values
# erstellen Arrays mit unabhängigen (X) bzw. abhängigen (y) Variablen
y = df[target_column].values

# teilt die Daten in Trainings- und Testdatensatz auf
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.30, random_state=40)
print(X_train.shape)
print(X_test.shape)  # Gibt Form des Trainingsatzes und Testsatzes aus

# Output: X Beobachtungen und Y Variablen

#----------Step 5:----------#
# Define model
model = Sequential()  # ruft den Sequential-Konstruktor auf
# stellt die erste Schicht dar, die die Aktivierungsfunktion und die Anzahl der Eingabedimensionen angibt
model.add(Dense(500, input_dim=4, activation="relu"))
model.add(Dense(100, activation="relu"))
# Stellen 2. Schicht dar, Hidden Layer. Ohne den Parameter input_dim
model.add(Dense(50, activation="relu"))
# erzeugt die Ausgabeschicht mit einem Knoten, der die Anzahl der Arbeitslosen in Tausend ausgeben soll.
model.add(Dense(1))
# model.summary() #Print model Summary

# definieren eines Optimierers und das Verlustmaß für das Training
model.compile(loss="mean_squared_error", optimizer="adam",
              metrics=["mean_squared_error"])
# passt das Modell auf den Trainingsdatensatz an
model.fit(X_train, y_train, epochs=20)

#----------Step 6:----------#
pred_train = model.predict(X_train)  # sagt die Zugdaten voraus (Train data)
# gibt RMSE-Wert für die Zugdaten aus
print(np.sqrt(mean_squared_error(y_train, pred_train)))
# Wiederholung
pred = model.predict(X_test)
print(np.sqrt(mean_squared_error(y_test, pred)))
