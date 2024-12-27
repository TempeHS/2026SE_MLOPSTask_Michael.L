import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
plt.style.use('style_Matplotlib_charts.mplstyle')
from sklearn.linear_model import LinearRegression


con = sql.connect("4.SQlite3.db")
cur = con.cursor()
col_0 = "feature"
col_1 = "target"
x = np.array(cur.execute(f"SELECT {col_0} FROM data").fetchall())
y = np.array(cur.execute(f"SELECT {col_1} FROM data").fetchall()).flatten()
con.close()
m = len(x)
print(f"Number of training examples is: {m}")
table = pd.DataFrame({
    col_0: x.flatten(),  # Flatten x for easy display
    col_1: y
})
print(table.head())
plt.scatter(x, y, marker='x', c='r')
plt.title("NESA Course Specifications Data")
plt.ylabel(f'Training {col_0}')
plt.xlabel(f'Training {col_1}')
plt.show()
m = len(x)
print(f"Number of training examples is: {m}")
my_model = LinearRegression()
my_model.fit(x, y)
y_pred = my_model.predict(x)
plt.plot(x, y_pred)
plt.scatter(x, y, marker='x', c='r')
plt.title("NESA Course Specifications Data")
plt.ylabel(f'Training {col_0}')
plt.xlabel(f'Training {col_1}')
plt.show()
test = np.array([4.5])
predict = np.array([4.5]).reshape(1, -1)
y_prediction = my_model.predict(predict)
y_pred = my_model.predict(x)
plt.plot(x, y_pred)
plt.scatter(x, y, marker='x', c='r')
plt.scatter(predict, y_prediction, marker='D', c='r', zorder=10, s=100)
plt.text(y_prediction, predict, f"Target {y_prediction[0]} is prediction from {predict[0,0]} input")
plt.title("NESA Course Specifications Data")
plt.ylabel(f'Training {col_0}')
plt.xlabel(f'Training {col_1}')
plt.show()
print(f"predicted feature is: {y_prediction}")