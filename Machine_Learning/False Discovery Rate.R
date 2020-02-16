### Homework Requirement

# [1] Explore the data and visualize: what variables are interesting? Choose a few, plot them together, and tell a story.
# [2] Describe the regression model in the code. Improve it?
# [3] How can a diff-in-diff improve the model?
# [4] Take the p-values from your regression and look for evidence of association. 
#     Relate what you learn to your story from [1]. How many true discoveries do you think we have?
# [5] Why should we be worried about our FDR control here?



#### Purchases of Ice Cream
ice <- read.csv("ice_cream.csv")

## explore
names(ice)

## create a new variable for price per unit
priceper1 <- (ice$price_paid_deal + ice$price_paid_non_deal) / ice$quantity
y <- log(1 + priceper1)

## collect some variables of interest
## create a data.frame
x <- ice[ ,c("flavor_descr", "size1_descr", "household_income", "household_size")]

## relevel 'flavor' to have baseline of vanilla
x$flavor_descr <- relevel(x$flavor_descr, "VAN")

## coupon usage
x$usecoup <- factor(ice$coupon_value > 0)
x$couponper1 <- ice$coupon_value / ice$quantity

## organize some demographics
x$region <- factor(ice$region, levels=1:4, labels=c("East","Central","South","West"))
x$married <- factor(ice$marital_status==1)
x$race <- factor(ice$race, levels=1:4, labels=c("white", "black", "asian", "other"))
x$hispanic_origin <- ice$hispanic_origin==1
x$microwave <- ice$kitchen_appliances %in% c(1,4,5,7)
x$dishwasher <- ice$kitchen_appliances %in% c(2,4,6,7)
x$sfh <- ice$type_of_residence == 1
x$internet <- ice$household_internet_connection == 1
x$tvcable <- ice$tv_items > 1

## combine x and y
## cbind is "column bind".  It takes two dataframes and makes one.
xy <- cbind(x,y)


## fit the regression
fit <- glm(y~., data=xy) 
summary(fit)

fit$coefficients[2][1]

## grab the non-intercept p-values from a glm
## -1 to drop the intercept, 4 is 4th column
pvals <- summary(fit)$coef[-1,4] 


## False Discovery Rate Function.
## Extract p-value cutoff for E[fdf] < q
fdr <- function(pvals, q, plotit=FALSE){
        pvals <- pvals[!is.na(pvals)]
        N <- length(pvals)
        
        k <- rank(pvals, ties.method="min")
        alpha <- max(pvals[ pvals <= (q*k/N) ])
        
        if(plotit){
                sig <- factor(pvals <= alpha)
                o <- order(pvals)
                plot(pvals[o], log="xy", col=c("grey60","red")[sig[o]], pch=20, 
                     ylab="p-values", xlab="tests ordered by p-value", main = paste('FDR =',q))
                lines(1:N, q*(1:N) / N)
        }
        
        return(alpha)
}


## calculate cut-off alpha
fdr_p <- fdr(pvals, 0.1)
alp <- ifelse(fdr_p < 0.05, yes = fdr_p, 0.05)

## print the complete result of the original model
summary(fit)

## partial F-test on flavor on the original model
varReduced <- xy[, -which(colnames(xy) %in% 'flavor_descr')]
fitReduced <- lm(y~., data = varReduced)
partialF_flavor <- anova(fit, fitReduced)

partialF_flavor$`Pr(>F)`


## perform stepwise selection to yield the improved model
library(olsrr)

## store the stepwise result
derp <- ols_step_both_aic(fullModel)

## run a regression using the optimized variables
olsVariables <- c(derp$predictors)
olsData <- xy_2[, olsVariables]
olsFit <- lm(y~., data = olsData)

## examine the performance of the improved model
summary(olsFit)
AIC(olsFit)


## examine the cut-off p-value of the improved model
olsPvals <- summary(olsFit)$coef[-1,4] 

fdr(olsPvals, 0.1)


## partial F-test on flavor on the improved model
varReduced <- olsData[, -which(colnames(olsData) %in% 'flavor_descr')]
fitReduced <- lm(y~., data = varReduced)
partialF_flavor <- anova(olsFit, fitReduced)

partialF_flavor$`Pr(>F)`


## partial F-test on children on the improved model
varReduced <- olsData[, -which(colnames(olsData) %in% 'age_and_presence_of_children')]
fitReduced <- lm(y~., data = varReduced)
partialF_flavor <- anova(olsFit, fitReduced)

partialF_flavor$`Pr(>F)`