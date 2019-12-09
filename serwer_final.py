import socket 
import re
from _thread import *
import threading 
import secrets
import time

TCP_IP = '192.168.0.2'
TCP_PORT = 15200
liczba_klientow=5
BUFFER_SIZE = 1024
def odczytanie_komunikatu(a):  #za pomoca regex'u odczytujemy numer operacji oraz jej arumenty, indentyfikator sesji, funkcja jako argument przyjmuje komunikt wyslany przez klienta, a odczytany przez serwer
    b = a.decode()
    operacja = re.findall(r'op1|op2|op3|op4', b)
    liczby = re.findall(r'\-?[1-9]*[0-9]+', b)
    identy = re.findall(r'IdentY\>\>.{16}\^', b)
    return [operacja[0], int(liczby[1]), int(liczby[2]), int(liczby[3]), identy[0]] #wartosci wyodrebione zwracamy jako lista

def kalkulacja_taka_sytuacja(lista): # wykonujemy operacje zlecona przez klienta na argumentach przez niego przeslanych, funkcja jako argument przyjmuje liste ktora zwraca funkcja odczytanie/komunikatu
    if lista[0] == 'op1':
        return (lista[1] - lista[2]) - lista[3]
    elif lista[0] == 'op2':
        if(lista[1]==0 or lista[2]==0 or lista[3]==0):
            return 'Err' # w przypadku dzielenia przez zero serwer funkcja zwraca string Err
            return (lista[1] / lista[2]) / lista[3]
    elif lista[0] == 'op3':
        return (lista[1] + lista[2]) + lista[3]
    elif lista[0] == 'op4':
        return (lista[1] * lista[2]) * lista[3]

def sklec_komunikat_serwer(data):#funkcja laczy komunikat ktory mamy przeslac klientowi, przyjmuje komunikat otrzymany od klienta
    pomocnicza=odczytanie_komunikatu(data)
    if kalkulacja_taka_sytuacja(pomocnicza)=='Err': #gdy nastapilo w funkcji kalkulacja_taka_sytuacja dzielenie przez zero wysylamy wiadomosc ze stosownym statusem
        MESSAGE = 'OperaC>>'+pomocnicza[0]+'^StatuS>>div0'+'^'+pomocnicza[4]+'IdczaS>>'+str(time.time())+'^'
    else: # w innym przypadku tworzymy standardowy komunikat z wynikiem dzialania
        MESSAGE = 'OperaC>>'+pomocnicza[0]+'^StatuS>>ok^'+'LiczbA>>'+str(kalkulacja_taka_sytuacja(pomocnicza))+'^'+pomocnicza[4]+'IdczaS>>'+str(time.time())+'^'
    return MESSAGE

def komunikat_z_idsesji(s): #funkcja jako argument przyjmuje idsesji wygenerowane przez funkcje generuj_id_sesji, sluzy od tworzenia wiadomosci zawierajacej id sesji
    MESSAGE = 'OperaC>>config^StatuS>>null^IdentY>>' + str(s) + '^IdczaS>>' + str(time.time()) +'^'
    return MESSAGE

def watki(c):   #funkcja watki , sluzy do obslugi watkow, umozliwiajacych polaczenie i obsluge wielu klientow w jednym czasie. W jej wnetrzu odczytujemy i wysylamy komunikaty na lini serwer-klient
    pomoc_id=0
    if(pomoc_id==0):
        wygenerowane_idsesji = generuj_id_sesji()
        
        c.send(komunikat_z_idsesji(wygenerowane_idsesji).encode()) #wysylamy klientowi wiadomosc z idsesji
        pomoc_id+=pomoc_id
    while True:
        try:
            data = c.recv(BUFFER_SIZE) #odbieramy wiadomosc od klienta
        except:
            print('Istniejące połączenie zostało gwałtownie zamknięte przez zdalnego hosta') #gdy polaczenie z klientem zostaje nagle zerwane
            break
        if not data:
            break
        print(data.decode())
        return_data=sklec_komunikat_serwer(data); #łączymy komunikat
        c.send(return_data.encode()) #wysyłamy komunikat do klienta który zamienilimy na bajty
    c.close() #zamykamy polaczenie z klientem  
    print('Rozlaczono z klientem')

def generuj_id_sesji(num_bytes = 8):
    return secrets.token_hex(num_bytes) #generujemy unikalne id sesji za pomoca biblioteki secrets

def Main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #tworzymy socket serwera
    s.bind((TCP_IP, TCP_PORT)) #socketowy przypisujemy adres i port
    print("socket podlaczony do portu", TCP_PORT) 
    s.listen(liczba_klientow) #klient nasluchuje maksymalna liczbe klientow jaka zostala nastawiona
    print("socket nasluchuje") 
    while True:
        c, addr = s.accept() #akceptujmey polaczenie
        print('Podlaczony do:', addr[0], ':', addr[1])
        start_new_thread(watki, (c,)) #zaczynamy nowy watek, który obsługuje polaczenie z 1 klientem
    s.close() 

Main()