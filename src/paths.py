"""
Module pour la gestion des chemins.
"""

# Imports
import os

# Chemin absolu pour ce fichier 
absFilePath = os.path.abspath(__file__)           

# Chemin absolu pour le repertoire
fileDir = os.path.dirname(os.path.abspath(__file__))

# Chemin absolu pour le repertoire parent
parentDir = os.path.dirname(fileDir)

# Chemin absolu pour le repertoire "data" du projet
dataPath = os.path.join(parentDir, 'data')

# Chemins pour les donnees 
obesityPath = os.path.join(dataPath, 'obesity.csv')
employmentPath = os.path.join(dataPath, 'employment.csv')
countriesPath = os.path.join(dataPath, 'world-countries.json')
