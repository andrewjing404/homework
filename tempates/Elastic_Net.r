library(glmnet)

## General elastic net regression
result_en <- glmnet(x, y, alpha = 0.5) # alpha is weight

# Draw coefficients plot
plot(result_en, xvar = "lambda", label = TRUE)

# Extract estimates
en_estimate <- coef(result_en, s = 0.01) # s is lambda


## Elastic net with cross validation
result_cv_en <- cv.glmnet(x, y, type.measure = "mse", nfolds = 10)

# Plot MSE vs lambda
plot(result_cv_en, main = "Select Best Lambda")

# Extract best lambda at this alpha
en_best_lambda_at_alpha <- result_cv_en$lambda.min

# lambda at 1se away
result_cv_en$lambda.1se

# Best estimates at a certain alpha
en_best_est_at_alpha <- coef(result_en, s = en_best_lambda_at_alpha)

## Find the best alpha + lambda combination (judged by MSE)
alpha_pool <- seq(0, 1, by = 0.05)

alpha <- c()
mse <- c()
lambda <- c()

for (a in alpha_pool) {
    result <- cv.glmnet(x, y, type.measure = "mse", nfolds = 10, alpha = a)
    mse <- mean(temp_result$cvsd)
    alpha <- c(alpha, a)
    mse <- c(mse, mse)
    lambda <- c(lambda, result$lambda.min)
}

# Print the best alpha, lambda, and their MSE
en_result <- as.data.frame(cbind(alpha, mse, lambda))
en_result[en_result$mse == min(en_result$mse), ]$alpha