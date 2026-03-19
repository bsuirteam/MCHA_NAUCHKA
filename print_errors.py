import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('errors.csv')

df.plot(x = "Generation", y = "Error")

plt.show()