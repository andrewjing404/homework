## Need to decide the cutoff point beforehand

rdd_fit <- glm(Y ~ cutoff + X_minus_cutoff + cutoff*X_minus_cutoff, data = data)
summary(rdd_fit2)