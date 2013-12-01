"""
No documentation, whee!
"""


dmax = 30000
x_offset = 0
y_offset = 0

x_divisor = 1
y_divisor = 1

		# ===========================
		# BASIC SURFACE CONFIGURATION
		# ===========================

Y_MAX = dmax / y_divisor + y_offset
Y_MIN = -dmax / y_divisor + y_offset

X_MAX = dmax / x_divisor + x_offset # My left
X_MIN = -dmax / x_divisor + x_offset # My right

X_LENGTH = abs(X_MAX - X_MIN)
Y_LENGTH = abs(Y_MAX - Y_MIN)
XY_AREA = X_LENGTH * Y_LENGTH

