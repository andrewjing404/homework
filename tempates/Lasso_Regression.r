library(glmnet)


## general Lasso
lasso_result <- glmnet(x, y, alpha = 1)

# Extract Lasso estimates for specific lambda
lasso_estimate <- coef(lasso_result, s = 0.5) # s is lambda

## Lasso with cross-validation
lasso_cv_result <- cv.glmnet(x, y, alpha = 1, nfolds = 10)

# Lasso Coefficients Plot (MSE, Log(lambda), and number of coefficients)
plot(lasso_cv_result, xvar = "lambda", label = TRUE)

# Extract best lambda
best_lambda <- lasso_cv_result$lambda.min

# Extract best coefficients at best lambda
lasso_best_estimate <- coef(lasso_result, s = best_lambda)