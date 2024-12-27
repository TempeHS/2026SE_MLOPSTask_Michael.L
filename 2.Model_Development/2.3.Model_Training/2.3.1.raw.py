import numpy as np
from sklearn.linear_model import LinearRegression


x = np.array([[2], [4], [6], [8], [10], [12], [14], [16]])
y = np.array([1, 3, 5, 7, 9, 11, 13, 15])
model = LinearRegression()
model.fit(x, y)
test = np.array([4])
y_prediction = model.predict(test.reshape(1, -1))
print(f"predicted feature is: {y_prediction}")