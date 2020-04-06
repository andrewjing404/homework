library(glmnet)


## General ridge regression
ridge_result <- glmnet(x, y, alpha = 0)

# Coefficient Plot
plot(ridge_result, xvar = "lambda", label = TRUE)

# Extract estimates at specific lambda
ridge_estimate <- coef(ridge_result, s = 0.01) # s is lambda

## Ridge regression with cross-validation
ridge_cv_result <- cv.glmnet(x, y, type.measure = "mse", nfolds = 10)

# Plot MSE vs lambda
plot(ridge_cv_result, main = "Select Best Lambda")

# Extract best lambda
ridge_best_lambda <- ridge_cv_result$lambda.min
ridge_best_estimate <- coef(ridge_result, s = ridge_best_lambda)