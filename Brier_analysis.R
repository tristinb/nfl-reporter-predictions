
#set wd
data <- read.csv('pundit_data.csv', header=TRUE)

# Remove intercept; just want averages

mod <- lm(squared_error~ -1+team, data= data)

results <- coef(summary(mod))[c(1:32),] # 32 teams
names <- row.names((coef(summary(mod)))) # Get names
row.names(results) <- substring(names[1:32], 5) # Remove first 4 chars
results <- results[,1] # Only care about coefs

# Order results from lowest to highest
results <- results[order(results)]
pdf('Brier.pdf') # Save image
barplot(results,las=2, ylab='Brier Score', main='Brier Score for Each Team Reporter \n (Lower Scores Indicate Better Predictions)')
dev.off()

# More complex model (control for wins, week)
mod_comp <- lm(squared_error~ -1+team+tot_wins+as.factor(week), data= data)
# Check residuals for normality
mod_stnd <- rstandard(mod_comp)
hist(mod_stnd)
qqnorm(mod_stnd)
qqline(mod_stnd)

results_comp <- coef(summary(mod_comp))[1:32,]
names_comp <- row.names((coef(summary(mod_comp))))
row.names(results_comp) <- substring(names_comp[1:32], 5)
results_comp <- results_comp[,1]
results_comp <- results_comp[order(results_comp)]

pdf('adjusted_Brier.pdf')
barplot(results_comp,las=2, ylab='Adjusted Brier Score', main='Adjusted Brier Score for Each Team Reporter')
dev.off()

anova(mod,mod_comp,test='F')

# Put table together

data2 <- read.csv('pundit_standings.csv',header=T)
data2 <- data2[order(data2$pundit_team),] # Alphabetical order by team

# Get results of comp in alphabetical order
mod_comp <- lm(squared_error~ -1+team+tot_wins+as.factor(week), data= data)
results_comp <- coef(summary(mod_comp))[1:32,]
names_comp <- row.names((coef(summary(mod_comp))))
row.names(results_comp) <- substring(names_comp[1:32], 5)
results_comp <- results_comp[,1]

data2 <- cbind(data2,results_comp) # Now combine (both in alph order)
data2 <- data2[order(data2$results_comp),] # Order by adj_brier score
data2$standing_adj <- c(1:32) #ranking 1 through 32
data_sub <- data2[,c(11,2,1,3,5,10)] # Reorder
colnames(data_sub) <- c('Standing','Team','Reporter','Average Spread','Brier Score','Adjusted Brier Score')

library(xtable)
print(xtable(data_sub,digits=3),include.rownames=FALSE)
