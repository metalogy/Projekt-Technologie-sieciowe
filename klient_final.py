import socket 
import time
import re

TCP_IP = '192.168.0.2'
TCP_PORT = 15200
BUFFER_SIZE = 1024
lista_operacji = [] #lista zawierająca stringi będące polami komunikatu oraz ich wartosciami, uzywamy jej do łączenia pól w jeden komunikat


def switch_wybor_operacji(x):
    return {
        1: 'OperaC>>op1^',
        2: 'OperaC>>op2^',
        3: 'OperaC>>op3^',
        4: 'OperaC>>op4^'
    }.get(x, 'OperaC>>ERROR^')  #zamieniamy wprowadzony numer na pole komunikatu z odpowiednia wartoscia, w przypadku złego wyboru przypisujemy wartosc ERROR
def pokaz_menu():
    print('Jaka operacje chcesz wykonac? Wybierz numer dzialania \n')
    print('Operacje: \n 1.ODEJMOWANIE \n 2.DZIELENIE \n 3.DODAWANIE \n 4.MNOZENIE \n ')
    nroperacji = int(input())
    OPERACJA = switch_wybor_operacji(nroperacji)
    while OPERACJA == 'OperaC>>ERROR^': #zabezpieczenie przed podaniem zlego numeru operacji
        print('Podano zly numer operacji, wybierz jeszcze raz')
        nroperacji = int(input())
        OPERACJA = switch_wybor_operacji(nroperacji)
    lista_operacji.insert(0, OPERACJA) #do zmiennej lista_operacji dodajemy pole OperaC z odpowiednia wartoscia
    if(nroperacji==1): # pomocnicza pętla używana do wyswietlania interfejsu w kliencie
        pomoc_operacji='odejmowanie'
    elif(nroperacji==2):
        pomoc_operacji='dzielenie'
    elif(nroperacji==3):
        pomoc_operacji='dodawnie'
    elif(nroperacji==4):
         pomoc_operacji='mnozenie'
    print('wybrales: ' + pomoc_operacji)

    print('Podaj pierwsza liczbe na ktorej chcesz wykonac dzialanie')  #wpisujemy 3 argumenty na jakich chcemy wykonac dzialanie
    nrliczby1 = int(input())
    lista_operacji.insert(2, 'LiczbA>>' + str(nrliczby1) + '^')
    print('Podaj druga liczbe calkowita na ktorej chcesz wykonac dzialanie')
    nrliczby2 = int(input())
    lista_operacji.insert(3, 'LiczbB>>' + str(nrliczby2) + '^')
    print('Podaj trzecia liczbe calkowita na ktorej chcesz wykonac dzialanie')
    nrliczby3 = int(input())
    lista_operacji.insert(4, 'LiczbC>>' + str(nrliczby3) + '^')
    lista_operacji.insert(1, 'StatuS>>null^')

def sklec_komunikat(id_sesji): #funkcja laczy komunikat, jako argument przyjmuje odczytany wczesniej identyfikator sesji
    #print('idsesji: ',id_sesji[0])
    MESSAGE = ''.join(lista_operacji) # wtym miejscu laczymy komunikat
    MESSAGE=MESSAGE+str(id_sesji[0])+'IdczaS>>'+str(time.time())+'^' # dodajemy do komunikatu znacznik sesji oraz znacznik czasowy
    lista_operacji.clear() # czyscimy zmienna lista_operacji aby w przypadku ponownego skorzystania z dzialania moc polaczyc komunikat w calosc
    return MESSAGE

def odczytanie_idsesji(a): #funkcja odczytuje i zwraca identyfikator sejsi z wiadomosci przeslanej przez serwer, jako argument przyjmuje wiadomosc wyslana przez serwer w formacie zamienionym na tekstowy
    identy = re.findall(r'IdentY\>\>.{16}\^', a) # z komunikatu wyslanego przez serwer po polaczeniu klienta za pomoca regex'a wyluskujemy pole numeru sesji z wartoscia i zapisujemy do zmiennej
    return [identy[0]]

def odczytanie_komunikatu(a):  #za pomoca regex'u odczytujemy numer operacji, wynik dzialania, indentyfikator sesji oraz status komunikatu, by wyswietlic wynik dzialania użytkownikowi, funkcja jako argument przyjmuje komunikt wyslany przez serwer, a odczytany przez klienta
    b = a.decode() # zamiana komunikatu z postaci bitowej na tekstowa
    operacja = re.findall(r'op1|op2|op3|op4', b) #znajdujemy numer operacji
    liczba = re.findall(r'\-?[0-9]+\.?[0-9]*', b) # znajdujemy wynik dzialania
    identy = re.findall(r'\^IdentY\>\>.{16}\^', b) #znajdujemy identyfiaktor sesji
    stat = re.findall(r'StatuS\>\>ok\^|StatuS\>\>div0\^', b) #znajdujemy status sesji
    return [operacja[0], float(liczba[1]), identy[0], stat[0]]  #wszystkie znalezione wartosci zapisujemy od listy, ktora funkcja zwraca

def Main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # tworzymy socket
    s.connect((TCP_IP, TCP_PORT)) #laczymy sie z serwerem
    id_sesji_data = s.recv(BUFFER_SIZE).decode() #odbieramy id sesji
    id_sesji = odczytanie_idsesji(id_sesji_data) #odczytujemy i zapisujemy idsesji
    print('Witamy w kliencie')

    zmienna = 1

    while(zmienna == 1): #wykonujemy operacje dopoki na zyczenie uzytkownika nie zakonczymy sesji
        pokaz_menu()
        s.send(sklec_komunikat(id_sesji).encode()) #wysylamy wiadomosc
        data = s.recv(BUFFER_SIZE) #odbieramy dane od serwwera
        print("Otrzymane dane z serwera:", data)
        pomocnicza=odczytanie_komunikatu(data) 
        if(pomocnicza[3]=='StatuS>>div0^'):
            print('Serwer zwrocil blad, dzielenie przez zero') # w przypadku zwrocenia przez serwer bledy dzielenia przez zero wyswietlamy stosowny komunikat
        else:
            print('Wynikiem działania jest', pomocnicza[1])
        print('Czy chcesz wykonac jeszcze jakas operacje? \n 1.TAK \n 2.NIE \n WPISZ CYFRE 1 LUB 2 ')
        zmienna = int(input())
    print('Dziekujemy za korzystanie z klienta, zamykam polaczenie z serwerem')
    s.shutdown(socket.SHUT_WR)
    buf = s.recv(1)
    if not buf: #zamykamy polaczenie kiedy bufor jest pusty
        s.close()
    lista_operacji.clear() #dla bezepieczenstwa raz jeszcze czyscimy liste operacji, która jest zmienna globalna
Main()