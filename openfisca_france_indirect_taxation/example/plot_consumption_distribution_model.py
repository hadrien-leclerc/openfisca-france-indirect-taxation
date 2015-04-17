# -*- coding: utf-8 -*-
"""
Created on Sun Mar 29 15:43:49 2015

@author: germainmarchand
"""

# -*- coding: utf-8 -*-


# OpenFisca -- A versatile microsimulation software
# By: OpenFisca Team <contact@openfisca.fr>
#
# Copyright (C) 2011, 2012, 2013, 2014 OpenFisca Team
# https://github.com/openfisca
#
# This file is part of OpenFisca.
#
# OpenFisca is free software; you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# OpenFisca is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import division

from pandas import DataFrame, concat
import matplotlib.pyplot as plt

import openfisca_france_indirect_taxation
from openfisca_survey_manager.survey_collections import SurveyCollection


from openfisca_france_data import default_config_files_directory as config_files_directory
from openfisca_france_indirect_taxation.surveys import SurveyScenario

# Le but est ici de voir l'évolution de la distribution selon les 8 postes agrégés
# des coicop12 qui nous intéressent de 2005 à 2010
# Par la suite nous ferons cette étude de 1995 à 2011 (comme de 2006 à 2010 les données sont calées sur 2005
# nous savons par avance que cette distribution sera constante).
# Ce document sert donc de structure.


# On cherche donc tout d'abord à importer nos données de 2005 à 2010

def get_input_data_frame(year):
    openfisca_survey_collection = SurveyCollection.load(
        collection = "openfisca_indirect_taxation", config_files_directory = config_files_directory)
    openfisca_survey = openfisca_survey_collection.get_survey("openfisca_indirect_taxation_data_{}".format(year))
    input_data_frame = openfisca_survey.get_values(table = "input")
    input_data_frame.reset_index(inplace = True)
    return input_data_frame


def simulate_df(var_to_be_simulated, year):
    '''
    Construction de la DataFrame à partir de laquelle sera faite l'analyse des données
    '''
    input_data_frame = get_input_data_frame(year)
    TaxBenefitSystem = openfisca_france_indirect_taxation.init_country()

    tax_benefit_system = TaxBenefitSystem()
    survey_scenario = SurveyScenario().init_from_data_frame(
        input_data_frame = input_data_frame,
        tax_benefit_system = tax_benefit_system,
        year = year,
        )
    simulation = survey_scenario.new_simulation()
    return DataFrame(
        dict([
            (name, simulation.calculate(name)) for name in var_to_be_simulated

            ])
        )


def wavg(groupe, var):
    '''
    Fonction qui calcule la moyenne pondérée par groupe d'une variable
    '''
    d = groupe[var]
    w = groupe['pondmen']
    return (d * w).sum() / w.sum()


def collapse(dataframe, groupe, var):
    '''
    Pour une variable, fonction qui calcule la moyenne pondérée au sein de chaque groupe.
    '''
    grouped = dataframe.groupby([groupe])
    var_weighted_grouped = grouped.apply(lambda x: wavg(groupe = x, var = var))
    return var_weighted_grouped


def df_weighted_average_grouped(dataframe, groupe, varlist):
    '''
    Agrège les résultats de weighted_average_grouped() en une unique dataframe pour la liste de variable 'varlist'.
    '''
    return DataFrame(
        dict([
            (var, collapse(dataframe, groupe, var)) for var in varlist
            ])
        )

if __name__ == '__main__':
    import logging
    log = logging.getLogger(__name__)
    import sys
    logging.basicConfig(level = logging.INFO, stream = sys.stdout)


# Exemple: graphe par décile de revenu par uc de la ventilation de la consommation selon les postes agrégés de la CN
    # Lite des coicop agrégées en 12 postes
    list_coicop12 = []
    for coicop12_index in range(1, 9):
        list_coicop12.append('coicop12_{}'.format(coicop12_index))
    # Liste des variables que l'on veut simuler
    var_to_be_simulated = [
        'ident_men',
        'pondmen',
        'decuc',
        'age',
        'decile',
        'revtot',
        'somme_coicop12_conso',
        'ocde10',
        'niveau_de_vie',
        ]
    # Merge des deux listes
    var_to_be_simulated += list_coicop12


    df2005 = simulate_df(var_to_be_simulated = var_to_be_simulated, year = 2005)
    annee = df2005.apply(lambda row: 2005, axis = 1)
    df2005["year"] = annee
    df2006 = simulate_df(var_to_be_simulated = var_to_be_simulated, year = 2006)
    annee = df2006.apply(lambda row: 2006, axis = 1)
    df2006["year"] = annee
    df2007 = simulate_df(var_to_be_simulated = var_to_be_simulated, year = 2007)
    annee = df2007.apply(lambda row: 2007, axis = 1)
    df2007["year"] = annee
    df2008 = simulate_df(var_to_be_simulated = var_to_be_simulated, year = 2008)
    annee = df2008.apply(lambda row: 2008, axis = 1)
    df2008["year"] = annee
    df2009 = simulate_df(var_to_be_simulated = var_to_be_simulated, year = 2009)
    annee = df2009.apply(lambda row: 2009, axis = 1)
    df2009["year"] = annee
    df2010 = simulate_df(var_to_be_simulated = var_to_be_simulated, year = 2010)
    annee = df2010.apply(lambda row: 2010, axis = 1)
    df2010["year"] = annee
    var_to_concat = list_coicop12 + ['somme_coicop12_conso']

    Wconcat2005 = df_weighted_average_grouped(dataframe = df2005, groupe = 'year', varlist = var_to_concat)
    Wconcat2006 = df_weighted_average_grouped(dataframe = df2006, groupe = 'year', varlist = var_to_concat)
    Wconcat2007 = df_weighted_average_grouped(dataframe = df2007, groupe = 'year', varlist = var_to_concat)
    Wconcat2008 = df_weighted_average_grouped(dataframe = df2008, groupe = 'year', varlist = var_to_concat)
    Wconcat2009 = df_weighted_average_grouped(dataframe = df2009, groupe = 'year', varlist = var_to_concat)
    Wconcat2010 = df_weighted_average_grouped(dataframe = df2010, groupe = 'year', varlist = var_to_concat)

    # Construction des parts pour 2005
    list_part_coicop12_2005 = []
    for i in range(1, 9):
        Wconcat2005['part_coicop12_{}'.format(i)] = Wconcat2005['coicop12_{}'.format(i)] / Wconcat2005['somme_coicop12_conso']
        'list_part_coicop12_{}_2005'.format(i)
        list_part_coicop12_2005.append('part_coicop12_{}'.format(i))

    # Construction des parts pour 2006
    list_part_coicop12_2006 = []
    for i in range(1, 9):
        Wconcat2006['part_coicop12_{}'.format(i)] = Wconcat2006['coicop12_{}'.format(i)] / Wconcat2006['somme_coicop12_conso']
        'list_part_coicop12_{}_2006'.format(i)
        list_part_coicop12_2006.append('part_coicop12_{}'.format(i))

    # Construction des parts pour 2007
    list_part_coicop12_2007 = []
    for i in range(1, 9):
        Wconcat2007['part_coicop12_{}'.format(i)] = Wconcat2007['coicop12_{}'.format(i)] / Wconcat2007['somme_coicop12_conso']
        'list_part_coicop12_{}_2007'.format(i)
        list_part_coicop12_2007.append('part_coicop12_{}'.format(i))

    # Construction des parts pour 2008
    list_part_coicop12_2008 = []
    for i in range(1, 9):
        Wconcat2008['part_coicop12_{}'.format(i)] = Wconcat2008['coicop12_{}'.format(i)] / Wconcat2008['somme_coicop12_conso']
        'list_part_coicop12_{}_2008'.format(i)
        list_part_coicop12_2008.append('part_coicop12_{}'.format(i))

    # Construction des parts pour 2009
    list_part_coicop12_2009 = []
    for i in range(1, 9):
        Wconcat2009['part_coicop12_{}'.format(i)] = Wconcat2009['coicop12_{}'.format(i)] / Wconcat2009['somme_coicop12_conso']
        'list_part_coicop12_{}_2009'.format(i)
        list_part_coicop12_2009.append('part_coicop12_{}'.format(i))

    # Construction des parts pour 2010
    list_part_coicop12_2010 = []
    for i in range(1, 9):
        Wconcat2010['part_coicop12_{}'.format(i)] = Wconcat2010['coicop12_{}'.format(i)] / Wconcat2010['somme_coicop12_conso']
        'list_part_coicop12_{}_2010'.format(i)
        list_part_coicop12_2010.append('part_coicop12_{}'.format(i))



    df_to_graph = concat([Wconcat2005[list_part_coicop12_2005], Wconcat2006[list_part_coicop12_2006], Wconcat2007[list_part_coicop12_2007], Wconcat2008[list_part_coicop12_2008], Wconcat2009[list_part_coicop12_2009], Wconcat2010[list_part_coicop12_2010]])

    axes = df_to_graph.plot(
        kind = 'bar',
        stacked = True,
        color = ['#800000','g','#660066','#1414ff','#ffce49','#383838','#f6546a','#229cdc']
        )
    plt.axhline(0, color = 'k')

    # Supprimer la légende du graphique
    ax=plt.subplot(111)
    ax.legend_.remove()
    plt.show()