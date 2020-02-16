library(readr)
library(ggplot2)
library(ggrepel)
library(glmnet)

###### Positiioning Maps
## Take in survey data, perform dimension reduction (here, Eigen transformation).
## Identify the two most important Eigen vector and draw positioning maps


positioning_map <- function(directory){
    table <- read_file(directory)
    table$`Poor Value` <- table$`Poor Value` * -1
    table$Uncomfortable <- table$Uncomfortable * -1
    table$Unreliable <- table$Unreliable * -1
    table$`Poorly Built` <- table$`Poorly Built` * -1
    brands <- table[, 1]
    attributes <- table[, -c(1, ncol(table))]
    attributes_name <- colnames(table[, -c(1, ncol(table))])
    preference <- table[, ncol(table)]
    correlation_matrix <- cov(attributes, method = "pearson")
    eigen <- eigen(correlation_matrix)$vectors
    Z1 <- eigen[, 1]*-1
    Z2 <- eigen[, 2]
    Z1_name <- paste(attributes_name[Z1 > 0.3], collapse = " + ")
    Z2_name <- paste(attributes_name[Z2 > 0.3], collapse = " + ")
    Z1 <- apply(attributes, 1, function(x) sum(x*Z1))
    Z2 <- apply(attributes, 1, function(x) sum(x*Z2))
    fit <- summary(lm(preference ~ Z1 + Z2))
    fit_coef <- fit$coefficients[, 1]
    fit_se <- fit$coefficients[, 2]
    ideal_vector <- as.vector(fit_coef[3]/fit_coef[2])
    iso_preference <- -1 / ideal_vector
    output <- c()
    output$brands <- brands
    output$Z1 <- Z1
    output$Z2 <- Z2
    output$Preference <- fit_coef[1] + Z1*fit_coef[2] + Z2*fit_coef[3]
    output <- as.data.frame(output)
    ggplot(output, aes(x=Z1, y=Z2)) +
        ggtitle("Positioning Map") +
        geom_point(color="blue") +
        geom_text_repel(aes(label=brands)) +
        labs(x = Z1_name , y = Z2_name) +
        theme_classic()
}


iso_preference_6 <- data.frame(x = c(0, (6-fit_coef[1])/fit_coef[2]), y = c((6-fit_coef[1])/fit_coef[3], 0))
iso_preference_4 <- data.frame(x = c(0, (4-fit_coef[1])/fit_coef[2]), y = c((4-fit_coef[1])/fit_coef[3], 0))
ggplot(iso_preference_6, aes(x=x, y=y)) + geom_path(size = 5)
summary(lm(preference ~ Z1 + Z2))

c(0, (4-fit[1])/fit[3])
c((4-fit[1])/fit[2], 0)
derp <- summary(fit)
derp$coefficients[,1]
# open csv or xlsx file
read_file <- function(directory) {
    library(stringr)
    dir_len <- str_length(directory)
    suffix <- substr(directory, dir_len-3, dir_len)
    if(suffix == ".csv") {
        file <- read_csv(directory)
        colnames(file) <- str_replace(colnames(file), " \n", " ")
        colnames(file) <- str_replace(colnames(file), "\n", " ")
    } else if (suffix == "xlsx") {
        file <- read_xlsx(directory)
    } else {
        error("Please make sure the file is either .csv or .xlsx.")
    }
    return(as.data.frame(file))
}


positioning_map("Cars_Data.csv")