from sys import exit
import copy
import time
import math
import random
from os import listdir
from os.path import isfile, join

class NodParcurgere:
    def __init__(self, info, parinte, cost=0, h=0):
        self.info=info
        self.parinte=parinte #parintele din arborele de parcurgere
        self.g=cost #consider cost=1 pentru o mutare
        self.h=h
        self.f=self.g+self.h
        self.idVasDinCareSeToarna = None
        self.idVasInCareSeToarna = None
        self.cantitateTurnataSiCuloare = None
    def obtineDrum(self):
        l = [self]
        nod = self
        while nod.parinte is not None:
            l.insert(0, nod.parinte)
            nod = nod.parinte
        return l

    def afisDrum(self, afisCost=False, afisLung=False):  # returneaza si lungimea drumului
        l = self.obtineDrum()
        for nod in l:
            g.write(str(nod) + "\n")
            #print(str(nod))
        if afisCost:
            g.write("Cost: " + str(self.g) + "\n")
            #print("Cost: ", self.g)
        if afisCost:
            g.write("Lungime: " + str(len(l)) + "\n")
            #print("Lungime: ", len(l))
        return len(l)

    def contineInDrum(self, infoNodNou):
        nodDrum = self
        while nodDrum is not None:
            if (infoNodNou == nodDrum.info):
                return True
            nodDrum = nodDrum.parinte
        return False

    def __str__(self):
        sir = ""
        if self.parinte != None:
            sir += "Din vasul " + str(self.idVasDinCareSeToarna) + " s-au turnat " + \
                str(self.cantitateTurnataSiCuloare[0]) + " litri de apa de culoare " + \
                str(self.cantitateTurnataSiCuloare[1]) + " in vasul " + \
                str(self.idVasInCareSeToarna) + '.\n'
        id = 0
        for stare in self.info:
            sir += str(id) + ": " + str(stare[0]) + " " + str(stare[1]) + \
                   " " + str(stare[2]) + "\n"
            id += 1
        return sir

class Graph: #graful problemei

    def __init__(self, nume_fisier):
        def obtineInfo(path = nume_fisier):
            try:
                f = open(path)
                text = f.read().split('\n')
                combinatii_culori = []
                index = 0
                for line in text:
                    l = line.split()
                    if len(l) == 3:
                        combinatii_culori.append(l)
                    else:
                        break
                    index += 1
                indexStareInitiala = text.index("stare_initiala")
                indexStareFinala = text.index("stare_finala")
                vase = []
                cost_culori = []
                stare_finala = []
                for i in range(index, indexStareInitiala):
                    culoare, cost = text[i].split()
                    cost_culori.append([culoare, int(cost)])
                for i in range(indexStareInitiala + 1, indexStareFinala):
                    #print(text[i])
                    token = text[i].split()
                    capacitate_maxima, cantitate_apa = token[0], token[1]
                    if len(token) == 3:
                        culoare = token[2]
                        vase.append([int(capacitate_maxima), int(cantitate_apa), culoare])
                    else:  # vasul este gol
                        vase.append([int(capacitate_maxima), int(cantitate_apa), ""])
                for i in range(indexStareFinala + 1, len(text)):
                    cantitate_apa, culoare = text[i].split()
                    stare_finala.append([int(cantitate_apa), culoare])
            except:
                print("Input invalid")
                exit(1)

            return combinatii_culori, cost_culori, vase, stare_finala  # combinatii, costuri, st_initiala, st_finala

        self.combinatii_culori, self.cost_culori, self.start, self.final = obtineInfo()
        print("Stare Initiala:", self.start)
        print("Stare finala:", self.final)
        #input()

    def testeaza_scop(self, nodCurent):
        for cant, culoare in self.final:
            ok = False
            for _, c, cul in nodCurent.info:
                if c == cant and cul == culoare:
                    ok = True
            if not ok:
                return False
        return True

    # vasul e de forma [cap_max, cant_apa, culoare]

    def combinare_culori(self, culoare1, culoare2):
        if culoare2 == "":
            return culoare1
        for combinatie in self.combinatii_culori:
            if (culoare1 == combinatie[0] and culoare2 == combinatie[1]) \
                or (culoare1 == combinatie[1] and culoare2 == combinatie[0]):
                    return combinatie[2]
        return "nedefinita"

    def calculeaza_cost(self, culoare1, culoare2, cantitate_turnata, cantitate_vas_inainte):
        cost1, cost2 = 1, 1     # by default dam costul culorii nedefinite. Daca gasim culoarea, atunci se modif.
        if culoare1 == "nedefinita" and culoare2 == "nedefinita":
            return cantitate_turnata
        for culoare, cost in self.cost_culori:
            if culoare == culoare1:
                cost1 = cost
            if culoare == culoare2:
                cost2 = cost
        culoare_rezultata = self.combinare_culori(culoare1, culoare2)
        if culoare_rezultata == "nedefinita":
            return cantitate_turnata * cost1 + cantitate_vas_inainte * cost2

        return cantitate_turnata * cost1  # daca ambele culori exista, iar combinatia lor exista.



    def genereazaSuccesori(self, nodCurent, tip_euristica="euristica banala"):
        listaSuccesori = []
        vase = nodCurent.info
        nr_vase = len(vase)
        for id in range(nr_vase):
            copie_interm = copy.deepcopy(vase)
            if copie_interm[id][1] == 0:  # vasul este gol
                continue
            for j in range(nr_vase):
                if id == j:
                    continue
                cantitate_turnata = min(copie_interm[id][1], copie_interm[j][0] - copie_interm[j][1])
                if cantitate_turnata == 0:
                    continue
                culoare1 = copie_interm[id][2]
                vase_noi = copy.deepcopy(copie_interm)
                vase_noi[id][1] -= cantitate_turnata
                if vase_noi[id][1] == 0:
                    vase_noi[id][2] = ""     # nu mai are culoare daca e gol

                cantitate_vas_inainte = copie_interm[j][1]
                vase_noi[j][1] += cantitate_turnata
                culoare2 = vase_noi[j][2]
                vase_noi[j][2] = self.combinare_culori(culoare1, culoare2)
                costTurnareApa = self.calculeaza_cost(culoare1, culoare2, cantitate_turnata, cantitate_vas_inainte)
                nod_nou = NodParcurgere(vase_noi, nodCurent, cost=nodCurent.g + costTurnareApa,
                                        h=self.calculeaza_h(infoNod=vase_noi, tip_euristica=tip_euristica))
                nod_nou.idVasDinCareSeToarna = id
                nod_nou.idVasInCareSeToarna = j
                nod_nou.cantitateTurnataSiCuloare = (cantitate_turnata, culoare1)
                if not nodCurent.contineInDrum(vase_noi):
                    listaSuccesori.append(nod_nou)

        return listaSuccesori

    def calculeaza_h(self, infoNod, tip_euristica = "euristica banala"):
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
            for cant, col in self.final:
                # h = 0
                ok = False
                for cap, can, c in infoNod:
                    if c == col:
                        ok = True
                if ok == False: # daca culoarea din starea finala nu se afla in starea curenta
                    cost_min = []
                    for cul1, cul2, cul3 in self.combinatii_culori: # calculez costul pentru producerea acelei culori
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
                return min(euristici)   # iau minimul acestor costuri
            return 0

        elif tip_euristica == "euristica admisibila 2":

            euristici = []
            for cant_finala, culoare_finala in self.final:
                ok = False
                # h = 0
                for cap, cant, cul in infoNod:
                    if culoare_finala == cul:
                        ok = True
                        break
                if ok == False: # daca culoarea din starea finala nu se afla in starea curenta
                    cost_min = []
                    cost1 = 0
                    cost2 = 0
                    for cul1, cul2, cul3 in self.combinatii_culori:
                        if cul3 == culoare_finala:
                            for culoare, cost in self.cost_culori:
                                if cul1 == culoare:
                                    cost1 = cost
                                if cul2 == culoare:
                                    cost2 = cost
                            nrApC1 = 0
                            nrApC2 = 0
                            for capacitate, cantitate, culoare in infoNod:
                                if cost1 == culoare:
                                    nrApC1 += 1
                                if cost2 == culoare:
                                    nrApC2 += 1

                            cost1 = cost1 * nrApC1
                            cost2 = cost2 * nrApC2
                            cost_min.append(cost1)
                            cost_min.append(cost2)
                    if cost_min:
                        euristici.append(min(cost_min))
            if euristici:
                return min(euristici)
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
                        h = max(cost_min)
                        euristici.append(h)
            if euristici:
                return max(euristici)
            return 0

    def __repr__(self):
        sir = ""
        for (k, v) in self.__dict__.items():
            sir += "{} = {}\n".format(k, v)
        return (sir)


def uniform_cost(gr, nrSolutiiCautate=1):
    startTime = time.time()
    # in coada vom avea doar noduri de tip NodParcurgere (nodurile din arborele de parcurgere)
    c = [NodParcurgere(gr.start, None, 0, 0)]
    foundSolution = False
    while len(c) > 0:
        # print("Coada actuala: " + str([str(x) for x in c]))
        # input()
        currentTime = time.time()
        durata = round(1000 * (currentTime - startTime))
        if durata > 1000*timeout:
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
            #print("\n----------------\n")
            #input()
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


def a_star(gr, nrSolutiiCautate, tip_euristica = "euristica admisibila 1"):

    startTime = time.time()
    foundSolution = False

    open = [NodParcurgere(gr.start, None, 0, gr.calculeaza_h(gr.start, tip_euristica))]
    closed = []
    while len(open) > 0:

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
            durata = round(1000* (finalTime - startTime))
            foundSolution = True
            g.write("Solutie: \n")
            #print("Solutie: ")
            nodCurent.afisDrum(afisCost=True, afisLung=True)
            g.write("Timp solutie: " + str(durata) + "ms\n")
            g.write("\n----------------\n")
            nrSolutiiCautate -= 1
            if nrSolutiiCautate == 0:
                return
        lSuccesori = gr.genereazaSuccesori(nodCurent,tip_euristica=tip_euristica)
        #print("Lista Succesori:", lSuccesori)

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

def a_star_optimizat(gr, nrSolutiiCautate, tip_euristica):

    startTime = time.time()
    foundSolution = False

    open = [NodParcurgere(gr.start, None, 0, gr.calculeaza_h(gr.start, tip_euristica))]
    closed = []

    while len(open) > 0:

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
        lSuccesori = gr.genereazaSuccesori(nodCurent,tip_euristica=tip_euristica)
        #print("Lista Succesori:", lSuccesori)

        for s in lSuccesori:
            gasitOpen = False
            for elemc in open:
                if s.info == elemc.info:
                    gasitOpen = True # se afla in open
                    # cazurile cu ponderi
                    if s.f >= elemc.f:  # nu se expandeaza fiindca are f-ul mai mare decat cel din open
                        lSuccesori.remove(s)
                        break
                    else:
                        open.remove(elemc)  # il sterg doar din open altfel
                        break
            if not gasitOpen:

                for elemc in closed:
                    if s.info == elemc.info:    # daca e in closed
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

def ida_star(gr, nrSolutiiCautate):
    startTime = time.time()
    foundSolution = False

    nodStart = NodParcurgere(gr.start, None, 0, gr.calculeaza_h(gr.start))
    limita = nodStart.f
    while True:
        currentTime = time.time()
        durata = round(1000 * (currentTime - startTime))
        if durata > 1000 * timeout:
            g.write("Timpul a expirat. ")
            if not foundSolution:
                g.write("Nu au fost gasite solutii.")
            break
       # print("Limita de pornire: ", limita)
        nrSolutiiCautate, rez = construieste_drum(gr, nodStart, limita, nrSolutiiCautate, startTime)
        if rez == "gata":
            break
        if rez == float('inf'):
            g.write("\nNu exista solutii!\n")
            break
        limita = rez
        #print(">>> Limita noua: ", limita)
        # input()

def construieste_drum(gr, nodCurent, limita, nrSolutiiCautate, startTime):
    #print("A ajuns la: ", nodCurent)
    if nodCurent.f>limita:
        return nrSolutiiCautate, nodCurent.f
    if gr.testeaza_scop(nodCurent) and nodCurent.f==limita :
        g.write("Solutie:\n")
        nodCurent.afisDrum(afisCost=True, afisLung=True)
        g.write("Limita: " + str(limita) + "\n")
        finalTime = time.time()
        durata = round(1000 * (finalTime - startTime))
        g.write("Timp solutie: " + str(durata) + "ms")
        g.write("\n----------------\n")
        # input()
        nrSolutiiCautate-=1
        if nrSolutiiCautate==0:
            return 0,"gata"
    lSuccesori=gr.genereazaSuccesori(nodCurent)
    minim=float('inf')
    for s in lSuccesori:
        nrSolutiiCautate, rez=construieste_drum(gr, s, limita, nrSolutiiCautate, startTime)
        if rez=="gata":
            return 0,"gata"
       # print("Compara ", rez, " cu ", minim)
        if rez<minim:
            minim=rez
        #    print("Noul minim: ", minim)
    return nrSolutiiCautate, minim


def get_euristica(id):
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
    #try:
    inputFiles = [f for f in listdir(inputFolderPath) if isfile(join(inputFolderPath, f))]
    outputFiles = [f for f in listdir(outputFolderPath) if isfile(join(outputFolderPath, f))]
    index = 0
    for file in inputFiles:
        inputFilePath = inputFolderPath + "\\" + file
        outputFilePath = outputFolderPath + "\\" + outputFiles[index]
        g = open(outputFilePath, "w")
        gr = Graph(inputFilePath)
        if algoritm == 1:   # UCS
            uniform_cost(gr,nrSolutii)
        elif algoritm == 2:   # A*
            a_star(gr, nrSolutii, tip_euristica)
        elif algoritm == 3:
            a_star_optimizat(gr, nrSolutii, tip_euristica)
        elif algoritm == 4:
            ida_star(gr, nrSolutii)
        else:
            print("Algoritm invalid")
            exit(1)
        index += 1
        g.close()
    # except:
    #     print("Invalid path")
    #
    # gr = Graph(inputFilePath)
    # g = open(outputFilePath, "w")
    # # gr = Graph("Input/input1.txt")
    # # g = open("Output/outputUCS.txt")
    # print("-------------------------------------")
    # a_star_optimizat(gr, nrSolutiiCautate= 3, tip_euristica= "euristica admisibila 1")
    # # ida_star(gr, nrSolutiiCautate=nrSolutii)
    # # uniform_cost(gr, nrSolutiiCautate= 2)
    # print("Done")
    # g.close()
    # exit(1)
