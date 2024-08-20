import analysis
import pandas as pd
import scipy.stats as stats
import warnings
from scipy.stats import normaltest


# On prend l'index de toutes les variables qui ne correspondent pas à notre variable d'interêt
def index_variables(data, outcome_variable):
    n = []
    for i in range(0, len(data.columns)):
        if data.columns[i] != outcome_variable and data.columns[i] != "Sample.ID":
            n.append(i)
    return (n)


# On va tester chaque variable et noter son nom et sa p value
def test_all_variables(data, outcome_variable):
    indexes = index_variables(data, outcome_variable)

    # List that will contain the informations for the table
    L = []

    # dictionary of the index of each individual along factor inside the independant variable
    groups = data.groupby(data[outcome_variable]).groups
    for index in indexes:
        # type of the variable, categorical or continuous
        a = (data.iloc[:, index]).dtype

        # check if the variable is continous
        if a == 'float64':
            n = 0

            for key in groups:
                d = data.loc[groups[key], data.columns[index]]
                # check if the distribution is normal of not for each sample
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    p = normaltest(d)
                    if p[1] > 0.05:
                        n = n + 1

            # if the distribution is normal
            if n == 0:
                resultat = stats.ttest_ind(data.loc[groups[list(groups.keys())[0]], data.columns[index]],
                                           data.loc[groups[list(groups.keys())[1]], data.columns[index]])
                L.append((data.columns[index], resultat.pvalue))
            else:
                resultat = stats.mannwhitneyu(data.loc[groups[list(groups.keys())[0]], data.columns[index]],
                                              data.loc[groups[list(groups.keys())[1]], data.columns[index]],
                                              alternative='two-sided')
                L.append((data.columns[index], resultat.pvalue))

        # if the data is categorical
        else:
            contingency_table = pd.crosstab(data.iloc[:, index], data[outcome_variable])
            chi2, p, dof, ex = stats.chi2_contingency(contingency_table)
            L.append((data.columns[index], p))

    print(f'Statistic test have been done for all the {len(indexes)} variables !')
    return L



# retrieve categpocorical data and their value for reference
def categorical_factor(data, outcome_variable):
    indexes = index_variables(data, outcome_variable)
    L = []
    for index in indexes:
        if (data.iloc[:, index]).dtype != 'float64':
            M = [data.columns[index]]
            M.extend(data.iloc[:, index].unique())
            L.append(M)
    return (L)


def write_template(liste, categorical_list):
    with open('./templates/table.html', 'w', encoding='utf-8') as file:
        file.write("""<!doctype html>
<html lang="fr">
	<head>
		<meta charset="utf-8">
		<title>STATICAN</title> 
        <link rel="stylesheet" type="text/css" href="{{ url_for('static', filename='css/table.css') }}">
		<link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Audiowide">
        <script defer src="{{ url_for('static', filename='js/app2.js') }}"></script>

	</head>

	<body>
        <div id="loading-spinner" class="loader"></div>
        <section>
            <div class = "entete">
                <span class = "txt">STATICAN</span> 
        		<span class = "gradient"></span>
        		<span class = "dodge"></span>
            </div>
            <div class = "colonne">
                <table>
                  <thead>
                    <tr>
                      <th scope="col">Variable name </th>
                      <th scope="col">P-Value</th>
                    </tr>
                  </thead>
                  <tbody class = "table_body">
                      """)
        for information in liste:

            if information[1] < 0.05:
                file.write(f"""<tr class = "significant">
                              <th>{information[0]}</th>
                              <td>{round(information[1], 3)}</td>
                          </tr>
                          """)

            else:
                file.write(f"""<tr>
                                  <th>{information[0]}</th>
                                  <td>{round(information[1], 3)}</td>
                              </tr>
                              """)
        file.write(f"""             
                   </table>
    <div style="display: flex; flex-direction: column; justify-content : space-evenly; align-items : center ; ">
        <div class = "rectangle" >
            <div class = "choix">

                <h3 style =  "color: gainsboro"> Import a list of  <span style="text-decoration: underline;"> maximum {int(len(liste) / 5)} variables </span> (more will induce overfitting) </h3>

                <form action="{{{{ url_for('predict_multi') }}}}" class = "formulaire" method="POST" enctype="multipart/form-data" id = "processForm">
                <div class="addfile">
                    <label for="comments" style = "color : lightgray">Variables chosen (coma separated):</label>
                    <textarea id="comments" name="comments" rows="4" cols="50"></textarea>
                </div>

                <h3 id = "boxappear" href ="#" class = "lien">Select reference for categorical variables</h3>

            </div>
            <div style = "display : flex ; align-items : center; text-align : center ; ">

            <div class="adfile">
                <label for="fileInput" class="fileLabel">             
                    <a class="fileText">Or add a CSV file</a>          
                    <input type="file" id="fileInput" name ="file">
                </label>
            </div>

            </div>

        </div>
        <div class = "hidden", id = "messageBox">
             """)

        for variable in categorical_list:
            file.write(f""" <label for="variable">{variable[0]} : </label>
                            <select name={variable[0]}>
""")
            for j in range(1, len(variable)):
                file.write(f""" <option value="{variable[j]}">{variable[j]}</option>""")
            file.write("</select><br>")

        file.write(f"""<a id = "boxgone" class = "button19">OK</a>
                   </div>
                   <input type='submit' value="submit" class = "button21" id = "submit"/>
        </form>
    </div>
            </section>


        </body>
    </html>""")


def check_query(query, data):
    L = []
    for vquery in query:
        a = 0
        for column in data.columns:
            if vquery.strip().lower() == column.lower():
                a += 1
        if a == 0:
            L.append(vquery)
    if len(L) != 0:
        return (L)
    else:
        return (None)

