# -*- coding: utf8 -*-

# Génère des phrases de poésie avec possibilité de choisir les rimes, le nombre de syllabes, de paragraphes, de vers etc...

# Documents nécéssaires dans le fichier :
# PoemeDB.sqlite3

## Introduction
# Importations
import sqlite3
from django.db import connections

# Initialisations

symboles = ",;:…./\&'§@#!()-_$*¥€%£?"
count = 0
err1 = ""
err2 = ""

# Création liste des mots possibles

motPossible = []

with connections['mots'].cursor() as cur:
    cur.execute('SELECT * FROM MOTS')
    ortho = cur.fetchall()

# Traitement des résultats
for mot1 in ortho:
    motPossible.append(mot1[0])

# Création syllPossible : dictionnaire des syllabes possibles présentes plus de 10 fois avec les associtations API, courant vers la notation de la base de données
# Création aidephon : texte à afficher dans fenêtre "Aide Phonétique", syllabes présentes plus de 20 fois
syllPossible = dict()
aidephon = []

with connections['mots'].cursor() as cur:
    cur.execute("""
    SELECT dersyll, courant, API, count(*) as nboccurence
    FROM SYLLABES, MOTS
    WHERE SYLLABES.id = MOTS.iddersyll
    GROUP BY iddersyll
    HAVING COUNT(iddersyll) >= 10
    ORDER BY LOWER(dersyll) ASC""")
    syllaide = cur.fetchall()

for syll in syllaide:
    syllPossible[syll[0]] = [syll[0]]
    syllPossible[syll[2]] = [syll[0]]
    aidephon.append({'courant': syll[0], 'dersyll': syll[1], 'API': syll[2], 'nboccurence': syll[3]})

## Fonctions

def analyse(nbsyll, dersyll = ''):
    """
    * Renvoie une phrase aléatoire de nbsyll-syllabes et de dernière syllabe dersyll
    * Ainsi que la dernière syllabe de cette phrase
    * Suppose que dersyll est possible et que nbsyll est un entier
    * nbsyll sera automatiquement mis entre 1 et 12
    """

    print(nbsyll)
    if nbsyll < 2:
        # Cas de une syllabe
        if dersyll == '':
            req = """
            AND iddersyll in (SELECT iddersyll
            FROM MOTS JOIN SYLLABES ON iddersyll = SYLLABES.id
            GROUP BY iddersyll
            HAVING COUNT(iddersyll) >= 10)"""
        else:
            req = """AND SYLLABES.dersyll = '%s'""" % dersyll

        with connections['mots'].cursor() as cur:
            cur.execute("""
            SELECT ortho, dersyll
            FROM MOTS JOIN SYLLABES ON iddersyll = SYLLABES.id
            WHERE nbsyll = 1
            AND length(ortho) > 3
            %s
            ORDER BY RANDOM() LIMIT 1;"""%req)
            newWords = cur.fetchone()

            nouveau = newWords[0]
            dersyll = newWords[1]

            cur.execute("""
            SELECT PONCT
            FROM PONCTUATION
            WHERE freq > (SELECT abs(random() / 10000000000000000000))
            ORDER BY random();""")

            ponct = cur.fetchone()[0]

        nouveau = nouveau[0].upper() + nouveau[1:] + ponct + "\n"
        return (nouveau, dersyll)

    if nbsyll > 12:
        # Si nbsyll trop élevé
        nbsyll = 12

    syllabe = dersyll

    with connections['mots'].cursor() as cur:
        cur.execute("""
        SELECT id, phrase
        FROM PHRASES
        WHERE nbsyllabe = ?
        ORDER BY RANDOM() LIMIT 1""", (nbsyll,))
        [id, phrase] = cur.fetchone()
    phraselist = phrase.split(" ")
    nouveau = ""

    for i in range(len(phraselist)):

        if i == len(phraselist) - 1 and syllabe != '':
            # Si dernier mot phrase et rime imposée :
            # Requête avec dernière syllabe
            req = """
            AND SYLLABES.dersyll = '%s'""" % syllabe
        elif i == len(phraselist) - 1:
            # Si dernier mot phrase, mais pas de rime imposée :
            # Choix syllabe existant plus de 10 fois
            req = """
            AND iddersyll in (SELECT iddersyll
            FROM MOTS JOIN SYLLABES ON iddersyll = SYLLABES.id
            GROUP BY iddersyll
            HAVING COUNT(iddersyll) >= 10)"""
        else:
            # Sinon, mot au milieu de phrase :
            # Pas de contrainte sur la dernière syllabe
            req = ""

        mot = phraselist[i].lower()
        if mot in symboles:
            # Si symbole : le laisser
            nouveau += mot + " "
        else:
            if mot[-1] in symboles and mot[:-1] in motPossible:
                # Si mot suivi de symbole (ex : mot = "ciel,") :
                # Garder symbole et changer le mot
                punctInside = mot[-1] + " "
                mot = mot[:-1]

            else:
                # Si pas de symbole : ponctuation vide
                punctInside = " "

            with connections['mots'].cursor() as cur:
                cur.execute("""
                SELECT cgram, genre, nombre, nbsyll, verper, haspir, cvcv
                FROM MOTS
                WHERE ortho = ?
                ORDER BY freqfilms DESC LIMIT 1""", (mot,))

                info = cur.fetchone()

            if len(mot) == 1 and info[6][0] == "C":
                nouveau += phraselist[i] + "'"
                punctInside = ""

            elif info[0][:3] == "ART" or info[0][:3] == "PRO" or info[0] == "ADJ:pos":
                nouveau += phraselist[i]
                punctInside = " "

            elif (info[0][:3] == "PRE" or info[0] == "CON") and len(mot) < 4:
                # Si petite préposition : la garder
                nouveau += phraselist[i]
                punctInside = " "

            else:
                if info[0][:3] == "PRE" or info[0][:3] == "CON":
                    # Si préposition mais pas petit mot :
                    # Ne pas prendre petit préposition
                    req = """ AND length(ortho) > 3""" + req

                elif info[0][:3] == "NOM" or info[0][:3] == "ADJ" or info[0][:3] == "VER":
                    # Si nom, adj ou ver :
                    # Garder 1er lettre cons ou voy pour liaison apostrophe

                    if info[4] != '':
                        # Garder que la personne du verbe sous forme %__%
                        # Si plusieurs possibilités de conjugaison, n'en garder qu'une

                        if mot[-1] == "s" and '2s' in info[4]:
                            # Mot à la 2e personne du singulier
                            info4 = ("%2s%",)
                        elif mot[-1] != "s" and ('1s' in info[4] or '3s' in info[4]):
                            if '1s' in info[4]:
                                # Mot à la 1e personne du singulier
                                info4 = ("%1s%",)
                            else:
                                # Mot à la 3e personne du singulier
                                info4 = ("%3s%",)
                        else:
                            # Mot à une autre personne
                            info4 = ("%" + info[4].split("-")[0] + "%",)

                        info = info[:4] + info4 + info[5:]

                    req = """AND cvcv LIKE '%s'"""%(info[-1][0]+"%") + req
                with connections['mots'].cursor() as cur:
                    cur.execute("""
                    SELECT ortho, dersyll
                    FROM MOTS JOIN SYLLABES ON iddersyll = SYLLABES.id
                    WHERE cgram = ?
                    AND genre = ?
                    AND nombre = ?
                    AND nbsyll = ?
                    AND verper LIKE ?
                    AND haspir = ?
                    %s
                    ORDER BY RANDOM() LIMIT 1"""%req, info[:-1])
                    newWords = cur.fetchone()
                try:
                    nouveaumot = newWords[0]
                    dersyll = newWords[1]
                except TypeError:
                    # print(phraselist, mot, newWords)
                    if count < 10:
                        return analyse(nbsyll, syllabe)
                    else:
                        raise RecursionError("Nombre de répétition dépassés, relance le poème")
                else:
                    # Si majuscule au milieu (ou au début) de la phrase : la garder
                    if phraselist[i][0].isupper():
                        nouveaumot = nouveaumot[0].upper() + nouveaumot[1:]

                    nouveau += nouveaumot

            nouveau += punctInside

    with connections['mots'].cursor() as cur:
        cur.execute("""
        SELECT PONCT
        FROM PONCTUATION
        WHERE freq > (SELECT abs(random() / 10000000000000000000))
        ORDER BY random();""")

        ponct = cur.fetchone()[0]

    nouveau = nouveau.strip(" ") + ponct + "\n"
    # print(id)
    return nouveau, dersyll

def poeme_texte(rimes, nbsyll):
    """
    * Génère des paragraphes de rime
    * rimes : "A_B_B_A_" = rimes embrassées, "A_B_A_B_" = rimes croisées
    * Forcer phonétique des rimes : rimes = "t@t_se_se_t@t" rime avec la phonétique donnée
    * nbsyll = [12,10,8] : 1er vers = 12 syllabes, 2e vers = 10 syllabes, 3e vers = 8 syllabes
    * Suppose rimes et nbsyll de la bonne forme (syllabes existent, nbsyll des entiers, nb lettre _ rime = len(nbsyll) )"""
    # Liste erreur : voir quelles phrases posent problème
    texteChargement = "Chargement ...\nVers déjà fait :\n\n"
    # Initialisations variables
    dictsyll = dict()
    rimes = rimes.split(" ")
    poeme = ""
    i = 0
    # Création poème
    for paragraphe in rimes:
        for verssyll in paragraphe.split("_")[:-1]:
            print(nbsyll)
            if "." in verssyll:
                phrase = analyse(nbsyll[i], verssyll.strip("."))
            elif verssyll in dictsyll:
                phrase = analyse(nbsyll[i], dictsyll[verssyll])
            else:
                phrase = analyse(nbsyll[i])
                dictsyll[verssyll] = phrase[1]
            count = 0
            poeme += phrase[0]
            i += 1
        # print()
        texteChargement += "\n"
        poeme += "\n"
    # Fin poème : un point
    poeme = poeme.strip("\n")[:-1].strip(" ") + "."
    return poeme

def prev(forme, sylltaille, rime):

    global err1
    global err2

    # Dictionnaire des noms de syllabes correspondant aux syllabes données
    syllname = dict()

    if len(forme) != 0:
        if len(sylltaille) != 0:
            # Création liste nbsyll
            sylltaille = sylltaille.split(",")
            nbsyll  = [""]* len(forme.replace(" ", ""))
            for syllUnit1 in sylltaille:
                syllUnit2 = syllUnit1.replace(" ", "").split("=")
                try:
                    int(syllUnit2[0])
                    int(syllUnit2[1])
                except ValueError:
                    # Si problème dans la façon dont est la taille des syllabes
                    err1 = syllUnit1 + " est mal écrit"
                    err2 = "Veuillez respecter la mise en forme :\n 1 = 12, 2 = 6 ..."
                    return None
                try:
                    if int(syllUnit2[1]) > 12:
                        # Si nb syllabe dépasse 12
                        err1 = "Attention, nombre de syllabes max dépassés\n(max = 12)"
                        nbsyll[int(syllUnit2[0]) - 1] = "_ " * 11
                    elif int(syllUnit2[1]) < 1:
                        # Si nb syllabe inférieur à 1
                        err1 = "Attention, nombre de syllabes min = 1"
                        nbsyll[int(syllUnit2[0]) - 1] = " "
                    elif int(syllUnit2[1]) == 1:
                        # Si nb syllabe = 1
                        nbsyll[int(syllUnit2[0]) - 1] = " "
                    else:
                        # Sinon
                        nbsyll[int(syllUnit2[0]) - 1] = "_ " * (int(syllUnit2[1]) - 1)
                except IndexError:
                    # Si nb syllabe dépasse nombre vers
                    err1 = "Vous avez dépassé le nombre de vers donnés dans  la forme"
                    return None
            # Pas de probleme : créer les str avec les _ suivant le nb de syllabes
            if nbsyll[0] == "":
                nbsyll[0] = "_ " * 11
            elif nbsyll[0] == " ":
                nbsyll[0] = ""
            for a in range(1, len(nbsyll)):
                if nbsyll[a] == "":
                    nbsyll[a] = str("_ " * (nbsyll[a-1].count("_")))
        else:
            # Si aucune info sur le nombre de syllabe donnée
            nbsyll = ["_ " * 11] * len(forme.replace(" ", ""))
        texte = ""
        if len(rime) == 0:
            # Sans rimes forcées, juste avec forme
            j = 0
            for i in range(len(forme)):
                if forme[i] == " ":
                    texte += '\n'
                else:
                    texte += str(nbsyll[j]) + forme[i] + "\n"
                    j+=1
        else:
            # Avec rimes forcées
            for rimeUnit in rime.split(","):
                a = rimeUnit.replace(" ", "").split("=")
                if a[0] in forme:
                    if a[1] in syllPossible:
                        syllname[a[0]] = syllPossible[a[1]][0]
                    else:
                        # Si syllabe pas possible
                        err1 = "Les rimes sont mal écrites"
                        err2 = str(a[1]) + " n'existe pas"
                        return None
                else:
                    # Si erreur sur la façon dont sont données les rimes
                    err1 = "Les rimes sont mals écrites"
                    err2 = "Veuillez respecter la mise en forme : A=t@t, B=se … (avec les bons symboles " \
                           "correspondants à ceux donnés dans forme)"
                    return None

            j = 0
            for i in range(len(forme)):
                if forme[i] == " ":
                    texte += '\n'
                else:
                    if forme[i] in syllname:
                        texte += str(nbsyll[j]) + syllname.get(forme[i]) + ".\n"
                    else:
                        texte += str(nbsyll[j]) + forme[i] + "\n"
                    j += 1

    else:
        # Si aucune forme n'est donnée
        err1 = "Vous n'avez donné aucune forme"
        return None

    forme = forme.replace(" ", "") # Variable globale de la forme pour être afficheé dans chargement
    print(forme)
    return texte

def main(rimes = "ABBA", syll = "1=12", rime = ""):
    global err1
    total = prev(rimes, syll, rime).split("\n")
    print(total)
    nbsyll = []
    forme = ""
    for formeVers in total:
        if formeVers != "":
            nbsyll.append(formeVers.count("_") + 1)
            forme += formeVers.split(" ")[-1] + "_"
        else:
            forme += " "
    try:
        texte = poeme_texte(forme, nbsyll).split("\n")
        print(texte)
    except:
        err1 = "Problème lors que la génération du poème"
        print(err1)
        return None
    else:
        return texte

#texte = main("ABBA CDDC EEF GGF", "1=12", "")