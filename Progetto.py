import json
from functools import partial
from tkinter import *
import requests
import tkinter.messagebox as popup

sessione = requests.Session()
admin = -1


def send_error(error_code):

    if error_code == 400:
        popup.showinfo("Errore", "Richiesta non valida")
    elif error_code == 403:
        popup.showinfo("Errore", "Non hai i permessi per usare questa funzione o password errata")
    elif error_code == 409:
        popup.showinfo("Errore", "Impossibile eseguire, conflitto nel server")
    elif error_code == 500:
        popup.showinfo("Errore", "Errore del server")
    else:
        popup.showinfo("Errore", "Errore durante la richiesta al server")


def login(username, password):
    username = username.get()
    password = password.get()
    url = 'http://127.0.0.1:8080/session'
    myobj = {'username': username, 'password': password}

    x = sessione.post(url, data=myobj)
    if x.status_code != 200:
        send_error(x.status_code)
    else:
        # print the response text (the content of the requested file):
        y = x.json()

        if y["admin"] == 0:
            global admin
            admin = 0
            # for widget in tkWindow.winfo_children():
            #   widget.destroy()
            BookTutoring()

        elif y["admin"] == 1:
            admin = 1
            BookTutoring()


def LoginForm():
    # username label and text entry box
    Label(tkWindow, text="UserName").grid(row=0, column=0)
    username = StringVar(value='root')
    Entry(tkWindow, textvariable=username).grid(row=0, column=1)

    # password label and password entry box
    Label(tkWindow, text="Password").grid(row=1, column=0)
    password = StringVar(value='root')
    Entry(tkWindow, textvariable=password, show='*').grid(row=1, column=1)

    Login = partial(login, username, password)

    # login button
    Button(tkWindow, text="Login", command=Login).grid(row=4, column=0)


def Logout():
    global admin
    for widget in tkWindow.winfo_children():
        widget.destroy()
    url = 'http://127.0.0.1:8080/session?logout'
    json = sessione.get(url)
    if json.status_code != 200:
        send_error(json.status_code)
    else:
        print(json)
        admin = -1
        LoginForm()


def getJSONday(dayNum):
    # CLEAR GUI
    global admin
    for widget in tkWindow.winfo_children():
        if type(widget) != Button:
            widget.destroy()
    col = 0
    if admin == 0:
        Label(tkWindow, text="Prenota", width=10).grid(row=1, column=1)
        col = 1

    Label(tkWindow, text="Orario", width=10).grid(row=1, column=2)
    Label(tkWindow, text="Corso", width=10).grid(row=1, column=3)
    Label(tkWindow, text="Professore", width=10).grid(row=1, column=4)
    url = 'http://127.0.0.1:8080/api/get?type=teachesOfDay&day=' + str(dayNum)
    json = sessione.get(url)
    if json.status_code != 200:
        send_error(json.status_code)
    else:
        json = json.json()
        rows = len(json["a"]) + len(json["b"]) + len(json["c"]) + len(json["d"])
        columns = 3 + col
        boxes = []
        boxVars = []

        # Create all IntVars, set to 0

        for i in range(rows):
            boxVars.append([])
            for j in range(columns):
                boxVars[i].append(IntVar())
                boxVars[i][j].set(0)

        indexToHour = ["a", "b", "c", "d"]
        indexToTime = ["15-16", "16-17", "17-18", "18-19"]
        m = 0
        rowTemp = []
        for hour in range(4):
            for teach in json[indexToHour[hour]]:
                Label(tkWindow, text=indexToTime[hour]).grid(row=m + 2, column=2)
                Label(tkWindow, text=teach["course"]["name"]).grid(row=m + 2, column=3)
                Label(tkWindow, text=teach["teacher"]["name"]+" "+teach["teacher"]["surname"], width=10).grid(row=m + 2, column=4)
                article = {
                    "hour": indexToHour[hour],
                    "day": dayNum,
                    "teacherId": teach["teacher"]["id"],
                    "courseId": teach["course"]["id"]
                }

                rowTemp.append(article)
                m = m + 1

        if admin == 0:
            for x in range(rows):
                boxes.append([])
                # Label(tkWindow, text=json["b"][0]["teacher"]["name"]).grid(row=x + 2, column=z + 2)
                for y in range(columns):
                    boxes[x].append(Checkbutton(tkWindow, variable=boxVars[x][y]))
                    boxes[x][y].grid(row=x + 2, column=1)

            def getSelected():
                selected = []
                for i in range(len(boxVars)):
                    for j in range(len(boxVars[i])):
                        if boxVars[i][j].get() == 1:
                            selected.append(rowTemp[i])

                for book in selected:
                    url2 = "http://127.0.0.1:8080/api/set?type=book"
                    res = sessione.post(url2, data=book)
                    if res.status_code != 200:
                        send_error(res.status_code)
                    else:
                        print(res)
                        getJSONday(dayNum)

            b = Button(tkWindow, text="Prenota", command=getSelected, width=10)
            b.grid(row=1000, column=5)


def MyBooks():
    global admin
    # CLEAR GUI
    for widget in tkWindow.winfo_children():
        widget.destroy()
    col = 0
    if admin == 1:
        Label(tkWindow, text="Utente", width=10).grid(row=1, column=6)
        col = 1
    Label(tkWindow, text="Prenota", width=10).grid(row=1, column=1)
    Label(tkWindow, text="Orario", width=10).grid(row=1, column=2)
    Label(tkWindow, text="Corso", width=10).grid(row=1, column=3)
    Label(tkWindow, text="Professore", width=10).grid(row=1, column=4)
    Label(tkWindow, text="Status", width=10).grid(row=1, column=5)
    url = 'http://127.0.0.1:8080/api/get?type=bookings'
    json = sessione.get(url)
    if json.status_code != 200:
        send_error(json.status_code)
    else:
        json = json.json()
        print(json)
        rows = len(json)
        columns = 5 + col
        boxes = []
        boxVars = []

        # Create all IntVars, set to 0

        for i in range(rows):
            boxVars.append([])
            for j in range(columns):
                boxVars[i].append(IntVar())
                boxVars[i][j].set(0)

        indexToDay = {"0": "Lunedì", "1": "Martedì", "2": "Mercoledì", "3": "Giovedì", "4": "Venerdì"}
        indexToTime = {"a": "15-16", "b": "16-17", "c": "17-18", "d": "18-19"}
        m = 0
        rowTemp = []
        for book in json:
            d = indexToDay[str(book["day"])]
            d = d + " " + indexToTime[book["hour"]]
            Label(tkWindow, text=d).grid(row=m + 2, column=2)
            Label(tkWindow, text=book["course"]["name"]).grid(row=m + 2, column=3)
            Label(tkWindow, text=book["teacher"]["name"]+" "+book["teacher"]["surname"], width=10).grid(row=m + 2, column=4)
            Label(tkWindow, text=book["status"]).grid(row=m + 2, column=5)
            if admin == 1:
                Label(tkWindow, text=book["user"]["name"]+" "+book["user"]["surname"], width=10).grid(row=m + 2, column=6)
            article = {
                "hour": book["hour"],
                "day": book["day"],
                "teacherId": book["teacher"]["id"],
                "courseId": book["course"]["id"],
                "username": book["user"]["username"],
                "id": book["id"],
                "status": book["status"]
            }

            rowTemp.append(article)
            m = m + 1

        for x in range(rows):
            boxes.append([])
            # Label(tkWindow, text=json["b"][0]["teacher"]["name"]).grid(row=x + 2, column=z + 2)

            for y in range(columns):
                boxes[x].append(Checkbutton(tkWindow, variable=boxVars[x][y]))
                boxes[x][y].grid(row=x + 2, column=1)

        def getSelected(s):
            selected = []
            for i in range(len(boxVars)):
                for j in range(len(boxVars[i])):
                    if boxVars[i][j].get() == 1:
                        selected.append(rowTemp[i])

            for book in selected:
                print(book)
                book["status"] = s
                url2 = "http://127.0.0.1:8080/api/set?type=updateStatus"
                res = sessione.post(url2, data=book)
                if res.status_code != 200:
                    send_error(res.status_code)
                else:
                    print(res)
                    MyBooks()

        Done = partial(getSelected, "done")
        Cancel = partial(getSelected, "canceled")
        if admin == 0:
            Button(tkWindow, text="Done", command=Done, width=10).grid(row=100, column=6)
        if admin == 1:
            Button(tkWindow, text="Add Things", command=AddThings, width=10).grid(row=4, column=8)
            Button(tkWindow, text="Remove Things", command=RemoveThings, width=10).grid(row=5, column=8)
        Button(tkWindow, text="Delete", command=Cancel, width=10).grid(row=100, column=7)
        Button(tkWindow, text="Rip. Disponibili", command=BookTutoring, width=10).grid(row=3, column=8)
        Button(tkWindow, text="Logout", command=Logout, width=10).grid(row=6, column=8)


def BookTutoring():
    # CLEAR GUI
    for widget in tkWindow.winfo_children():
        widget.destroy()
    lunedì = partial(getJSONday, 0)
    martedì = partial(getJSONday, 1)
    mercoledì = partial(getJSONday, 2)
    giovedì = partial(getJSONday, 3)
    venerdì = partial(getJSONday, 4)
    Button(tkWindow, text="Lunedì", command=lunedì, width=10).grid(row=0, column=1)
    Button(tkWindow, text="Martedì", command=martedì, width=10).grid(row=0, column=2)
    Button(tkWindow, text="Mercoledì", command=mercoledì, width=10).grid(row=0, column=3)
    Button(tkWindow, text="Giovedì", command=giovedì, width=10).grid(row=0, column=4)
    Button(tkWindow, text="Venerdì", command=venerdì, width=10).grid(row=0, column=5)
    Button(tkWindow, text="My Books", command=MyBooks, width=10).grid(row=2, column=7)
    Button(tkWindow, text="Logout", command=Logout, width=10).grid(row=5, column=7)
    if admin == 1:
        Button(tkWindow, text="Add Things", command=AddThings, width=10).grid(row=3, column=7)
        Button(tkWindow, text="Remove Things", command=RemoveThings, width=10).grid(row=4, column=7)
    getJSONday(0)


def AddThings():
    for widget in tkWindow.winfo_children():
        widget.destroy()

    url = 'http://127.0.0.1:8080/api/get?type=courses'
    jsonC = sessione.get(url)
    if jsonC.status_code != 200:
        send_error(jsonC.status_code)
    else:
        jsonC = jsonC.json()
        optionsC = []
        for x in jsonC:
            optionsC.append(x["name"])

        # datatype of menu text
        clickedC = StringVar()
        # initial menu text
        clickedC.set(jsonC[0])
    url = 'http://127.0.0.1:8080/api/get?type=teachers'
    jsonD = sessione.get(url)
    if jsonD.status_code != 200:
        send_error(jsonD.status_code)
    else:
        jsonD = jsonD.json()
        optionsD = []
        for x in jsonD:
            optionsD.append(x["surname"])

        # datatype of menu text
        clickedD = StringVar()
        # initial menu text
        clickedD.set(jsonD[0])

    def AggiungiCorso(nome, des):
        nome = nome.get()
        des = des.get()
        url2 = "http://127.0.0.1:8080/api/set?type=course"
        c = {"name": nome, "description": des}
        res = sessione.post(url2, data=c)
        if res.status_code != 200:
            send_error(res.status_code)
        else:
            print(res)
            RAD()

    def AggiungiDocente(nome, cognome):
        nome = nome.get()
        cognome = cognome.get()
        url2 = "http://127.0.0.1:8080/api/set?type=teacher"
        c = {"name": nome, "surname": cognome}
        res = sessione.post(url2, data=c)
        if res.status_code != 200:
            send_error(res.status_code)
        else:
            print(res)
            RAD()

    def AggiungiInsegnamento():
        print(clickedC.get())
        c = json.loads(clickedC.get().replace("'", "\""))
        d = json.loads(clickedD.get().replace("'", "\""))
        z = {"courseId": c["id"],
             "teacherId": d["id"]}
        url2 = "http://127.0.0.1:8080/api/set?type=teach"
        res = sessione.post(url2, data=z)
        if res.status_code != 200:
            send_error(res.status_code)
        else:
            print(res)
            RAD()

    Label(tkWindow, text="Aggiungi Corso").grid(row=0, column=1)
    NomeCorso = StringVar()
    Label(tkWindow, text="Nome: ").grid(row=1, column=0)
    Entry(tkWindow, textvariable=NomeCorso).grid(row=1, column=1)
    DesCorso = StringVar()
    Label(tkWindow, text="Descrizione: ").grid(row=2, column=0)
    Entry(tkWindow, textvariable=DesCorso).grid(row=2, column=1)
    AC = partial(AggiungiCorso, NomeCorso, DesCorso)
    Button(tkWindow, text="Aggiungi", command=AC, width=10).grid(row=3, column=1)

    Label(tkWindow, text="Aggiungi Professore").grid(row=5, column=1)
    NomeProf = StringVar()
    Label(tkWindow, text="Nome: ").grid(row=6, column=0)
    Entry(tkWindow, textvariable=NomeProf).grid(row=6, column=1)
    CognomeProf = StringVar()
    Label(tkWindow, text="Cognome: ").grid(row=7, column=0)
    Entry(tkWindow, textvariable=CognomeProf).grid(row=7, column=1)
    AP = partial(AggiungiDocente, NomeProf, CognomeProf)
    Button(tkWindow, text="Aggiungi", command=AP, width=10).grid(row=8, column=1)

    Label(tkWindow, text="Aggiungi Insegnamento", width=50).grid(row=11, column=1)
    Label(tkWindow, text="Corso: ").grid(row=12, column=0)
    drop1 = OptionMenu(tkWindow, clickedC, *jsonC).grid(row=12, column=1)
    Label(tkWindow, text="Professore: ").grid(row=13, column=0)
    drop2 = OptionMenu(tkWindow, clickedD, *jsonD).grid(row=13, column=1)
    Button(tkWindow, text="Aggiungi", command=AggiungiInsegnamento, width=10).grid(row=15, column=1)

    Button(tkWindow, text="Rip. Disponibili", command=BookTutoring, width=10).grid(row=1, column=12)
    Button(tkWindow, text="My Books", command=MyBooks, width=10).grid(row=2, column=12)
    Button(tkWindow, text="Remove Things", command=RemoveThings, width=10).grid(row=3, column=12)
    Button(tkWindow, text="Logout", command=Logout, width=10).grid(row=4, column=12)


def RemoveThings():
    for widget in tkWindow.winfo_children():
        widget.destroy()

    url = 'http://127.0.0.1:8080/api/get?type=courses'
    jsonC = sessione.get(url)
    if jsonC.status_code != 200:
        send_error(jsonC.status_code)
    else:
        jsonC = jsonC.json()
        optionsC = []
        for x in jsonC:
            optionsC.append(x["name"])
        # datatype of menu text
        clickedC = StringVar()
        # initial menu text
        clickedC.set(jsonC[0])
    url = 'http://127.0.0.1:8080/api/get?type=teachers'
    jsonD = sessione.get(url)
    if jsonD.status_code != 200:
        send_error(jsonD.status_code)
    else:
        jsonD = jsonD.json()
        optionsD = []
        for x in jsonD:
            optionsD.append(x["surname"])

        # datatype of menu text
        clickedD = StringVar()
        # initial menu text
        clickedD.set(jsonD[0])

    url = 'http://127.0.0.1:8080/api/get?type=teaches'
    jsonT = sessione.get(url)
    if jsonT.status_code != 200:
        send_error(jsonT.status_code)
    else:
        jsonT = jsonT.json()
        optionsT = []
        for x in jsonT:
            optionsT.append(x["course"]["name"] + " - " + x["teacher"]["surname"])

        # datatype of menu text
        clickedT = StringVar()
        # initial menu text
        clickedT.set(jsonT[0])

    def RimuoviCorsi():
        print(clickedC.get())

        c = json.loads(clickedC.get().replace("'", "\""))
        c = {"id": c["id"]}
        print(c)
        url2 = "http://127.0.0.1:8080/api/delete?type=course"
        res = sessione.post(url2, data=c)
        if res.status_code != 200:
            send_error(res.status_code)
        else:
            print(res)
            RRT()

    def RimuoviDocenti():
        print(clickedD.get())
        c = json.loads(clickedD.get().replace("'", "\""))
        c = {"id": c["id"]}
        url2 = "http://127.0.0.1:8080/api/delete?type=teacher"
        res = sessione.post(url2, data=c)
        if res.status_code != 200:
            send_error(res.status_code)
        else:
            print(res)
            RRT()

    def RimuoviInsegnamenti():
        c = json.loads(clickedT.get().replace("'", "\""))
        c = {'teacherId': c["teacher"]["id"], 'courseId': c["course"]["id"]}
        url2 = "http://127.0.0.1:8080/api/delete?type=teach"
        res = sessione.post(url2, data=c)
        if res.status_code != 200:
            send_error(res.status_code)
        else:
            print(res)
            RRT()

    # Create Dropdown menu
    Label(tkWindow, text="Rimuovi Corso", width=50).grid(row=0, column=0)
    drop1 = OptionMenu(tkWindow, clickedC, *jsonC).grid(row=1, column=0)
    Button(tkWindow, text="Rimuovi", command=RimuoviCorsi, width=10).grid(row=2, column=0)
    Label(tkWindow, text="Rimuovi Docente", width=50).grid(row=3, column=0)
    drop2 = OptionMenu(tkWindow, clickedD, *jsonD).grid(row=4, column=0)
    Button(tkWindow, text="Rimuovi", command=RimuoviDocenti, width=10).grid(row=5, column=0)
    Label(tkWindow, text="Rimuovi Insegnamento", width=50).grid(row=6, column=0)
    drop3 = OptionMenu(tkWindow, clickedT, *jsonT).grid(row=7, column=0)
    Button(tkWindow, text="Rimuovi", command=RimuoviInsegnamenti, width=10).grid(row=8, column=0)

    Button(tkWindow, text="Rip. Disponibili", command=BookTutoring, width=10).grid(row=1, column=12)
    Button(tkWindow, text="My Books", command=MyBooks, width=10).grid(row=2, column=12)
    Button(tkWindow, text="Add Things", command=AddThings, width=10).grid(row=3, column=12)
    Button(tkWindow, text="Logout", command=Logout, width=10).grid(row=4, column=12)


def RAD():
    AddThings()


def RRT():
    RemoveThings()


# window
tkWindow = Tk()
width = tkWindow.winfo_screenwidth()
height = tkWindow.winfo_screenheight()
log = StringVar(value='log')
# setting tkinter window size
tkWindow.geometry("%dx%d" % (width, height))
tkWindow.title('Book Tutoring')
LoginForm()
tkWindow.mainloop()
