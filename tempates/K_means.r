## Use BIC to find the best K for K-means clustering


kmeansBIC <- function(fit) {
    m <- ncol(fit$centers)
    n <- length(fit$cluster)
    k <- nrow(fit$centers)
    D <- fit$tot.withinss
    return(D + log(n) * m * k)
}

# scale data - method 1
scaled_data <- scale(as.matrix(data / rowSums(data)))

# scale data - method 2
scaled_data <- scale(data)

# what K values want to try
k_pool <- seq(3, 20)
kmean_result <- lapply(X = k_pool, FUN = kmeans, x = scaled_data, nstart = 25, iter.max = 50)

k_list <- c()
BIC_list <- c()
deviance_list <- c()

for (i in 1:length(k_pool)) {
    k <- k_pool[i]
    k_list <- c(k_list, k)
    BIC <- kmeansBIC(kmean_result[[i]])
    BIC_list <- c(BIC_list, BIC)
    deviance <- kmean_result[[i]]$tot.withinss
    deviance_list <- c(deviance_list, deviance)
    cat("k =", k, "BIC =", BIC, "\n")
    if (i == length(k_pool)) {
        cat("\nMinimum BIC is:", min(BIC_list))
        cat("Optimal k is:", k_list[BIC_list == min(BIC_list)], "\n")
        result_optimized <- kmeans(congress109Counts_scaled, nstart = 5, iter.max = 20, centers = k_list[BIC_list == min(BIC_list)])
        print(tapply(congress109Ideology$party, result_optimized$cluster, table))
    }
}

# Use elbow curve method to choose the optimal K
plot(x = k_list, y = deviance_list)