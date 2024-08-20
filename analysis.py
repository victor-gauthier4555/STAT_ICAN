#importing the necesarry modules for the analysis...


import pandas as pd
import os
import shutil
import subprocess
import random as rd
from scipy.stats import normaltest
import warnings
from statistics import mean
import seaborn as sns
from statannotations.Annotator import Annotator
import matplotlib as plt
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import fisher_exact
from config import BASE_DIR

R_ROSE = r'C:\Users\Rose Tchala Sare\AppData\Local\Programs\R\R-4.3.2\bin\Rscript.exe'
R_VICTOR = '/usr/local/bin/Rscript'

R_PATH=R_ROSE

#Now we are going to open the data 

def pre_process(sens, data): #This function transpose the data if it is reversed
    if sens == "Column" :
        print("The data will be transposed")
        data_transposed = data.transpose()
        return(data_transposed)
    else:
        return(data)

def categories(data): #This function returns the index of categorical variables
    index = []
    i = 1
    a = None
    while a != 'float64'  and i < len(data.columns) :
        a = (data.iloc[:, i]).dtype

        if a == 'O' :
            #print("OK")

            index.append(i)
        i = i + 1
    return(index)


def feature_indexes(data, index): #return the column indexes of features without including catégorical variables 
    return([i for i in range(max(index) + 1 , len(data.columns))])

def general_folder(name, categories, data) : #create a folder for the analysis to be performed 
    #returns a list containing the paths for the folder (elemen 0) and all the categorical variables 

    # Absolute path to the directory
    wanted_path = os.path.join(BASE_DIR, f'analysis/{name}_analysis')
    # Relative path to the directory
    directory_path = f'analysis/{name}_analysis'
    
    L = [directory_path]

    # Check if the directory exists
    if os.path.exists(wanted_path):
        # If it exists, remove it and create a new one
        shutil.rmtree(wanted_path)
        os.makedirs(wanted_path)
        print(f'Folder for {name} succefully created ! ')

    else:
        # If it doesn't exist, simply create a new one
        os.makedirs(wanted_path)
        print(f'Folder for {name} succefully created ! ')
        fichier_general = f'analysis/{name}_analysis'

    for i in categories : 
        #print(data.columns[i])
        os.mkdir(os.path.join(wanted_path, data.columns[i]))
        print(f'Folder for the categorcal variable {data.columns[i]} created succefully ! ')

        L.append(f'analysis/{name}_analysis/{data.columns[i]}')
    
    print(L)
    return(L)

def APC(data_path, general_paths):
    print("Welcome to the PCA function")

    #R STUDIO PARAMETERS
    r_path = R_PATH #path where r studio is installed
    r_script_path = os.path.join(BASE_DIR, 'r_script/PCA.R') #path of the R script

    #Initiating the iteration over the gategorical variables

    for i in range(1,len(general_paths)):

        filename = os.path.join(BASE_DIR, general_paths[i], 'PCA.png')
        command = [r_path, r_script_path,data_path, str(len(general_paths)), str(i), filename]

        result = subprocess.run(command, check = True, capture_output=True, text=True) ;
        r_output = result.stdout
        print(f"PCA is done in  {filename}")


def random_indexes(feature_indexes):
    if len(feature_indexes) > 10 :
        return(rd.sample(feature_indexes, k = 10))
    else :
        n = int(feature_indexes * 0.1)
        return(rd.sample(feature_indexes, k = n))
    
def parameters(random_list, index_categorical,data):

    #This list will contain the parameters for the box plots
    M = []

    #We iterate over the number of categorical variables
    for index in index_categorical :

        #This list will contain the number of normal-distributed sample among the factor for each column
        L = []

        for indice in random_list :
            groups = data.groupby(data.columns[index]).groups
            n = 0            
        
            for key in groups :
                d = data.loc[groups[key], data.columns[indice]]  # This selects column 6 from the grouped data

                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    a = normaltest(d)
            
                    if a[1] < 0.05 :
                        n = n + 1

            L.append(n)

        if mean(L) > ( len(groups) / 2 ) :
            M.append("t-test_ind")
        else :
            M.append("Mann-Whitney-gt")

    print( f"These are the parameters we'll use for our boxplot according to the categorical variables {M}")
    return(M)

def boxplots(general_paths,data,feature_indexes,index_categorical):

    #Take radom column indices 
    n = random_indexes(feature_indexes)

    #Define the parametrical or not distribution for the columns
    parametres = parameters(n,index_categorical,data)

    debut = max(index_categorical) + 1

    for indexo in index_categorical :

        boxplot_path = os.path.join(BASE_DIR, general_paths[indexo], 'boxplot')

        print(f"We are starting the boxplots with {data.columns[indexo]}")


        if os.path.exists(boxplot_path):
            # If it exists, remove it and create a new one
            shutil.rmtree(boxplot_path)
            os.makedirs(boxplot_path)

        else:
            # If it doesn't exist, simply create a new one
            os.makedirs(boxplot_path)


        groups = data.groupby(data.columns[indexo]).groups
        liste = [key for key in groups]
        print(liste)


        M =[]
        k = len(liste)
        for element in liste :
            a = liste.index(element)
            for j in range(1,k):
                M.append((element, liste[a + j]))
            k -= 1
        
        print(M)
        pairs = M
        
        for col in data.loc[:, data.columns[debut]:].columns:
        
            states_palette = states_palette = sns.color_palette("YlGnBu", n_colors=5)

            #Setting parameters for Mann Whitney data
            hue_plot_params = {
            'data':      data,
            'x':         data.columns[indexo],
            'y':         col,
            "palette":   states_palette
            }
        
            #creating the plot
            ax = sns.boxplot(x= data.columns[indexo], y=col, data= data)
            ax.set_title(f"{col}")
            ax.set_ylabel('log(10) area')
        
        
            #create the mann whitney annotations
            annotator = Annotator(ax, pairs, **hue_plot_params)
            y = indexo - 1
            annotator.configure(test=parametres[y], show_test_name=False).apply_and_annotate()
        
        
            #saving the figure
            plt.savefig(os.path.join(boxplot_path, col + '.png'), dpi=2400)
            #plt.show()
            plt.close()  # Close the plot to release resources

        
        print(f"The boxplot for {data.columns[indexo]} are done")

def who_is_binary(data,index_categorical) : #We whant to know who is the binary variable is there is one

    #This list will contain the index of binary variables
    M = []

    #We iterate over the number of categorical variables
    for index in index_categorical :


        groups = data.groupby(data.columns[index]).groups
        
        if len(groups) == 2 :
            M.append(index)
            print(f'{data.columns[index]} is a binary variable')
    
    return(M)

def fold_change_graph(data, data_path, index_categorical, general_path):
    print("Welcome to the fold change function")

    r_path = R_PATH  # Relative path to Rscript
    r_script_path = os.path.join(BASE_DIR, 'r_script/FOLD_CHANGE.R')  # chemin du script R

    index_binary = who_is_binary(data, index_categorical)

    if len(index_binary) >= 0:
        for index_binaire in index_binary:
            filename = os.path.join(BASE_DIR, general_path[index_binaire], f'{data.columns[index_binaire]}_FC_plot.png')
            filenamecsv = os.path.join(BASE_DIR, general_path[index_binaire], f'{data.columns[index_binaire]}_table.csv')
            filenamevolcano = os.path.join(BASE_DIR, general_path[index_binaire], f'{data.columns[index_binaire]}_Volcano_plot.png')

            command = [r_path, r_script_path, data_path, str(len(general_path)), str(index_binaire + 1), filename, filenamecsv, filenamevolcano]

            try:
                result = subprocess.run(command, check=True, capture_output=True, text=True)
                print(f"Fold Change Analysis is done for {data.columns[index_binaire]}")
                print("stdout:", result.stdout)  # Affiche la sortie standard
                print("stderr:", result.stderr)  # Affiche les erreurs
            except subprocess.CalledProcessError as e:
                print(f"Error occurred: {e}")
                print("stdout:", e.stdout)  # Affiche la sortie standard en cas d'erreur
                print("stderr:", e.stderr)  # Affiche les erreurs en cas d'erreur



def heatmap(data_path, general_paths):
    print("We are generating the heatmaps now !")

    #R STUDIO PARAMETERS
    r_path = R_PATH #path where r studio is installed
    r_script_path = os.path.join(BASE_DIR, 'r_script/HEATMAP.R') #path of the R script

    #Initiating the iteration over the gategorical variables

    for i in range(1,len(general_paths)):

        filename = os.path.join(BASE_DIR, general_paths[i], 'HEATMAP.png')
        command = [r_path, r_script_path,data_path, str(len(general_paths)), str(i), filename]
        result = subprocess.run(command, check = True, capture_output=True, text=True) ; r_output = result.stdout
        print(f"Heatmap is done in  {filename}")


def conversion_output_r(r_output):
    ligne = r_output.strip().split("\n")
    L = []
    for element in ligne:
        element = element.strip('').split()
        M = [e.strip('"') for e in element]

        if "[" in element[0]:
            L.append(M[1::])
        else:
            L.append(M)

    df = pd.DataFrame(L[1::], columns=L[0])
    return (df)


def who_is_significant(data_path, general_paths, data, index_categorical, feature_indexes):
    print("Wanna know the significant metabolites ?")

    # Take radom column indices
    n = random_indexes(feature_indexes)

    # Define the parametrical or not distribution for the columns
    parametres = parameters(n, index_categorical, data)

    # We'll transform these parameters into a vector in r studio

    arg_r = f"c('{parametres[0]}'"
    for i in range(1, len(parametres)):
        arg_r = arg_r + f" ,'{parametres[i]}' "
    arg_r += ")"

    # R STUDIO PARAMETERS
    r_path = R_PATH  # path where r studio is installed
    r_script_path = os.path.join(BASE_DIR, 'r_script/SIGNIFICANTS.R')


    data_folder = "./static/data"
    if os.path.exists(data_folder):
        # If it exists, remove it and create a new one
        shutil.rmtree(data_folder)
        os.makedirs(data_folder)

    else:
        # If it doesn't exist, simply create a new one
        os.makedirs(data_folder)
    print("Dossier data bien crée dans la mémoire de l'application")

    filename = f"{data_folder}/SIGNIFICANTS.csv"

    command = [r_path, r_script_path, data_path, arg_r]
    result = subprocess.run(command, check=True, capture_output=True, text=True);
    r_output = result.stdout

    df = conversion_output_r(r_output)
    # saving the result as a data.frame
    print(f"The significants metabolites have been retrieved !")

    return (df)


def i_am_significant(data):
    data_folder = "./static/data"
    # data = pd.read_csv(f"{data_folder}/SIGNIFICANTS.csv", sep = ';',low_memory = False,encoding = 'utf-8' )

    # These are the query files
    FARID_data = pd.read_csv("./static/pathways/AnnotatedMetabolites.csv", sep=";", encoding='utf-8')
    KEGG_data = pd.read_csv("./static/pathways/MAIN Pathways_Homo sapiens_KEGG.csv", sep=";", encoding='utf-8')
    metabolome = pd.read_csv("./static/pathways/metabolome.csv", sep=";", encoding='utf-8', header=None)

    # Retrieving the metabolome list
    all = [met for met in metabolome.iloc[:, 0]]

    # total of our metabolites of our lab database
    N = len(all)
    N = 368

    # Iteration over the variables
    for k in range(0, len(data.columns)):
        filename = f"{data_folder}/{data.columns[k]}_SIGNIFICANTS.csv"

        # using the local storage
        # filename = "SIGNIFICANTS.csv"

        with open(filename, "w") as file:

            # This is the header of the csv file
            file.write("Pathway name;P-Value;Coverage;Retrieved Metabolites;Expected\n")
            L = []

            # First step : retrieve the KEGG ID of the query list of metabolites
            for metabolite in data.iloc[:, k]:
                for i in range(0, len(FARID_data.iloc[:, 0])):
                    if metabolite == FARID_data.iloc[i, 0] or metabolite == FARID_data.iloc[i, 1]:
                        L.append(FARID_data.iloc[i, 2])
            # print(L)

            # List of the non significant metabolites in our metabolome
            non_significant = []
            for i in range(0, len(all)):
                if all[i] not in L:
                    non_significant.append(all[i])

            # Now we do have the KEGG ID's. Let's retrieve the pathways !
            current_path = ""

            # Significant who are in the pathway
            M = []

            for j in range(0, len(KEGG_data["Pathways"])):
                if KEGG_data.iloc[j, 0] != current_path:

                    if len(M) > 1:
                        # Preparation de la table de contingence pour le fisher exact test

                        # x = count
                        m_x = count_0 - count
                        k_x = len(L) - count
                        N_m_k_x = N - count_0 - k_x

                        # contigency table
                        table = np.array([[count, m_x], [k_x, N_m_k_x]])
                        res = fisher_exact(table, alternative='greater')

                        # Décomposer le tuple retourné par fisher_exact
                        oddsratio, pvalue = res

                        ligne = f"{M[0].replace('- Homo sapiens (human)', '')};{pvalue};{count}//{count_0};{','.join(M[1:len(M)])};{round((len(L) / N) * count_0, 3)}\n"
                        file.write(ligne)

                    current_path = KEGG_data.iloc[j, 0]

                    count = 0
                    count_0 = 0
                    M = [current_path]
                    # print(current_path)
                    for element in L:
                        if KEGG_data.iloc[j, 2] == element:
                            M.append(KEGG_data.iloc[j, 2])
                            count += 1
                    for element in all:
                        if KEGG_data.iloc[j, 2] == element:
                            count_0 += 1

                else:
                    for element in L:
                        if KEGG_data.iloc[j, 2] == element:
                            M.append(KEGG_data.iloc[j, 1])
                            count += 1
                            # print(M)
                            # print(count)
                    for element in all:
                        if KEGG_data.iloc[j, 2] == element:
                            count_0 += 1
            print(f"Enrichment analysis done for {data.columns[k]}")

    # with open(filename,"rb") as f :
    #    file_content = f.read()
    #    encoded_file_content = base64.b64encode(file_content).decode('utf-8')
    #    return(encoded_file_content)


    # with open(filename,"rb") as f :
    #    file_content = f.read()
    #    encoded_file_content = base64.b64encode(file_content).decode('utf-8')
    #    return(encoded_file_content)


def enrichment_plots():
    r_path = R_PATH  # path where r studio is installed
    r_script_path = os.path.join(BASE_DIR, 'r_script/ENRICHMENT.R')  # path of the R script

    directory = f"./static/data"
    for file in os.listdir(directory):
        if "SIGNIFICANTS.csv" in file:
            # data = pd.read_csv(file, sep = ";", encoding='utf-8')

            # setting the filenames
            filename1 = f'{directory}/{file.replace("SIGNIFICANTS.csv", "")}barplot.png'
            filename2 = f'{directory}/{file.replace("SIGNIFICANTS.csv", "")}dotplot.png'

            command = [r_path, r_script_path, f"{directory}/{file}", filename1, filename2]
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True);
            r_output = result.stdout
            print(r_output)
        
      









  




