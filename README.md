# Gramian Angular Field Visualization of Time Series

Given the intrest with algorithm trading in the financial technology sector, I wanted to create a so-called "Trading-Bot" by using the novel prediction machine learning algortihms


## Time Series Analysis Algorithms:

### Gramian Angular Field :

Gramian Angular Field (GAF) Imaging turns out one of the most popular time series imaging algorithms.
First proposed by team of faculty and students from the Department of Mathematics and Computer Science of the University of Cagliari in Italy, 
the approach transforms time-series into images and uses hence CNN to identify visual patterns for prediction.

![image](https://github.com/takumiSudo/algo_trading/assets/126654769/5aa13da4-ef0d-4f3d-ad03-056ba3f2fe87)

Converting the i-j element of the matrix back to the Cartesian coordinates: cos(θ_i+θ_j)=cos(θ_i)cos(θ_j)+sin(θ_i)sin(θ_j)=x_i x_j+√(1-x_i²)√(1-x_j²) and we can immediately see the following properties of the definition:

  If and only if x_i=x_j, the element equals -1.
  If and only if x_i=x_j=0, the element equals 1.
  If x_i=-x_j while the absolute value of both is close to -1. This means that the value of the element cannot capture the sign of the correlation.
  
  
  
Step 1: Scale the serie onto [-1, 1] with a Min-Max scaler
We proceed similarly than in the naïve implementation. Coupled with the Min-Max scaler, our polar encoding will be bijective, the use the arccos function bijective (see next step).

Step 2: Convert the scaled time serie into “polar coordinates”
Two quantities need to be accounted for, the value of the time series and its corresponding timestamp. These two variables will be expressed respectively with the angle and the radius.

Assuming our time series is composed of N timestamps t with corresponding values x, then:

The angles are computed using arccos(x). They lie within [0, ∏].
The radius variable is computed by first, we divide the interval [0, 1] into N equal parts. We therefore obtain N+1 delimiting points {0, …, 1}. We then discard 0 and associate consecutively these points to the time series.
Mathematically, it translates to this:

![image](https://github.com/takumiSudo/algo_trading/assets/126654769/ad53c035-760b-4438-88f8-2fc1dfc18f84)

