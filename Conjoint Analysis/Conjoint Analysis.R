library(dplyr)
library(readxl)
library(readr)
library(stringr)
library(stats)

###### Conjoint Analysis
## Feed in survey data and determine what's the best design of the product.
## At the best design, what's the mamximized profit.
## Not considering competitors' moves.


# please define the dummy price and the other price in the survey.
# the function doesn't work on experiments with mroe than 2 levels of price.
dummy_price <- 2500
the_other_price <- 2000
price_range <- range(dummy_price, the_other_price)[2] - range(dummy_price, the_other_price)[1]
Intercept <- 1000 
`Screen 52 inch` <- 500
`Screen 65 inch` <- 1000
`2D or 3D` <- 250
`Sony = 1` <- 250
component_cost <- c(1000, 500, 1000, 250, 250, 0)
our_design <- c(1, 0, 1, 0, 0, 2500)
competitor_1 <- c(1, 1, 0, 1, 1, 2500)
competitor_2 <- c(1, 0, 1, 1, 0, 2000)
profile <- matrix(c(our_design, competitor_1, competitor_2), ncol = 6, byrow = TRUE)
profile <- as.data.frame(profile)
profile$Cost <- 0
rownames(profile) <- c("our_design", "competitor_1", "competitor_2")
colnames(profile) <- c("(Intercept)",
                       "`Screen 52 inch`",
                       "`Screen 65 inch`",
                       "`2D or 3D`",
                       "`Sony = 1`",
                       "`Price (low = 0; high =1)`",
                       "Cost")
for (row in 1:nrow(profile)) {
    profile$Cost[row] <- sum(component_cost * profile[row, -ncol(profile)])
}


# The final conjoint analysis
conjoint <-function(pref, design) {
    pref <- read_file(pref)
    design <- read_file(design)
    design_level <- colnames(design)
    pref_levels <- colnames(pref)
    lm_result <- lm_participant(pref)
    attributes_importance <- attribute_importance(lm_result)
    lm_result <- willingness_to_pay(price_range, lm_result)
    report <- lm_result[, -2:-4]
    colnames(report) <- c("Partworth", "Willingness to Pay")
    optimal <- optimization(profile, lm_result)
    print("Reporting Attribute Importantce:")
    print(attributes_importance)
    print("Partworth and WTP:")
    print(report)
    print("Optimal scenario:")
    print(optimal)
}


# calculate marketshare
optimization <- function(profile, lm_result) {
    price_profit <- as.data.frame(matrix(ncol = 2))
    trial_price <- seq(1000, 5000, 100)
    no_price <- length(trial_price)
    for (no_of_price in 1:no_price) {
        profile$"`Price (low = 0; high =1)`"[1] <- trial_price[no_of_price]
        for (row in 1:nrow(profile)) {
            utility <- sum(profile[row,1:5] * lm_result$Estimate[-nrow(lm_result)])
            utility <- utility + 
                lm_result$Estimate[nrow(lm_result)] * (profile[row, 6]-2000) / price_range
            profile$Utility[row] <- utility
            profile$Attractiveness[row] <- exp(utility)
            profile$Margin <- profile$"`Price (low = 0; high =1)`"[1] - profile$Cost[1]
        }
        total_attractiveness <- sum(profile$Attractiveness)
        profile$Market_share <- 100*profile$Attractiveness[1]/total_attractiveness
        profile$profit_per_tv <- profile$Market_share[1] * profile$Margin[1] / 100
        price_profit <- rbind(price_profit, cbind(profile$"`Price (low = 0; high =1)`"[1], profile$profit_per_tv[1]))
    }
    optimal_price <- price_profit$V1[price_profit$V2 == max(price_profit$V2, na.rm = TRUE)][2]
    maximum_profit <- max(price_profit$V2, na.rm = TRUE)
    profile$"`Price (low = 0; high =1)`"[1] <- optimal_price
    for (row in 1:nrow(profile)) {
        utility <- sum(profile[row,1:5] * lm_result$Estimate[-nrow(lm_result)])
        utility <- utility + 
            lm_result$Estimate[nrow(lm_result)] * (profile[row, 6]-2000) / price_range
        profile$Utility[row] <- utility
        profile$Attractiveness[row] <- exp(utility)
    }
    total_attractiveness <- sum(profile$Attractiveness)
    market_share <- 100*profile$Attractiveness[1]/total_attractiveness
    optimal <- data_frame(optimal_price, market_share, maximum_profit)
    return(optimal)
}


# alculate profit of a certain configuration.
profit <- function(design) {
    lm_result$Estimate
}


# calculate willingness to pay
willingness_to_pay <- function(price_range, lm_result) {
    WTP <- data.frame()
    price_per_utility <- price_range/abs(tail(lm_result$Estimate, 1))
    lm_result$WTP <- lm_result$Estimate * price_per_utility
    return(lm_result)
}


# calculate the range of the coefficient
coefficient_range <- function(data_frame) {
    range(0, data_frame)[2] - range(0, data_frame)[1]
}


# estimate attribute importance(%)
attribute_importance <- function(lm_result) {
    screen_size_range <- coefficient_range(lm_result[rownames(lm_result) %in% c("`Screen 65 inch`", "'Screen 65 inch'"), 1])
    dimension_range <- coefficient_range(lm_result[rownames(lm_result) %in% c("`2D or 3D`"), 1])
    brand_range <- coefficient_range(lm_result[rownames(lm_result) %in% c("`2D or 3D`"), 1])
    price_range <- coefficient_range(lm_result[rownames(lm_result) %in% c("`Price (low = 0; high =1)`"), 1])
    total_range <- sum(screen_size_range, dimension_range, brand_range, price_range)
    screen_size_importance <- screen_size_range/total_range
    dimension_importance <- dimension_range/total_range
    brand_importance <- brand_range/total_range
    price_importance <- price_range/total_range
    attributes_importance <- c("screen_size" = screen_size_importance, "dimension" = dimension_importance,
                                  "brand" = brand_importance, "price" = price_importance)
    return(attributes_importance)
}


# regress each partifipant
lm_participant <- function(pref) {
    excluded_variables <- c("Your Name ", "Profile Nos", "Profiles", "Preference Ranks")
    lm_result <- data.frame()
    lm_result <- lm(pref$'Preference Ranks' ~ ., data=pref[, !(names(pref) %in% excluded_variables)])
    lm_result <- summary(lm_result)$coefficients
    lm_result <- as.data.frame(lm_result)
    return(lm_result)
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
    return(file)
}


# calls the function
conjoint(pref="Preferences BAX 2020 - Preferences.csv", design="Design Matrix.xlsx")
