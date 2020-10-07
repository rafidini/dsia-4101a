"""
Module pour le traitement des donnees.
"""

# Imports
import re
import pycountry_convert as pc

# Fonctions complementaires
def convert_country_to_continent(country_name):
    """
    Convert a country name to the corresponding continent.
    """

    continents_dict = {
        'NA': 'North America',
        'SA': 'South America',
        'AS': 'Asia',
        'OC': 'Oceania',
        'AF': 'Africa',
        'EU': 'Europe',
        '?': 'Unknown'
    }

    try:
        country_code = pc.country_name_to_country_alpha2(country_name, cn_name_format="default")
        continent_code = pc.country_alpha2_to_continent_code(country_code)
        return continents_dict[continent_code]
    except KeyError:
        # Exception in employment
        if country_name in ['Korea', 'Republic of Korea', 'Timor-Leste']:
            return continents_dict['AS']

        # Exceptions in obesity
        return convert_country_to_continent(country_name.split(" ")[0])

def convert_country_to_country_code(country_name):
    """
    Convert a country name to the corresponding country code iso3.
    """

    try:
        country_code = pc.country_name_to_country_alpha3(country_name, cn_name_format="default")
        return country_code
    except KeyError:
        if country_name in ['Korea', 'Republic of Korea', 'Timor-Leste']:
            return {
                "Republic of Korea":"KOR",
                "Korea":"PRK",
                "Timor-Leste":"TLS"
                }[country_name]

        return convert_country_to_country_code(country_name.split(" ")[0])

def extract_float(string, index=0):
    """ Extrait les nombres a virgules dans une chaine de caracteres, et retourne
    celui a l'index donne en parametre. Par defaut l'index est a 0.

    >>> extract_float("0.5 [0.1-0.7]")
    0.5
    """

    # Worst case
    if index < 0:
        return None

    # No data case
    if string == "No data":
        return 0.0

    # Defining the regular expression
    reg_exp = re.compile(r"\d+\.\d+")

    # Tuple normally containing 3 float
    tup = [float(e) for e in reg_exp.findall(string)]

    # Bad case 27 <= len(string) <= 31
    if len(string) in range(27,31):
        return (tup[index] + tup[index + 3]) / 2
    # Normal case, 13 <= len(string) <= 16
    return tup[index]

def is_desk_manual(string):
    """
    Determine si la chaine de caracteres (ici un 'subject') est plutot:
      - Un travail de type manuel = "M"
      - Un travail bureautique = "D"
      - Ou autre = "?"

    Ces valeurs sont retournees par rapport a notre etude faite au prealable
    sur un jupyter notebook, les valeurs sont subjectives.
    """
    manual = ['A', 'B', 'C ', 'D', 'E', 'F', 'G', 'H', 'I', 'S', 'T']
    desk = ['J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', ' R', 'U']

    for man in manual:
        if '({})'.format(man) in string:
            return 'M'

    for des in desk:
        if '({})'.format(des) in string:
            return 'D'

    return 'U'

# Fonctions principales
def process_obesity(obesity):
    """
    Traite la DataFrame 'obesity' pour la rendre exploitable, la fonction
    retourne une DataFrame traitee.
    """

    # Nouveaux noms de colonnes
    names = {
        "Country" : "country",
        "Year" : "year",
        "Obesity (%)" : "str_obesity",
        "Sex" : "sex"
    }

    # Renomme les colonnes
    obesity = obesity.rename(columns=names)

    # Nouvelles colonnes
    new_obesity_columns = ['obesity', 'min_obesity', 'max_obesity']

    # Creation des nouvelles colonnes
    for itt, _ in enumerate(new_obesity_columns):
        obesity[new_obesity_columns[itt]] = obesity['str_obesity'].apply(
            lambda x: extract_float(x, index=0))

    # Nouvelles valeurs pour la colonne 'sex'
    new_sex = {e:e[0].upper() for e in set(obesity.sex)}

    # Remplacement des anciennes valeurs par les nouvelles
    obesity['sex'] = obesity['sex'].replace(new_sex)

    # Changement du type de la colonne
    obesity['sex'] = obesity['sex'].astype('category')
    obesity['country'] = obesity['country'].astype('string')

    # Enleve les colonnes inutiles
    obesity = obesity.drop(columns = ['str_obesity'])

    # Creation de la colonne 'continent' a partir de la colonne 'country' et la
    # fonction 'convert_country_to_continent'
    obesity['continent'] = obesity['country'].apply(lambda x: convert_country_to_continent(x))

    # Creation de la colonne 'country_code' a partir de la colonne 'country' et
    # la fonction 'convert_country_to_country_code'
    obesity['country_code'] = obesity['country'].apply(lambda x: convert_country_to_country_code(x))

    return obesity

def process_employment(employment):
    """
    Traite la DataFrame 'employment' pour la rendre exploitable, la fonction
    retourne une DataFrame traitee.
    """

    # Variables pour le traitement
    sex_values = {
        "Males":'M',
        "Females":'F',
        "All persons":'B'
    }

    # Les colonnes inutiles
    useless_columns = ['SUBJECT', 'Frequency', 'SEX', 'FREQUENCY', 'TIME',
    'Unit Code', 'Reference Period Code', 'Reference Period', 'Flag Codes',
    'Flags', 'Unit', 'PowerCode', 'PowerCode Code']

    # Suppression des colonnes inutiles
    employment = employment.drop(columns=useless_columns)

    # Nouveaux noms de colonnes lies aux pays
    loc_country = {'LOCATION':'country_code', 'Country':'country'}

    # Renommage de ces colonnes
    employment = employment.rename(columns=loc_country)

    # Changement de type en chaine de caracteres pour ces colonnes
    for col in loc_country.values():
        employment[col] = employment[col].astype('string')

    # Creation de la variable 'activity' pour le type d'activite a partir de la colonne 'Subject'
    employment['activity'] = employment['Subject'].apply(lambda x: is_desk_manual(x))

    # Changement de type pour la colonne 'activity' en variable ategorielle
    employment['activity'] = employment['activity'].astype('category')

    # Changement de nom pour la colonne 'Subject' = 'subject'
    employment = employment.rename(columns={'Subject':'subject'})

    # Remplacement des valeurs pour la colonne 'Sex'
    employment = employment.replace({'Sex':sex_values})

    # Changement du type de la colonne 'Sex' en variable categorielle
    employment['Sex'] = employment['Sex'].astype('category')

    # Changement de nom pour la colonne 'Sex' = 'sex'
    employment = employment.rename(columns={'Sex':'sex'})

    # Changement de nom pour la colonne 'Time' = 'year' pour plus de clarte
    employment = employment.rename(columns={'Time':'year'})

    # Changement de nom pour la colonne 'Value' = 'value'
    employment = employment.rename(columns={'Value':'value'})

    # Remplacement des valeurs dans la colonne 'value' pour les faire correspondre
    # a la veritable echelle
    employment['value'] = employment['value'].apply(lambda x: x* 1000)

    # Creation de la colonne 'continent' a partir de la colonne 'country' et la
    # fonction 'convert_country_to_continent'
    employment['continent'] = employment['country'].apply(lambda x: convert_country_to_continent(x))

    return employment
