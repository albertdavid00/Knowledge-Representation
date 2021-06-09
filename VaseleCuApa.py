from sys import exit
import copy
import time
import math
import random
from os import listdir
from os.path import isfile, join


class NodParcurgere:
    counter = 0

    def __init__(self, info, parinte, cost=0, h=0):
        self.info = info
        self.parinte = parinte  # parintele din arborele de parcurgere
        self.g = cost  # consider cost=1 pentru o mutare
        self.h = h
        self.f = self.g + self.h
        self.idVasDinCareSeToarna = None
        self.idVasInCareSeToarna = None
        self.cantitateTurnataSiCuloare = None
        NodParcurgere.counter += 1
        self.id = NodParcurgere.counter

    def obtineDrum(self) -> list:
        l = [self]
        nod = self
        while nod.parinte is not None:
            l.insert(0, nod.parinte)
            nod = nod.parinte
        return l

    def afisDrum(self, afisCost=False, afisLung=False) -> int:  # returneaza si lungimea drumului
        l = self.obtineDrum()
        for nod in l:
            g.write(str(nod) + "\n")
            # print(str(nod))
        if afisCost:
            g.write("Cost: " + str(self.g) + "\n")
            # print("Cost: ", self.g)
        if afisCost:
            g.write("Lungime: " + str(len(l)) + "\n")
            # print("Lungime: ", len(l))
        return len(l)

    def contineInDrum(self, infoNodNou: list) -> bool:
        nodDrum = self
        while nodDrum is not None:
            if (infoNodNou == nodDrum.info):
                return True
            nodDrum = nodDrum.parinte
        return False

    def __str__(self) -> str:
        sir = "\nId nod: " + str(self.id) + "\n"
        if self.parinte != None:
            sir += "Din vasul " + str(self.idVasDinCareSeToarna) + " s-au turnat " + \
                   str(self.cantitateTurnataSiCuloare[0]) + " litri de apa de culoare " + \
                   str(self.cantitateTurnataSiCuloare[1]) + " in vasul " + \
                   str(self.idVasInCareSeToarna) + '\n'
        id = 0
        for stare in self.info:
            sir += str(id) + ": " + str(stare[0]) + " " + str(stare[1]) + \
                   " " + str(stare[2]) + "\n"
            id += 1
        return sir


class Graph:  # graful problemei

    def __init__(self, nume_fisier: str):
        def obtineInfo(path: str = nume_fisier):  # citire din fisier
            try:
                f = open(path)
                text = f.read().split('\n')
                combinatii_culori = []
                index = 0
                for line in text:
                    l = line.split()
                    if len(l) == 3:  # inca am combinatii de culori
                        combinatii_culori.append(l)
                    else:  # trecem la urmatoarea etapa, anume starea initiala
                        break
                    index += 1
                indexStareInitiala = text.index("stare_initiala")
                indexStareFinala = text.index("stare_finala")
                vase = []
                cost_culori = []
                stare_finala = []
                for i in range(index, indexStareInitiala):  # iau culoarea si costul de pe fiecare linie
                    culoare, cost = text[i].split()
                    cost_culori.append([culoare, int(cost)])  # le adaug intr-o lista
                for i in range(indexStareInitiala + 1, indexStareFinala):  # iau starea initiala
                    # print(text[i])
                    token = text[i].split()  # despart capacitatea, cantitatea de apa si culoarea daca exista
                    capacitate_maxima, cantitate_apa = token[0], token[1]
                    if len(token) == 3:  # avem culoare
                        culoare = token[2]
                        vase.append([int(capacitate_maxima), int(cantitate_apa), culoare])
                    else:  # vasul este gol
                        vase.append([int(capacitate_maxima), int(cantitate_apa), ""])
                for i in range(indexStareFinala + 1, len(text)):  # citesc liniile pentru starea finala
                    cantitate_apa, culoare = text[i].split()
                    stare_finala.append([int(cantitate_apa), culoare])
            except:
                print("Input invalid")
                exit(1)

            return combinatii_culori, cost_culori, vase, stare_finala  # combinatii, costuri, st_initiala, st_finala

        self.combinatii_culori, self.cost_culori, self.start, self.final = obtineInfo()
        print("Stare Initiala:", self.start)
        print("Stare finala:", self.final)
        # input()

    def testeaza_scop(self, nodCurent: NodParcurgere) -> bool:
        for cant, culoare in self.final:  # daca toate culorile (si cantitatile lor) din starea finala se afla
            ok = False  # in nodul curent atunci este nod scop
            for _, c, cul in nodCurent.info:
                if c == cant and cul == culoare:
                    ok = True
            if not ok:
                return False
        return True

    # vasul e de forma [cap_max, cant_apa, culoare]

    def combinare_culori(self, culoare1: str, culoare2: str) -> str:  # combin culorile conform inputului
        if culoare2 == "":  # daca culoarea 2 nu exista (vasul in care turnam este gol)
            return culoare1
        for combinatie in self.combinatii_culori:
            if (culoare1 == combinatie[0] and culoare2 == combinatie[1]) \
                    or (culoare1 == combinatie[1] and culoare2 == combinatie[0]):
                return combinatie[2]
        return "nedefinita"  # daca nu exista combinatia

    def calculeaza_cost(self, culoare1: str, culoare2: str, cantitate_turnata: int, cantitate_vas_inainte: int) -> int:
        cost1, cost2 = 1, 1  # by default dam costul culorii nedefinite. Daca gasim culoarea, atunci se modif.
        if culoare1 == "nedefinita" and culoare2 == "nedefinita":
            return cantitate_turnata + cantitate_vas_inainte
        for culoare, cost in self.cost_culori:
            if culoare == culoare1:
                cost1 = cost
            if culoare == culoare2:
                cost2 = cost
        culoare_rezultata = self.combinare_culori(culoare1, culoare2)
        if culoare_rezultata == "nedefinita":
            return cantitate_turnata * cost1 + cantitate_vas_inainte * cost2

        return cantitate_turnata * cost1  # daca ambele culori exista, iar combinatia lor exista.

    # def se_poate_compune(self, nodCurent, culoare):
    #     vase = nodCurent.info
    #     for cap, cant,

    def nod_inutil(self, infoNod: list) -> bool:
        for cant_finala, culoare_finala in self.final:  # iau vasele din starea finala
            ok = False
            for cap, cant, cul in infoNod:
                if culoare_finala == cul:
                    ok = True  # daca culoarea finala se afla in vasul curent atunci ies din for
                    break
            if ok == False:  # daca culoarea din starea finala nu se afla in starea curenta
                gasit_culoare = False
                for cul1, cul2, cul3 in self.combinatii_culori:
                    # ma uit din ce culori se poate compune daca se poate
                    if cul3 == culoare_finala:
                        gasit_culoare = True  # deci se poate compune din alte culori
                if not gasit_culoare:  # daca nu se poate obtine din alte combinatii de culori returnam True -> nod inutil
                    return True
        return False

    def FaraSolutie(self) -> bool:
        if self.nod_inutil(gr.start):
            return True
        # for cant, _ in self.final:
        #     ok = False
        #     for cap_max, c, cul in self.start:
        #         if cap_max == cant:
        #             ok = True
        #     if not ok:
        #         return True

        return False

    def genereazaSuccesori(self, nodCurent: NodParcurgere, tip_euristica: str = "euristica banala") -> list:
        listaSuccesori = []
        vase = nodCurent.info  # vasele sunt de forma (cap_max, cantitate_curenta, culoare)
        nr_vase = len(vase)
        for id in range(nr_vase):  # iau fiecare vas
            copie_interm = copy.deepcopy(vase)
            if copie_interm[id][1] == 0:  # vasul este gol
                continue
            for j in range(nr_vase):
                if id == j:
                    continue
                # aflu cantitatea care se poate turna in vasul v[j] care este minimul dintre cantitatea din v[id]
                # si cantitatea care ii lipseste lui v[j] pentru a fi plin
                cantitate_turnata = min(copie_interm[id][1], copie_interm[j][0] - copie_interm[j][1])
                if cantitate_turnata == 0:  # inseamna ca vasul j este plin deja
                    continue
                culoare1 = copie_interm[id][2]
                vase_noi = copy.deepcopy(copie_interm)  # creez o noua copie pentru noul nod
                vase_noi[id][1] -= cantitate_turnata  # scad cantitatea turnata din vas
                if vase_noi[id][1] == 0:  # cantitatea == 0
                    vase_noi[id][2] = ""  # nu mai are culoare daca e gol

                cantitate_vas_inainte = copie_interm[j][1]
                vase_noi[j][1] += cantitate_turnata  # adaug noua cantitate in vasul v[j]
                culoare2 = vase_noi[j][2]
                vase_noi[j][2] = self.combinare_culori(culoare1, culoare2)  # pun noua culoare dupa combinare in v[j]
                costTurnareApa = self.calculeaza_cost(culoare1, culoare2, cantitate_turnata, cantitate_vas_inainte)
                nod_nou = NodParcurgere(vase_noi, nodCurent, cost=nodCurent.g + costTurnareApa,
                                        h=self.calculeaza_h(infoNod=vase_noi, tip_euristica=tip_euristica))
                nod_nou.idVasDinCareSeToarna = id
                nod_nou.idVasInCareSeToarna = j
                nod_nou.cantitateTurnataSiCuloare = (cantitate_turnata, culoare1)
                if not nodCurent.contineInDrum(vase_noi):
                    if not self.nod_inutil(nod_nou.info):
                        listaSuccesori.append(nod_nou)
                    else:
                        NodParcurgere.counter -= 1  # scadem counter-ul daca nodul nu este adaugat la succesori

        return listaSuccesori

    def calculeaza_h(self, infoNod: list, tip_euristica: str = "euristica banala") -> int:
        # daca exista vasele din starea finala in starea curenta returnez 1, altfel 0
        if tip_euristica == "euristica banala":
            for cant, culoare in self.final:
                ok = False
                for _, c, cul in infoNod:
                    if c == cant and cul == culoare:
                        ok = True
                if not ok:
                    return 0
            return 1

        elif tip_euristica == "euristica admisibila 1":

            euristici = []
            for cant, col in self.final:  # iau vasele din scop
                # h = 0
                ok = False
                for cap, can, c in infoNod:  # iau vasele din nodul curent
                    if c == col:
                        ok = True
                if ok == False:  # daca culoarea din starea finala nu se afla in starea curenta
                    cost_min = []
                    for cul1, cul2, cul3 in self.combinatii_culori:  # calculez costul pentru producerea acelei culori
                        if cul3 == col:
                            for culoare, cost in self.cost_culori:
                                if cul1 == culoare:
                                    cost1 = cost
                                    cost_min.append(cost1)
                                if cul2 == culoare:
                                    cost2 = cost
                                    cost_min.append(cost2)
                    if cost_min:
                        h = min(cost_min)
                        euristici.append(h)
            if euristici:
                return min(euristici)  # iau minimul acestor costuri
            return 0

        elif tip_euristica == "euristica admisibila 2":
            euristici = []
            for cantFinala, culoareFinala in self.final:  # iau vasele din scop
                ok = False
                for capCurent, cantCurenta, culoareCurenta in infoNod:  # iau vasele din nodul curent
                    if culoareCurenta == culoareFinala:
                        ok = True
                if ok == False:  # daca culoarea din starea finala nu se afla in starea curenta
                    cost_min = []
                    culoare1 = ""
                    culoare2 = ""
                    for cul1, cul2, cul3 in self.combinatii_culori:
                        if cul3 == culoareFinala:
                            # iau culorile care compun acea culoare scop
                            culoare1 = cul1
                            culoare2 = cul2
                    # Pun in vas1 si vas2, vasele din nodul curent care compun nodul final si care au cantitatea
                    # de culoare cea mai mica
                    vas1 = []
                    vas2 = []
                    for cap, cant, cul in infoNod:
                        if cul == culoare1:
                            if vas1 == []:
                                vas1 = [cap, cant, cul]
                            else:
                                if cant < vas1[1]:
                                    vas1 = [cap, cant, cul]
                        if cul == culoare2:
                            if vas2 == []:
                                vas2 = [cap, cant, cul]
                            else:
                                if cant < vas2[1]:
                                    vas2 = [cap, cant, cul]
                    if vas1 != [] and vas2 != []:
                        # calculez in ce mod este cel mai bine sa torn apa pentru a avea un cost minim.
                        cantitate_turnata1 = min(vas1[1], vas2[0] - vas2[1])
                        cost1 = self.calculeaza_cost(vas1[2], vas2[2], cantitate_turnata1, vas2[1])
                        cantitate_turnata2 = min(vas2[1], vas1[0] - vas1[1])
                        cost2 = self.calculeaza_cost(vas2[2], vas1[1], cantitate_turnata2, vas1[1])
                        cost_min.append(cost1)
                        cost_min.append(cost2)
                    if cost_min:
                        h = min(cost_min)
                        euristici.append(h)
            if euristici:
                return min(euristici)  # iau minimul acestor costuri
            return 0

        elif tip_euristica == "euristica neadmisibila":
            euristici = []
            for cant, col in self.final:
                # h = 0
                ok = False
                for cap, can, c in infoNod:
                    if c == col:
                        ok = True
                if ok == False:
                    cost_min = []
                    for cul1, cul2, cul3 in self.combinatii_culori:
                        if cul3 == col:
                            for culoare, cost in self.cost_culori:
                                if cul1 == culoare:
                                    cost1 = cost
                                    cost_min.append(cost1)
                                if cul2 == culoare:
                                    cost2 = cost
                                    cost_min.append(cost2)
                    if cost_min:
                        h = max(cost_min)  # iau costul maxim al culorilor care compun culoarea finala
                        euristici.append(h)
            if euristici:
                return max(euristici)
            return 0

    def __repr__(self):
        sir = ""
        for (k, v) in self.__dict__.items():
            sir += "{} = {}\n".format(k, v)
        return (sir)


def uniform_cost(gr: Graph, nrSolutiiCautate: int = 1):
    global nr_max_noduri
    startTime = time.time()
    # in coada vom avea doar noduri de tip NodParcurgere (nodurile din arborele de parcurgere)
    c = [NodParcurgere(gr.start, None, 0, 0)]
    foundSolution = False
    while len(c) > 0:
        if (len(c)) > nr_max_noduri:
            nr_max_noduri = len(c)
        # print("Coada actuala: " + str([str(x) for x in c]))
        # input()
        currentTime = time.time()
        durata = round(1000 * (currentTime - startTime))
        if durata > 1000 * timeout:
            g.write("Timpul a expirat. ")
            if not foundSolution:
                g.write("Nu au fost gasite solutii.")
            break
        nodCurent = c.pop(0)

        if gr.testeaza_scop(nodCurent):
            finalTime = time.time()
            durata = round(1000 * (finalTime - startTime))
            foundSolution = True
            g.write("Solutie: \n")
            # print("Solutie: \n", end="")
            nodCurent.afisDrum(afisCost=True, afisLung=True)
            g.write("\nTimp solutie: " + str(durata) + "ms.\n")
            g.write("\n----------------\n")
            # print("\n----------------\n")
            # input()
            nrSolutiiCautate -= 1
            if nrSolutiiCautate == 0:
                return
        lSuccesori = gr.genereazaSuccesori(nodCurent)
        for s in lSuccesori:
            i = 0
            gasit_loc = False
            for i in range(len(c)):
                # ordonez dupa cost(notat cu g aici și în desenele de pe site)
                if c[i].g > s.g:
                    gasit_loc = True
                    break
            if gasit_loc:
                c.insert(i, s)
            else:
                c.append(s)


def a_star(gr: Graph, nrSolutiiCautate: int, tip_euristica: str = "euristica admisibila 1"):
    global nr_max_noduri
    startTime = time.time()
    foundSolution = False

    open = [NodParcurgere(gr.start, None, 0, gr.calculeaza_h(gr.start, tip_euristica))]
    closed = []
    while len(open) > 0:
        if (len(open) + len(closed)) > nr_max_noduri:
            nr_max_noduri = len(open) + len(closed)
        currentTime = time.time()
        durata = round(1000 * (currentTime - startTime))
        if durata > 1000 * timeout:
            g.write("Timpul a expirat. ")
            if not foundSolution:
                g.write("Nu au fost gasite solutii.")
            break

        nodCurent = open.pop(0)
        closed.append(nodCurent)  # a fost vizitat

        if gr.testeaza_scop(nodCurent):  # daca am ajuns la un nod scop
            finalTime = time.time()
            durata = round(1000 * (finalTime - startTime))
            foundSolution = True
            g.write("Solutie: \n")
            # print("Solutie: ")
            nodCurent.afisDrum(afisCost=True, afisLung=True)
            g.write("Timp solutie: " + str(durata) + "ms\n")
            g.write("\n----------------\n")
            nrSolutiiCautate -= 1
            if nrSolutiiCautate == 0:
                return
        lSuccesori = gr.genereazaSuccesori(nodCurent, tip_euristica=tip_euristica)
        # print("Lista Succesori:", lSuccesori)

        for s in lSuccesori:
            i = 0
            gasit_loc = False
            for i in range(len(open)):
                # diferenta fata de UCS e ca ordonez dupa f
                if open[i].f >= s.f:
                    gasit_loc = True
                    break
            if gasit_loc:
                open.insert(i, s)
            else:
                open.append(s)


def a_star_optimizat(gr: Graph, nrSolutiiCautate: int, tip_euristica: str):
    global nr_max_noduri
    startTime = time.time()
    foundSolution = False

    open = [NodParcurgere(gr.start, None, 0, gr.calculeaza_h(gr.start, tip_euristica))]
    closed = []

    while len(open) > 0:
        if (len(open) + len(closed)) > nr_max_noduri:
            nr_max_noduri = len(open) + len(closed)
        currentTime = time.time()
        durata = round(1000 * (currentTime - startTime))
        if durata > 1000 * timeout:
            g.write("Timpul a expirat. ")
            if not foundSolution:
                g.write("Nu au fost gasite solutii.")
            break

        nodCurent = open.pop(0)
        closed.append(nodCurent)  # a fost vizitat

        if gr.testeaza_scop(nodCurent):  # daca am ajuns la un nod scop
            finalTime = time.time()
            durata = round(1000 * (finalTime - startTime))
            foundSolution = True
            g.write("Solutie: \n")
            # print("Solutie: ")
            nodCurent.afisDrum(afisCost=True, afisLung=True)
            g.write("Timp solutie: " + str(durata) + "ms\n")
            g.write("\n----------------\n")
            nrSolutiiCautate -= 1  # scad nr de solutii
            if nrSolutiiCautate == 0:
                return
        lSuccesori = gr.genereazaSuccesori(nodCurent, tip_euristica=tip_euristica)
        # print("Lista Succesori:", lSuccesori)

        for s in lSuccesori:
            gasitOpen = False
            for elemc in open:
                if s.info == elemc.info:
                    gasitOpen = True  # se afla in open
                    # cazurile cu ponderi
                    if s.f >= elemc.f:  # nu se expandeaza fiindca are f-ul mai mare decat cel din open
                        lSuccesori.remove(s)
                        break
                    else:
                        open.remove(elemc)  # il sterg doar din open altfel
                        break
            if not gasitOpen:

                for elemc in closed:
                    if s.info == elemc.info:  # daca e in closed
                        if s.f >= elemc.f:  # nu adaug succesor
                            lSuccesori.remove(s)
                            break
                        else:
                            closed.remove(elemc)  # il sterg din coada
                            break

        for s in lSuccesori:
            i = 0
            gasit_loc = False
            for i in range(len(open)):

                if open[i].f > s.f or (open[i].f == s.f and open[i].g <= s.g):  # f-uri egale => ordonare desc dupa g
                    gasit_loc = True
                    break
            if gasit_loc:
                open.insert(i, s)
            else:
                open.append(s)

    if not foundSolution:
        g.write("Nu au fost gasite solutii")


def ida_star(gr:Graph, nrSolutiiCautate:int):
    global nr_max_noduri
    startTime = time.time()
    foundSolution = False
    nodStart = NodParcurgere(gr.start, None, 0, gr.calculeaza_h(gr.start))
    nr_noduri = 1
    limita = nodStart.f
    while True:
        if nr_max_noduri < nr_noduri:
            nr_max_noduri = nr_noduri
        currentTime = time.time()
        durata = round(1000 * (currentTime - startTime))
        if durata > 1000 * timeout:
            g.write("Timpul a expirat. ")
            if not foundSolution:
                g.write("Nu au fost gasite solutii.")
            break
        # print("Limita de pornire: ", limita)
        nrSolutiiCautate, rez = construieste_drum(gr, nodStart, limita, nrSolutiiCautate, startTime, nr_noduri)
        if rez == "gata":
            break
        if rez == float('inf'):
            g.write("\nNu exista solutii!\n")
            break
        limita = rez
        # print(">>> Limita noua: ", limita)
        # input()


def construieste_drum(gr:Graph, nodCurent:NodParcurgere, limita:int, nrSolutiiCautate:int, startTime, nr_noduri:int):
    global nr_max_noduri
    nr_noduri += 1
    if nr_max_noduri < nr_noduri:
        nr_max_noduri = nr_noduri
    # print("A ajuns la: ", nodCurent)
    if nodCurent.f > limita:
        return nrSolutiiCautate, nodCurent.f
    if gr.testeaza_scop(nodCurent) and nodCurent.f == limita:
        g.write("Solutie:\n")
        nodCurent.afisDrum(afisCost=True, afisLung=True)
        g.write("Limita: " + str(limita) + "\n")
        finalTime = time.time()
        durata = round(1000 * (finalTime - startTime))
        g.write("Timp solutie: " + str(durata) + "ms")
        g.write("\n----------------\n")
        # input()
        nrSolutiiCautate -= 1
        if nrSolutiiCautate == 0:
            return 0, "gata"
    lSuccesori = gr.genereazaSuccesori(nodCurent)
    minim = float('inf')
    for s in lSuccesori:
        nrSolutiiCautate, rez = construieste_drum(gr, s, limita, nrSolutiiCautate, startTime, nr_noduri + len(lSuccesori))
        if rez == "gata":
            return 0, "gata"

        if rez < minim:
            minim = rez

    return nrSolutiiCautate, minim


def get_euristica(id:int)->str:
    if id == 1:
        return "euristica banala"
    if id == 2:
        return "euristica admisibila 1"
    if id == 3:
        return "euristica admisibila 2"
    if id == 4:
        return "euristica neadmisibila"
    raise Exception("Euristica invalida")


if __name__ == "__main__":
    print("Introduceti calea catre folderul de intrare:")
    inputFolderPath = input()
    print("Introduceti calea catre folderul de iesire:")
    outputFolderPath = input()
    print("Introduceti numarul de solutii dorite: ")
    nrSolutii = int(input())
    print("Introduceti timpul de timeout (secunde): ")
    timeout = int(input())
    print("Introduceti euristica dorita (indexul):\n\t1.euristica banala\n\t2.euristica admisibila 1" +
          "\n\t3.euristica admisibila 2\n\t4.euristica neadmisibila")
    id_euristica = int(input())
    try:
        tip_euristica = get_euristica(id_euristica)
    except:
        print("Euristica invalida")
        exit(1)
    print("Alegeti algoritmul dorit (indexul): \n\t1.UCS\n\t2.A*\n\t3.A* optimizat\n\t4.IDA*")
    algoritm = int(input())
    # try:
    inputFiles = [f for f in listdir(inputFolderPath) if isfile(join(inputFolderPath, f))]
    outputFiles = [f for f in listdir(outputFolderPath) if isfile(join(outputFolderPath, f))]
    index = 0
    for file in inputFiles:
        NodParcurgere.counter = 0
        nr_max_noduri = 1
        inputFilePath = inputFolderPath + "\\" + file
        outputFilePath = outputFolderPath + "\\" + outputFiles[index]
        g = open(outputFilePath, "w")
        gr = Graph(inputFilePath)
        index += 1
        if gr.FaraSolutie():
            g.write("Problema nu are solutii\n")
            continue
        if algoritm == 1:  # UCS
            uniform_cost(gr, nrSolutii)
            g.write("\nNumarul maxim de noduri in memorie la un moment dat: " + str(nr_max_noduri) + "\n")
            g.write("\nNumar total de noduri calculate: \n" + str(NodParcurgere.counter) + "\n")
        elif algoritm == 2:  # A*
            a_star(gr, nrSolutii, tip_euristica)
            g.write("\nNumarul maxim de noduri in memorie la un moment dat: " + str(nr_max_noduri) + "\n")
            g.write("\nNumar total de noduri calculate: \n" + str(NodParcurgere.counter) + "\n")
        elif algoritm == 3:
            a_star_optimizat(gr, nrSolutii, tip_euristica)
            g.write("\nNumarul maxim de noduri in memorie la un moment dat: " + str(nr_max_noduri) + "\n")
            g.write("\nNumar total de noduri calculate: \n" + str(NodParcurgere.counter) + "\n")
        elif algoritm == 4:
            ida_star(gr, nrSolutii)
            g.write("\nNumarul maxim de noduri in memorie la un moment dat: " + str(nr_max_noduri) + "\n")
            g.write("\nNumar total de noduri calculate: \n" + str(NodParcurgere.counter) + "\n")
        else:
            print("Algoritm invalid")
            exit(1)
        g.close()
    exit(0)
