suppressPackageStartupMessages(library(reshape))
suppressPackageStartupMessages(library(ggplot2))



#In lines arguments for runing the script in python ; command line arguments

args <- commandArgs(trailingOnly = TRUE)
Working_directory = args[1] ; categorical_variables = as.numeric(args[2]) ; k = as.numeric(args[3]) ;  filename = args[4] ;


#Working_directory =  "C:/Users/Rose Tchala Sare/static/uploads"
#categorical_variables = 4
#k = 3

#ouverture et lecture du fichier
setwd(Working_directory)
df = read.csv("data.csv", sep = ";")

n = categorical_variables + 1


#on va faire le heatmap
k = k + 1

df2 = df[,n:ncol(df)]
df2 = cbind(df2, df[,k])
colnames(df2)[ncol(df2)] = colnames(df)[k]
rownames(df2) = df$Sample.ID


df3 <- melt(df2)
colnames(df3) <- c("x", "y", "value")


#setting a title 
titre = colnames(df)[k]

#pdf(file = filename)
png(file = filename)

ggplot(df3, aes(x = x, y = y, fill = value)) +
  geom_tile()  +
  scale_fill_gradient(low = "blue", high = "purple") + ggtitle(titre)


dev.off()
