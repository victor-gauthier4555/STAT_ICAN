import os
import shutil
from config import BASE_DIR


def clear_old_images():
    static_imag = os.path.join(BASE_DIR, 'static/images')
    if os.path.exists(static_imag):
        shutil.rmtree(static_imag)
    os.makedirs(static_imag)

def copy_images(keyword, analysis_path):

    clear_old_images()

    #We will create space inside the app to copy the graphs we want inside it
    static_imag = os.path.join(BASE_DIR, 'static/images')
    if os.path.exists(static_imag):
            # If it exists, remove it and create a new one
            shutil.rmtree(static_imag)
            os.makedirs(static_imag)

    else:
            # If it doesn't exist, simply create a new one
            os.makedirs(static_imag)
    print("Dossier de graphs bien crée dans la mémoire de l'application")
    
    #We'll access inside each graphs and choose the ones containing our keywords
    #This is the  nuùber of images in the folder
    n = 0
    directory = os.path.join(BASE_DIR, analysis_path[0])
    for folder in os.listdir(directory) :
            if ".csv" not in folder : 
                for fichier in os.listdir(f'{directory}/{folder}') :
                    if keyword in fichier :
                        plot_directory = f"{directory}/{folder}/{fichier}"

                        fichier = f"{folder}_{keyword}_{n}.png"

                        dest_file_path = os.path.join(static_imag, fichier)
                        shutil.copy2(plot_directory, dest_file_path)
                        n = n+1

    print("All the images have been retrieved succefully !")
    return(n)


def write_template(n):
    file_directory = os.path.join(BASE_DIR, 'templates/result.html')
    images_directory = os.path.join(BASE_DIR, 'static/images')
    plot_names = os.listdir(images_directory)

    with open(file_directory, "w") as file:
        if n == 1:
            plot_name = f"images/{plot_names[0]}"
            file.write(f"""<!doctype html>
<html lang="fr">
    <head>
        <meta charset="utf-8">
        <title>STATICAN</title> 
        <link rel="stylesheet" type="text/css" href="{{{{ url_for('static', filename='css/style5.css') }}}}">
        <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Audiowide">
    </head>
    <body>
        <a href="{{{{ url_for('site3') }}}}" class="bouton-retour">
            <img src="{{{{ url_for('static', filename='css/images/IMAGE_RETOUR_4.png') }}}}" alt="Retour">
        </a>
        <section> 
            <div class = "entete">
                <span class = "txt">STATICAN</span> 
                <span class = "gradient"></span>
                <span class = "dodge"></span>
            </div>
            <div class = "centre_unique">
                <img src = "{{{{ url_for('static', filename='{plot_name}') }}}}" alt="#" class = "image_simple">
            </div>
        </section>
    </body>
</html>""")
        elif n > 1:
            file.write(f"""<!doctype html>
<html lang="fr">
    <head>
        <meta charset="utf-8">
        <title>STATICAN</title> 
        <link rel="stylesheet" type="text/css" href="{{{{ url_for('static', filename='css/style5.css') }}}}">
        <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Audiowide">
        <script defer src = "{{{{ url_for('static', filename='js/app1.js') }}}}"></script>
    </head>
    <body>
        <a href="{{{{ url_for('site3') }}}}" class="bouton-retour">
            <img src="{{{{ url_for('static', filename='css/images/IMAGE_RETOUR_4.png') }}}}" alt="Retour">
        </a>
        <section> 
            <div class = "entete">
                <span class = "txt">STATICAN</span> 
                <span class = "gradient"></span>
                <span class = "dodge"></span>
            </div> 
            <div class = 'centre'>
                <div class = 'images'>""")
            for plot_name in plot_names:
                plot_name = f'images/{plot_name}'
                file.write(
                    f"""<div class = "slide"> <img src = "{{{{ url_for('static', filename='{plot_name}') }}}}" alt=""> </div>""")
            file.write("""</div>
                <div class="boutons">""")
            j = 0
            while n > 0:
                file.write(f"""<a href="#" class="bouton{j}"></a> """)
                n -= 1
                j += 1
            file.write("""</div>
            </div>
        </section>
    </body>
</html>""")


def write_foldchange(analysis_path):
    n = copy_images("FC_plot",analysis_path)
    print("Fold change template is generating...")
    write_template(n)
              
    

def write_volcano(analysis_path):
    n = copy_images("Volcano",analysis_path)
    write_template(n)

def write_PCA(analysis_path):
    n = copy_images("PCA",analysis_path)
    write_template(n)



def write_HEATMAP(analysis_path):
    n = copy_images("HEATMAP",analysis_path)
    write_template(n)


