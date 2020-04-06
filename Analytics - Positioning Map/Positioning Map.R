library(readr)
library(ggplot2)
library(ggrepel)


positioning_map <- function(directory){
    table <- read_file(directory)
    brands <- table[, 1]
    attributes <- table[, -c(1, ncol(table))]
    preference <- table[, ncol(table)]
    correlation_matrix <- cor(attributes, method = "pearson")
    eigen <- eigen(correlation_matrix)$vectors[, 1:2]
    Z1 <- eigen[, 1]
    Z2 <- eigen[, 2]
    Z1 <- apply(attributes, 1, function(x) sum(x*Z1))
    Z2 <- apply(attributes, 1, function(x) sum(x*Z2))
    lm(preference ~ Z1 + Z2)
    output <- c()
    output$brands <- brands
    output$Z1 <- Z1
    output$Z2 <- Z2
    output <- as.data.frame(output)
    ggplot(output, aes(x=Z1, y=Z2)) +
        ggtitle("Positioning Map") +
        geom_point(color="blue") +
        geom_text_repel(aes(label=brands)) +
        theme_classic()
}


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



