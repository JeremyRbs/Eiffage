# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ExportProjet
                                 A QGIS plugin
 Cette extension permet d'exporter l'ensemble des couches de votre projet, avec ou sans votre QGIS.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2022-03-01
        git sha              : $Format:%H$
        copyright            : (C) 2022 by Jérémy RIBES / Eiffage Énergie Systèmes
        email                : Jeremy.RIBES@eiffage.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import *

from qgis.core import *

from qgis.utils import iface

from PyQt5 import *

# Initialisation des ressources Qt depuis le fichier resources.py
from .resources import *

# Import des scripts pour le dialog
from .export_projet_dialog import ExportProjetDialog
import os.path

""" Plugin QGIS """
class ExportProjet:

    """ Constructeur """
    def __init__(self, iface):

        self.iface = iface      # Sauvegarde de la référence de l'interface QGIS
        
        self.plugin_dir = os.path.dirname(__file__)     # Initialise le dossier principal du plugin
        
        locale = QSettings().value('locale/userLocale')[0:2]    # Initialise le dossier locale
        
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'ExportProjet_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Déclaration des différentes instances
        self.actions = []
        self.menu = self.tr(u'&Export Projet')

        # Vérifie si le plugin a bien démarré au lancement de QGIS
        # Doit être présent dans initGui() pour pouvoir relancer le plugin
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('ExportProjet', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):

        icon = QIcon("C:/Users/jribes/AppData/Roaming/QGIS/QGIS3/profiles/default/python/plugins/export_projet/icon.png")
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/export_projet/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Exporter vos fichiers'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Export Projet'),
                action)
            self.iface.removeToolBarIcon(action)


    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = ExportProjetDialog()

        # show the dialog
        self.dlg.show()
        
        self.progress = self.dlg.progressBar
        
        self.dlg.boutonParcourir.clicked.connect(self.parcourir)
        
        self.dlg.boutonOk.clicked.connect(self.execute)
        self.dlg.boutonFermer.clicked.connect(self.dlg.close)
            
    def execute(self):

        # Création du dialogue avec ses éléments (après traduction) et garde sa référence
        # Création d'un seul GUI ONCE dans le callback, ce qui va seulement chargé une fois la fenêtre quand le plugin est lancé
        if self.first_start == True:
            self.first_start = False
            self.dlg = ExportProjetDialog()

        # Affichage du dialogue
        self.dlg.show()
        
        # Récupération du chemin de dossier
        dossier = self.dlg.cheminDossier.text()
        
        liste = []  # Création d'une liste pour répertorier toutes les couches du projet actuel
        listeNom = []   # Création d'une liste pour récupérer les noms des couches du projet actuel
        
        # Récupération des informations pour dupliquer les couches
        layers = iface.mapCanvas().layers()
        transform_context = QgsProject.instance().transformContext()
        save_options = QgsVectorFileWriter.SaveVectorOptions()
        save_options.driverName = "ESRI Shapefile"
        save_options.fileEncoding = "UTF-8"

        # Ajout de toutes les couches dans la liste
        for layer in layers:
            liste.append(layer)
            listeNom.append(layer.name())

        # Création des couches dans le nouveau dossier
        for i in liste:
            error = QgsVectorFileWriter.writeAsVectorFormatV2(i,
                                                              dossier+'/'+i.name(),
                                                              transform_context,
                                                          save_options)
            # Vérification du succès de la méthode
            if error[0] == QgsVectorFileWriter.NoError:
                self.dlg.lineEdit.setText("Succès !")
            else:
                self.dlg.lineEdit.setText("Erreur !")
                                                          
        # Si le radioButton est sélectionné alors ajout du projet QGIS
        if self.dlg.radioButton.clicked :
            dossier = self.dlg.cheminDossier.text()     # Récupération du chemin
            project = QgsProject.instance()     # Déclaration et initialisation du projet actuel
            project.write(dossier + '/suivis_travaux.qgs')  # Création du projet dans le nouveau dossier

            # Suppression des anciens fichiers (chemin dossier)
            for layer in layers:
                QgsProject.instance().removeMapLayers( [layer.id()] )
            
            # Ajout des nouvelles couches (chemin dossier)
            for i in listeNom:
                vlayer = iface.addVectorLayer(dossier+'/'+i+".shp", i, "ogr")
                if not vlayer:
                  print("La couche n'a pas réussi à se charger !")
            
            # Personnalisation de la couche câble
            layers = QgsProject.instance().mapLayersByName('cable')
            if layers :
            
                # Ajout de nouvelles colonnes
                nombreElements = layers[0].featureCount()
                colonneEtat = QgsField('Etat', QVariant.String, 'String',80)
                layers[0].dataProvider().addAttributes([colonneEtat])
                layers[0].updateFields()
                idx = layers[0].fields().indexOf('Etat')
                colonneDate = QgsField('Date', QVariant.Date)
                layers[0].dataProvider().addAttributes([colonneDate])
                idx = layers[0].fields().indexOf('Date')
                
                # Remplissage de la colonne État
                features = layers[0].getFeatures()
                for feature in features:
                    with edit(layers[0]):
                        feature['Etat'] = 'A FAIRE'
                        layers[0].updateFeature(feature)
                
                # Application d'un style sur la couche
                if layers[0].geometryType() == QgsWkbTypes.LineGeometry:
                    layers[0].loadNamedStyle('C:/Users/jribes/AppData/Roaming/QGIS/QGIS3/profiles/default/python/plugins/export_projet/styleCables.qml')
                layers[0].triggerRepaint()
                
                # La liste se vide pour éviter les erreurs
                layers.clear()
            
            # Personnalisation de la couche points techniques
            layers = QgsProject.instance().mapLayersByName('ptech')
            if layers :
            
                # Ajout de nouvelles colonnes
                nombreElements = layers[0].featureCount()
                colonneEtat = QgsField('Etat', QVariant.String, 'String',80)
                layers[0].dataProvider().addAttributes([colonneEtat])
                layers[0].updateFields()
                idx = layers[0].fields().indexOf('Etat')
                colonneDate = QgsField('Date', QVariant.Date)
                layers[0].dataProvider().addAttributes([colonneDate])
                idx = layers[0].fields().indexOf('Date')
                
                # Remplissage de la colonne État
                features = layers[0].getFeatures()
                for feature in features:
                    with edit(layers[0]):
                        feature['Etat'] = 'A FAIRE'
                        layers[0].updateFeature(feature)
                
                # Application d'un style sur la couche
                if layers[0].geometryType() == QgsWkbTypes.PointGeometry:
                    layers[0].loadNamedStyle('C:/Users/jribes/AppData/Roaming/QGIS/QGIS3/profiles/default/python/plugins/export_projet/stylePointsTechniques.qml')
                layers[0].triggerRepaint()
                
                # La liste se vide pour éviter les erreurs
                layers.clear()
            
            # Personnalisation de la couche des éléments de branchements passifs
            layers = QgsProject.instance().mapLayersByName('ebp')
            if layers :
            
                # Ajout de nouvelles colonnes
                nombreElements = layers[0].featureCount()
                colonneEtat = QgsField('Etat', QVariant.String, 'String',80)
                layers[0].dataProvider().addAttributes([colonneEtat])
                layers[0].updateFields()
                idx = layers[0].fields().indexOf('Etat')
                colonneDate = QgsField('Date', QVariant.Date)
                layers[0].dataProvider().addAttributes([colonneDate])
                idx = layers[0].fields().indexOf('Date')
                
                # Remplissage de la colonne État
                features = layers[0].getFeatures()
                for feature in features:
                    with edit(layers[0]):
                        feature['Etat'] = 'A FAIRE'
                        layers[0].updateFeature(feature)
                
                # Application d'un style sur la couche
                if layers[0].geometryType() == QgsWkbTypes.PointGeometry:
                    layers[0].loadNamedStyle('C:/Users/jribes/AppData/Roaming/QGIS/QGIS3/profiles/default/python/plugins/export_projet/styleBoitiers.qml')
                layers[0].triggerRepaint()
                
                # La liste se vide pour éviter les erreurs
                layers.clear()
                  
            
        
        # Barre de progression
        self.completed = 0

        while self.completed < 100:
            self.completed += 0.0001
            self.progress.setValue(self.completed)
            
        self.dlg.lineEdit.setAlignment(QtCore.Qt.AlignCenter)   # Centre le texte de l'objet lineEdit

    """ Méthode pour ouvrir la sélection de dossier, sélectionner le dossier et l'afficher sur la fenêtre """
    def parcourir(self):
        
        # Si le bouton Parcourir est cliqué alors lancement de la recherche de dossier puis affichage
        if self.dlg.boutonParcourir.clicked :
            dossier = QtWidgets.QFileDialog.getExistingDirectory(None, 'Sélectionner le dossier où déposer les shapes', 'C:\\', QtWidgets.QFileDialog.ShowDirsOnly)
            self.dlg.cheminDossier.setText(dossier)
        