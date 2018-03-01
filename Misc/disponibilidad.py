"""
Calculo de la disponibilidad de un sistema al duplicar los componentes
"""

def f(x):
  return x + (1.0 - x)*x

def g(x):
  return f(x) + (1.0-f(x))*x

#Disponibilidad de cada componente del sistema
x = [0.85, 0.9, 0.999, 0.98, 0.85, 0.99, 0.9999, 0.95]

f(0.8)

l = [g(x[i]) for i in range(len(x)) ]

from numpy import prod

#Disponibilidad del sistema
prod(l)
