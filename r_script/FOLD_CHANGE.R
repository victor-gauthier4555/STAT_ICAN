#install.packages("gtools")
suppressPackageStartupMessages(library(gtools))
suppressPackageStartupMessages(library(ggplot2))
suppressPackageStartupMessages(library(forcats))
#install.packages("reshape")


#In lines arguments for runing the script in python ; command line arguments

args <- commandArgs(trailingOnly = TRUE)
Working_directory = args[1] ; categorical_variables = as.numeric(args[2]) ; k = as.numeric(args[3]) ;  filename = args[4] ; filenamecsv = args[5] ; filenamevolcano = args[6]


#Working_directory =  "C:/Users/Rose Tchala Sare/Documents/application"
#categorical_variables = 4
#k = 3

#ouverture et lecture du fichier
setwd(Working_directory)
df = read.csv("data.csv", sep = ";", encoding = "UTF-8")
#df = read.csv(file = "exemple_ligne_2.csv", sep = ";")


#on effectue l'analyse pour chaque metabolite

p_value = NULL
t_statistic = NULL
fold_change = NULL

valeurs = unique(df[,k])


index_1 = which(df[,k] == valeurs[1])
index_2 = which(df[,k] == valeurs[2])

n = categorical_variables + 1

for(i in n:ncol(df)){
  a = t.test(df[index_1,i], df[index_2,i])
  p_value = c(p_value, a$p.value)
  t_statistic = c(t_statistic, a$statistic)
  fold_change = c(fold_change,log2( mean(df[index_1,i])/ mean(df[index_2,i])) )
}

#Saving the dataframe

metabolites = colnames(df)[n:ncol(df)]

df1 = data.frame("Metabolites" = metabolites,
                 "T.Statistic" = t_statistic,
                 "P.Value" = p_value,
                 "Log2.Fold.Change" = fold_change
)


write.table(df1, file = filenamecsv, sep = ";", row.names = F, fileEncoding = "UTF-8")

#performing the fold change plot

index_significant = which(p_value < 0.05)

#pdf(file = filename)
png(file = filename)

#setting a title 
titre = colnames(df)[k]


plot(fold_change, ylab = "Log2 Fold change", main = titre)  # type = "o" connects points with lines


if( length(index_significant) > 0 ){
  for(i in 1:length(index_significant)){
    if( fold_change[index_significant[i]] < 0){
      points(index_significant[i], fold_change[index_significant[i]], col = 'blue', pch = 19)
    }
    else{
      points(index_significant[i],fold_change[index_significant[i]], col = 'red', pch = 19)
    }
  }
}

grid()
#saving the plot

dev.off()

df1$log2FoldChange = fold_change

#Add a column for different expressed genes
df1$Expression <- "NO"


df1$Expression[which( df1$log2FoldChange > 0 &df1$P.Value < 0.05) ] <- "UP"
df1$Expression[which(df1$log2FoldChange < 0 & df1$P.Value < 0.05)] <- "DOWN"



df1$nom = NA

df1$nom[df1$Expression != "NO"] <- df1$Metabolites[df1$Expression != "NO"]


e = ggplot(data=df1, aes(x=log2FoldChange, y=-log10(P.Value),label = nom, col = Expression)) + 
  geom_point() + 
  theme_minimal() +
  geom_text() +
  ggtitle(titre)

if(length( unique(df1$Expression) ) == 1 ){
  if(unique(df1$Expression) == "NO"){
    e = e + scale_color_manual(values=c("black"))
  }
}else {
  e = e + scale_color_manual(values=c("blue", "black", "red"))
}



#pdf(file = filenamevolcano)
png(file = filenamevolcano)
e

dev.off()

