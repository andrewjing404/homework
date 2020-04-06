library(boot)

bs <- function(data, indicies){
    #data has to be a df, and including indicies will allow slicing the data
    d <- data[indicies, ]
    # calculation, things want to be bootstrapped
    # then return the result
    return()
}

results <- boot(data = data, statistic=bs, R=1000)

plot(results)

# display 95% CI
quantile(results$t, c(0.025, 0.975))