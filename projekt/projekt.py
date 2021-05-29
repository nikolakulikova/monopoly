import random
import tkinter as tk
import math
import json
import time
import threading


class Hrac:
    def __init__(self, meno_hraca="", figurka="", cesta="", pocet_penazi=0, dalsi=None, pocitac=False):
        self.meno = meno_hraca
        self.figurka = figurka
        self.cesta = cesta
        self.peniaze = pocet_penazi
        self.pozemky = []
        self.odpustenie_dane = False
        self.priepustka = False
        self.karta_parking = False
        self.bol_vo_vazeni = False
        self.vo_vazeni = False
        self.next = dalsi if dalsi is not None else self
        self.pocitac = pocitac
        self.policko = 0
        self.zaciatok_tahu = False

    def kolko_mam(self, farba):
        poc = 0
        for pozemok in self.pozemky:
            if pozemok.farba == farba:
                poc += 1
        return poc

    def prechod_startom(self):
        if not self.bol_vo_vazeni:
            self.peniaze += 2000000
        self.bol_vo_vazeni = False

    def priemyselne(self):
        priem = 0
        for pozemok in self.pozemky:
            if pozemok.ma_priemyselnu():
                priem += 1
        return priem

    def cierne(self):
        cier = 0
        for pozemok in self.pozemky:
            if pozemok.ma_ciernu():
                cier += 1
        return cier

    def cisticky(self):
        cier = 0
        for pozemok in self.pozemky:
            cier += pozemok.cisticky()
        return cier

    def vymaz_cierne(self):
        for pozemok in self.pozemky:
            while pozemok.ma_ciernu():
                pozemok.zburaj("cier")

    def __len__(self):
        l = 1
        hrac = self.next
        while hrac != self:
            l += 1
            hrac = hrac.next
        return l

    def posun(self, kolko):
        self.policko += kolko
        if self.policko >= 40:
            self.prechod_startom()
            self.policko -= 40

    def uloz(self):
        res = dict()
        res["meno"] = self.meno
        res["cesta"] = self.cesta
        res["peniaze"] = self.peniaze
        res["pozemky"] = [x.nazov for x in self.pozemky]
        res["odpustenie_dane"] = self.odpustenie_dane
        res["priepustka"] = self.priepustka
        res["karta_parking"] = self.karta_parking
        res["bol_vo_vazeni"] = self.bol_vo_vazeni
        res["vo_vazeni"] = self.vo_vazeni
        # res["next"] = self.next
        res["pocitac"] = self.pocitac
        res["policko"] = self.policko
        res["zaciatok_tahu"] = self.zaciatok_tahu
        return res

    def nahraj(self, res):
        self.meno = res["meno"]
        self.cesta = res["cesta"]
        self.peniaze = res["peniaze"]
        self.odpustenie_dane = res["odpustenie_dane"]
        self.priepustka = res["priepustka"]
        self.karta_parking = res["karta_parking"]
        self.bol_vo_vazeni = res["bol_vo_vazeni"]
        self.vo_vazeni = res["vo_vazeni"]
        self.figurka = tk.PhotoImage(self.cesta)
        self.figurka = self.figurka.subsample(50, 50)
        # res["next"] = self.next
        self.pocitac = res["pocitac"]
        self.policko = res["policko"]
        self.zaciatok_tahu = res["zaciatok_tahu"]


class Pozemok:
    def __init__(self, nazov="", farba="", cena=0, cena_za_budovu=0, prenajom=0, prenajom_za_budovu=0, suradnice=None,
                 popis="", n=0):
        if suradnice is None:
            suradnice = []
        self.nazov = nazov
        self.obdlzniky = []

        self.farba = farba if farba != 0 else "light gray"
        self.cena = int(cena)
        self.cena_za_obyt = int(cena_za_budovu[0])
        self.cena_za_priemysel = int(cena_za_budovu[1])
        self.prenajom = int(prenajom)
        self.prenajom_za_budovu = int(prenajom_za_budovu)
        self.vlastnik = None
        self.suradnice = suradnice
        self.hraci = []
        self.plocha = []
        self.budovy = []
        self.popis = popis
        self.n = n

    def inside(self, x, y):
        if int(self.suradnice[0]) < x < int(self.suradnice[2]) and int(self.suradnice[1]) < y < int(self.suradnice[3]):
            return True
        return False

    def clear(self):
        self.budovy = []
        self.vlastnik = None
        for y in range(len(self.plocha)):
            for x in range(len(self.plocha[y])):
                if len(self.plocha[y][x]) == 1:
                    continue
                self.plocha[y][x][1] = None

    def cisticky(self):
        cist = 0
        for budova in self.budovy:
            if budova.typ == "cist":
                cist += 1
        return cist

    def najdi(self, sx, sy):
        x, y = 0, 0
        while True:
            je = True
            for i in range(sy):
                if y + i == len(self.plocha):
                    je = False
                    continue
                for j in range(sx):
                    if x + j == len(self.plocha[y + i]):
                        je = False
                        break
                    if len(self.plocha[y + i][x + j]) == 1:
                        je = False
                        break
                    if self.plocha[y + i][x + j][1] is not None:
                        je = False
                        break
            if je:
                return [x, y, x + sx, y + sy]
            x += 1
            if x == len(self.plocha[y]):
                x = 0
                y += 1
            if y == len(self.plocha):
                break
        x, y = 0, 0
        while True:
            je = True
            for i in range(sx):
                if y + i == len(self.plocha):
                    je = False
                    continue
                for j in range(sy):
                    if x + j == len(self.plocha[y + i]):
                        je = False
                        break
                    if len(self.plocha[y + i][x + j]) == 1:
                        je = False
                        break
                    if self.plocha[y + i][x + j][1] is not None:
                        je = False
                        break
            if je:
                return [x, y, x + sy, y + sx]
            x += 1
            if x == len(self.plocha[y]):
                x = 0
                y += 1
            if y == len(self.plocha):
                break

    def postav(self, budova):
        if self.popis != "":
            return
        if budova.nazov != "":
            nazov = budova.nazov
            if nazov == "skola":
                sur = self.najdi(2, 1)
                b = Budova(budova.typ, budova.poc, None)
                b.rodic = budova
                for i in range(sur[1], sur[3]):
                    for j in range(sur[0], sur[2]):
                        self.plocha[i][j][1] = b
                self.plocha[sur[1]][sur[0]][1] = budova
                if sur[2] - sur[0] != 2:
                    budova.rotate()
            if nazov == "vaz":
                sur = self.najdi(2, 2)
                b = Budova(budova.typ, budova.poc, None)
                b.rodic = budova
                for i in range(sur[1], sur[3]):
                    for j in range(sur[0], sur[2]):
                        self.plocha[i][j][1] = b

                self.plocha[sur[1]][sur[0]][1] = budova

            if nazov == "park":
                x, y = 0, 0
                while True:
                    if len(self.plocha[y][x]) != 1 and len(self.plocha[y][x + 1]) != 1 and len(
                            self.plocha[y + 1][x]) != 1:
                        if self.plocha[y][x][1] is None and self.plocha[y][x + 1][1] is None and self.plocha[y + 1][x][
                            1] is None:
                            break
                    x += 1
                    if x == len(self.plocha[y]) - 1:
                        x = 0
                        y += 1
                self.plocha[y][x][1] = budova
                b = Budova(budova.typ, budova.poc, None)
                b.rodic = budova
                self.plocha[y][x + 1][1] = b
                self.plocha[y + 1][x][1] = b
            if nazov == "cier":
                x, y = 0, 0
                while True:
                    if len(self.plocha[y][x]) != 1 and len(self.plocha[y][x + 1]) != 1 and len(
                            self.plocha[y + 1][x]) != 1:
                        if self.plocha[y][x][1] is None and self.plocha[y][x + 1][1] is None and self.plocha[y + 1][x][
                            1] is None:
                            break
                    x += 1
                    if x == len(self.plocha[y]) - 1:
                        x = 0
                        y += 1
                self.plocha[y][x][1] = budova
                b = Budova(budova.typ, budova.poc, None)
                b.rodic = budova
                self.plocha[y][x + 1][1] = b
                self.plocha[y + 1][x][1] = b
            if nazov == "voda":
                sur = self.najdi(1, 1)
                b = Budova(budova.typ, budova.poc, None)
                b.rodic = budova
                for i in range(sur[1], sur[3]):
                    for j in range(sur[0], sur[2]):
                        self.plocha[i][j][1] = b

                self.plocha[sur[1]][sur[0]][1] = budova
            if nazov == "cist":
                sur = self.najdi(3, 1)
                b = Budova(budova.typ, budova.poc, None)
                b.rodic = budova
                for i in range(sur[1], sur[3]):
                    for j in range(sur[0], sur[2]):
                        self.plocha[i][j][1] = b

                self.plocha[sur[1]][sur[0]][1] = budova
                if sur[2] - sur[0] != 3:
                    budova.rotate()
            if nazov == "vet":
                sur = self.najdi(1, 1)
                b = Budova(budova.typ, budova.poc, None)
                b.rodic = budova
                for i in range(sur[1], sur[3]):
                    for j in range(sur[0], sur[2]):
                        self.plocha[i][j][1] = b

                self.plocha[sur[1]][sur[0]][1] = budova
            if nazov == "sklad":
                sur = self.najdi(2, 1)
                b = Budova(budova.typ, budova.poc, None)
                b.rodic = budova
                for i in range(sur[1], sur[3]):
                    for j in range(sur[0], sur[2]):
                        self.plocha[i][j][1] = b

                self.plocha[sur[1]][sur[0]][1] = budova
                if sur[2] - sur[0] != 2:
                    budova.rotate()
            if nazov == "stad":
                sur = self.najdi(2, 2)
                b = Budova(budova.typ, budova.poc, None)
                b.rodic = budova
                for i in range(sur[1], sur[3]):
                    for j in range(sur[0], sur[2]):
                        self.plocha[i][j][1] = b

                self.plocha[sur[1]][sur[0]][1] = budova
        elif budova.poc == 2:
            sur = self.najdi(2, 1)
            b = Budova(budova.typ, budova.poc, None)
            b.rodic = budova
            for i in range(sur[1], sur[3]):
                for j in range(sur[0], sur[2]):
                    self.plocha[i][j][1] = b

            self.plocha[sur[1]][sur[0]][1] = budova
            if sur[2] - sur[0] != 2:
                budova.rotate()
        else:
            sur = self.najdi(1, 1)
            b = Budova("", budova.poc, None)
            b.rodic = budova
            for i in range(sur[1], sur[3]):
                for j in range(sur[0], sur[2]):
                    self.plocha[i][j][1] = b
            self.plocha[sur[1]][sur[0]][1] = budova

        self.budovy.append(budova)

    def zburaj(self, typ):
        to_remove = None
        ktore = ["park", "skola", "vet", "voda"] if typ == "cerv" else ["vaz", "cist", "cier", "sklad"]
        for y in range(len(self.plocha)):
            for x in range(len(self.plocha[y])):
                if len(self.plocha[y][x]) == 1:
                    continue
                if self.plocha[y][x][1] is None:
                    continue
                if self.plocha[y][x][1].typ in ktore:
                    to_remove = self.plocha[y][x][1]
                    break
            if to_remove is not None:
                break
        if to_remove is None:
            return
        for y in range(len(self.plocha)):
            for x in range(len(self.plocha[y])):
                if len(self.plocha[y][x]) == 1:
                    continue
                if self.plocha[y][x][1] is None:
                    continue
                if self.plocha[y][x][1] == to_remove or self.plocha[y][x][1].rodic == to_remove:
                    self.plocha[y][x][1] = None
        self.budovy.remove(to_remove)

    def prenajom_celkovy(self):
        if self.vlastnik is None:
            return int(self.cena)
        obyt = 0
        priem = 0
        c = False
        for budova in self.budovy:
            if budova.typ == "cierna" or budova.typ in ["vaz", "cist", "cier", "sklad"]:
                c = True
            if budova.typ == "obyt":
                obyt += self.prenajom_za_budovu * budova.poc
            if budova.typ == "priem":
                priem += self.prenajom_za_budovu * budova.poc

        r = obyt + priem if not c else priem
        return int(r) if r != 0 else int(self.prenajom)

    def ma_cervenu(self):
        poc = 0
        for budova in self.budovy:
            if budova.typ == "cervena" or budova.typ in ["skola", "voda", "vet", "park"]:
                poc += 1
        return poc

    def ma_ciernu(self):
        poc = 0
        for budova in self.budovy:
            if budova.typ == "cierna" or budova.typ in ["vaz", "cist", "cier", "sklad"]:
                poc += 1
        return poc

    def ma_priemyselnu(self):
        poc = 0
        for budova in self.budovy:
            if budova.typ == "priem":
                poc += 1
        return poc

    def kresli_hracov(self, canvas):
        for hrac in range(len(self.hraci)):
            x = int(self.suradnice[0]) + 15 if hrac % 2 == 0 else int(self.suradnice[2]) - 15
            y = int(self.suradnice[1]) + 25 if hrac // 2 == 0 else int(self.suradnice[3]) - 15

            if not self.hraci[hrac].figurka in canvas.image:
                canvas.image.append(self.hraci[hrac].figurka)
                canvas.create_image(x, y, image=self.hraci[hrac].figurka)
            canvas.coords(self.hraci[hrac].figurka, x, y)
        self.kresli_budovy(canvas)

    def kresli_budovy(self, canvas):
        for y in range(len(self.plocha)):
            for x in range(len(self.plocha[y])):
                if len(self.plocha[y][x]) == 1:
                    continue
                if self.plocha[y][x][1] is not None:
                    if self.plocha[y][x][1].image is None:
                        continue
                    if not self.plocha[y][x][1].image in canvas.image:
                        canvas.image.append(self.plocha[y][x][1].image)
                        canvas.create_image(self.plocha[y][x][0][0], self.plocha[y][x][0][1],
                                            image=self.plocha[y][x][1].image, anchor="nw")
                        canvas.update()
        return

    def nahraj_stred(self, zoznam):
        mx, my = 0, 0
        for prvok in zoznam:
            if prvok[3] > mx:
                mx = prvok[3]
            my += prvok[1] - prvok[0]
        for i in range(my):
            self.plocha.append([])
            for j in range(mx):
                self.plocha[i].append(["X"])
        for p in zoznam:
            w, h = (p[6] - p[4]) / (p[3] - p[2]), (p[7] - p[5]) / (p[1] - p[0])
            tx, ty = p[4], p[5]
            for y in range(p[1] - p[0]):
                for x in range(p[3] - p[2]):
                    self.plocha[y + p[0]][x + p[2]] = [[int(tx + x * w), int(ty + y * h)], None]

    def uloz(self):
        res = dict()
        res["nazov"] = self.nazov
        res["obdlzniky"] = self.obdlzniky
        res["farba"] = self.farba
        res["cena"] = self.cena
        res["cena_za_obyt"] = self.cena_za_obyt
        res["cena_za_priemysel"] = self.cena_za_priemysel
        res["prenajom"] = self.prenajom
        res["prenajom_za_budovu"] = self.prenajom_za_budovu
        res["vlastnik"] = self.vlastnik.meno if self.vlastnik is not None else None
        res["suradnice"] = self.suradnice
        res["hraci"] = [x.meno for x in self.hraci]
        res["budovy"] = []
        for budova in self.budovy:
            res["budovy"].append(budova.uloz())
        res["popis"] = self.popis
        res["n"] = self.n
        return res

    def nahraj(self, res):
        self.nazov = res["nazov"]
        self.obdlzniky = res["obdlzniky"]
        self.farba = res["farba"]
        self.cena = res["cena"]
        self.cena_za_obyt = res["cena_za_obyt"]
        self.cena_za_priemysel = res["cena_za_priemysel"]
        self.prenajom = res["prenajom"]
        self.prenajom_za_budovu = res["prenajom_za_budovu"]
        self.vlastnik = res["vlastnik"]
        self.suradnice = res["suradnice"]
        self.hraci = res["hraci"]
        for budova in res["budovy"]:
            b = Budova(budova["typ"], budova["poc"], budova["path"], budova["nazov"])
            self.postav(b)

        self.popis = res["popis"]
        self.n = res["n"]


class Budova:
    def __init__(self, typ, poc, image, nazov=""):
        self.typ = typ
        self.poc = int(poc)
        self.path = image
        self.image = tk.PhotoImage(file=image) if image is not None else None
        self.nazov = nazov
        self.image = self.image.subsample(50, 50) if image is not None else None
        self.rot = False
        self.rodic = None

    def rotate(self):
        self.rot = True
        self.path = self.path[:self.path.find(".")] + "_r" + self.path[self.path.find("."):]
        self.image = tk.PhotoImage(file=self.path)
        self.image = self.image.subsample(50, 50)

    def uloz(self):
        res = dict()
        res["typ"] = self.typ
        res["poc"] = self.poc
        res["path"] = self.path
        res["nazov"] = self.nazov

        return res


class Karticka:
    def __init__(self, nazov, popis):
        self.nazov = nazov
        self.popis = popis

    def vypis(self, sirka):
        s = ""
        s += ' ' * int((sirka - len(self.nazov)) / 2) + self.nazov + '\n\n'
        d = 0
        for i in self.popis.split(' '):
            if d + len(i) < sirka:
                s += i + ' '
                d += len(i) + 1
            else:
                s += "\n" + i + " "
                d = len(i) + 1
        return s


class HraciePole:
    def __init__(self):
        self.karticky = []
        self.zaciatocne_peniaze = 4000000
        self.plocha = [None] * 40
        self.nacitaj_karticky()
        self.nacitaj_plochu()
        self.poc_hracov = 0
        self.prvy = None
        self.hraci = []
        self.n = 0

    def kocka(self):
        kolko = random.randrange(1, 7)
        return kolko

    def nacitaj_karticky(self, nazov_suboru="sanca.txt"):
        with open(nazov_suboru, 'r', encoding='utf-8') as subor:
            for riadok in subor:
                r = riadok.strip().split("#")
                self.karticky.append(Karticka(r[0], r[1]))

    def nacitaj_plochu(self, nazov_suboru="pozemky.txt"):
        with open(nazov_suboru, 'r', encoding='utf-8') as subor:
            specialne = False
            for riadok in subor:
                r = riadok.strip().split(",")
                if len(r) == 1:
                    specialne = True
                    continue
                if specialne:
                    if (len(r) > 6):
                        self.plocha[int(r[-1])] = Pozemok(r[0], 0, 0, [0, 0], 0, 0, [r[2], r[3], r[4], r[5]], r[1])
                else:
                    self.plocha[int(r[-1])] = Pozemok(r[0], r[1], r[2], [r[3], r[4]], r[5], r[6],
                                                      [r[7], r[8], r[9], r[10]], n=int(r[11]))
        with open("polia.txt", 'r', encoding='utf-8') as subor:
            js = json.loads(subor.read())
            for i in js:
                self.plocha[int(i)].nahraj_stred(js[i])

    def uloz(self):
        res = dict()
        # res["karticky"] = self.karticky
        # res["zaciatocne_peniaze"] = self.zaciatocne_peniaze
        res["plocha"] = []
        for p in self.plocha:
            res["plocha"].append(p.uloz())
        res["poc_hracov"] = self.poc_hracov
        # res["prvy"] = self.prvy
        res["hraci"] = []
        for pomoc in self.hraci:
            res["hraci"].append(pomoc.uloz())
        with open("save.json", "w") as file:
            json.dump(res, file, indent=4)

    def nahraj(self):

        with open("save.json", "r") as file:
            res = json.loads(file.read())

        self.hraci = []
        for hrac in res["hraci"]:
            self.hraci.append(Hrac())
            self.hraci[-1].nahraj(hrac)

        self.poc_hracov = res["poc_hracov"]

        n = 0
        for pozemok in res["plocha"]:
            for i in range(len(pozemok["hraci"])):
                for hrac in self.hraci:
                    if hrac.meno == pozemok["hraci"][i]:
                        pozemok["hraci"][i] = hrac
            for hrac in self.hraci:
                if hrac.meno == pozemok["vlastnik"]:
                    pozemok["vlastnik"] = hrac

            self.plocha[n].nahraj(pozemok)
            n += 1
        for pozemok in self.plocha:
            if pozemok.popis != "":
                continue

            for hrac in self.hraci:
                if pozemok.vlastnik == hrac:
                    hrac.pozemky.append(pozemok)

        self.prvy = self.hraci[0]

    def pridaj_hraca(self, meno_hraca, figurka, cesta, pocet_penazi, pocitac=False):
        hrac = Hrac(meno_hraca, figurka, cesta, pocet_penazi, None, pocitac)
        self.poc_hracov += 1
        if len(self.hraci) == 0:
            self.hraci = [hrac, ]
            self.prvy = hrac
        else:
            self.hraci.append(hrac)

    def dopln_hracov(self):
        pom = self.prvy
        # self.hraci = [pom, ]
        # while pom.next != self.prvy:
        #     pom = pom.next
        #     self.hraci.append(pom)

    def next(self):
        self.n += 1
        if self.n >= len(self.hraci):
            self.n = 0
        self.prvy = self.hraci[self.n]
        self.prvy.zaciatok_tahu = True


class GUI:
    def __init__(self):
        self.kocka = True
        self.k = 6
        self.timer = None
        self.kolko = 0
        self.najviac_hrac = None
        self.najviac_suma = 0
        self.pozemok_na_drazenie = None
        self.skonci = False
        self.width = 600
        self.height = 600
        self.meno = ""
        self.win = tk.Tk()
        self.win.title("MONOPOLY")
        self.canvas = tk.Canvas(bg="royal blue", height=self.height, width=self.width)
        self.poc_h = 0
        self.poc_p = 0
        self.aukcia = False
        self.stavba = False
        self.kocka = True
        self.sanca = False
        self.canvas.pack()
        self.canvas.image = []
        self.hra = HraciePole()

        self.navod = """
                Klikáte na kocku a figúrky sa samé posúvajú o hodený počet miest.
 Ak prídete na nejaký pozemok môžete ho kúpiť ak nemá vlastníka, alebo ak ma vlastníka tak mu musíte zaplatiť prenájom. Kúpite ho stlačením tlačidla Kúpiť, ak nemáte dostatok peňazí vypíše sa hláška o nedostatku peňazí a na ťahu je ďalší hráč.
 Pokiaľ stupíte na políčko “Šanca “, musíte kliknúť na kartičku na hracej ploche a tá vám povie čo treba spraviť.
 Ak stupíte na políčko “Stavebné povolenie“ musíte si vybrať jednu z budov, ktorú chcete postaviť a aj pozemok, na ktorý má ísť. Pozemok vyberiete kliknutím na políčko na hracej ploche, nie na políčko kde sa stavajú budovy.
 Červená budova – bonusová- ochraňuje pozemok, ak ju máte na pozemku tak na tento pozemok nemôže protihráč ani vy postaviť nebezpečnú budovu.
 Čierna- nebezpečná- budova ak sa nachádza na pozemku tak pri vstupe na políčko tohto pozemku protihráč platí iba čistý nájom, nájom za obytné budovy sa nezarátava pokiaľ na pozemku nie je priemyselná budova (ak je tak sa normálne platí aj za obytné).

 Ak stupíte na políčko priemyselná daň musíte zaplatiť za všetky vaše priemyselné budovy.

 Ak stupíte na políčko väzenie(2 políčka na hracej ploche) musíte hodiť 6 aby ste sa vykúpili z neho, hádžete 3-krát alebo sa môžete vykúpiť za 500 000.

 Ak stupíte na políčko “ Bezplatné parkovanie“ dostanete kartičku na odpustenie nájmu avšak ak medzičasom niekto stupí na toto políčko tak túto kartu strácate.

 Pri stupení na váš pozemok môžete stavať budovy – treba kliknúť na tlačidlo STAVBA a náhodne sa vyberie počet blokov a môžete si vybrať či chcete obytný blok alebo priemyselnú budovu. Po vybratí sa táto budova automaticky dá na pole daného pozemku.

 Ak stupíte na políčko “Aukcia“ vyberiete si pozemok bez majiteľa a vyberiete pozemok na hracej ploche, nie na stavebnej ploche. Máte 30 sekúnd na vydraženie pozemku. Pokiaľ chcete zvýšiť navrhovanú sumu tak kliknete na kruh s cenou a potom vyberte meno hráča, ktoré vám prislúcha.
 Kartičky(pod vašim meno) vyvetlivky:
 -čísla súvisia s farbou políčka a číšlo je určitá štvrť políčka
 - V je priepustka z väzenia
 -P bezplatné parkovanie(odpustenie nájmu)
 -O odpustenie dane 
 Pri prechode štartom získate 2 milióny ak ste toto kolo neboli vo väzení.
 Ak chcete hru skončiť, stlačte X v pravom hornom rohu, môžete hru uložiť .
"""
        # hr = Hrac("ahoj", None, 56666666)
        # h = HraciePole(1, True)
        # h.plocha[1].vlastnik = hr

        # h.plocha[0].vykresli(self.canvas, hr)
        # self.kresli_hru()
        self.kresli_menu()
        # self.policko = None
        # self.test()

    def kresli_menu(self):
        self.canvas.delete("all")
        self.canvas.create_text(self.width / 2, 50, text="Monopoly", fill="GOLD", font="arial 60")
        self.canvas.create_rectangle(100, self.height / 3 + 50, self.width - 100, self.height / 3 + 125,
                                     fill="light pink")
        self.canvas.create_text(self.width / 2, self.height / 3 + 87.5, text="Nová Hra", font="arial 30")
        self.canvas.create_rectangle(100, 2 * self.height / 3 - 50, self.width - 100, 2 * self.height / 3 + 25,
                                     fill="light pink")
        self.canvas.create_text(self.width / 2, 2 * self.height / 3 - 12.5, text="Nahrať Hru", font="arial 30")
        self.canvas.bind("<ButtonPress>", self.klikaj_menu)

    def klikaj_menu(self, event):
        x, y = event.x, event.y
        if 100 < x < self.width - 100 and self.height / 3 + 50 < y < self.height / 3 + 125:
            self.nova_hra = True
            self.vyber_hracov()
        if 100 < x < self.width - 100 and self.height * 2 / 3 - 50 < y < 2 * self.height / 3 + 25:
            try:
                self.hra = HraciePole()
                self.hra.nahraj()
            except Exception:
                return
            for hrac in self.hra.hraci:
                f1 = tk.PhotoImage(file=hrac.cesta)
                f1 = f1.subsample(50, 50)
                if not hrac.pocitac:
                    self.poc_h += 1
                else:
                    self.poc_p += 1
                hrac.figurka = f1
            self.kresli_hru()

    def vyber_hracov(self):
        self.canvas.delete("all")
        self.canvas.bind("<ButtonPress>", self.klikaj_vyber_hracov)
        self.canvas.create_text(self.width / 2, 50, text="Výber Počtu Hračov", fill="GOLD", font="arial 30")

        self.canvas.create_rectangle(self.width / 4 - 20, self.height / 2 - 20, self.width / 4 + 20,
                                     self.height / 2 + 20, fill="grey")
        self.canvas.create_text(self.width / 4, self.height / 2 - 5, text="-", font="arial 50")
        self.canvas.create_rectangle(3 * self.width / 4 - 20, self.height / 2 - 20, 3 * self.width / 4 + 20,
                                     self.height / 2 + 20, fill="grey")
        self.canvas.create_text(3 * self.width / 4, self.height / 2, text="+", font="arial 50")
        self.canvas.create_text(self.width / 2, self.height / 2 - 75, text="Hráči", font="arial 25")
        self.canvas.create_text(self.width / 2, self.height / 2, text=self.poc_h, font="arial 25", tag="pocet_hracov")

        self.canvas.create_rectangle(self.width / 4 - 20, 3 * self.height / 4 - 20, self.width / 4 + 20,
                                     3 * self.height / 4 + 20, fill="grey")
        self.canvas.create_text(self.width / 4, 3 * self.height / 4 - 5, text="-", font="arial 50")
        self.canvas.create_rectangle(3 * self.width / 4 - 20, 3 * self.height / 4 - 20, 3 * self.width / 4 + 20,
                                     3 * self.height / 4 + 20, fill="grey")
        self.canvas.create_text(3 * self.width / 4, 3 * self.height / 4, text="+", font="arial 50")
        self.canvas.create_text(self.width / 2, 3 * self.height / 4 - 75, text="Počítače", font="arial 25")
        self.canvas.create_text(self.width / 2, 3 * self.height / 4, text=self.poc_p, font="arial 25",
                                tag="pocet_pocitacov")

        self.canvas.create_rectangle(0, self.height - 50, 100, self.height, fill="tomato")
        self.canvas.create_text(50, self.height - 25, text="Naspäť", font="arial 20")

        self.canvas.create_rectangle(self.width - 100, self.height - 50, self.width, self.height, fill="light green")
        self.canvas.create_text(self.width - 50, self.height - 25, text="Ďalej", font="arial 20")
        return

    def klikaj_vyber_hracov(self, event):
        x, y = event.x, event.y
        if self.width / 4 - 20 < x < self.width / 4 + 20 and self.height / 2 - 20 < y < self.height / 2 + 20:
            if self.poc_h > 0:
                self.poc_h -= 1
                self.canvas.itemconfig("pocet_hracov", text=self.poc_h)
        if 3 * self.width / 4 - 20 < x < 3 * self.width / 4 + 20 and self.height / 2 - 20 < y < self.height / 2 + 20:
            if self.poc_h + self.poc_p < 4:
                self.poc_h += 1
                self.canvas.itemconfig("pocet_hracov", text=self.poc_h)

        if self.width / 4 - 20 < x < self.width / 4 + 20 and 3 * self.height / 4 - 20 < y < 3 * self.height / 4 + 20:
            if self.poc_p > 0:
                self.poc_p -= 1
                self.canvas.itemconfig("pocet_pocitacov", text=self.poc_p)
        if 3 * self.width / 4 - 20 < x < 3 * self.width / 4 + 20 and 3 * self.height / 4 - 20 < y < 3 * self.height / 4 + 20:
            if self.poc_h + self.poc_p < 4:
                self.poc_p += 1
                self.canvas.itemconfig("pocet_pocitacov", text=self.poc_p)
        if 0 < x < 100 and self.height - 50 < y < self.height:
            self.poc_h = self.poc_p = 0
            self.kresli_menu()
        if self.width - 100 < x < self.width and self.height - 50 < y < self.height:
            if self.poc_h + self.poc_p < 2:
                return
            self.vyber_figurky()

    def vyber_figurky(self):
        self.canvas.delete("all")
        self.canvas.bind("<ButtonPress>", self.klikaj_vyber_figurky)
        self.canvas.create_text(self.width / 2, 50, text="Výber Figurky", font="arial 50", fill="gold")
        self.meno = "Hráč1" if self.poc_h > 0 else "Hráč1(Počítač)"
        self.clicked = [True] * 4
        self.canvas.create_text(self.width / 2, self.height / 3, text=self.meno, tag="kto_je_na_rade")

        figurka1 = tk.PhotoImage(file="figurky/1_p.gif")
        figurka1 = figurka1.subsample(10, 10)
        self.canvas.image = [figurka1, ]
        self.canvas.create_rectangle(self.width / 3 + 50, self.height / 2 + 50, self.width / 3 - 50,
                                     self.height / 2 - 50, fill="CornFlowerBlue", outline="CornFlowerBlue", tag="f1b")
        self.canvas.create_image(self.width / 3, self.height / 2, image=figurka1, tag="figurka1")
        figurka2 = tk.PhotoImage(file="figurky/2_p.gif")
        figurka2 = figurka2.subsample(10, 10)
        self.canvas.image.append(figurka2)
        self.canvas.create_rectangle(2 * self.width / 3 + 50, self.height / 2 + 50, 2 * self.width / 3 - 50,
                                     self.height / 2 - 50, fill="CornFlowerBlue", outline="CornFlowerBlue", tag="f2b")
        self.canvas.create_image(2 * self.width / 3, self.height / 2, image=figurka2, tag="figurka2")
        figurka3 = tk.PhotoImage(file="figurky/3_p.gif")
        figurka3 = figurka3.subsample(10, 10)
        self.canvas.image.append(figurka3)
        self.canvas.create_rectangle(self.width / 3 + 50, 3 * self.height / 4 + 50, self.width / 3 - 50,
                                     3 * self.height / 4 - 50, fill="CornFlowerBlue", outline="CornFlowerBlue",
                                     tag="f3b")
        self.canvas.create_image(self.width / 3 + 10, 3 * self.height / 4, image=figurka3, tag="figurka3")
        figurka4 = tk.PhotoImage(file="figurky/4_p.gif")
        figurka4 = figurka4.subsample(10, 10)
        self.canvas.image.append(figurka4)
        self.canvas.create_rectangle(2 * self.width / 3 + 50, 3 * self.height / 4 + 50, 2 * self.width / 3 - 50,
                                     3 * self.height / 4 - 50, fill="CornFlowerBlue", outline="CornFlowerBlue",
                                     tag="f4b")
        self.canvas.create_image(2 * self.width / 3, 3 * self.height / 4, image=figurka4, tag="figurka4")
        self.canvas.update()

    def klikaj_vyber_figurky(self, event):
        x, y = event.x, event.y
        if self.width / 3 - 50 < x < self.width / 3 + 50 and self.height / 2 - 50 < y < self.height / 2 + 50 and \
                self.clicked[0]:
            self.clicked[0] = False
            f1 = tk.PhotoImage(file="figurky/1_h.gif")
            f1 = f1.subsample(50, 50)
            if self.poc_h > 0:
                self.hra.pridaj_hraca(self.meno, f1, "figurky/1_h.gif", self.hra.zaciatocne_peniaze)
                self.poc_h -= 1
            elif self.poc_p > 0:
                self.hra.pridaj_hraca(self.meno, f1, "figurky/1_h.gif", self.hra.zaciatocne_peniaze, True)
                self.poc_p -= 1
            self.canvas.delete("figurka1")
            self.canvas.delete("f1b")
            self.meno = f"Hráč{(len(self.hra.hraci) + 1)}" if self.poc_h > 0 else f"Hráč{len(self.hra.hraci) + 1}(Počítač)"
            self.canvas.itemconfig("kto_je_na_rade", text=self.meno)
        if 2 * self.width / 3 - 50 < x < 2 * self.width / 3 + 50 and self.height / 2 - 50 < y < self.height / 2 + 50 and \
                self.clicked[1]:
            self.clicked[1] = False
            f2 = tk.PhotoImage(file="figurky/2_h.gif")
            f2 = f2.subsample(50, 50)
            if self.poc_h > 0:
                self.hra.pridaj_hraca(self.meno, f2, "figurky/2_h.gif", self.hra.zaciatocne_peniaze)
                self.poc_h -= 1
            elif self.poc_p > 0:
                self.hra.pridaj_hraca(self.meno, f2, "figurky/2_h.gif", self.hra.zaciatocne_peniaze, True)
                self.poc_p -= 1
            self.canvas.delete("figurka2")
            self.canvas.delete("f2b")
            self.meno = f"Hráč{(len(self.hra.hraci) + 1)}" if self.poc_h > 0 else f"Hráč{len(self.hra.hraci) + 1}(Počítač)"
            self.canvas.itemconfig("kto_je_na_rade", text=self.meno)
        if self.width / 3 - 50 < x < self.width / 3 + 50 and 3 * self.height / 4 - 50 < y < 3 * self.height / 4 + 50 and \
                self.clicked[2]:
            self.clicked[2] = False
            f3 = tk.PhotoImage(file="figurky/3_h.gif")
            f3 = f3.subsample(50, 50)
            if self.poc_h > 0:
                self.hra.pridaj_hraca(self.meno, f3, "figurky/3_h.gif", self.hra.zaciatocne_peniaze)
                self.poc_h -= 1
            elif self.poc_p > 0:
                self.hra.pridaj_hraca(self.meno, f3, "figurky/3_h.gif", self.hra.zaciatocne_peniaze, True)
                self.poc_p -= 1
            self.canvas.delete("figurka3")
            self.canvas.delete("f3b")
            self.meno = f"Hráč{(len(self.hra.hraci) + 1)}" if self.poc_h > 0 else f"Hráč{len(self.hra.hraci) + 1}(Počítač)"
            self.canvas.itemconfig("kto_je_na_rade", text=self.meno)
        if 2 * self.width / 3 - 50 < x < 2 * self.width / 3 + 50 and 3 * self.height / 4 - 50 < y < 3 * self.height / 4 + 50 and \
                self.clicked[3]:
            self.clicked[3] = False
            f4 = tk.PhotoImage(file="figurky/4_h.gif")
            f4 = f4.subsample(50, 50)
            if self.poc_h > 0:
                self.hra.pridaj_hraca(self.meno, f4, "figurky/4_h.gif", self.hra.zaciatocne_peniaze)
                self.poc_h -= 1
            elif self.poc_p > 0:
                self.hra.pridaj_hraca(self.meno, f4, "figurky/4_h.gif", self.hra.zaciatocne_peniaze, True)
                self.poc_p -= 1
            self.canvas.delete("figurka4")
            self.canvas.delete("f4b")
            self.meno = f"Hráč{(len(self.hra.hraci) + 1)}" if self.poc_h > 0 else f"Hráč{len(self.hra.hraci) + 1}(Počítač)"
            self.canvas.itemconfig("kto_je_na_rade", text=self.meno)
        if self.poc_h + self.poc_p == 0:
            self.canvas.delete("kto_je_na_rade")
            self.clicked = [False] * 4
            self.canvas.create_rectangle(self.width - 100, self.height - 50, self.width, self.height,
                                         fill="light green")
            self.canvas.create_text(self.width - 50, self.height - 25, text="Ďalej", font="arial 30")
            if self.width - 100 < x < self.width and self.height - 50 < y < self.height:
                for hrac in self.hra.hraci:
                    self.hra.plocha[0].hraci.append(hrac)
                    if not hrac.pocitac:
                        self.poc_h += 1
                    else:
                        self.poc_p += 1
                self.kresli_hru()

        return

    def kresli_hru(self):
        self.canvas.image = []
        self.canvas.delete("all")
        parketa = tk.PhotoImage(file="parketa.gif")
        self.canvas.image.append(parketa)
        self.canvas.create_image(self.width / 2, self.height / 2, image=parketa, tag="parketa")
        otaznik = tk.PhotoImage(file="otaznik.png")
        otaznik = otaznik.subsample(15, 15)
        self.canvas.image.append(otaznik)
        self.canvas.create_image(2 * self.width / 3 + 175, self.height - 30, image=otaznik, tag="otaznik")
        x = tk.PhotoImage(file="x.png")
        x = x.subsample(5, 5)
        self.canvas.image.append(x)
        self.canvas.create_image(2 * self.width / 3 + 175, 28, image=x, tag="x")
        doska = tk.PhotoImage(file="doska.gif")
        doska = doska.subsample(2, 2)
        self.canvas.image.append(doska)
        self.canvas.create_image(self.width / 2, self.height / 2, image=doska, tag="doska")
        sanca = tk.PhotoImage(file="sanca.gif")
        sanca = sanca.subsample(5, 5)
        self.canvas.image.append(sanca)
        self.canvas.create_image(self.width / 3 + 20, self.height / 3 + 85, image=sanca, tag="sanca")
        self.canvas.bind("<ButtonPress>", self.klik_hra)
        self.miesto_peniaze()
        self.canvas.update()

        for p in self.hra.plocha:
            p.kresli_hracov(self.canvas)
        self.canvas.update()
        self.kresli_kocku()
        self.canvas.create_rectangle(self.width / 2 + 40, self.height / 2 - 10, 2 * self.width / 3,
                                     self.height / 2 + 10, fill="royal blue", outline="navy blue", width=3,
                                     tag="stavba")
        self.canvas.create_text(self.width / 2 + 68, self.height / 2, text="STAVBA", fill="gold", tag="stavba_text")

        for hrac in self.hra.hraci:
            if hrac.peniaze < 0:
                self.prehral(hrac)
        if self.poc_h + self.poc_p == 1:
            self.kresli_koniec(self.hra.hraci[0])
            return
        self.canvas.update()
        if self.hra.prvy is None:
            return
        if self.hra.prvy.vo_vazeni:
            if self.hra.prvy.priepustka:
                self.hra.prvy.priepustka = False
                self.hra.prvy.vo_vazeni = False
            else:
                self.kocka = False
                self.vazenie()

        if self.hra.prvy.zaciatok_tahu and self.hra.prvy.cierne() != 0:
            self.hra.prvy.zaciatok_tahu = False
            self.cierne()

        if self.kocka and self.hra.prvy.pocitac:
            self.canvas.unbind("<ButtonPress>")
            self.hod_kocku()
        if self.sanca and self.hra.prvy.pocitac:
            self.sanca = False
            karticka = self.hra.karticky[random.randrange(0, len(self.hra.karticky))]
            self.vykresli_oznam(karticka)

    def kresli_koniec(self, hrac):
        self.canvas.delete("all")
        self.canvas.bind("<ButtonPress>", lambda event: self.klikaj_kokniec(event))
        # self.canvas = tk.Canvas(bg="royal blue", height=self.height, width=self.width)
        # self.canvas.create_rectangle(self.width / 2 - 150, self.height / 2 - 150, self.width / 2 + 150, self.height / 2 + 150, fill="light pink")
        text = "Vyhral : " + hrac.meno
        self.canvas.create_text(self.width / 2, self.height / 2, text=text, fill="gold", font="arial 30")
        self.canvas.create_rectangle(self.width / 2 - 100, self.height - 50, self.width / 2 + 100,
                                     self.height, fill="blue")
        self.canvas.create_text(self.width / 2, self.height - 25, text="Hlavné menu", fill="gold", font="arial 20")
        self.canvas.update()

    def klikaj_kokniec(self, event):
        x, y = event.x, event.y
        if self.width / 2 - 100 < x < self.width / 2 + 100 and self.height - 50 < y < self.height:
            self.kresli_menu()

    def miesto_peniaze(self):
        hraci_poc = len(self.hra.hraci)
        pomoc = self.hra.hraci[0]
        if hraci_poc < self.hra.poc_hracov + self.poc_p:
            self.hra.dopln_hracov()
        hraci_poc = len(self.hra.hraci)
        if hraci_poc == 2:
            self.canvas.create_rectangle(self.width / 3, 2 * self.height / 3 + 150, self.width / 3 + 200,
                                         2 * self.height / 3 + 170,
                                         fill="light green" if pomoc == self.hra.prvy else "tan")
            self.canvas.create_text(self.width / 3 + 100, 2 * self.height / 3 + 160,
                                    text=f"{pomoc.meno} {pomoc.peniaze}$")
            for i in range(len(pomoc.pozemky)):
                self.canvas.create_rectangle(i * 30, 2 * self.height / 3 + 170, i * 30 + 30,
                                             2 * self.height / 3 + 200, fill=pomoc.pozemky[i].farba)
                self.canvas.create_text(i * 30 + 15, 2 * self.height / 3 + 185, text=str(pomoc.pozemky[i].n),
                                        font="arial 15")

            # self.odpustenie_dane = False
            # self.priepustka = False
            # self.karta_parking = False
            if pomoc.priepustka:
                self.canvas.create_rectangle(70, 535, 90, 570, fill="light gray")
                self.canvas.create_text(80, 552.5, text="V", font="arial 15")
            if pomoc.karta_parking:
                self.canvas.create_rectangle(100, 535, 120, 570, fill="light gray")
                self.canvas.create_text(110, 552.5, text="P", font="arial 15")
            if pomoc.odpustenie_dane:
                self.canvas.create_rectangle(130, 535, 150, 570, fill="light gray")
                self.canvas.create_text(140, 552.5, text="O", font="arial 15")

            pomoc = self.hra.hraci[1]
            self.canvas.create_rectangle(self.width / 3, 30, self.width / 3 + 200, 50,
                                         fill="light green" if pomoc == self.hra.prvy else "tan")
            self.canvas.create_text(self.width / 3 + 100, 40, text=f"{pomoc.meno} {pomoc.peniaze}$", angle=180)
            for i in range(len(pomoc.pozemky)):
                self.canvas.create_rectangle(i * 30, 0, i * 30 + 30, 30, fill=pomoc.pozemky[i].farba)
                self.canvas.create_text(i * 30 + 15, 15, text=str(pomoc.pozemky[i].n), font="arial 15", angle=180)
            if pomoc.priepustka:
                self.canvas.create_rectangle(70, 30, 90, 65, fill="light gray")
                self.canvas.create_text(80, 47.5, text="V", font="arial 15", angle=180)
            if pomoc.karta_parking:
                self.canvas.create_rectangle(100, 30, 120, 65, fill="light gray")
                self.canvas.create_text(110, 47.5, text="P", font="arial 15", angle=180)
            if pomoc.odpustenie_dane:
                self.canvas.create_rectangle(130, 30, 150, 65, fill="light gray")
                self.canvas.create_text(140, 47.5, text="O", font="arial 15", angle=180)

        if hraci_poc == 3:
            self.canvas.create_rectangle(self.width / 3, 2 * self.height / 3 + 150, self.width / 3 + 200,
                                         2 * self.height / 3 + 170,
                                         fill="light green" if pomoc == self.hra.prvy else "tan")
            self.canvas.create_text(self.width / 3 + 100, 2 * self.height / 3 + 160,
                                    text=f"{pomoc.meno} {pomoc.peniaze}$")
            for i in range(len(pomoc.pozemky)):
                self.canvas.create_rectangle(i * 30, 2 * self.height / 3 + 170, i * 30 + 30,
                                             2 * self.height / 3 + 200, fill=pomoc.pozemky[i].farba)
                self.canvas.create_text(i * 30 + 15, 2 * self.height / 3 + 185, text=str(pomoc.pozemky[i].n),
                                        font="arial 15")
            if pomoc.priepustka:
                self.canvas.create_rectangle(70, 535, 90, 570, fill="light gray")
                self.canvas.create_text(80, 552.5, text="V", font="arial 15")
            if pomoc.karta_parking:
                self.canvas.create_rectangle(100, 535, 120, 570, fill="light gray")
                self.canvas.create_text(110, 552.5, text="P", font="arial 15")
            if pomoc.odpustenie_dane:
                self.canvas.create_rectangle(130, 535, 150, 570, fill="light gray")
                self.canvas.create_text(140, 552.5, text="O", font="arial 15")

            pomoc = self.hra.hraci[1]
            self.canvas.create_rectangle(2 * self.width / 3 + 140, self.height / 3, 2 * self.width / 3 + 160,
                                         self.height / 3 + 150, fill="light green" if pomoc == self.hra.prvy else "tan")
            self.canvas.create_text(2 * self.width / 3 + 150, self.height / 3 + 75,
                                    text=f"{pomoc.meno} {pomoc.peniaze}$", angle=90)
            for i in range(len(pomoc.pozemky)):
                self.canvas.create_rectangle(self.width - 30, self.height - i * 30 - 90, self.width,
                                             self.height - i * 30 - 60, fill=pomoc.pozemky[i].farba)
                self.canvas.create_text(self.width - 15, self.height - 75 - i * 30, text=str(pomoc.pozemky[i].n),
                                        font="arial 15", angle=90)
            if pomoc.priepustka:
                self.canvas.create_rectangle(530, 530, 565, 510, fill="light gray")
                self.canvas.create_text(547.5, 520, text="V", font="arial 15", angle=90)
            if pomoc.karta_parking:
                self.canvas.create_rectangle(530, 500, 565, 480, fill="light gray")
                self.canvas.create_text(547.5, 490, text="P", font="arial 15", angle=90)
            if pomoc.odpustenie_dane:
                self.canvas.create_rectangle(530, 470, 565, 450, fill="light gray")
                self.canvas.create_text(547.5, 460, text="O", font="arial 15", angle=90)

            pomoc = self.hra.hraci[2]
            self.canvas.create_rectangle(self.width / 3, 30, self.width / 3 + 200, 50,
                                         fill="light green" if pomoc == self.hra.prvy else "tan")
            self.canvas.create_text(self.width / 3 + 100, 40, text=f"{pomoc.meno} {pomoc.peniaze}$", angle=180)
            for i in range(len(pomoc.pozemky)):
                self.canvas.create_rectangle(i * 30, 0, i * 30 + 30, 30, fill=pomoc.pozemky[i].farba)
                self.canvas.create_text(i * 30 + 15, 15, text=str(pomoc.pozemky[i].n), font="arial 15", angle=180)

            if pomoc.priepustka:
                self.canvas.create_rectangle(70, 30, 90, 65, fill="light gray")
                self.canvas.create_text(80, 47.5, text="V", font="arial 15", angle=180)
            if pomoc.karta_parking:
                self.canvas.create_rectangle(100, 30, 120, 65, fill="light gray")
                self.canvas.create_text(110, 47.5, text="P", font="arial 15", angle=180)
            if pomoc.odpustenie_dane:
                self.canvas.create_rectangle(130, 30, 150, 65, fill="light gray")
                self.canvas.create_text(140, 47.5, text="O", font="arial 15", angle=180)

        if hraci_poc == 4:
            self.canvas.create_rectangle(self.width / 3, 2 * self.height / 3 + 150, self.width / 3 + 200,
                                         2 * self.height / 3 + 170,
                                         fill="light green" if pomoc == self.hra.prvy else "tan")
            self.canvas.create_text(self.width / 3 + 100, 2 * self.height / 3 + 160,
                                    text=f"{pomoc.meno} {pomoc.peniaze}$")
            for i in range(len(pomoc.pozemky)):
                self.canvas.create_rectangle(i * 30, 2 * self.height / 3 + 170, i * 30 + 30,
                                             2 * self.height / 3 + 200, fill=pomoc.pozemky[i].farba)
                self.canvas.create_text(i * 30 + 15, 2 * self.height / 3 + 185, text=str(pomoc.pozemky[i].n),
                                        font="arial 15")
            if pomoc.priepustka:
                self.canvas.create_rectangle(70, 535, 90, 570, fill="light gray")
                self.canvas.create_text(80, 552.5, text="V", font="arial 15")
            if pomoc.karta_parking:
                self.canvas.create_rectangle(100, 535, 120, 570, fill="light gray")
                self.canvas.create_text(110, 552.5, text="P", font="arial 15")
            if pomoc.odpustenie_dane:
                self.canvas.create_rectangle(130, 535, 150, 570, fill="light gray")
                self.canvas.create_text(140, 552.5, text="O", font="arial 15")

            pomoc = self.hra.hraci[1]
            self.canvas.create_rectangle(2 * self.width / 3 + 140, self.height / 3, 2 * self.width / 3 + 160,
                                         self.height / 3 + 150, fill="light green" if pomoc == self.hra.prvy else "tan")
            self.canvas.create_text(2 * self.width / 3 + 150, self.height / 3 + 75,
                                    text=f"{pomoc.meno} {pomoc.peniaze}$", angle=90)
            for i in range(len(pomoc.pozemky)):
                self.canvas.create_rectangle(self.width - 30, self.height - i * 30 - 90, self.width,
                                             self.height - i * 30 - 60, fill=pomoc.pozemky[i].farba)
                self.canvas.create_text(self.width - 15, self.height - 75 - i * 30, text=str(pomoc.pozemky[i].n),
                                        font="arial 15", angle=90)

            if pomoc.priepustka:
                self.canvas.create_rectangle(530, 530, 565, 510, fill="light gray")
                self.canvas.create_text(547.5, 520, text="V", font="arial 15", angle=90)
            if pomoc.karta_parking:
                self.canvas.create_rectangle(530, 500, 565, 480, fill="light gray")
                self.canvas.create_text(547.5, 490, text="P", font="arial 15", angle=90)
            if pomoc.odpustenie_dane:
                self.canvas.create_rectangle(530, 470, 565, 450, fill="light gray")
                self.canvas.create_text(547.5, 460, text="O", font="arial 15", angle=90)

            pomoc = self.hra.hraci[2]
            self.canvas.create_rectangle(self.width / 3, 30, self.width / 3 + 200, 50,
                                         fill="light green" if pomoc == self.hra.prvy else "tan")
            self.canvas.create_text(self.width / 3 + 100, 40, text=f"{pomoc.meno} {pomoc.peniaze}$", angle=180)
            for i in range(len(pomoc.pozemky)):
                self.canvas.create_rectangle(i * 30, 0, i * 30 + 30, 30, fill=pomoc.pozemky[i].farba)
                self.canvas.create_text(i * 30 + 15, 15, text=str(pomoc.pozemky[i].n), font="arial 15", angle=180)

            if pomoc.priepustka:
                self.canvas.create_rectangle(70, 30, 90, 65, fill="light gray")
                self.canvas.create_text(80, 47.5, text="V", font="arial 15", angle=180)
            if pomoc.karta_parking:
                self.canvas.create_rectangle(100, 30, 120, 65, fill="light gray")
                self.canvas.create_text(110, 47.5, text="P", font="arial 15", angle=180)
            if pomoc.odpustenie_dane:
                self.canvas.create_rectangle(130, 30, 150, 65, fill="light gray")
                self.canvas.create_text(140, 47.5, text="O", font="arial 15", angle=180)

            pomoc = self.hra.hraci[3]
            self.canvas.create_rectangle(30, self.height / 3, 50, self.height / 3 + 150,
                                         fill="light green" if pomoc == self.hra.prvy else "tan")
            self.canvas.create_text(40, self.height / 3 + 75, text=f"{pomoc.meno} {pomoc.peniaze}$", angle=270)
            for i in range(len(pomoc.pozemky)):
                self.canvas.create_rectangle(0, self.height - i * 30 - 90, 30,
                                             self.height - i * 30 - 60, fill=pomoc.pozemky[i].farba)
                self.canvas.create_text(15, self.height - 75 - i * 30, text=str(pomoc.pozemky[i].n),
                                        font="arial 15", angle=270)

            if pomoc.priepustka:
                self.canvas.create_rectangle(70, 530, 35, 510, fill="light gray")
                self.canvas.create_text(57.5, 520, text="V", font="arial 15", angle=270)
            if pomoc.karta_parking:
                self.canvas.create_rectangle(70, 500, 35, 480, fill="light gray")
                self.canvas.create_text(57.5, 490, text="P", font="arial 15", angle=270)
            if pomoc.odpustenie_dane:
                self.canvas.create_rectangle(70, 470, 35, 450, fill="light gray")
                self.canvas.create_text(57.5, 460, text="O", font="arial 15", angle=270)

    def klik_hra(self, event):
        x, y = event.x, event.y
        if self.width / 3 < x < self.width / 3 + 40 and self.height / 3 + 60 < y < self.height / 2 + 10 and self.sanca:
            self.sanca = False
            karticka = self.hra.karticky[random.randrange(0, len(self.hra.karticky))]
            self.vykresli_oznam(karticka)  # sanca
        if 435 < x < 460 and 315 < y < 340 and self.kocka:
            self.hod_kocku()  # kocka
        if self.width / 2 + 40 < x < 2 * self.width / 3 and self.height / 2 - 10 < y < self.height / 2 + 10 and self.stavba:
            self.kresli_stavba()  # stavba
        if self.width - 50 < x < self.width and 0 < y < 50:
            self.zavri()  # X
            self.canvas.bind("<ButtonPress>", self.klik_zavri)
        if self.width - 50 < x < self.width and self.height - 60 < y < self.height:  # ?
            self.kresli_navod(0)

    def kresli_otaznik(self):
        ot_obr = tk.PhotoImage(file="ot_obr.png")
        ot_obr = ot_obr.subsample(2, 2)
        self.canvas.image.append(ot_obr)
        self.canvas.create_image(self.width / 2, self.height / 2, image=ot_obr, tag="ot_obr")
        x1 = tk.PhotoImage(file="x.png")
        x1 = x1.subsample(8, 8)
        self.canvas.image.append(x1)
        self.canvas.create_image(2 * self.width / 3 + 42, self.width / 3 - 97, image=x1, tag="x1")

    def klik_otaz(self, event):
        x, y = event.x, event.y
        if 2 * self.width / 3 + 20 < x < 2 * self.width / 3 + 60 and self.height / 3 - 110 < y < self.height / 3 - 80:
            self.canvas.delete("x1", "ot_obr")
            self.canvas.bind("<ButtonPress>", self.klik_hra)

    def klik_zavri(self, event):
        x, y = event.x, event.y
        if self.width / 3 + 20 < x < self.width / 3 + 60 and self.height / 3 + 100 < y < self.height / 3 + 140:
            self.canvas.delete("all")
            self.hra.uloz()
            exit()
        elif 2 * self.width / 3 - 60 < x < 2 * self.width / 3 - 20 and self.height / 3 + 100 < y < self.height / 3 + 140:
            self.canvas.delete("all")
            exit()

    def zavri(self):
        self.canvas.create_rectangle(self.width / 3, self.height / 3, 2 * self.width / 3, self.height / 3 + 150,
                                     fill="light grey", tag="zavri")
        self.canvas.create_text(self.width / 3 + 100, self.height / 3 + 50, text="Uložiť hru?", font="arial 10",
                                tag="zavri_text")
        self.canvas.create_rectangle(self.width / 3 + 20, self.height / 3 + 100, self.width / 3 + 60,
                                     self.height / 3 + 140, fill="light green", tag="zavri_ano")
        self.canvas.create_text(self.width / 3 + 40, self.height / 3 + 120, text="ANO", font="arial 10",
                                tag="zavri_ano_text")
        self.canvas.create_rectangle(2 * self.width / 3 - 60, self.height / 3 + 100, 2 * self.width / 3 - 20,
                                     self.height / 3 + 140, fill="salmon", tag="zavri_nie")
        self.canvas.create_text(2 * self.width / 3 - 40, self.height / 3 + 120, text="NIE", font="arial 10",
                                tag="zavri_nie_text")

    def kresli_stavba(self):
        kolko = random.randrange(1, 4)
        if kolko == 1:
            text1 = "objekty/obyt_j_p.gif"
            text2 = "objekty/priem_j_p.gif"
        elif kolko == 2:
            text1 = "objekty/obyt_d_p.gif"
            text2 = "objekty/priem_d_p.gif"
        elif kolko == 3:
            text1 = "objekty/obyt_v_p.gif"
            text2 = "objekty/priem_v_p.gif"
        self.canvas.delete("stavba_text")
        self.canvas.create_text(self.width / 2 + 68, self.height / 2, text=kolko, fill="gold", tag="stavba_text")
        self.canvas.update()
        time.sleep(1)
        self.canvas.create_rectangle(200, 200, self.width - 200, self.height - 200, fill="light gray")
        if not self.hra.prvy.pocitac:
            self.canvas.create_rectangle(200, self.height - 250, self.width / 2, self.height - 200, fill="tan")
            self.canvas.create_text(self.width / 4 + 100, self.height - 225, text="Obytný")
        obytny = tk.PhotoImage(file=text1)
        obytny = obytny.subsample(18, 18)
        self.canvas.image.append(obytny)
        self.canvas.create_image(self.width / 4 + 100, self.height / 2 - 45, image=obytny, tag="obytny")

        if not self.hra.prvy.pocitac:
            self.canvas.create_rectangle(self.width / 2, self.height - 250, self.width - 200, self.height - 200,
                                     fill="cyan")
            self.canvas.create_text(3 * self.width / 4 - 100, self.height - 225, text="Priemyselný")
        prie = tk.PhotoImage(file=text2)
        prie = prie.subsample(18, 18)
        self.canvas.image.append(prie)
        self.canvas.create_image(3 * self.width / 4 - 100, self.height / 2 - 50, image=prie, tag="priem")

        self.canvas.bind("<ButtonPress>", lambda event, arg=kolko: self.klikaj_stavba(event, arg))
        self.stavba = False
        if self.hra.prvy.peniaze < self.hra.plocha[self.hra.prvy.policko].cena_za_obyt * kolko:
            self.canvas.update()
            time.sleep(0.5)
            self.skonci = True
            self.vykresli_oznam("Nedostatok peňazí na kúpu tohto množstva budov")
        if self.hra.prvy.pocitac:
            self.canvas.update()
            time.sleep(1)
            if self.hra.prvy.peniaze < self.hra.plocha[self.hra.prvy.policko].cena_za_obyt * kolko:
                self.koniec_tahu()
                return
            self.canvas.unbind("<ButtonPress>")
            if kolko == 1:
                obr1 = "objekty/obyt_j_h.gif"
                obr2 = "objekty/priem_j_h.gif"
            elif kolko == 2:
                obr1 = "objekty/obyt_d_h.gif"
                obr2 = "objekty/priem_d_h.gif"
            else:
                obr1 = "objekty/obyt_v_h.gif"
                obr2 = "objekty/priem_v_h.gif"

            if self.hra.prvy.peniaze < self.hra.plocha[self.hra.prvy.policko].cena_za_priemysel * kolko:
                budova = Budova("obyt", kolko, obr1)
                self.hra.prvy.peniaze -= self.hra.plocha[self.hra.prvy.policko].cena_za_obyt * kolko
                self.hra.plocha[self.hra.prvy.policko].postav(budova)
                self.koniec_tahu()
            else:
                if random.randrange(0, 3) == 0:
                    self.hra.prvy.peniaze -= self.hra.plocha[self.hra.prvy.policko].cena_za_priemysel * kolko
                    budova = Budova("priem", kolko, obr2)
                    self.hra.plocha[self.hra.prvy.policko].postav(budova)
                    self.koniec_tahu()
                else:
                    budova = Budova("obyt", kolko, obr1)
                    self.hra.prvy.peniaze -= self.hra.plocha[self.hra.prvy.policko].cena_za_obyt * kolko
                    self.hra.plocha[self.hra.prvy.policko].postav(budova)
                    self.koniec_tahu()

    def klikaj_stavba(self, event, kolko):
        x, y = event.x, event.y
        if kolko == 1:
            obr1 = "objekty/obyt_j_h.gif"
            obr2 = "objekty/priem_j_h.gif"
        elif kolko == 2:
            obr1 = "objekty/obyt_d_h.gif"
            obr2 = "objekty/priem_d_h.gif"
        elif kolko == 3:
            obr1 = "objekty/obyt_v_h.gif"
            obr2 = "objekty/priem_v_h.gif"
        if 200 < x < self.width / 2 and self.height - 250 < y < self.height - 200:
            budova = Budova("obyt", kolko, obr1)
            self.hra.prvy.peniaze -= self.hra.plocha[self.hra.prvy.policko].cena_za_obyt * kolko
            self.hra.plocha[self.hra.prvy.policko].postav(budova)
            self.koniec_tahu()

        elif self.width / 2 < x < self.width - 200 and self.height - 250 < y < self.height - 200:
            if self.hra.prvy.peniaze < self.hra.plocha[self.hra.prvy.policko].cena_za_obyt * kolko:
                return
            budova = Budova("priem", kolko, obr2)
            self.hra.prvy.peniaze -= self.hra.plocha[self.hra.prvy.policko].cena_za_priemysel * kolko
            self.hra.plocha[self.hra.prvy.policko].postav(budova)
            self.koniec_tahu()

    def kresli_vyber(self, o1, o2):
        text1 = f"objekty/{o1}_p.gif"
        text2 = f"objekty/{o2}_p.gif"
        nazvy = {"cier": "Tepelná elektráreň", "cist": "Čistička vôd", "voda": "Vodáreň", "obyt": "Obytný",
                 "priem": "Priemyselný", "park": "Park", "sklad": "Sklad", "skola": "Škola", "vaz": "Väzenie",
                 "vet": "Veterná elektráreň"}

        t1 = self.zarovnaj(nazvy[o1] if o1 in nazvy else o1.title(), 0, 2, 15)
        t2 = self.zarovnaj(nazvy[o2] if o2 in nazvy else o2.title(), 0, 2, 15)

        self.canvas.create_rectangle(200, 200, self.width - 200, self.height - 200, fill="light gray")
        obytny = tk.PhotoImage(file=text1)
        obytny = obytny.subsample(18, 18)
        self.canvas.image.append(obytny)
        self.canvas.create_image(self.width / 4 + 100, self.height / 2 - 45, image=obytny, tag=o1)
        if self.hra.prvy.pocitac is False:
            self.canvas.create_rectangle(200, self.height - 250, self.width / 2, self.height - 200, fill="tan")
            self.canvas.create_text(self.width / 4 + 100, self.height - 225, text=t1)

            self.canvas.create_rectangle(self.width / 2, self.height - 250, self.width - 200, self.height - 200,
                                         fill="cyan")
            self.canvas.create_text(3 * self.width / 4 - 100, self.height - 225, text=t2)
        prie = tk.PhotoImage(file=text2)
        prie = prie.subsample(18, 18)
        self.canvas.image.append(prie)
        self.canvas.create_image(3 * self.width / 4 - 100, self.height / 2 - 50, image=prie, tag=o2)
        self.canvas.update()

        self.canvas.bind("<ButtonPress>", lambda event: self.klikaj_vyber(event, [o1, o2]))
        if self.hra.prvy.pocitac:
            self.canvas.unbind("<ButtonPress>")
            time.sleep(2)
            for pozemok in self.hra.prvy.pozemky:
                if pozemok.ma_cervenu() == 0:
                    obr1 = f"objekty/{o1}_h.gif"
                    budova = Budova(o1, 0, obr1, o1)
                    pozemok.postav(budova)
                    self.koniec_tahu()
                    return
            for pozemok in self.hra.plocha:
                if pozemok.popis != "":
                    continue
                if pozemok.vlastnik is not None and pozemok.vlastnik != self.hra.prvy:
                    if pozemok.ma_cervenu() != 0:
                        continue
                    obr2 = f"objekty/{o2}_h.gif"
                    budova = Budova(o2, 0, obr2, o2)
                    pozemok.postav(budova)
                    self.koniec_tahu()
                    return
            for pozemok in self.hra.plocha:
                if pozemok.popis != "":
                    continue
                if pozemok.vlastnik != self.hra.prvy:
                    if pozemok.ma_cervenu() != 0:
                        continue
                    obr2 = f"objekty/{o2}_h.gif"
                    budova = Budova(o2, 0, obr2, o2)
                    pozemok.postav(budova)
                    self.koniec_tahu()
                    return
            for pozemok in self.hra.prvy.pozemky:
                obr1 = f"objekty/{o1}_h.gif"
                budova = Budova(o1, 0, obr1, o1)
                pozemok.postav(budova)
                self.koniec_tahu()
                return
        self.stavba = False

    def klikaj_vyber(self, event, args):
        o1, o2 = args[0], args[1]
        x, y = event.x, event.y
        obr1 = f"objekty/{o1}_h.gif"
        obr2 = f"objekty/{o2}_h.gif"
        if 200 < x < self.width / 2 and self.height - 250 < y < self.height - 200:
            budova = Budova(o1, 0, obr1, o1)
            self.kresli_hru()
            self.canvas.bind("<ButtonPress>", lambda event: self.vyber_policko(event, budova))
        elif self.width / 2 < x < self.width - 200 and self.height - 250 < y < self.height - 200:
            budova = Budova(o2, 0, obr2, o2)
            self.kresli_hru()
            self.canvas.bind("<ButtonPress>", lambda event: self.vyber_policko(event, budova))

    def vyber_policko(self, event, budova):
        x, y = event.x, event.y
        for policko in self.hra.plocha:
            if policko.popis != "":
                continue
            if policko.inside(x, y):
                if budova.typ in ["vaz", "cist", "cier", "sklad"]:
                    if policko.ma_cervenu() != 0:
                        return
                policko.postav(budova)
                self.koniec_tahu()

    def kresli_kocku(self):
        self.canvas.delete("kocka")
        kocka_obr = "kocka/" + str(self.k) + ".gif"
        kocka = tk.PhotoImage(file=kocka_obr)
        kocka = kocka.subsample(13, 13)
        self.canvas.image.append(kocka)
        self.canvas.create_image(self.width / 2 + 150, self.height / 2 + 25, image=kocka, tag="kocka")

    def hod_kocku(self):
        self.k = self.hra.kocka()
        self.hra.plocha[self.hra.prvy.policko].hraci.remove(self.hra.prvy)
        self.hra.prvy.posun(self.k)
        self.hra.plocha[self.hra.prvy.policko].hraci.append(self.hra.prvy)
        self.kocka = False
        self.kresli_hru()
        self.vykresli(self.hra.plocha[self.hra.prvy.policko])

    def vykresli(self, policko):
        self.canvas.bind("<ButtonPress>", lambda event, arg=policko: self.vykresli_klik(event, arg))
        self.canvas.create_rectangle(600 / 2 - 50, 600 / 3 - 15, 600 / 2 + 50, 600 / 3 * 2, fill=policko.farba)
        self.canvas.create_rectangle(600 / 2 - 50, 600 / 3 - 15, 600 / 2 + 50, 600 / 3 + 30, fill=policko.farba)
        text = Karticka("", policko.nazov)
        text = text.vypis(14)
        text = text[text.find("\n\n") + 1:]
        self.canvas.create_text(600 / 2, 600 / 3, text=text, font="arial 10")
        if self.hra.prvy.pocitac:
            self.canvas.unbind("<ButtonPress>")
        if policko.popis == "":
            if policko.vlastnik is None:
                text = "Cena pozemku je "
                if self.hra.prvy.pocitac is False:
                    self.canvas.create_rectangle(600 / 2 - 50, 600 / 3 * 2 - 25, 600 / 2, 600 / 3 * 2, fill="red")
                    self.canvas.create_rectangle(600 / 2, 600 / 3 * 2 - 25, 600 / 2 + 50, 600 / 3 * 2, fill="green")
                    self.canvas.create_text(600 / 2 - 25, 600 / 3 * 2 - 12.5, text="Nekúpiť")
                    self.canvas.create_text(600 / 2 + 25, 600 / 3 * 2 - 12.5, text="Kúpiť")
                text += str(policko.prenajom_celkovy()) + "$"
            elif policko.vlastnik == self.hra.prvy:
                text = f"obytný dom {policko.cena_za_obyt}$\n\npriemyselná budova {policko.cena_za_priemysel}$"
                if self.hra.prvy.pocitac is False:
                    self.canvas.create_rectangle(600 / 2 - 50, 600 / 3 * 2 - 25, 600 / 2, 600 / 3 * 2, fill="red")
                    self.canvas.create_rectangle(600 / 2, 600 / 3 * 2 - 25, 600 / 2 + 50, 600 / 3 * 2, fill="green")
                    self.canvas.create_text(600 / 2 - 25, 600 / 3 * 2 - 12.5, text="Nestavať")
                    self.canvas.create_text(600 / 2 + 25, 600 / 3 * 2 - 12.5, text="Stavať")
            else:
                if policko.vlastnik.vo_vazeni:
                    text = "Hráčovi " + policko.vlastnik.meno + " by si zaplatil " + str(
                        policko.prenajom_celkovy()) + "$ ale je vo väzení"
                elif self.hra.prvy.karta_parking:
                    text = "Hráčovi " + policko.vlastnik.meno + " by si zaplatil " + str(
                        policko.prenajom_celkovy()) + "$ ale máš kartičku bezplatné parkovanie"
                else:
                    text = "Hráčovi " + policko.vlastnik.meno + " zaplatíš " + str(policko.prenajom_celkovy()) + "$"
                if self.hra.prvy.pocitac is False:
                    self.canvas.create_rectangle(600 / 2 - 25, 600 / 3 * 2 - 25, 600 / 2 + 25, 600 / 3 * 2, fill="blue")
                    self.canvas.create_text(600 / 2, 600 / 3 * 2 - 12.5, text="Dobre")


        else:
            text = policko.popis
            if self.hra.prvy.pocitac is False:
                self.canvas.create_rectangle(600 / 2 - 25, 600 / 3 * 2 - 25, 600 / 2 + 25, 600 / 3 * 2, fill="blue")
                self.canvas.create_text(600 / 2, 600 / 3 * 2 - 12.5, text="Dobre")
        text = Karticka("", text)
        text = text.vypis(14)
        text = text[text.find("\n\n") + 1:]
        self.canvas.create_text(600 / 2, 600 / 2 - 15, text=text, font="arial 10")
        if self.hra.prvy.pocitac:
            self.canvas.unbind("<ButtonPress>")
            self.canvas.update()
            time.sleep(2)
            if policko.popis == "":
                if policko.vlastnik is None:
                    if self.hra.prvy.peniaze < policko.prenajom_celkovy():
                        self.koniec_tahu()
                    elif self.hra.prvy.kolko_mam(policko.farba) != 0:
                        policko.vlastnik = self.hra.prvy
                        self.hra.prvy.pozemky.append(policko)
                        self.hra.prvy.peniaze -= policko.prenajom_celkovy()
                        self.koniec_tahu()
                    else:
                        if random.randrange(0, 4) != 0:
                            policko.vlastnik = self.hra.prvy
                            self.hra.prvy.pozemky.append(policko)
                            self.hra.prvy.peniaze -= policko.prenajom_celkovy()
                        self.koniec_tahu()
                elif policko.vlastnik == self.hra.prvy:
                    if self.hra.prvy.peniaze < policko.cena_za_obyt:
                        self.koniec_tahu()
                        return
                    self.stavba = True
                    self.vykresli_oznam("Prosím kliknite na tlačidlo stavba.")
                    time.sleep(0.5)
                    self.kresli_hru()
                    self.kresli_stavba()
                else:
                    if policko.vlastnik.vo_vazeni:
                        self.koniec_tahu()
                    elif self.hra.prvy.karta_parking:
                        self.hra.prvy.karta_parking = False
                        self.koniec_tahu()
                    else:
                        suma = policko.prenajom_celkovy()
                        self.hra.prvy.peniaze -= suma
                        policko.vlastnik.peniaze += suma if suma < self.hra.prvy.peniaze else self.hra.prvy.peniaze
                        self.koniec_tahu()


            else:
                if policko.nazov == "Šanca":
                    self.sanca = True
                    self.kresli_hru()
                elif policko.nazov == "Priemyselná daň":
                    if self.hra.prvy.priemyselne() != 0 and self.hra.prvy.odpustenie_dane is False:
                        self.hra.prvy.peniaze -= 2000000
                    elif self.hra.prvy.priemyselne() != 0 and self.hra.prvy.odpustenie_dane:
                        self.hra.prvy.odpustenie_dane = False
                    self.koniec_tahu()
                elif policko.nazov == "Stavebné povolenie":
                    if "tepelnú" in policko.popis:
                        self.kresli_vyber("vet", "cier")
                    if "čističku" in policko.popis:
                        self.kresli_vyber("voda", "cist")
                    if "školu" in policko.popis:
                        self.kresli_vyber("skola", "vaz")
                    if "park" in policko.popis:
                        self.kresli_vyber("park", "sklad")
                elif policko.nazov == "Väzenie" or policko.nazov == "Chodťe do väzenia":
                    self.hra.plocha[self.hra.prvy.policko].hraci.remove(self.hra.prvy)
                    self.hra.plocha[10].hraci.append(self.hra.prvy)
                    self.hra.prvy.policko = 10
                    self.hra.prvy.bol_vo_vazeni = True
                    self.hra.prvy.vo_vazeni = True
                    self.koniec_tahu()
                elif policko.nazov == "Aukcia":
                    for pozemok in self.hra.plocha:
                        if pozemok.vlastnik is None and pozemok.popis == "":
                            self.canvas.unbind("<ButtonPress>")
                            pozemok = self.vyber_pozemku_dedicstvo(self.hra.prvy)
                            self.najviac_suma = 100000 if 100000 <= self.hra.prvy.peniaze else self.hra.prvy.peniaze
                            self.najviac_hrac = self.hra.prvy
                            self.vyber = False
                            self.pozemok_na_drazenie = pozemok
                            self.kresli_hru()
                            self.aukcia_kresli(self.najviac_suma)
                            self.update_time()
                            self.canvas.update()
                            return
                    self.skonci = True
                    self.vykresli_oznam("Všetky pozemky majú svojích vlastníkov")

                elif policko.nazov == "Bezplatné parkovanie":
                    for hrac in self.hra.hraci:
                        hrac.karta_parking = False
                    self.hra.prvy.karta_parking = True
                    self.koniec_tahu()
                elif policko.nazov == "Štart":
                    self.hra.prvy.prechod_startom()
                    self.koniec_tahu()

    def vykresli_klik(self, event, policko):
        x, y = event.x, event.y
        if policko.popis == "":
            if policko.vlastnik is None:
                if 600 / 2 - 50 < x < 600 / 2 and 600 / 3 * 2 - 25 < y < 600 / 3 * 2:
                    self.koniec_tahu()
                if 600 / 2 < x < 600 / 2 + 50 and 600 / 3 * 2 - 25 < y < 600 / 3 * 2:
                    if self.hra.prvy.peniaze < policko.prenajom_celkovy():
                        self.skonci = True
                        self.vykresli_oznam("Nemáte dostatok peňazí na nákup tohto pozemku")
                        return
                    policko.vlastnik = self.hra.prvy
                    self.hra.prvy.pozemky.append(policko)
                    self.hra.prvy.peniaze -= policko.prenajom_celkovy()
                    self.koniec_tahu()
            elif policko.vlastnik == self.hra.prvy:
                if 600 / 2 - 50 < x < 600 / 2 and 600 / 3 * 2 - 25 < y < 600 / 3 * 2:
                    self.koniec_tahu()
                if 600 / 2 < x < 600 / 2 + 50 and 600 / 3 * 2 - 25 < y < 600 / 3 * 2:
                    self.stavba = True
                    self.vykresli_oznam("Prosím kliknite na tlačidlo stavba.")
            else:
                if 600 / 2 - 25 < x < 600 / 2 + 25 and 600 / 3 * 2 - 25 < y < 600 / 3 * 2:
                    if policko.vlastnik.vo_vazeni:
                        self.koniec_tahu()
                        return
                    if self.hra.prvy.karta_parking:
                        self.hra.prvy.karta_parking = False
                        self.koniec_tahu()
                        return
                    suma = policko.prenajom_celkovy()
                    policko.vlastnik.peniaze += suma if suma < self.hra.prvy.peniaze else self.hra.prvy.peniaze
                    self.hra.prvy.peniaze -= suma
                    self.koniec_tahu()
                    return
                # canvas.create_text(600 / 2, 600 / 3 * 2 - 12.5, text="dobre")
                # text = "Hracovi " + policko.vlastnik.meno + " zaplatis "
                # text += str(policko.prenajom_celkovy()) + "$"

        else:
            if 600 / 2 - 25 < x < 600 / 2 + 25 and 600 / 3 * 2 - 25 < y < 600 / 3 * 2:
                if policko.nazov == "Šanca":
                    self.sanca = True
                    self.kresli_hru()
                elif policko.nazov == "Priemyselná daň":
                    if self.hra.prvy.priemyselne() != 0 and self.hra.prvy.odpustenie_dane is False:
                        self.hra.prvy.peniaze -= 2000000
                    elif self.hra.prvy.priemyselne() != 0 and self.hra.prvy.odpustenie_dane:
                        self.hra.prvy.odpustenie_dane = False
                    self.koniec_tahu()
                elif policko.nazov == "Stavebné povolenie":
                    if "tepelnú" in policko.popis:
                        self.kresli_vyber("vet", "cier")
                    if "čističku" in policko.popis:
                        self.kresli_vyber("voda", "cist")
                    if "školu" in policko.popis:
                        self.kresli_vyber("skola", "vaz")
                    if "park" in policko.popis:
                        self.kresli_vyber("park", "sklad")
                elif policko.nazov == "Väzenie" or policko.nazov == "Chodťe do väzenia":
                    self.hra.plocha[self.hra.prvy.policko].hraci.remove(self.hra.prvy)
                    self.hra.plocha[10].hraci.append(self.hra.prvy)
                    self.hra.prvy.policko = 10
                    self.hra.prvy.bol_vo_vazeni = True
                    self.hra.prvy.vo_vazeni = True
                    self.hra.next()
                    self.kocka = True
                    self.kresli_hru()
                elif policko.nazov == "Aukcia":
                    for pozemok in self.hra.plocha:
                        if pozemok.vlastnik is None and pozemok.popis == "":
                            self.najviac_hrac = self.hra.prvy
                            self.kresli_hru()
                            self.canvas.bind("<ButtonPress>", lambda event: self.vyber_policko_aukcia(event))
                            return
                    self.skonci = True
                    self.vykresli_oznam("Všetky pozemky majú svojích vlastníkov")

                elif policko.nazov == "Bezplatné parkovanie":
                    for hrac in self.hra.hraci:
                        hrac.karta_parking = False
                    self.hra.prvy.karta_parking = True
                    self.hra.next()
                    self.kocka = True
                    self.kresli_hru()
                elif policko.nazov == "Štart":
                    self.hra.prvy.prechod_startom()
                    self.hra.next()
                    self.kocka = True
                    self.kresli_hru()

    def vykresli_oznam(self, oznam):
        karticka = None
        self.canvas.create_rectangle(600 / 2 - 75, 600 / 3 - 15, 600 / 2 + 75, 600 / 3 * 2 + 20, fill="light gray")
        if type(oznam) == Karticka:
            karticka = oznam
            oznam = karticka.popis
            text = Karticka("", karticka.nazov)
            text = text.vypis(15)
            text = text[text.find("\n\n") + 1:]
            self.canvas.create_rectangle(600 / 2 - 75, 600 / 3 - 15, 600 / 2 + 75, 600 / 3 + 30, fill="light gray")
            self.canvas.create_text(600 / 2, 600 / 3, text=text, font="arial 10")
        self.canvas.bind("<ButtonPress>", lambda event, arg=karticka: self.klikaj_oznam(event, arg))
        text = Karticka("", oznam)
        text = text.vypis(20)
        text = text[text.find("\n\n") + 1:]
        self.canvas.create_text(600 / 2, 600 / 2, text=text, font="arial 10")
        if self.hra.prvy.pocitac is False:
            self.canvas.create_rectangle(600 / 2 - 25, 600 / 3 * 2 - 5, 600 / 2 + 25, 600 / 3 * 2 + 20, fill="blue")
            self.canvas.create_text(600 / 2, 600 / 3 * 2 + 7.5, text="Dobre")
        if self.hra.prvy.pocitac:
            self.canvas.unbind("<ButtonPress>")
            self.canvas.update()
            time.sleep(2)
            if karticka is not None:
                self.vykonaj_karticku(karticka)
                self.sanca = False
            else:
                if self.skonci:
                    self.skonci = False
                    self.koniec_tahu()
                else:
                    self.kresli_hru()

    def klikaj_oznam(self, event, karticka):
        x, y = event.x, event.y
        if 600 / 2 - 25 < x < 600 / 2 + 25 and 600 / 3 * 2 - 5 < y < 600 / 3 * 2 + 20:
            if karticka is not None:
                self.vykonaj_karticku(karticka)
                self.sanca = False
            else:
                if self.skonci:
                    self.skonci = False
                    self.koniec_tahu()
                self.kresli_hru()

    def vyber_pozemku_zle(self, hrac):
        res = None
        for pozemok in self.hra.plocha:
            if pozemok.popis != "":
                continue
            if pozemok.vlastnik == hrac:
                continue
            if pozemok.ma_cervenu() > 0:
                continue
            if pozemok.vlastnik is not None:
                return pozemok
            res = pozemok
        if res is None:
            m = hrac.pozemky[0]
            for pozemok in hrac.pozemky:
                if pozemok.ma_cervenu() > 0:
                    continue
                if len(pozemok.budovy) < len(m.budovy):
                    m = pozemok
            return m
        return res

    def vyber_pozemku_dobre(self, hrac):
        m = None
        s = None
        for pozemok in self.hra.plocha:
            if pozemok.popis != "":
                continue
            if pozemok.vlastnik != hrac:
                continue
            if pozemok.ma_cervenu() > 0:
                s = pozemok
                continue
            if m is None:
                m = pozemok
            elif pozemok.prenajom_celkovy() > m.prenajom_celkovy():
                m = pozemok

        if m is not None:
            return m
        if s is not None:
            return s

        for pozemok in self.hra.plocha:
            if pozemok.popis != "":
                continue
            if pozemok.vlastnik is not None:
                continue
            if m is None:
                m = pozemok
            elif pozemok.prenajom_celkovy() > m.prenajom_celkovy():
                m = pozemok

        if m is not None:
            return m

        for pozemok in self.hra.plocha:
            if pozemok.popis != "":
                continue
            if m is None:
                m = pozemok
            elif pozemok.prenajom_celkovy() < m.prenajom_celkovy():
                m = pozemok

        if m is not None:
            return m

    def vyber_pozemku_zemetrasenie(self, hrac):
        res = None
        for pozemok in self.hra.plocha:
            if pozemok.popis != "":
                continue
            if pozemok.vlastnik == hrac:
                continue
            if pozemok.ma_cervenu() == 0:
                continue
            if pozemok.vlastnik is not None:
                return pozemok
            res = pozemok
        if res is None:
            m = hrac.pozemky[0]
            for pozemok in hrac.pozemky:
                if pozemok.ma_cervenu() == 0:
                    continue
                if len(pozemok.budovy) < len(m.budovy):
                    m = pozemok
            return m
        return res

    def vyber_pozemku_kradez(self, hrac):
        m = None
        for pozemok in self.hra.plocha:
            if pozemok.popis != "":
                continue
            if pozemok.vlastnik == hrac:
                continue
            if pozemok.vlastnik is None:
                continue
            if hrac.kolko_mam(pozemok.farba) != 0:
                return pozemok
            if m is None:
                m = pozemok
            elif pozemok.prenajom_celkovy() > m.prenajom_celkovy():
                m = pozemok
        return m

    def vyber_pozemku_dedicstvo(self, hrac):
        m = None
        for pozemok in self.hra.plocha:
            if pozemok.popis != "":
                continue
            if pozemok.vlastnik is not None:
                continue
            if hrac.kolko_mam(pozemok.farba) != 0:
                return pozemok
            if m is None:
                m = pozemok
            elif pozemok.prenajom_celkovy() > m.prenajom_celkovy():
                m = pozemok
        return m

    def vyber_pozemku_zabavenie(self, hrac):
        m = None
        for pozemok in hrac.pozemky:
            if m is None:
                m = pozemok
            elif pozemok.prenajom_celkovy() < m.prenajom_celkovy():
                m = pozemok
        return m

    def vykonaj_karticku(self, karticka):
        if karticka.nazov == "ČISTIČKA ODPADOV":
            obr1 = f"objekty/cist_h.gif"
            budova = Budova("cist", 0, obr1, "cist")
            self.kresli_hru()
            self.canvas.bind("<ButtonPress>", lambda event: self.vyber_policko(event, budova))
            if self.hra.prvy.pocitac:
                self.canvas.unbind("<ButtonPress>")
                pozemok = self.vyber_pozemku_zle(self.hra.prvy)
                pozemok.postav(budova)
                self.koniec_tahu()


        elif karticka.nazov == "MÝTNE":
            self.hra.prvy.peniaze -= 500000
            self.hra.plocha[self.hra.prvy.policko].hraci.remove(self.hra.prvy)
            self.hra.plocha[20].hraci.append(self.hra.prvy)
            self.hra.prvy.policko = 20
            self.kocka = True
            self.hra.next()
            self.kresli_hru()

        elif karticka.nazov == "PREPLNENÉ VÄZENIE":
            obr1 = f"objekty/vaz_h.gif"
            budova = Budova("vaz", 0, obr1, "vaz")
            self.kresli_hru()
            self.canvas.bind("<ButtonPress>", lambda event: self.vyber_policko(event, budova))
            if self.hra.prvy.pocitac:
                self.canvas.unbind("<ButtonPress>")
                pozemok = self.vyber_pozemku_zle(self.hra.prvy)
                pozemok.postav(budova)
                self.koniec_tahu()

        elif karticka.nazov == "ZEMETRASENIE!":
            self.kresli_hru()
            for pozemok in self.hra.plocha:
                if pozemok.popis == "" and pozemok.ma_cervenu() > 0:
                    self.canvas.bind("<ButtonPress>", lambda event: self.zemetrasenie_klik(event))
                    if self.hra.prvy.pocitac:
                        self.canvas.unbind("<ButtonPress>")
                        pozemok = self.vyber_pozemku_zemetrasenie(self.hra.prvy)
                        pozemok.zburaj("cerv")
                        self.koniec_tahu()
                    return
            self.skonci = True
            self.vykresli_oznam("Žiaden pozemok nemá červenú budovu, ktorú by ste mohli zničiť")



        elif karticka.nazov == "JEDNODUCHÝ ZÁROBOK":
            self.hra.prvy.peniaze += 1000000
            self.hra.prvy.next.peniaze -= 1000000
            self.kocka = True
            self.hra.next()
            self.kresli_hru()

        elif karticka.nazov == "SPREJERSKÁ POHROMA":
            self.hra.prvy.peniaze -= len(self.hra.prvy.pozemky) * 50000
            self.kocka = True
            self.hra.next()
            self.kresli_hru()

        elif karticka.nazov == "KRÁDEŽ":
            self.kresli_hru()
            for pozemok in self.hra.plocha:
                if pozemok.popis == "" and pozemok.vlastnik != self.hra.prvy and pozemok.vlastnik is not None:
                    self.canvas.bind("<ButtonPress>", lambda event: self.kradez_klik(event))
                    if self.hra.prvy.pocitac:
                        self.canvas.unbind("<ButtonPress>")
                        pozemok = self.vyber_pozemku_kradez(self.hra.prvy)
                        pozemok.vlastnik.pozemky.remove(pozemok)
                        self.hra.prvy.pozemky.append(pozemok)
                        pozemok.vlastnik = self.hra.prvy
                        self.koniec_tahu()
                    return
            self.skonci = True
            self.vykresli_oznam("Žiaden hráč nemá pozemok, ktorý by ste mohli ukradnúť")


        elif karticka.nazov == "CHOĎTE DO DRAHOKAMENÍC":
            self.hra.plocha[self.hra.prvy.policko].hraci.remove(self.hra.prvy)
            self.hra.plocha[39].hraci.append(self.hra.prvy)
            self.hra.prvy.policko = 39
            self.kocka = True
            self.hra.next()
            self.kresli_hru()

        elif karticka.nazov == "CHOĎTE DO PROSTRIEDKOVA":
            if self.hra.prvy.policko > 24:
                self.hra.prvy.peniaze += 2000000
            self.hra.plocha[self.hra.prvy.policko].hraci.remove(self.hra.prvy)
            self.hra.plocha[24].hraci.append(self.hra.prvy)
            self.hra.prvy.policko = 24
            self.kocka = True
            self.hra.next()
            self.kresli_hru()

        elif karticka.nazov == "DEDIČSTVO":
            self.kresli_hru()
            if self.hra.prvy.peniaze < 500000:
                self.skonci = True
                self.vykresli_oznam("Nemáte dostatok peňazí")
                return
            for pozemok in self.hra.plocha:
                if pozemok.vlastnik is None and pozemok.popis == "":
                    self.canvas.bind("<ButtonPress>", lambda event: self.dedicstvo_klik(event))
                    if self.hra.prvy.pocitac:
                        self.canvas.unbind("<ButtonPress>")
                        pozemok = self.vyber_pozemku_dedicstvo(self.hra.prvy)
                        self.hra.prvy.pozemky.append(pozemok)
                        pozemok.vlastnik = self.hra.prvy
                        self.koniec_tahu()
                    return
            self.skonci = True
            self.vykresli_oznam("Všetky pozemky majú svojích vlastníkov")


        elif karticka.nazov == "TOXICKÝ ODPAD":
            if self.hra.prvy.cisticky() == 0:
                self.hra.plocha[self.hra.prvy.policko].hraci.remove(self.hra.prvy)
                self.hra.prvy.policko = 10
                self.hra.plocha[10].hraci.append(self.hra.prvy)
                self.hra.prvy.vo_vazeni = True
                self.hra.prvy.bol_vo_vazeni = True
            else:
                self.hra.prvy.peniaze -= self.hra.prvy.cisticky() * 1000000
            self.koniec_tahu()

        elif karticka.nazov == "PREJDITE NA ŠTART":
            self.hra.prvy.peniaze += 2000000
            self.hra.plocha[self.hra.prvy.policko].hraci.remove(self.hra.prvy)
            self.hra.plocha[0].hraci.append(self.hra.prvy)
            self.hra.prvy.policko = 0
            self.koniec_tahu()

        elif karticka.nazov == "VRAŤTE SA O 3 POLÍČKA SPÄŤ":
            self.hra.plocha[self.hra.prvy.policko].hraci.remove(self.hra.prvy)
            self.hra.plocha[self.hra.prvy.policko - 3].hraci.append(self.hra.prvy)
            self.hra.prvy.policko -= 3
            self.koniec_tahu()

        elif karticka.nazov == "CHOĎTE DO VÄZENIA":
            self.hra.plocha[self.hra.prvy.policko].hraci.remove(self.hra.prvy)
            self.hra.plocha[10].hraci.append(self.hra.prvy)
            self.hra.prvy.bol_vo_vazeni = self.hra.prvy.vo_vazeni = True
            self.hra.prvy.bol_vo_vazeni = self.hra.prvy.bol_vo_vazeni = True
            self.hra.prvy.policko = 10
            self.koniec_tahu()

        elif karticka.nazov == "PRIEPUSTKA Z VÄZENIA":
            self.hra.prvy.priepustka = True
            self.koniec_tahu()

        elif karticka.nazov == "ODPUSTENIE DANE":
            self.hra.prvy.odpustenie_dane = True
            self.koniec_tahu()

        elif karticka.nazov == "AUKCIA":
            for pozemok in self.hra.plocha:
                if pozemok.vlastnik is None and pozemok.popis == "":
                    self.kresli_hru()
                    self.canvas.bind("<ButtonPress>", lambda event: self.vyber_policko_aukcia(event))
                    if self.hra.prvy.pocitac:
                        self.canvas.unbind("<ButtonPress>")
                        pozemok = self.vyber_pozemku_dedicstvo(self.hra.prvy)
                        self.najviac_suma = 100000 if 100000 <= self.hra.prvy.peniaze else self.hra.prvy.peniaze
                        self.najviac_hrac = self.hra.prvy
                        self.vyber = False
                        self.pozemok_na_drazenie = pozemok
                        self.kresli_hru()
                        self.aukcia_kresli(self.najviac_suma)
                        self.update_time()
                        self.canvas.update()
                        return
                    return
            self.skonci = True
            self.vykresli_oznam("Všetky pozemky majú svojích vlastníkov")

        elif karticka.nazov == "BEZPLATNÁ STAVBA":
            obr1 = f"objekty/obyt_j_h.gif"
            budova = Budova("obyt", 1, obr1)
            if len(self.hra.prvy.pozemky) != 0:
                self.kresli_hru()
                self.canvas.bind("<ButtonPress>", lambda event: self.bezplatna_stavba_klik(event, budova))
                if self.hra.prvy.pocitac:
                    self.canvas.unbind("<ButtonPress>")
                    pozemok = self.vyber_pozemku_zabavenie(self.hra.prvy)
                    pozemok.postav(budova)
            else:
                self.hra.prvy.peniaze += 500000

            self.koniec_tahu()

        elif karticka.nazov == "ZABAVENIE MAJETKU":
            self.kresli_hru()
            for pozemok in self.hra.plocha:
                if pozemok.popis == "" and pozemok.vlastnik == self.hra.prvy:
                    self.canvas.bind("<ButtonPress>", lambda event: self.zabavenie_klik(event))
                    if self.hra.prvy.pocitac:
                        self.canvas.unbind("<ButtonPress>")
                        pozemok = self.vyber_pozemku_zabavenie(self.hra.prvy)
                        self.hra.prvy.pozemky.remove(pozemok)
                        pozemok.clear()
                        self.hra.prvy.peniaze += 1000000
                        self.koniec_tahu()
                    return
            self.hra.prvy.peniaze -= 1000000
            self.skonci = True
            self.vykresli_oznam("Nemáte žiaden pozemok, ktorý by bolo možné zabaviť")

    def bezplatna_stavba_klik(self, event, budova):
        x, y = event.x, event.y
        for policko in self.hra.plocha:
            if policko.popis != "":
                continue
            if policko.inside(x, y):
                if policko.vlastnik != self.hra.prvy:
                    return
                policko.postav(budova)
                self.koniec_tahu()

    def dedicstvo_klik(self, event):
        x, y = event.x, event.y
        for pozemok in self.hra.plocha:
            if pozemok.popis != "":
                continue
            if pozemok.inside(x, y) and pozemok.vlastnik is None:
                pozemok.vlastnik = self.hra.prvy
                self.hra.prvy.pozemky.append(pozemok)
                self.hra.prvy.peniaze -= 500000
                self.koniec_tahu()

    def zemetrasenie_klik(self, event):
        x, y = event.x, event.y
        for pozemok in self.hra.plocha:
            if pozemok.popis != "":
                continue
            if pozemok.ma_cervenu():
                if pozemok.inside(x, y):
                    pozemok.zburaj("cerv")
                    self.koniec_tahu()

    def kradez_klik(self, event):
        x, y = event.x, event.y
        for pozemok in self.hra.plocha:
            if pozemok.popis != "":
                continue
            if pozemok.vlastnik is not None and pozemok.vlastnik != self.hra.prvy:
                if pozemok.inside(x, y):
                    pozemok.vlastnik.pozemky.remove(pozemok)
                    pozemok.vlastnik = self.hra.prvy
                    self.hra.prvy.pozemky.append(pozemok)
                    self.koniec_tahu()

    def zabavenie_klik(self, event):
        x, y = event.x, event.y
        for pozemok in self.hra.plocha:
            if pozemok.popis != "":
                continue
            if pozemok.vlastnik == self.hra.prvy:
                if pozemok.inside(x, y):
                    pozemok.clear()
                    self.hra.prvy.pozemky.remove(pozemok)
                    self.hra.prvy.peniaze += 1000000
                    self.koniec_tahu()

    def vazenie(self):
        self.kocka = False
        self.canvas.bind("<ButtonPress>", lambda event: self.vazenie_klik(event))
        self.canvas.create_rectangle(200, 200, self.width - 200, self.height - 200, fill="light gray")
        self.canvas.create_text(self.width / 2, self.height / 3 + 50, text="Ste vo väzení", fill="red", font="arial 20")
        self.canvas.create_text(self.width / 2, self.height / 2, text="Môžete si vybrať čo ďalej")
        if not self.hra.prvy.pocitac:
            self.canvas.create_rectangle(200, self.height - 250, self.width / 2, self.height - 200, fill="light blue")
            self.canvas.create_text(self.width / 4 + 100, self.height - 225, text="Hádzať")
        if not self.hra.prvy.pocitac:
            self.canvas.create_rectangle(self.width / 2, self.height - 250, self.width - 200, self.height - 200,
                                         fill="light green")
            self.canvas.create_text(3 * self.width / 4 - 100, self.height - 225, text=" Vykúpiť\n(500000$)")

        if self.hra.prvy.pocitac:
            self.canvas.update()
            self.canvas.unbind("<ButtonPress>")
            time.sleep(2)
            self.hra.prvy.vo_vazeni = False
            if random.randrange(0, 4) == 0 or self.hra.prvy.peniaze < 500000:
                for i in range(3):
                    self.k = self.hra.kocka()
                    self.kresli_hru()
                    self.canvas.update()
                    time.sleep(1)
                    if self.k == 6:
                        self.kocka = True
                        self.hra.prvy.vo_vazeni = False
                        self.kresli_hru()
                        return

                self.hra.prvy.vo_vazeni = True
                self.koniec_tahu()
            else:
                self.kocka = True
                self.hra.prvy.peniaze -= 500000
                self.hra.prvy.vo_vazeni = False
                self.kresli_hru()

    def vazenie_klik(self, event):
        x, y = event.x, event.y
        if self.width / 2 < x < self.width - 200 and self.height - 250 < y < self.height - 200:
            if self.hra.prvy.peniaze < 500000:
                self.vykresli_oznam("Nedostatok peňazí na zaplatenie kaucie")
            else:
                self.kocka = True
                self.hra.prvy.peniaze -= 500000
                self.hra.prvy.vo_vazeni = False
                self.kresli_hru()
        if 200 < x < self.width / 2 and self.height - 250 < y < self.height - 200:
            self.hadzanie_vo_vazeni()

    def hadzanie_vo_vazeni(self):
        self.hra.prvy.vo_vazeni = False
        self.kresli_hru()
        self.canvas.bind("<ButtonPress>", lambda event: self.hadzanie_vo_vazeni_klik(event, 0))

    def hadzanie_vo_vazeni_klik(self, event, pocet):
        x, y = event.x, event.y
        if 435 < x < 460 and 315 < y < 340:
            self.k = self.hra.kocka()
            pocet += 1
            if self.k == 6:
                self.kocka = True
                self.hra.prvy.vo_vazeni = False
                self.kresli_hru()
            elif pocet == 3:
                self.hra.prvy.vo_vazeni = True
                self.koniec_tahu()
            else:
                self.kresli_hru()
                self.canvas.bind("<ButtonPress>", lambda event: self.hadzanie_vo_vazeni_klik(event, pocet))

    def cierne(self):
        self.canvas.bind("<ButtonPress>", lambda event: self.cierne_klik(event))
        self.canvas.create_rectangle(200, 200, self.width - 200, self.height - 200, fill="light gray")
        self.canvas.create_text(self.width / 2, self.height / 3 + 50, text="!Čierne stavby!", fill="red",
                                font="arial 20")
        self.canvas.create_text(self.width / 2, self.height / 2, text="Môžete si vybrať čo ďalej")
        if not self.hra.prvy.pocitac:
            self.canvas.create_rectangle(200, self.height - 250, self.width / 2, self.height - 200, fill="tomato")
            self.canvas.create_text(self.width / 4 + 100, self.height - 225, text="Ignorovať")
        if not self.hra.prvy.pocitac:
            self.canvas.create_rectangle(self.width / 2, self.height - 250, self.width - 200, self.height - 200,
                                         fill="light green")
            self.canvas.create_text(3 * self.width / 4 - 100, self.height - 225, text="Vykúpiť")
            self.canvas.create_text(3 * self.width / 4 - 100, self.height - 210,
                                text=f"({self.hra.prvy.cierne() * 500000})$")
        if self.hra.prvy.pocitac:
            self.canvas.unbind("<ButtonPress>")
            self.canvas.update()
            time.sleep(1)
            suma = self.hra.prvy.cierne() * 500000
            if self.hra.prvy.peniaze < suma:
                self.kresli_hru()
            else:
                self.hra.prvy.peniaze -= suma
                self.hra.prvy.vymaz_cierne()
                self.kresli_hru()

    def cierne_klik(self, event):
        x, y = event.x, event.y
        suma = self.hra.prvy.cierne() * 500000
        if self.width / 2 < x < self.width - 200 and self.height - 250 < y < self.height - 200:
            if self.hra.prvy.peniaze < suma:
                self.vykresli_oznam("Nedostatok peňazí na odkúpenie čiernych budov")
                self.hra.prvy.zaciatok_tahu = True
            else:
                self.hra.prvy.peniaze -= suma
                self.hra.prvy.vymaz_cierne()
                self.kresli_hru()
        if 200 < x < self.width / 2 and self.height - 250 < y < self.height - 200:
            self.kresli_hru()

    def casovac(self):
        p = self.kolko + 1
        for i in range(p):
            time.sleep(1)
            self.kolko -= 1

    def pocitac_bid(self, hrac):
        while self.kolko > 0:
            time.sleep(random.randrange(1, 3))
            if self.kolko <= 0:
                break
            if hrac == self.najviac_hrac:
                continue
            if hrac.peniaze >= self.najviac_suma + 10000:
                if not self.vyber:
                    self.najviac_suma = self.najviac_suma + 10000
                    self.najviac_hrac = hrac

            time.sleep(random.randrange(2, 4))

    def update_time(self):
        while self.kolko > 0:
            if self.vyber:
                self.canvas.create_text(45, 45, fill="gold", text=f"{self.kolko}s", font="arial 20", tag="cas")
                self.canvas.update()
                self.canvas.delete("cas")
                continue
            self.aukcia_kresli(self.najviac_suma)
            self.canvas.create_text(45, 45, fill="gold", text=f"{self.kolko}s", font="arial 20", tag="cas")
            self.canvas.update()
            self.canvas.delete("cas")
        self.timer = None
        self.kolko = 0
        self.aukcia = False
        self.kresli_hru()
        self.koniec_aukcie()

    def vyber_policko_aukcia(self, event):
        x, y = event.x, event.y
        for pozemok in self.hra.plocha:
            if pozemok.popis != "":
                continue
            if pozemok.vlastnik is None:
                if pozemok.inside(x, y):
                    self.najviac_suma = 100000 if 100000 <= self.hra.prvy.peniaze else self.hra.prvy.peniaze
                    self.vyber = False
                    self.pozemok_na_drazenie = pozemok
                    self.najviac_hrac = self.hra.prvy
                    self.aukcia_kresli(self.najviac_suma)
                    self.update_time()
                    return

    def aukcia_kresli(self, cena):
        if self.timer is None:
            self.canvas.create_text(45, 45, fill="gold", text=f"{15}s", font="arial 20", tag="cas")
            self.timer = threading.Thread(target=self.casovac)
            self.kolko = 15
            self.timer.start()
            for hrac in self.hra.hraci:
                if hrac.pocitac:
                    t = threading.Thread(target=self.pocitac_bid, args=[hrac, ])
                    t.start()
        self.canvas.delete("aukcia_oval")
        self.canvas.delete("aukcia_meno")
        self.canvas.delete("aukcia_cena")
        i = 0
        for h in self.hra.hraci:
            if h.pocitac is False:
                self.canvas.delete(f"aukcia_meno{i}")
                i += 1
        self.canvas.delete("aukcia_vyber_hracov")
        self.canvas.bind("<ButtonPress>", lambda event: self.aukcia_klik(event))
        self.canvas.create_oval(200, 200, self.width - 200, self.height - 200, fill="light gray", tag="aukcia_oval")
        self.canvas.create_text(self.width / 2, self.height / 2 - 25, text=f"{self.najviac_hrac.meno}", font="arial 20",
                                tag="aukcia_meno")
        self.canvas.create_text(self.width / 2, self.height / 2, text=f"{cena}$", font="arial 20", tag="aukcia_cena")

    def aukcia_klik(self, event):
        x, y = event.x, event.y
        if self.poc_h == 0:
            return
        if math.sqrt((self.width / 2 - x) ** 2 + (self.height / 2 - y) ** 2) <= self.width / 2 - 200:
            self.vyber = True
            self.kresli_vyber_hracov()

    def kresli_vyber_hracov(self):
        self.canvas.bind("<ButtonPress>", lambda event: self.kresli_vyber_hracov_klik(event))
        self.canvas.create_rectangle(200, 200, self.width - 200, self.height - 200, fill="light gray",
                                     tag="aukcia_vyber_hracov")
        i = 0
        for hrac in self.hra.hraci:
            c = ((self.height - 400) / self.poc_h)
            if hrac.pocitac is False:
                self.canvas.create_rectangle(200, 200 + c * i, self.width - 200, 200 + c + c * i, tag=f"aukcia_meno{i}")
                self.canvas.create_text(self.width / 2, 200 + c / 2 + c * i, text=self.hra.hraci[i].meno)
                i += 1

    def kresli_vyber_hracov_klik(self, event):
        x, y = event.x, event.y
        i = 0
        for hrac in self.hra.hraci:
            c = ((self.height - 400) / self.poc_h)
            if hrac.pocitac is False:
                if 200 < x < self.width - 200 and 200 + c * i < y < 200 + c + c * i:
                    if hrac.peniaze >= self.najviac_suma + 10000:
                        self.najviac_suma += 10000
                        self.najviac_hrac = hrac
                        self.vyber = False
                i += 1

    def koniec_aukcie(self):
        self.najviac_hrac.peniaze -= self.najviac_suma
        self.pozemok_na_drazenie.vlastnik = self.najviac_hrac
        self.najviac_hrac.pozemky.append(self.pozemok_na_drazenie)
        self.skonci = True
        self.vykresli_oznam(f"Aukciu vyhral {self.najviac_hrac.meno} za {self.najviac_suma}")


    def koniec_tahu(self):
        self.kocka = True
        self.hra.next()
        self.kresli_hru()

    def prehral(self, hrac):
        self.hra.hraci.remove(hrac)
        self.hra.plocha[hrac.policko].hraci.remove(hrac)
        if self.hra.n == len(self.hra.hraci):
            self.hra.n = 0
            self.hra.prvy = self.hra.hraci[0]
        for policko in hrac.pozemky:
            policko.clear()

        if hrac.pocitac:
            self.poc_p -= 1
        else:
            self.poc_h -= 1

    def kresli_navod(self, strana):
        self.canvas.bind("<ButtonPress>", lambda event: self.klikaj_navod(event, strana))
        self.canvas.delete("BG_navod")
        self.canvas.delete("BG_text")
        navod = self.zarovnaj(self.navod, strana * 15, strana * 15 + 15)
        self.canvas.create_rectangle(100, 100, self.width - 100, self.height - 100, fill="light gray", tag="BG_navod")
        self.canvas.create_text(self.width / 2, self.height / 2, text=navod, tag="BG_text")
        x1 = tk.PhotoImage(file="x.png")
        x1 = x1.subsample(8, 8)
        self.canvas.image.append(x1)
        self.canvas.create_image(self.width - 115, 115, image=x1, tag="x1")
        if strana != 0:
            self.canvas.create_rectangle(self.height - 160, self.height - 130, self.width - 130, self.height - 100,
                                         fill="tan")
            self.canvas.create_text(self.height - 145, self.height - 115, text="<")
        navod = self.zarovnaj(self.navod, strana * 15 + 15, strana * 15 + 30)
        if navod.strip() != "":
            self.canvas.create_rectangle(self.height - 130, self.height - 130, self.width - 100, self.height - 100,
                                         fill="tan")
            self.canvas.create_text(self.height - 115, self.height - 115, text=">")

    def klikaj_navod(self, event, strana):
        x, y = event.x, event.y
        if self.height - 160 < x < self.width - 130 and self.height - 130 < y < self.height - 100:
            if strana != 0:
                self.kresli_navod(strana - 1)

        if self.height - 130 < x < self.width - 100 and self.height - 130 < y < self.height - 100:
            navod = self.zarovnaj(self.navod, strana * 15 + 15, strana * 15 + 30)
            if navod.strip() != "":
                self.kresli_navod(strana + 1)

        if 470 < x < 500 and 100 < y < 130:
            self.kresli_hru()

    def zarovnaj(self, text, od, do, size=50):
        t = ""
        act = 0
        i = 0
        n = True
        for slovo in text.split(" "):
            if len(slovo) == 0:
                continue
            if slovo[-1] == "\n":
                t += slovo
                act = 0
                i += 1
                continue
            if i == od and n:
                t = slovo + " "
                n = False
                continue
            if i > do:
                return t
            if len(slovo) + act < size:
                t += slovo + " "
            else:
                t += "\n" + slovo + " "
                act = 0
                i += 1
            act += len(slovo)

        if i < od:
            return ""
        return t


program = GUI()
