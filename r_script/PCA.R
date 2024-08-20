#Loading the usefull libraries

suppressPackageStartupMessages(library(factoextra))
library(FactoMineR)

#In lines arguments for runing the script in python ; command line arguments

args <- commandArgs(trailingOnly = TRUE)
Working_directory = args[1] ; categorical_variables = as.numeric(args[2]) ; k = as.numeric(args[3]) ;  filename = args[4]




#test ouverture et lecture du fichier
#categorical_variables = 4
#k = 2
#Working_directory =  "C:/Users/Rose Tchala Sare/static/uploads"


setwd(Working_directory)
df = read.csv("data.csv", sep = ";")

print(nrow(df))

#rearanging the dataframe

rownames(df) = df[,1]
df[,1] = NULL

#Scaling and centering the data
X = scale(df[,categorical_variables:ncol(df)], scale = T, center = T)

#Performing the PCA
APC = PCA(X, scale.unit = F, graph = F)

#setting a title 
titre = colnames(df)[k]

#Saving and plotting the PCA

output_filename=file.path(filename,"PCA")
#pdf(file = filename)
png(file = filename)

fviz_pca_ind(APC,label = F, col.ind = as.factor(df[,k]), title = titre)


dev.off()


