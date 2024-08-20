
args <- commandArgs(trailingOnly = TRUE)
Working_directory = args[1] ; parametres = args[2] ;  #filename = args[3] ;
parametres <- eval(parse(text=parametres))


#test
#Working_directory =  "C:/Users/Rose Tchala Sare/Documents/application"
#setwd(Working_directory)
#df = read.csv("Exemple_ligne_2.csv", sep = ";")

#parametres = c("Mann-Whitney-gt","Mann-Whitney-gt","Mann-Whitney-gt","Mann-Whitney-gt")

#Working_directory =  "C:/Users/Rose Tchala Sare/static/uploads"
#setwd(Working_directory)
#df = read.csv("data.csv", sep = ";")



#ouverture et lecture du fichier
setwd(Working_directory)
df = read.csv("data.csv", sep = ";", encoding = "UTF-8")


rownames(df) = df[,1]
df[,1] = NULL

n = length(parametres)

#creating a vector with our data
vecteur = NULL
metabolites = NULL

for(i in 1:n){

  #setting the rowname for our table
  name = as.character(colnames(df)[i])
  colonnes = NULL
  valeurs = unique(df[,i])

  if(parametres[i] == "Mann-Whitney-gt"){
    if( length(valeurs) == 2 ){

      #We check the indexes of the binary variable


      index_1 = which(df[,i] == valeurs[1])
      index_2 = which(df[,i] == valeurs[2])

      for(j in (n+1):ncol(df)){
        a = t.test(df[index_1,j], df[index_2,j])
        #a = wilcox.test(df[index_1,j], df[index_2,j])

        if(a$p.value < 0.05 ){

          colonnes = c(colonnes, colnames(df)[j])



        }

      }

    }
    else if(length(valeurs) > 2){
      for(j in  (n+1):ncol(df)){
        a  = kruskal.test( x = df[,j], g = as.factor(df[,i]))

        if(a$p.value < 0.05 ){
          colonnes = c(colonnes, colnames(df)[j])
        }
      }


    }

  }
  else{
    if( length(valeurs) == 2 ){

      #We check the indexes of the binary variable


      index_1 = which(df[,i] == valeurs[1])
      index_2 = which(df[,i] == valeurs[2])

      for(j in (n+1):ncol(df)){
        a = t.test(df[index_1,j], df[index_2,j])
        #a = wilcox.test(df[index_1,j], df[index_2,j])

        if(a$p.value < 0.05 ){

          colonnes = c(colonnes, colnames(df)[j])



        }

      }

    }
    else if(length(valeurs) > 2){
      for(j in  (n+1):ncol(df)){

        colonne = as.character(colnames(df)[j])
        a  = summary(aov(df[,j] ~ as.factor(df[,i]) ))


        if ( a[[1]][["Pr(>F)"]][1] < 0.05 ){
          colonnes = c(colonnes, colnames(df)[j])
        }
      }


    }

  }

  #Filling the vector in question
  metabolites = c(metabolites, colonnes)
  vecteur = c(vecteur, length(colonnes))

}

#Now we are starting the redaction of our final dataframe
m = max(vecteur)
df1 = matrix(data = c(rep("NA", m * n)), nrow = m)

#We'll fill the NA values with the metabolites
for(i in 1:n){
  k = (vecteur[i])

  if(k > 0){
  df1[1:k,i] = metabolites[1:k]
  metabolites = metabolites[-c(1:k)]
  }
}

if(ncol(df1) > 0){
  #lets add our column  names
  colnames(df1) = colnames(df)[1:n]

  #write.table(df1, file = filename, sep = ";", row.names = F, fileEncoding = "UTF-8")
  df1}
