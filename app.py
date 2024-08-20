print("début")

import shap
from flask import Flask, render_template, request, send_file, redirect, url_for, make_response, Markup, session
from flask import g, session
from flask import jsonify
import matplotlib.pyplot as plt
import os
import pandas as pd
from sklearn.metrics import accuracy_score, auc, roc_curve
from sklearn.model_selection import GridSearchCV, train_test_split
from werkzeug.utils import secure_filename
import analysis
import shutil
import display_results
import analysis_multivariate
import io
import zlib
import base64
from config import UPLOAD_FOLDER
from xgboost import XGBClassifier
import seaborn as sns
from XGBOOST import preprocess_dataframe, prepare_XY, prepare_XY2
import numpy as np
# Charger et prétraiter les données


# Compressing and decompressing methods
def compress_data(data):
    compressed_data = zlib.compress(data.encode('utf-8'))
    return base64.b64encode(compressed_data).decode('utf-8')


def decompress_data(data):
    compressed_data = base64.b64decode(data.encode('utf-8'))
    return zlib.decompress(compressed_data).decode('utf-8')


# create an instance of flask
app = Flask(__name__, static_folder='static')
app.secret_key = 'RoseIsTheQueen'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


@app.route('/')
def welcome():
    print("Arrivée sur la page d'acceuil")
    return render_template("home.html")




@app.route('/choose.html')
def choose():
    return render_template("choose.html")


@app.route('/site.html')
def site():
    return render_template("site.html")

@app.route('/site3.html')
def site3():
    return render_template("site3.html")



@app.route('/predict', methods=['POST'])
def predict():
    erreur = None

    # Display the loader as soon as the analysis function starts
    loader_response = make_response(render_template("loader.html"))
    loader_response.headers['Content-Type'] = 'text/html'  # Ensure proper content type

    if request.method == 'POST':

        if 'file' not in request.files:
            print('No file part')
            return render_template("site.html")

        file = request.files['file']

        name = request.form.get("name")
        format = request.form.get("format")

        nom_fichier = (file.filename)

        if nom_fichier == "":
            erreur = "Please enter a file"


        elif ".csv" not in nom_fichier:
            erreur = "You should import a CSV file"

        if name == "":
            if erreur == None:
                erreur = "Please enter your project's name"
            else:
                erreur = f'{erreur} and enter a name'

        if format == "":

            if erreur == None:
                erreur = "Please choose a format"
            else:
                erreur = f'{erreur} and choose a format before submitting'
        else:
            if format == "Samples in row":
                sens = "Row"
            else:
                sens = "Column"

        if erreur == None:

            # Configure the secret key
            app.secret_key = 'RoseIsTheQueen'

            # Configure the upload folder for when we get the server, in the waiting time we r using the local storage



            # Creation du message à affichier pour l'analyse...
            process = f'The analysis for {name} is starting now...'

            # Saving the file
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'data.csv'))

            # making sure the file is read like a table
            data = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], 'data.csv'), sep=";", encoding='utf-8')

            data = analysis.pre_process(sens, data)

            print("Nous allons vous rediriger vers la page d'analyse")

            g.name = name
            g.data = data

            return render_template("site2.html", message_erreur=erreur, processing_sentence=process)

        else:

            return render_template("site.html", message_erreur=erreur)


@app.after_request
def call_site2(response):
    if request.path == '/predict':
        print("Début de l'analyse")

        if hasattr(g, 'name') and hasattr(g, 'data'):
            # Accessing the 'name' and 'data' variables stored in the 'g' object
            name = g.name
            data = g.data

            site2(name, data)

            message = f"The analysis for {name} is done !"

            return make_response(render_template("site3.html",
                                                 processing_sentence=message))  # Use make_response to create a proper response object

        # Add your function call or logic here
    return response


def site2(name, data):  # Perform the PCA
    print("Bienvenue sur la page de chargement qui débute avec l'analyse !")
    index_categorical = analysis.categories(data)

    a = analysis.general_folder(name, index_categorical, data)

    # Saving this path to the general space
    session['a'] = a
    analysis.APC(app.config['UPLOAD_FOLDER'], a)

    index_metabo = analysis.feature_indexes(data, index_categorical)

    # performing the boxplots
    # analysis.boxplots(a,data,index_metabo,index_categorical)

    # testing the binary function
    session['binary_variables'] = analysis.who_is_binary(data, index_categorical)

    # performing the foldchange analysis for the binary variables
    analysis.fold_change_graph(data, app.config['UPLOAD_FOLDER'], index_categorical, a)

    # performing the heatmap
    analysis.heatmap(app.config['UPLOAD_FOLDER'], a)

    # time.sleep(5)

    # RETRIEVING SIGNIFICANT DATA

    df = analysis.who_is_significant(UPLOAD_FOLDER, a, data,
                                     index_categorical, index_metabo)

    if df is not None:

        analysis.i_am_significant(df)

    else:

        print('There is no significant metabolites for this dataset')


    # generating significance table


@app.route('/display', methods=['POST'])
def display():
    # retrieving the number of categorical variables

    n_categories = session.get('a')
    n_binary = session.get('binary_variables')

    if len(n_binary) == 0:
        return render_template("site4_1.html")
    else:
        return render_template("site4_2.html")


@app.route('/test', methods=['POST'])
def test():
    return render_template("home.html")


@app.route('/foldchange', methods=['POST'])
def foldchange():
    analysis_path = session.get('a')
    display_results.write_foldchange(analysis_path)
    return render_template("result.html")


@app.route('/volcanoplot', methods=['POST'])
def volcanoplot():
    analysis_path = session.get('a')

    display_results.write_volcano(analysis_path)
    return render_template("result.html")


@app.route('/PCA', methods=['POST'])
def PCA():
    analysis_path = session.get('a')

    display_results.write_PCA(analysis_path)
    return render_template("result.html")



@app.route('/HEATMAP', methods=['POST'])
def HEATMAP():
    analysis_path = session.get('a')

    display_results.write_HEATMAP(analysis_path)
    return render_template("result.html")


@app.route('/pathways', methods=['POST'])

def pathways() :

    print("Welcome to the pathway and enrichment analysis ")

    analysis.enrichment_plots()

    return render_template("pathway.html")


# FOR THE MULTIVARIATE ANALYSIS

@app.route('/site_MV.html')
def MV():
    return render_template("site_MV.html")


@app.route('/predictMV', methods=['POST'])
def predictMV():
    erreur = None

    # Display the loader as soon as the analysis function starts
    loader_response = make_response(render_template("loader.html"))
    loader_response.headers['Content-Type'] = 'text/html'  # Ensure proper content type

    if request.method == 'POST':

        if 'file' not in request.files:
            print('No file part')
            return render_template("site.html")

        file = request.files['file']

        name = request.form.get("name")
        outcome_variable = request.form.get("variableid")
        format = request.form.get("format")

        nom_fichier = (file.filename)

        if nom_fichier == "":
            erreur = "Please enter a file"


        elif ".csv" not in nom_fichier:
            erreur = "You should import a CSV file"

        if name == "":
            if erreur == None:
                erreur = "Please enter your project's name"
            else:
                erreur = f'{erreur} and enter a name'

        if format == "":

            if erreur == None:
                erreur = "Please choose a format"
            else:
                erreur = f'{erreur} and choose a format before submitting'
        else:
            if format == "Samples in row":
                sens = "Row"
            else:
                sens = "Column"

        if outcome_variable == "":
            erreur = "Please enter the label of the outcome variable"

        if erreur == None:

            # Configure the secret key
            app.secret_key = 'RoseIsTheQueen'

            # Creation du message à affichier pour l'analyse...
            process = f'The analysis for {name} is starting now...'

            # saving thru the session
            stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
            data = pd.read_csv(stream, sep=";", encoding='utf-8')

            # Saving the label of the outcome variable
            session['ov'] = outcome_variable

            compressed_data = compress_data(data.to_json())

            # session["Data"] = compressed_data
            # print("Data saved to session:", session['Data'])

            # making sure the file is read like a table

            # checking if the variable outcome has been entered correctly

            if outcome_variable not in data.columns:
                erreur = "The variable was not found in your data. Please enter the correct variable label."
                return render_template("site_MV.html", message_erreur=erreur)

            data = analysis.pre_process(sens, data)

            print("Nous allons vous rediriger vers la page d'analyse")

            g.name = name
            g.data = data
            g.variable_outcome = outcome_variable

            return redirect(url_for('predict_multi'))

        else:
            return render_template("site_MV.html", message_erreur=erreur)
    return redirect(url_for('predict_multi'))


@app.after_request
def call_multivariate_analysis(response):
    if request.path == '/predictMV':
        print("Début de l'analyse multivariée")

        if hasattr(g, 'name') and hasattr(g, 'data'):
            # Accessing the 'name' and 'data' variables stored in the 'g' object
            name = g.name
            data = g.data
            outcome_variable = g.variable_outcome

            multivariate_analysis(name, data, outcome_variable)

            message = f"The analysis for {name} is done !"

            return make_response(render_template("table.html",
                                                 processing_sentence=message))  # Use make_response to create a proper response object

        # Add your function call or logic here
    return response


def multivariate_analysis(name, data, outcome_variable):  # Perform the PCA
    print("Bienvenue sur la fonction d'analyse multivariée")

    # retrieving index of the variables we will study
    L = analysis_multivariate.test_all_variables(data, outcome_variable)

    # writing the table template

    M = analysis_multivariate.categorical_factor(data, outcome_variable)
    g.mmm = M
    analysis_multivariate.write_template(L, M)


@app.route('/predict_multi', methods=['POST', 'GET'])
def predict_multi():
    if request.method == 'POST':
        text = request.form.get('comments')
        file = request.files.get('file')
        nom_fichier = file.filename if file else ""

        if not text and not nom_fichier:
            print("No information was entered")
            return render_template("error.html", processing_sentence="No information was entered")
        else:
            if nom_fichier:
                if ".csv" in nom_fichier:
                    stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
                    query = pd.read_csv(stream, header=None, sep=";")
                    if len(query.columns) != 1:
                        print("Please enter the variables names in columns")
                        return render_template("error.html",
                                               processing_sentence="Please enter the variables names in ONE column")
                    else:
                        query = list(query.iloc[:, 0])
            else:
                print("We are processing the text input")
                query = text.split(",")
                print("query = ")
                print(query)
            # print(query)

            reference_list = []
            for vquery in query:
                reference = request.form.get(vquery)
                if reference:
                    reference_list.append((vquery, reference))

            file_content = request.form.get('fileContent')
            if file_content:
                try:
                    data = base64.b64decode(file_content.split(',')[1])
                    print("The data has been retrieved and decoded successfully!")
                    decoded_str = data.decode('utf-8')
                    stream = io.StringIO(decoded_str)
                    data = pd.read_csv(stream, sep=';')

                    print(query)
                    print(data.columns)

                    a = analysis_multivariate.check_query(query, data)


                except Exception as e:
                    print(f"Error decoding file content: {e}")

            else:
                data = pd.read_csv(stream, sep=';')
                query = text.split(",")
                a = analysis_multivariate.check_query(query, data)

            if a is not None:
                return (render_template("error.html",
                                        processing_sentence=f"The following variable(s) are not present in the dataset {a}"))

            else:
                outcome_variable = session.get('ov')
                print(outcome_variable)

            # PERFORM MULTIVARIATE ANALYSIS WITH THE OUTCOME VARIABLE AS THE DEPENDENT VARIABLE




                df = preprocess_dataframe(data)

                X, y = prepare_XY2(outcome_variable, df,query)
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=5)

                param_grid = {
                    'n_estimators': [100, 200, 300],
                    'max_depth': [3, 4, 5],
                    'learning_rate': [0.01, 0.1, 0.2],
                    'subsample': [0.8, 0.9, 1.0],
                    'colsample_bytree': [0.8, 0.9, 1.0]
                }

                grid_search = GridSearchCV(estimator=XGBClassifier(), param_grid=param_grid,
                                           scoring='accuracy', cv=5, verbose=1, n_jobs=-1)
                grid_search.fit(X, y)

                best_params = grid_search.best_params_
                best_model = XGBClassifier(**best_params)
                best_model.fit(X_train, y_train)

                importances = best_model.feature_importances_
                indices = np.argsort(importances)[::-1]
                selected_features = X_train.columns[indices]

                plt.figure(figsize=(17, 6))
                plt.title("Importances des caractéristiques")
                plt.barh(range(len(selected_features)), importances[indices], align="center")
                plt.yticks(range(len(selected_features)), selected_features)
                plt.gca().invert_yaxis()
                plt.xlabel('Importance')
                plt.ylabel('Caractéristique')
                img4 = io.BytesIO()
                plt.savefig(img4, format='png', dpi=300)
                img4.seek(0)
                plot_url4 = base64.b64encode(img4.getvalue()).decode()
                plt.close()

                y_pred = best_model.predict(X_test)
                y_pred_proba = best_model.predict_proba(X_test)[:, 1]
                fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
                roc_auc = auc(fpr, tpr)

                # Calculer l'accuracy
                accuracy = accuracy_score(y_test, y_pred)
                print(f"Accuracy: {accuracy}")

                plt.figure(figsize=(10, 6))
                plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (AUC = {roc_auc:.2f})')
                plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
                plt.xlim([0.0, 1.0])
                plt.ylim([0.0, 1.05])
                plt.xlabel('False Positive Rate')
                plt.ylabel('True Positive Rate')
                plt.title('Receiver Operating Characteristic')
                plt.legend(loc="lower right")
                img1 = io.BytesIO()
                plt.savefig(img1, format='png', dpi=300)
                img1.seek(0)
                plot_url1 = base64.b64encode(img1.getvalue()).decode()
                plt.close()

                correlations = X_train.corr()
                plt.figure(figsize=(13, 11))
                sns.heatmap(correlations, vmax=1.0, center=0, fmt='.2f', cmap="YlGnBu",
                            square=True, linewidths=.5, annot=True, cbar_kws={"shrink": .70})
                plt.title('Correlation Heatmap', fontsize=16)
                img2 = io.BytesIO()
                plt.savefig(img2, format='png', dpi=300)
                img2.seek(0)
                plot_url2 = base64.b64encode(img2.getvalue()).decode()
                plt.close()

                explainer = shap.TreeExplainer(best_model)
                shap_values = explainer.shap_values(X_train)

                # Résumé des valeurs SHAP
                shap.summary_plot(shap_values, X_train, show=False)
                img3 = io.BytesIO()
                plt.savefig(img3, format='png', dpi=300)
                img3.seek(0)
                plot_url3 = base64.b64encode(img3.getvalue()).decode()

                return render_template('plot_XG.html', plot_url1=plot_url1, plot_url2=plot_url2, plot_url3=plot_url3,
                                       plot_url4=plot_url4)

    return render_template("table.html")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
