import re

# Extracted text from PDF files
text_sample1 = """TICKET
23208
CAMION
: BB 488 ZQ
CLIENT
HUIL. DE CHAMBARAND
100 B IMP. GRANDVEAN, 38940 ROYBON, FR
NO SIRET 51927761000019 Tél :0033 (0)4.76.36.20.66.
SORTIE LE 05/04/2023 A 11:25 ENTREE LE 05/04/2023 A 10:10
No 1/050298
No
1/050293
EXPEDITION
ALBERT
ETS ALBERT
GRANGENEUVE
26400 CHABRILLAN; FRANCE
FOURNISSEUR
ADRESSE
COMMUNE
HUILERIE
HUILERIE DE CHAMBARAND SAS
: 100 B IMPASSE GRAND JEAN
38940 FOYEON, FRANCE
PRODUITS
DURABILITE
NETTOYAGE CAMION
TOURTEAU PRESSION DE COLZA
:
N/A
N/A
NETTOYAGE A SEC
TOURS PRECEDENTS
: ALIMENTS
CONTRAT N
230302
PLOMBS N°
ETAT BACHE CAMION
BON
MAUVAIS
SILOS
HUMIDITE
%
P1
15240 kg
P2
43420 kg
NET
28180 kg
Ce
ALIMENT DE TOURTEAU DE PRESSION DE COLZA
Matière première des aliments pour animaux Code catalogue communautaire 2.14.6 Constituants analytiques, sur produit brut: Protéines brutes: 28 à 30%
-Cellulose-brute: 13%
Matière grasse brute: 10 à 15% (Valeurs indicatives)
"""

text_sample2 = """TICKET
23252
CAMION
AC811MD
CLIENT
HUIL. DE CHAMBARAND
100 B IMP. GRANDJEAN, 38940 ROYBON, FR
N° SIRET 51927761000019 Tél :0033 (0)4.76.36.20.66.
SORTIE LE 07/04/2023 A 11:22
ENTREE LE 07/04/2023 A 11:11
HUILERIE
RECEPTION
No 1/050382 No 1/050380
HUILERIE DE CHAMBARAND SAS
100BIS IMPASSE GRANDJEAN
38940 ROYBON, FRANCE
FOURNISSEUR
ADRESSE
COMMUNE
: BERNARD
BERNARD AGRICULTURE
: 179 RTE DE TREVOUX
01390 STANDRE DE CORCY, FRANCE
PRODUITS
DURABILITE
A
GRAINE DE COLZA
N/A
N/A
NETTOYAGE A SEC
NETTOYAGE CAMION
A
TOURS PRECEDENTS
CONTRAT N
PLOMBS N°
ETAT BACHE CAMION
:
SILOS
HUMIDITE
:
2X CEREALES/TX SOJA
121008
: 2
BON
MAUVAIS
%
P1
43840 kg
P2
14720 kg
NET
29120 kg
CE
@BERNARD
SILO: 9016 Villefranche Tél. silo: 0474072330
Entrée: 07/04/2023 08:23:52 Sortie : 07/04/2023 08:37:08
PRODUIT : 311000 COLZA
BON DE MOUVEMENT CEREALES
Sortie Reprise pour compte
Bon n° EXP_14_7396
10016761
BERNARD AGRICULTURE
ST ANDRE DE CORCY
Récolte: 2022
Type expédition : Vente
Cellule(s): C6 SILO BERNARD
Traitement: NON
CARACTERISTIQUES:
HUMIDITE : 6,7
IMPURETES: 1,2
Brut (DSD 061041): 43860 kg
Tare (DSD 24388): 14680 kg
Poids net: 29180 kg
TRANSPORT:
Transporteur : EGUITA
Nettoyage: Nettoyage à sec
Visa : OA
Transports précédents :
Graines oléagineuses (colza, tournesol...) Tourteaux de soja
Cereales
Véhicule: GC159PH Remorque : AC811MD
Benne (véh.):
Benne (rem.):
OBSERVATIONS:
ORIGINE France
valeur GES colza=797gCO2eq/Kg
Contrat 121008 // Huilerie de chambarand certificat BERNARD 2BSvs n°2BS020148
Opérateur/trice:
Signature du tiers:
TURE UNIQUE / Unique consignment note
chant la case intéressée
déclaration
de
ut de transport ou de la lité du transporteur en cas de perte ou
à la livraison est limitée au montant de
ransport.
EGUITA
☐ INTERNATIONAL
CMR
Ce transporteur est soumis nonobstant toute clause tive au contrat de transport international du transporteur This carriage is subject notwithstanding any clause to on the Contract for the international Carriage
OF
e
Date :
CONDL
tention Travaux agricoles - Location de bennes
SASU au capital de 15.000 €
Chantre - 26320 SAINT MARCEL LES VALENCE
.: 04 75 60 64 35 - Fax: 04 82 53 50 15
ET: 534
-
www.eguita.fr Info@egulta.fr
23000018-APE 4941 BN TVA FR 08 534 434 238
NATURE DE LA MARCHANDISE
102
RUNNING METER
VALEUR DECLAREE Declared Value
POIDS VOLUME METRE LINEAIRE
Weight
5 180
IMMATRIC LL Vehic
N° IDTF:
ndises dangereuses / Dangerous goods
port sous température dirigée / Refrigerated transport
ntre-Remboursement / Cash on delivery
transports
ge charges
DONNEUR D'ORDRES (Client ou commissionnaire)
DOCUMENTS ANNEXĖS
Nom :
Documents attached
Adresse
CHARGÉES CHEZ L'EXPÉDITEUR
REMISES A L'EXPÉDITEUR
LIVRÉES AU DESTINATAIRE
RENDUES PAR LE
DESTINATAIRE
NON RENDUES A REPRENDRE
PALETTES
BACS
ROLLS
CERTIFICAT DE LAVAGE
CÉDENTS CHARGEMENTS
TYPE DE NETTOYAGE : Produit:
Lavage externe : Eau froide
Eau du réseau oui A Balayage
non
BO Lavage eau froide C□ Lavage avec détergent agréé DO Lavage + désinfectant agréé
Eau chaude Vapeur Séchage: Vapeur
lavage intérieur : Eau froide
Eau chaude
Vapeur Air chaud
Raclette
006553
traire, à la Convention rela- de marchandises par route. contrary, to the Convention goods by road (CMR).
Aril 23
EURS / Drivers
son
ATIONS / Plate N°
les moteur
remorques
MD
80x120
100x120
EUROPE
CACHET STATION :
DOCUMENT DE SUIVI / Follow-up document
OUI NON
DESTINATAIRE
Consignee:
Adresse : Adress
Ville :
City:
1
how
2. my har
DATE ET HEURE D'ARRIVÉE LE : Arrival date and hour:
DECHARGEMENT
nloading
H
.DPT:
Pays
Area code
Cour
PRESTATIONS ANNEXES EXECUTÉES PAR LE CONDUCTEUR: Chargeme Additional services executees by the driver: Loading
DATE ET HEURE DE DÉPART LE: Shipment date and hour:
......
......
t
OUI NON
.h
CHARGEMENT / Loading
ÉDITEUR - REMETTANT 'eur - Remitter:
Isse:
OXYANE
DPT
INSPIRER L'AVENIR
Pays :
SITE DE VILLEFRANCHE
ET HEURE D'ARRIVÉE LERUe Léon Jacquemaire
date and hour: 69400,
ATIONS ANEXES EXE OTRA Cope-sur-Saônegement
nal services executeds by
Fax: 04.74.07.05.47
ET HEURE DE DS villefranche@groupe-oxyane.fr
nt date and hour:
VES/ Reservations
Signature of Remitter
SIGNATURE DU REMETTANT
SIGNATURE DU TRANSPORTEUR Signature of Carrier
SIGNATURE DU DESTINATAIRE Signature of Consignee
SIGNATURE DU
ERVES / Reservations
RANSPORTEUR
of Carrier
Signature
RANSPORTEUR Rouge: DESTINATAIRE⚫ Vert: EXPEDITEUR ⚫ Noir: SOUCHE⚫ Blue: for carrier⚫ Rad: consignee⚫ Green: sender⚫ Black: counter foil
"""

text_sample3 = """TICKET
23252
CAMION
AC811MD
CLIENT
HUIL. DE CHAMBARAND
100 B IMP. GRANDJEAN, 38940 ROYBON, FR
N° SIRET 51927761000019 Tél :0033 (0)4.76.36.20.66.
SORTIE LE 07/04/2023 A 11:22
ENTREE LE 07/04/2023 A 11:11
HUILERIE
RECEPTION
No 1/050382 No 1/050380
HUILERIE DE CHAMBARAND SAS
100BIS IMPASSE GRANDJEAN
38940 ROYBON, FRANCE
FOURNISSEUR
ADRESSE
COMMUNE
: BERNARD
BERNARD AGRICULTURE
: 179 RTE DE TREVOUX
01390 STANDRE DE CORCY, FRANCE
PRODUITS
DURABILITE
A
GRAINE DE COLZA
N/A
N/A
NETTOYAGE A SEC
NETTOYAGE CAMION
A
TOURS PRECEDENTS
CONTRAT N
PLOMBS N°
ETAT BACHE CAMION
:
SILOS
HUMIDITE
:
2X CEREALES/TX SOJA
121008
: 2
BON
MAUVAIS
%
P1
43840 kg
P2
14720 kg
NET
29120 kg
"""

text_sample4 = """TICKET
23253
CAMION
: CH 111 WK
CLIENT
FOURNISSEUR
HUIL. DE CHAMBARAND
100 3 IMP. GRANDJEAN, 38940 ROYBON,
N° SIRET 51927761000019 Tél :0033 (0)4.76.36.20.66.
FR
SORTIE LE 07/04/2023 A 11:49 ENTREE LE 07/04/2023 A 11:40
No
No
1/050385 1/050384
RECEPTION
HUILERIE
HUILERIE DE CHAMBARAND SAS
100BIS IMPASSE GRANDJEAN
38940 ROYBON, FRANCE
BERNARD AGRICULTURE
BERNARD
179 RTE DE TREVOUX
ADRESSE
COMMUNE
:
01390 STANDRE DE CORCY, FRANCE
PRODUITS
: A
GRAINE DE COLZA
DURABILITE
NETTOYAGE CAMION
N/A
N/A
A
NETTOYAGE A SEC
TOURS PRECEDENTS
:
3X COLZA
CONTRAT N
: 121008
PLOMBS N°
ETAT BACHE CAMION
:
SILOS
HUMIDITE
BON
MAUVAIS
: 2
6.5%
P1
43700 kg
P2
13540 kg
NET
30160 kg
CE
@BERNARD
Production, Ve, thes
SILO: 9016 Villefranche
Tél. silo: 0474072330
Entrée: 07/04/2023 09:00:44
Sortie : 07/04/2023 09:18:18
PRODUIT: 311000 COLZA
BON DE MOUVEMENT CEREALES
Sortie Reprise pour compte
Bon n° EXP_14_7397
10016761
BERNARD AGRICULTURE ST ANDRE DE CORCY
Récolte: 2022
Type expédition : Vente
Cellule(s): C6 SILO BERNARD
Traitement: NON
CARACTERISTIQUES:
HUMIDITE : 6,7
IMPURETES: 1,1
Brut (DSD 24393): 43660 kg
Tare (DSD 24391): 13520 kg
Poids net : 30140 kg
TRANSPORT:
Transporteur : EGUITA
Nettoyage: Nettoyage à sec
Visa : OA
Transports précédents :
Graines oléagineuses (colza, tournesol...) Graines oléagineuses (colza, tournesol...) Graines oléagineuses (colza, tournesol...)
OBSERVATIONS:
Véhicule : DW905NH Remorque : CH111WK
Benne (véh.): --
Benne (rem.): -
Contrat 121008 // Huilerie de chambarand ORIGINE France
valeur GES colza=797gCO2eq/Kg
certificat BERNARD 2BSvs n°2BS020148
Opérateur/trice:
Signature du tiers:
LETTRE DE VOITURE UNIQUE / Unique consignment note
NATIONAL
Valider en cochant la case intéressée
A défaut de convention écrite entre les parties au contrat de transport ou de la déclaration de valeur spécifiée par le donneur d'ordres, la responsabilité du transporteur en cas de perte ou avarie survenue aux marchandises ou en cas de retard à la livraison est limitée au montant de l'indemnité prévue par le contrat type concernant le transport.
Transport - Manutention
EGUITA Travaux agricoles
BAGLI au capital de 10 000 €
INTERNATIONAL
CMR
0008845
Ce transporteur est soumis nonobstant toute clause contraire, à la Convention rela- tive au contrat de transport international du transporteur, de marchandises par route. This carriage is subject notwithstanding any clause to the contrary, to the Convention on the Contract for the international Carriage of goods by road (CMR).
Location de bennes
10 Chemin du Chantre - 26320 SAINT MARCEL LES VALENCE Tél. : 04 75 60 64 35 - Fax: 04 82 53 50 15
MARQUE
NOMBRE
Mark ou m
Number
www.eguita.fr - info@eguita.fr
SIRET 534 434 238 00018 - APE 4041 - NTVA FR DB 534 434 238
NATURE DE LA MARCHANDISE
zotivo но
N° IDTF:
Marchandises dangereuses / Dangerous goods
Transport sous température dirigée / Refrigerated transport
Contre-Remboursement / Cash on delivery
POIDS VOLUME METRE LINEAIRE
RUNNING METER
VALEUR DECLAREE
Declared at
Date :
CONDUCTEURS / Drivers
Ky on
IMMATRICULATIONS / Plate N
Véhicules moteur
DU SOS VG ***
(semi)-remorques
CHILL WAK
DONNEUR D'ORDRES (Client ou commissionnaire)
DOCUMENTS ANNEXÉS
Documents attached
Nom :
Adresse :
CONDITIONS GÉNÉRALES AU VERSO 'LE REFUS NON MOTIVÉ DE SIGNATURE ENGAGE LA RESPONSABILITÉ DES INTERESSES
Prix de transports
Carriage charges
PRECEDENTS CHARGEMENTS
idzu
201
80x120
100x120
EUROPE
CHARGÉES CHEZ REMISES A
L'EXPÉDITEUR L'EXPÉDITEUR
LIVRÉES AU DESTINATAIRE
RENDUES PAR LE NON RENDUES DESTINATAIRE A REPRENDRE
PALETTES
BACS
ROLLS
CERTIFICAT DE LAVAGE
Lavage externe :
lavage intérieur :
CACHET STATION:
Eau froide
Eau chaude☐ Vapeur Air chaud
Raclette
CHARGEMENT/Loading
EXPÉDITEUR - REMETTANT
Sendeur - Remitter :
Adresse :
Adress
Ville: I fe
City:
DATE ET HEURE D'ARRIVÉE LE :
Arrival date and hour:
TYPE DE NETTOYAGE : Produit:
Eau du réseau oui non A□ Balayage
BO Lavage eau froide
C□ Lavage avec détergent agréé D☐ Lavage + désinfectant agréé
· Oxyore.
Eau froide
Eau chaude Vapeur Séchage: Vapeur
DOCUMENT DE SUIVI/Follow-up document
DESTINATAIRE : Consignee:
Adresse : Adress
Ville: R Bor
Area code
.Pays :
Country
F
City:
.DPT:......
PRESTATIONS ANNEXES EXECUTÉES PAR LE CONDUCTEUR : Chargement OUI NON Additional services executees by the driver: Loading
DATE ET HEURE DE DÉPART LE :
Shipment date and hour:
OXYANE
RESERV Respons
SIGNATURE DOREMETTANT
Signature of Flo
INSPIRER L'AVENIR
-SIGNATURE DU TRANSPORTEUR
Signature of Carrier
SITE DE VILLEFRANCHE
Rue Léon Jacquemaire
69400, Villefranche-sur-Saône
Tel: 74.07.23 30gFax 04174507.05.47EDITEUR
• Bleu: TEASP
site Villefranche@nrun
Ben
DATE ET HEURE D'ARRIVÉE LE :
Arrival date and hour:
DECHARGEMENT / Unloading
Mammon
..DPT:
Area code
Pays : Country
h
PRESTATIONS ANNEXES EXECUTÉES PAR LE CONDUCTEUR: Chargement OUI NON Additional services executees by the driver: Loading
DATE ET HEURE DE DÉPART LE : Shipment date and hour:
‚à
HUILERIE DES UNALIBARA SIGNATURE DU TRANSPORTEUR
SAS au Capital de 100 000 €
100 B, Impasse Grand Jean 38940 ROYBON (France)
Tél. 00 33 4 76 36 20 66 - Fax 00 33 4 76 36 21 21
• Noir: SOUCHE⚫ Blue: for carrier⚫ Red: cânsignes 192017: Gendenlack: counter foil
RESERVES / Reservations
Signature of Carrier
"""

text_sample5 = """TICKET
23246
CAMION
: GJ 617 XP
CLIENT
HUIL. DE CHAMBARAND
100 B IMP. GRANDJEAN, 38940 ROYBON, FR
No SIRET 51927761000019 Tél :0033 (0)4.76.36.20.66.
SORTIE LE 07/04/2023 A 08:48 ENTREE LE 07/04/2023 A 08:16
No 1/050371 No 1/050369
EXPEDITION
: AGRIFARM
AGR FARM SRL
VIA PANCALIERI 24
VIGOGNE 10067;
ITALIE
FOURNISSEUR
ADRESSE
: HUILERIE
HUILERIE DE CHAMBARAND SAS
: 100 B IMPASSE GRAND JEAN
COMMUNE
: 38940 ROYBON, FRANCE
PRODUITS
DURABILITE
NETTOYAGE CAMION
G
TOURTEAU PRESSION DE COLZA
:
N/A
N/A
A
NETTOYAGE A SEC
TOURS PRECEDENTS
DRECHE+AVOINE/TTXTCU
CONTRAT N
230130
PLOMBS No
ETAT BACHE CAMION
: x
BON
MAUVAIS
SILOS
:
3
HUMIDITE
:
%
P1
13640 kg
P2
40060 kg
NET
26420 kg
CE
ALIMENT DE TOURTEAU DE PRESSION DE COLZA
Matière première des aliments pour animaux Code catalogue communautaire 2.14.6
Constituants analytiques, sur produit brut:
Protéines brutes: 28 à 30%
Cellulose brute: 13%
Matière grasse brute: 10 à 15% (Valeurs indicatives)
CONDITIONS GENERALES AU VERSO *LE REFUS NON MOTIVÉ DE SIGNATURE ENGAGE LA RESPONSABILITÉ DES INTÉRESSÉS
LETTRE DE VOITURE UNIQUE / Unique consignment note
NATIONAL
Valider en cochant la case intéressée
A défaut de convention écrite entre les parties au contrat de transport ou de la déclaration de valeur spécifiée par le donneur d'ordres, la responsabilite du transporteur en cas de perte ou vario survenue aux marchandises ou en cas de retard a la raison est limitée au montant de findemnite prévue par le contrat type concemant le transport
RHIN RHONE LOGISTIQUE
SARL au capital de 140 000 €
INTERNATIONAL
CMR
41091
Ce transporteur est soumis nonobstant toute clause contraire, à la Convention relati- ve au contrat de transport international du transporteur, de marchandises par route. This carriage is subject notwithstanding any clause to the contrary, to the Convention on the Contract for the international Carriage of goods by road (CMR).
ZAC DES GIRANAUX - 70100 ARC LES GRAY
-
Tél. Exploitation : 07 87 22 52 88 - Tél. Administratif : 03 84 65 18 75 RCS Vesoul 841 722 135 T.V.A. FR 46 841 722 135
POIDS VOLUME METRE LINEAIRE
Weight
RUNNING METER
MARQUE
NOMBRE
Mark ou n°
Number
NATURE DE LA MARCHANDISE
VALEUR DECLAREE Declared Value
Date:
07/03/2
CONDUCTEURS / Drivers
IMMATRICULATIONS / Plate N°
Véhicules moteur
N° IDTF :
Marchandises dangereuses / Dangerous goods
Transport sous température dirigée / Refrigerated transport
Contre-Remboursement / Cash on delivery
Prix de transports
Carriage charges
DONNEUR D'ORDRES (Client ou commissionnaire)
DOCUMENTS ANNEXÉS Documents artached
Nom :
Adresse :
CHARGÉES CHEZ L'EXPÉDITEUR
REMISES A L'EXPÉDITEUR
LVREES AU DESTINATARE
RENDUES PAR LE DESTINATAIRE
NON RENDUES A REPRENDRE
PALETTES
BACS
ROLLS
CERTIFICAT DE LAVAGE EN STATION UNIQUEMENT
(semi)-remorques
80x120
100x120
EUROPE
lavage intérieur :
CACHET STATION:
Eau froide
Eau chaude
PRECEDENTS CHARGEMENTS
CMR-10
CMR -2
TYPE DE NETTOYAGE:
Lavage avec détergent agréé
Produit:
Eau du réseau oui☐ non
A Balayage
BO Lavage eau froide
CMR -3
DO Lavage + désinfectant agréé
CHARGEMENT / Loading
DOCUMENT DE SUIVI / Follow-up document
DECHARGEMENT / Unloading
EXPÉDITEUR - REMETTANT: Sendeur - Remitter :
Adresse :
Adress
DESTINATAIRE : Consignee :
Adresse : Adress
รา
ne
Ville :.
City:
.DPT:
Area code
Pays : Country
Ville :
City:
..DPT:
Area code
.Pays :
Country
.à
ESTRAR LE CONDUCTEUR : Chargement
DATE ET HEURE D'ARRIVÉE LE :
Arrival date and hour:
Additional
PRESTATIONS TULEERIE DE CHAMBARAND..............................
DATE ET HEURE DE SAS au Capital de 100 000 €
Shipment date and hour!
LAVAGE EN FERME UNIQUEMENT
38940 ROYBON (France)
RESERVES THIS MEANT 66 - Fax 009947636 21 ZANSPORTEUR
SIGNATURE
Signature of Remmer
Siret 519 277 610 00019 TVA FR 38 519 277 610
Signature of Carrier
EAU DE RESEAU
DATE ET HEURE D'ARRIVÉE LE : Arrival date and hour:
‚à
OUI NON
PRESTATIONS ANNEXES EXECUTÉES PAR LE CONDUCTEUR: Chargement Additional services executees by the driver: Loading
OUI NON
h
DATE ET HEURE DE DÉPART LE:
a.
Shipment date and hour:
.à
CAPTAGE
SIGNATURE DU DESTINATAIRE Signature of Consignee
RESERVES / Reservations SIGNATURE DU TRANSPORTEUR
Signature of Carrier
⚫ Bleu TRANSPORTEUR Rouge: DESTINATAIRE⚫ Vert: EXPEDITEUR⚫ Noir SOUCHE⚫ Blue: for carrier ● Redcarsighte
Giten sendir⚫ Black: counter foil
"""

text_sample6 = """TICKET
23241
CAMION
: CV 697 AX
CLIENT
HUIL. DE CHAMBARAND
100 B IMP GRANDJEAN, 38940 ROYBON, FR
•
No SIRET 51927761000019
Tél :0033 (0)4.76.36.20.66.
SORTIE LE 06/04/2023 A 16:31 ENTREE LE 06/04/2023 A 16:13
: HUILERIE
RECEPTION
No 1/050362
No 1/050359
HUILERIE DE CHAMBARAND SAS
100BIS IMPASSE GRANDJEAN
38940 ROYBON, FRANCE
FOURNISSEUR
ADRESSE
COMMUNE
: BERNARD
BERNARD AGRICULTURE
: 179 RTE DE TREVOUX
01390 STANDRE DE CCRCY, FRANCE
PRODUITS
DURABILITE
NETTOYAGE CAMION
TOURS PRECEDENTS
CONTRAT N
PLOMBS N°
A
GRAINE DE COLZA
:
N/A
N/A
A
NETTOYAGE A SEC
TXCOLZA/2X CEREALES
121008-1
ETAT BACHE CAMION
:
BON
MAUVAIS
SILOS
HUMIDITE
bim
%
P1
P2
NET
:
44120 kg
13200 kg
30920 kg
CE
@BERNARD
SILO: 9016 Villefranche
Tél. silo: 0474072330
Entrée: 06/04/2023 13:36:00
Sortie : 06/04/2023 13:58:58
PRODUIT : 311000 COLZA
BON DE MOUVEMENT CEREALES
Sortie Reprise pour compte Bon n° EXP_14_7388
10016761
BERNARD AGRICULTURE
ST ANDRE DE CORCY
Récolte: 2022
Type expédition : Vente
Cellule(s): C6 SILO BERNARD
Traitement: NON
CARACTERISTIQUES :
HUMIDITE:7
IMPURETES : 1,5
TRANSPORT:
Brut (DSD 061036): 44260 kg
Tare (DSD 24377): 13280 kg
Poids net : 30980 kg
Transporteur : EGUITA
Nettoyage : Nettoyage à sec
Visa : OA
Transports précédents :
Tourteaux colza
Cereales
Graines oléagineuses (colza, tournesol...)
OBSERVATIONS:
Véhicule : CY992YP Remorque : CV697AX
Benne (véh.): -
Benne (rem.):
certificat BERNARD 2BSvs n°2BS020148
Contrat 121008 // Huilerie de chambarand ORIGINE France
valeur GES colza=797gCO2eq/Kg
Opérateur/trice:
Signature du tiers:
LETTRE DE VOITURE UNIQUE / Unique consignment note
NATIONAL
Valider en cochant la case intéressée
A défaut de convention écrite entre les parties au contrat de transport ou de la déclaration de valeur spécifiée par le donneur d'ordres, la responsabilité du transporteur en cas de perte ou avarie survenue aux marchandises ou en cas de retard à la livraison est limitée au montant de l'indemnité prévue par le contrat type concernant le transport.
EGUITA
INTERNATIONAL
CMR
0006407
Ce transporteur est soumis nonobstant toute clause contraire, à la Convention rela- tive au contrat de transport international du transporteur, de marchandises par route. This carriage is subject notwithstanding any clause to the contrary, to the Convention on the Contract for the international Carriage of goods by road (CMR).
Transport - Manutention Travaux agricoles - Locatlon de bennes
SASU au capřist de 15 000 €
10 Chemin du Chantre - 26320 SAINT MARCEL LES VALENCE Tel.: 04 75 60 64 35 - Fax : 04 82 53 50 15 www.eguita.fr - info@eguita.fr
MARQUE NOMBRE
Mark oun
Number
SIRET : 634 434 233 00018 - APE 4941 9-N TWA FR DE 534 434 238
NATURE DE LA MARCHANDISE
сва
POIDS VOLUME METRE LINEAIRE
Weight
VALEUR DECLAREE
Declared Val
&
RANNING METE
30980
N° IDTF:
Marchandises dangereuses / Dangerous goods
Transport sous température dirigée / Refrigerated transport
Contre-Remboursement / Cash on delivery
DOCUMENTS ANNEXÉS
Documents attached
Date :
60 2022
CONDUCTEURS / Drivers
Pulill
IMMATRICULATIONS / Plate N°
Véhicules moteur
судячие
(semi)-remorques
CV 697 AX
DONNEUR D'ORDRES (Client ou commissionnaire)
Nom :
Adresse :
CONDITIONS GENERALES AU VERSO "LE REFUS NON MOTIVÉ DE SIGNATURE ENGAGE LA RESPONSABILITE DES INTÉRESSÉS
Prix de transports
Carriage charges
PRÉCÉDENTS CHARGEMENTS
BLE JOERA
80x120
100x120
EUROPE
CHARGÉES CHEZ L'EXPÉDITEUR
REMISES A L'EXPÉDITEUR
LIVRÉES AU DESTINATAIRE
RENDUES PAR LE NON RENDUES DESTINATAIRE A REPRENDRE
PALETTES
BACS ROLLS
CERTIFICAT DE LAVAGE
Lavage externe :
lavage intérieur :
CACHET STATION:
Eau froide
Eau chaude
Eau chaude
Vapeur Séchage:
Vapeur Raclette
Vapeur Air chaud
CHARGEMENT / Loading
EXPÉDITEUR - REMETTANT: Sendeur - Remitter:
Adresse :
Adress
Ville :
City:
DATE ET HEURE D'ARRIVÉE LE :
Arrival date and hour:
J. Wel
.DP
PRESTATIONS ANNEXES EXECUTÉES PAR
TYPE DE NETTOYAGE : Produit:
Eau du réseau oui non A□ Balayage
BO Lavage eau froide
C□ Lavage avec détergent agréé DJ Lavage + désinfectant agréé
Eau froide
DOCUMENT DE SUIVI / Follow-up document
BERNARD
OXYANE
INSPIRER L'AVENIR
SITE DE VILLEFRANCHE
Rue Léon Jacquemaire NON 69400, Villefranche-sur-Saône
Additional services executees by the driver: Loading
DATE ET HEURE DE DÉPART LE :
Shipment date and hour:
RESERVES / Reservations
Signature of Remitter
SIGNATURE DU REMETTANT
DESTINATAIRE : Consignee:
Adresse:
Adress
Ville : City:
DATE ET HEURE D'ARRIVÉE LE : Arrival date and hour:
Hudder
DECHARGEMENT / Unloading
ROY
.DPT:
Area code
Them beren
BON
Pays : *Country
h
NON LI
PRESTATIONS ANNEXES EXHUILERIE DE CHAMBARAND
Additional services executees by the driver: Loading DATE ET HEURE DE DÉPART LE :
Tél : 04.74.07.23.30 Fax: 04.74.07.05.47 Shipment date and he
silo.villefranche@groupe-oxyane.fr
SIGNATURE DU TRANSPORTEUR Signature of Carrier
100
SAS au Capital de 100 000 €
Impasse Grand Jean 38940 ROYBON (Francois Tél. 00 33 4 76 36-20-66 SIGNATURE DU 78/3652PZIEUR SIGNATURE DU DESTINATAIRE Siret 19 277 610 00019re of Carrier
TVA FR 38 519 277 610
Signature of Consignee
/Reservations
• Bleu : TRANSPORTEUR Rouge: DESTINATAIRE. Vert: EXPEDITEUR⚫ Noir: SOUCHE⚫ Blue: for carrier ⚫ Red: consignee ⚫ Green: sender ⚫ Black: counter foil
"""

text_sample7 = """TICKET
:
23242
CAMION
: CW253GL
CLIENT
HUIL. DE CHAMBARAND
100 B IMP. GRANDJEAN, 38940 ROYBON, FR
N° SIRET 51927761000019 Tél :0033 (0)4.76.36.20.66.
SORTIE LE 06/04/2023 A 16:48
ENTREE LE 06/04/2023 A 16:22
No 1/050363
No
1/050360
HUILERIE
RECEPTION
HUILERIE DE CHAMBARAND SAS 100BIS IMPASSE GRANDJEAN 38940 ROYBON, FRANCE
FOURNISSEUR
: DROMOISE
DROMOISE DE CEREALES
ZA LA PIMPIE
ADRESSE
COMMUNE
PRODUITS
DURABILITE
:
26120 MONTELIER, FRANCE
GRAINE DE COLZA DURABLE
N/A
N/A
NETTOYAGE A SEC
NETTOYAGE CAMION
A
TOURS PRECEDENTS
CONTRAT N
PLOMBS No
3X CEREALES
:
2221125
ETAT BACHE CAMION
:
BON
MAUVAIS
SILOS
:3
HUMIDITE
7,2%
P1
45760 kg
P2
14360 kg
NET
31400 kg
CE
Site: 49 - IZEAUX 049
0476914232
DROMOISE DE CEREALES
Société Coopérative Agricole
17 Rue des Charmilles – BP 26 – 26120 MONTELIER – Tél : 04.75.60.15.00 SCA à capital vanable – No agrément HCCA 11300 – RC S 342283009 Romans Siren 342.283.009 – NAF 46212 – No TVA : FR 55 342 283 009
Le 06/04/2023
Page 1 sur 1
Bon de Vente
Bon n°: 2304 000 119
du 06/04/2023
C0603
HUILERIE CHAMBARAND
100 B IMPASSE GRANDJEAN
Opérateur :
PENIN MATTHIEU
BP 10
38940
ROYBON
Réf. client :
2221125
ORIGINE DE LA PRODUCTION : FRANCE
Réf. courtier : 2220925
Deux echantillons preleves sur cette expedition dont un remis au chauffeur.
CDC CW253GL 095
COLZA DURABLE 2BSVS 2022
Transporteur :
Céréale :22421
Eléments de pesée
Poids brut:
31,400T
Tare:
Cellule
490209
490209
Contrôle transport
Réponse
Propreté
Contrôle conformité
Etanchéité
Contrôle conformité
Poids net :
31,400T
Poids normes :
31,400T
N° lot
Vide cell. Désins. OGM
31,400T
2
N
N N
Poids net Poids normes
31,400
Transports précédents
COLZA
BLE
BLE
2BSvs 2BS050017-NUTS2-GES797gCO2eq/kg MS Rhône-Alpes
Contacts service clients: 04 75 60 15 61 ou 04 75 60 15 37 Signature du chauffeur:
COOPÉRATIVE DRÔMOISE DE CÉRÉALES
DRUFONTS7
167.
17:
VERTULL
"""

text_sample8 = """TICKET
: 23237
CAMION
: R 2409 BCN
CLIENT
FOURNISSEUR
ADRESSE
:
HUIL.
DE CHAMBARAND
100 B IMP. GRAND JEAN, 38940 ROYBON, FR
No SIRET 51927761000019 Tél :0033 (0)4.76.36.20.66.
SORTIE LE 06/04/2023 A 13:04
ENTREE LE 06/04/2023 A 12:07
No 1/050352
No 1/050351
: CAILA
EXPEDITION
CAILA & PARES SA
POL. IND. SECT. ZONA FRANCA, SECTOR B 08040 BARCELONA, ESPANA
HUILERIE
HUILERIE DE CHAMBARAND SAS
100 B IMPASSE GRAND JEAN
COMMUNE
: 38940 ROYBON, FRANCE
PRODUITS
DURABILITE
NETTOYAGE CAMION
D
HUILE DE COLZA BRUTE
:
N/A
N/A
: B
NETTOYAGE A L EAU
TOURS PRECEDENTS
: 2X CHOCOLAT/ GLUCOSE
CONTRAT N
PLOMBS N°
:
AVBF 01-21-03-23
: 8X 23651->23658
ETAT BACHE CAMION
:
BON
MAUVAIS
SILOS
:
1,2,3
HUMIDITE
%
P1
15600 kg
P2
40140 kg
NET
24540 kg
910€
Є
22331,40
F20741
CE
ambos inclusive y
Les parties encadrées de lignes grasses doivent être remplies par le transporteur The spaces framed with heavy lines must be filled in by the carrier
Los recuadros en línea gruesa deben ser rellenados por el portador
19+21+22
y compris et
1-15
including and
A rellenar bajo la responsabilidad del remitente A remplir sous la responsabilité de l'expéditeur
To be completed on the sender's responsability
1
Ejemplar para el remitente Copy for sender
Remilene ombreoncilio is
RB
1 Expéditer (höft adresse, pays)
exemplaire de l'expéditeur
HAMBARAND
Sender (name, address, Country) re 100.000 €
100 B. Impasse Grand Jean
38940 BOYBON (France)
Tel: 0033 4 76 36 20 66 - Fax 00 33 4 76 36 21 21
Siret 519 277 610 00019 TVA ER 32 519 277 610
Consignatario (nombre, domicilio, país) 2 Destinataire (nom, adresse, pays)
Consignee (name, address, country)
CAICA Y PARES SA Zona Franca ESPANA
Lugar de entrega de la mercancía (lugar, país)
3 Lieu prévu pour la livraison de la marchandise (lieu, pays)
Place of delivery of the goods (place, country)
Lugar y fecha de carga de la mercancía (lugar, país, fecha)
4 Lieu et date de la prise en charge de la marchandise (lieu, pays, date)
Place and date of taking over the goods (place, country, date)
Rayban le 6 104 123
neT: 23237
Documentos anexos
5 Documents annexés
Documents attached
+ Analyse
Marcas y números
6 Marques et numéros
Marks and Nos
Número de bultos
7 Nombre des colis
Number of packages
Clase de embalaje 8 Mode d'emballage Method of packing
CARTA DE PORTE INTERNACIONAL LETRRE DE VOITURE INTERNATIONALE INTERNATIONAL CONSIGNMENT NOTE
Ce Transport est soumis, no obstant toute clause contaire, à la Convention relative au contrat de transport international de marchandises par route (CMR).
Porteador (nombre, domicilio, país) 16 Transporteur (nom, adresse, pays)
Carrier (name, address, country)
2712272 122409 BCN
CMR
Este transporte queda sometido no obstante toda cláusula contraria, al Convenio sobre el Contrato de transporte Internacional de Mercancías por Carretera (CMR).
This carriage is subject, notwithstandind any clause to the contrary, to the Convention on the Contract for the International Carriage of goods by road (CMR)
FRF.RAMOS
GLOBAL LIQUID FOOD LOGISTICS
NIF B-43.352.939
C/ del mas de Plana, 3 - Pol. Alba, 43480 Vila-seca, Tarragona
Tels. 977 77 37 32 - 977 77 19 03 - Fax 977 34 10 74
Porteadores sucesivos (nombre, domicilio, país) 17 Transporteurs successifs (nom, adresse, pays)
Successive carriers (name, address, country)
MAXUT PORTES, S.L.
Ress gobservaciones del porteador 18 Reserves et observations du transporteur
Carrier's reservations and observations
c/ Minaya, 27 - pl. 1 - pta. 4 Teléfono 610 095 773
$2500 VILLARROBLEDO (Albacete)
ematt maxutportessi@maxutportessl.com
Naturaleza de la mercancía
9 Nature de la marchand se
Nature of the goods
1 Citerne d'huile de colzable
N° estadístico 10 N° statistique
Statistical number
Volumen m3
11
Peso bruto, kg Poids brut, kg Gross weight in kg
12 Cubage m3
Volume in m3
24540 Key
Classe
Class
Chiffre Number
Lettre Letter
(ADR*)
Instrucciones del remitente
13 Instructions de l'expéditeur Sender's instructions
Plomb 23657->23658
Forma de pago
14 Prescriptions d'affranchissement
Instructions as to payment for carriage Porte pagado / Franco / Carriage paid
Porte debido / Non franco / Carriage forward
21 Formalizado en
22
Etablie à
Established in
6109123 Roybon
a
le
on
HUILERIE DE CHAMBARAND
SAS au Capital de 100 000 €
NO BImpasse Grand Jean 38940 BOYRON
nce)
Tél. 00 33476362460 Fax 00 33 4 76 34 21 21
Siret 519 277 610 00019
Firma y sello del remitente
Signature et timbre del expéditeur Signature and stamp of the sender
277 610
23
20
Estipulaciones particulares
19 Conventions particulières
Special agreements
La duración de este transporte estará sujeta a las normas establecidas en cada país en el acuerdo euorpeo sobre
las
condiciones de trabajo (Acuerdo A. E. T. R.)
20
A pagar por:
To be paid by:
Remitente Senders
Precio del transporte:
Carriage charges:
Descuentos:
Deductions:
Líquido / Balance
Suplementos:
Supplem. charges:
Gastos accesorios:
Other charges:
TOTAL:
+
15 Reembolso / Remboursement / Cash on delivery
FR FRAMOS
GLOBAL LIQUID FOOD LOGISTICS
8-43.38E
C/ del mas de na, 3 Po Tels. 977 37 37 32
19 03 - Fax 977 34 10 74
60 Vila-seca, Tarragona
Firma y sellfiel transportista Signatur ut timbre du transporteur Signature and stamp of the carrier
Moneda Currency
24
Recibo de la mercancía / Marchandises recues/
Goods recetved.
Lugar
Lieu
Place
a
le
on
20
20
Firma y sello del consignatario Signature et timbre du destinataire Signature and stamp of the consignee
• En cas de marchandises dangereuses indiquer, catre la certification envetuelle, à la dernière ligne de cadre:la chiffre et le cas échéant, la lettre.
• En el caso de mercancías peligrosas, indicar, además de la certifiación reglamentaria, en la última línea del recuadro: la clase, la cifra y, en su caso, la letra. *In case of dangerous goods mention, besides the possible certification, on the last line of the column the particulars of the class, the number and the letter, if any.
Consignatario
Consignee
020905
- dd
PROP
POIDS LOURDS
Certificat de lavage international
International cleaning document
CERTIFICAT DE LAVAGE INTERIEUR ET DESINFECTION
CERTIFICATE OF INTERIOR CLEANING AND DISINFECTION
сонта
ONION
CERTIFIED
Iso 22000
N° du client / Customer No: C00680
Client/Customer : RAMOS S.L TRANSPORTES
POLIGONO INDUSTRIAL ALBA
CALLE DELMAS DE PLANA No3
ES 43480 Vila-Seca
Type de véhicule / Type of vehicle: MULTICUVES
Dernier produit transporté / Last transported product: CHOCOLAT
N° unique de certificat / Serial number: 230406058 Référence client / Customer reference:
N° CMR / No CMR :
Identification véhicules / Identification numbers
N° Tracteur / No Tractor : 2712 LFR
N° Semi / No Semi : R 2409 BCN
Nbre de compartiment(s) lavé(s) / Number of compartment(s) washed : 4
Avant-dernier produit transporté / Before last transported product: CHOCOLAT
Avant avant dernier produit transporté / Before before last transported product : GLUCOSE
Procédure de lavage / Washing procedure:
LAVAGE ALIMENTAIRE - CHOCOLAT - avec Détergent Alcallin BASO 5962
POO - Rincage aux têtes de lavage - Eau chaude (T>40°C)
E90 - PLOMBS: Du no 000055244 au no000055251
MISE EN DECHARGE DECHETS >100 L - PRIX par tranche de 100L
NETTOYAGE MANUEL SPECIFIQUE
Prestations complémentaires / Additional services :
E41 - Lavage du collecteur
* E55 - Lavage accessoires
[*] E52 - Lavage bac à égouttures
* E69 - Lavage dômes trou d'homme
* E71 - Lavage des Joints Trou d'homme
E77 - Lavage interne Haute Pression de la vanne de décompression
T01 - Contrôle Visuel après lavage
XI T02 - Contrôle Olfactif après lavage
F98 - Station de lavage agréée alimentaire
[*] E99 - Rincage Rampe de lavage
Lavage Raclette
Détail de la prestation / Detail of the service: P20 - Cycle LAVAGE RENFORCE supplémentaire
Observations / Comments
Morceau de raclette plastique présent dans la citerne et le collecteur.
Station de lavage / Cleaning station: Prop Poids lourds
Nom du laveur / Name cleaner: Julien JOLY
Date et heure de début de lavage/Time begin: 06/04/23 08:00
Date et heure de fin de lavage / Time out :
06/04/23 10:10
La station de lavage et le conducteur attestent que les moyens décrits ci-dessus ont effectivement été mis en oeuvre pour le nettoyage de l'intérieur de la citerne/de la benne. The cleaning station and the driver confirm that the above service(s) to clean the tank as been carried out.
Représentant de la station/Cleaning Station:
M ou Mme JOLY
Signature:
Ро
Conducteur / Driver : BLASCO Vladimir
Signature
PROP POIDS LOURDS
45, avenue des Frères Lumière 38300 BOURGOIN-JALLIEU
8000 € - Siret 751 211 327 00018
SAS Capital
Tel: 04 74 43 01 86 - Fax: 04 74 28 95 73 - E.mail: prop-poids-lourds@orange.fr
www.prop-poids-lourds.fr
QUALIMAT
Hailerie de Chambarand
Roybon le 6109123
Product description
Load numbers
Crude rapeseed oil, cold pressed
23237
Parameter
Specifications Clear liquid
Appearance
Water content +
impurities
<0.1%
FFA
<2%
HUILERIE DE CHAMBARAND SAS
QUÁ
雨
... 1
་
Z!j} •
766 21 21
Certificate of analysis
Test results Clear liquid
Method of analysis
<0.1%
03%
Outsourced (DIN EN ISO 663:2009-03 and Thermogravimetric)
Near Infrared (NIR)
HUILERIE DE CHAMBARAND SAS 100 bis impasse Grandjean 38940 ROYBON, France phone +33 (0)476363014
RC Grenoble B 519 277 610, N°TVA: FR38 519 277 610 SIRET 51927761000019 APE 1041 AZ
"""




def extract_fields(text):
    data = {}

    type_field = re.search(r"(EXPEDITION|RECEPTION)", text)
    if type_field:
        data["type"] = type_field.group(1)

    ticket_number = re.search(r"TICKET\s+(\d+)", text)
    if ticket_number:
        data["ticket number"] = ticket_number.group(1)

    camion_line = re.search(r"CAMION\n:?\s*([A-Z\d\s]+)(?=CLIENT)", text)
    if camion_line:
        data["immatriculation camion"] = camion_line.group(1).strip()


    if data.get("type") == "EXPEDITION":
        client = re.search(r"EXPEDITION\n:?\s*(.+?)\n", text)
        if client:
            data["client"] = client.group(1).strip()

        address = re.search(r'EXPEDITION(.+?)HUILERIE', text, re.DOTALL)
        if address:
            address_lines = address.group(1).split('\n')
            start_index = -1
            end_index = -1
            for i, line in enumerate(address_lines):
                if "EXPEDITION" in line:
                    start_index = i + 2
                if "HUILERIE" in line:
                    end_index = i - 1
            if start_index >= 0 and end_index >= 0:
                data['adresse client'] = ' '.join(address_lines[start_index:end_index+1]).strip()


        sortie = re.search(r"SORTIE LE\s+(\d{2}/\d{2}/\d{4})", text)
        if sortie:
            data["date de sortie"] = sortie.group(1)

        produit = re.search(r"(?<!HUILE\s)TOURTEAU", text)
        if produit:
            data["produit"] = "TOURTEAU"
        else:
            data["produit"] = "HUILE"

    contract_line = re.search(r"CONTRAT N", text)
    if contract_line:
        lines_after_contract = text[contract_line.end():].split('\n')
        for line in lines_after_contract:
            if "CONTRAT N" in line:
                continue
            if re.search(r'\d{6,}', line):
                data['numéro de contrat'] = line.strip(": ")
                break

    if data.get("type") == "RECEPTION":
        fournisseur_line = re.search(r"(?<=COMMUNE\n)[:\s]*(.+)\n", text)
        if fournisseur_line:
            fournisseur = fournisseur_line.group(1).strip()
            if fournisseur == "PRODUITS":
                fournisseur_line = re.search(r"(?<=FOURNISSEUR\n)[:\s]*(.+)\n", text)
                if fournisseur_line:
                    data["fournisseur"] = fournisseur_line.group(1).strip()
            else:
                data["fournisseur"] = fournisseur
        else:
            fournisseur_line = re.search(r"(?<=COMMUNE\n).*\n(.+)", text, re.DOTALL)
            if fournisseur_line:
                fournisseur = fournisseur_line.group(1).strip()
                if fournisseur == "PRODUITS":
                    fournisseur_line = re.search(r"(?<=FOURNISSEUR\n)[:\s]*(.+)\n", text)
                    if fournisseur_line:
                        data["fournisseur"] = fournisseur_line.group(1).strip()
                else:
                    data["fournisseur"] = fournisseur

        contract_number = data.get('numéro de contrat')
        if contract_number == '121008':
            data["fournisseur"] = "BERNARD"

        entree = re.search(r"ENTREE LE\s+(\d{2}/\d{2}/\d{4})", text)
        if entree:
            data["date entree"] = entree.group(1)

        produit = "GRAINE"
        data["produit"] = produit

    poids_net = re.search(r"P2\s*\d+\s*kg\s*NET\s*(\d+)", text)
    if poids_net:
        data["poids net"] = poids_net.group(1)

    return data



# Use the `extract_fields` function on the extracted text for each sample
extracted_data_sample1 = extract_fields(text_sample1)
print("Sample 1:", extracted_data_sample1)

extracted_data_sample2 = extract_fields(text_sample2)
print("Sample 2:", extracted_data_sample2)

extracted_data_sample3 = extract_fields(text_sample3)
print("Sample 3:", extracted_data_sample3)

extracted_data_sample4 = extract_fields(text_sample4)
print("Sample 4:", extracted_data_sample4)

extracted_data_sample5 = extract_fields(text_sample5)
print("Sample 5:", extracted_data_sample5)

extracted_data_sample6 = extract_fields(text_sample6)
print("Sample 6:", extracted_data_sample6)

extracted_data_sample7 = extract_fields(text_sample7)
print("Sample 7:", extracted_data_sample7)

extracted_data_sample8 = extract_fields(text_sample8)
print("Sample 8:", extracted_data_sample8)

