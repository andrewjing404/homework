library(dplyr)
library(stringr)


#Question 1.a
stock <- read.csv("Question1.csv")

summary(lm(stock$WALMARTRET~stock$MKTRET))
summary(lm(stock$SABRERET~stock$MKTRET))
summary(lm(stock$DELLRET~stock$MKTRET))

#Question 1.c
(tDell <- (1.66791-1)/0.32605)
1 - pt(tDell, df=60-1)

#Question 1.d
tWalmart <- (0.73167-1)/0.19121
pt(tWalmart, df=60-1)


#Question 2
install.packages("benford.analysis")
library(benford.analysis)

invoice <- read.csv("Question2.csv")

(bfd <- benford(invoice$Amount, number.of.digit=1))

plot(bfd)


#Question5
library(car)
library(nortest)
justice <- read.csv("Question5.csv")

#Why exclude STATE from the model
nrow(justice)
length(levels(justice$STATE))

#Why apply log transformation
plot(justice$POLICE, justice$EXPEND)
plot(log(justice$POLICE), log(justice$EXPEND))

#Fitting the model
justiceModel <- lm(log(EXPEND) ~ log(POLICE), data = justice)
justiceResids <- residuals(justiceModel)

#Normality of the residuals
ad.test(justiceResids)
qqnorm(justiceResids)
hist(justiceResids)

#Homoscedasticity of variance
ncvTest(justiceModel)

#Model description
summary(justiceModel)

#Prediction
predict.lm(justiceModel, data.frame(POLICE = 10000), interval = "confidence")
exp(predict.lm(justiceModel, data.frame(POLICE = 10000), interval = "confidence"))


#Question 6.a
farming <- read.csv("Question6.csv")

plot(farming$Crew.Size, farming$Output, xlab="Crew Size", ylab="Output")

#Question 6.b
Output <- farming$Output
CrewSize <- farming$Crew.Size
CrewSizeSQ <- CrewSize^2

summary(lm(Output ~ CrewSize))
summary(lm(Output ~ CrewSize + CrewSizeSQ))

#Question 6.c
predict.lm(lm(Output ~ CrewSize + CrewSizeSQ), data.frame(CrewSize=5, CrewSizeSQ=25), interval = "confidence")

#Question 6.d
CrewSizeQB <- CrewSize^3
summary(lm(Output ~ CrewSize + CrewSizeSQ + CrewSizeQB))


#Question 7.a
joy <- read.csv("Question7.csv")

Happy <- joy$Happiness
Age <- joy$Age
FamInc <- joy$Family.Income
LnHappy <- log(Happy)
LnAge <- log(Age)
LnFamInc <- log(FamInc)

#Lin-lin model
linlin <- lm(Happy ~ Age + FamInc)
summary(linlin)
ad.test(residuals(linlin))
ncvTest(linlin)

#Lin-log model
linlog <- lm(Happy ~ LnAge + LnFamInc)
summary(linlog)
ad.test(residuals(linlog))
ncvTest(linlog)

#Log-lin model
loglin <- lm(LnHappy ~ Age + FamInc)
summary(loglin)
ad.test(residuals(loglin))
ncvTest(loglin)

#Log-log model
loglog <- lm(LnHappy ~ LnAge + LnFamInc)
summary(loglog)
ad.test(residuals(loglog))
ncvTest(loglog)

#Question 7.b
Ages <- seq(12, 80)
(linlogHappy <- predict.lm(linlog, data.frame(LnAge=log(Ages), LnFamInc=log(80000))))

names(linlogHappy) <- Ages
linlogHappy

plot(Ages, linlogHappy, xlab="Age", ylab="Happiness Rating", main="Lin-log Model")

#Question 7.3
FamIncs <- seq(10000, 250000, 1000)
(linlogHappy_2 <- predict.lm(linlog, data.frame(LnAge=log(60), LnFamInc=log(FamIncs))))

names(linlogHappy_2) <- FamIncs
linlogHappy_2

plot(FamIncs, linlogHappy_2, xlab="Family Income", ylab = "Happiness Rating", main="Lin-log Model")


#Question 8
traffic <- read.csv("Question8.csv")
Fix <- traffic$X8.00.Arr
Flex <- traffic$Flextime

#Histograms
hist(Fix)
hist(Flex)

#Normality
shapiro.test(Fix)

#Test
wilcox.test(Fix, Flex, paired = TRUE)


#Question 12.a
winter <- read.csv("Question12.csv")

#Preparation
ltModel <- lm(SALES ~ TIME, data = winter)
ltResids <- residuals(ltModel)
ltFits <- predict(ltModel)

#Model output
summary(ltModel)

#Residual plot
plot(ltResids, ltFits, xlab="Residual", ylab="Fits")

#Question 12.b
plot(winter$TIME, winter$SALES, xlab="Time", ylab="Sales")

#Question 12.c
Q <- factor(winter$QUARTER)
dummies <- model.matrix(~Q)
dummies <- dummies[,-1]
winter <- cbind(winter,dummies)

#Question 12.d
#create the full model
fltModel <- lm(SALES ~ TIME + Q2 + Q3 + Q4, data=winter)
summary(fltModel)

#Partial F-test
anova(ltModel, fltModel)


#Question 14.a
absn <- read.csv("Question14.csv")

ABSENT <- absn$ABSENT
COMPLX <- absn$COMPLX
SENINV <- 1/absn$SENIOR

FS1 <- ifelse(absn$SATIS == 1, 1, 0)
FS2 <- ifelse(absn$SATIS == 2, 1, 0)
FS3 <- ifelse(absn$SATIS == 3, 1, 0)
FS4 <- ifelse(absn$SATIS == 4, 1, 0)
FS5 <- ifelse(absn$SATIS == 5, 1, 0)

#Full model
fabsnModel <- lm(ABSENT ~ COMPLX + SENINV + FS2 + FS3 + FS4 + FS5)
summary(fabsnModel)

#Question 14.b
rabsnModel <- lm(ABSENT ~ COMPLX + SENINV)
summary(rabsnModel)

#QUestion 14.c
anova(rabsnModel, fabsnModel)

#Question 14.d
predict.lm(fabsnModel, data.frame(COMPLX=60, SENINV=1/30, FS2=0, FS3=0, FS4=0, FS5=0))

#Question 14.e
predict.lm(fabsnModel, data.frame(COMPLX=60, SENINV=1/30, FS2=0, FS3=0, FS4=0, FS5=1))

#Question 15.f
predict.lm(fabsnModel, data.frame(COMPLX=10, SENINV=1/3, FS2=0, FS3=0, FS4=0, FS5=0))

#Question 15.g
predict.lm(fabsnModel, data.frame(COMPLX=10, SENINV=1/3, FS2=0, FS3=0, FS4=0, FS5=1))


#Question 15.a
vs <- read.csv("Question15.csv")

salary <- vs$SALARY
educat <- vs$EDUCAT
exper <- vs$EXPER
months <- vs$MONTHS
male <- ifelse(vs$GENDER=="MALE", 1, 0)

#model
eduGenModel <- lm(salary ~ educat + male)
summary(eduGenModel)

#Question 15.b
library(dplyr)

vs %>%
    filter(GENDER == "MALE") -> maleVS

vs %>%
    filter(GENDER == "FEMALE") -> femaleVS

maleModel <- lm(SALARY ~ EDUCAT, data=maleVS)
femaleModel <- lm(SALARY ~ EDUCAT, data=femaleVS)

plot(maleVS$EDUCAT, predict(maleModel), col="Blue", xlab="EDUCAT", ylab="Predicted Salary", xlim=c(0,18), ylim=c(3500,6200))
abline(maleModel, col="Blue")
abline(femaleModel, col="Red")

#Question 15.c
intModel <- lm(salary ~ educat + male + educat:male)
summary(intModel)


#Question 16.b
exp(0.0302) - 1

exp(0.053) - 1

exp(0.0456) - 1

exp(0.0114) - 1


#Question 17
library(olsrr)
heat <- read.csv("Question17.csv")

#Preparation
COST <- heat$COST
TEMP <- heat$TEMP
INSUL <- heat$INSUL
AGE <- heat$AGE
GARAGE<- ifelse(heat$GARAGE=="Yes", 1, 0)

#Model selection
ols_step_both_p(lm(COST ~ TEMP+INSUL+AGE+GARAGE, data=heat), prem=0.1, pent=0.1)

#Regression diagnostics
heatModel <- lm(COST ~ TEMP+INSUL+GARAGE, data=heat)
heatResids <- residuals(heatModel)

#Normality
shapiro.test(heatResids)
hist(heatResids)

#Homoscedasticity
ncvTest(heatModel)