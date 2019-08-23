from modbus_rtu_v3 import Api
import argparse
import textwrap




parser = argparse.ArgumentParser(
    prog='PROG',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=textwrap.dedent('''\
        Main program do osblugi Api dla modbasa rtu.
        --------------------------------------------------------
            Musi sie znajdowac w tym samym folderze co modbus_rtu_v3
            Za pomoca parsera odczytuje opcje wprowadzane w terminal.
            Pomoc dla opcji po wpisaniu w terminal:
            python modbus_master.py -h
            !!!!Wersja zmiany adresu dla czujnikow appr!!!!
        --------------------------------------------------------
        '''))


parser.add_argument('-c', action='store', dest='port',
                    help='Port')

parser.add_argument('-b', action='store', dest='speed', default=9600, type=int,
                    help='Predkość połączenia def: 9600')

parser.add_argument('-u', action='append', dest='unit',
                    default=[],
                    help='Adres Modbus ex:(-u 1,2,3,4)', )

parser.add_argument('-s', action='store', dest='reg_start', type=int,
                    help='Start zapytania')

parser.add_argument('-l', action='store', dest='reg_lenght', type=int,
                    help='Długość zapytania')

parser.add_argument('-i', action='store_const', dest='data_type',
                    const='ui16',
                    help='Rejetry typu int')

parser.add_argument('-f', action='store_const', dest='data_type',
                    const='float',
                    help='Rejetry typu float')

parser.add_argument('-q', action='store', dest='qty', default=3, type=int,
                    help='Ilosc powtorzen def: 3')

parser.add_argument('-aa', action='store_true', default=False,
                    dest='app_add_change',
                    help='Uruchominie zmiany adresu dla appar')

parser.add_argument('-af', action='store_true', default=False,
                    dest='fif_add_change',
                    help='Uruchominie zmiany adresu dla fif')

parser.add_argument('-as', action='store_true', default=False,
                    dest='app_speed_change',
                    help='Uruchominie zmiany predkosci dla appr')

parser.add_argument('-o', action='store', dest='valOld',
                    help='Stara wartosc ')

parser.add_argument('-n', action='store', dest='valNew',
                    help='Nowa wartosc')

parser.add_argument('--version', action='version', version='%(prog)s 1.0')

results = parser.parse_args()  # pobranie rezultatow parsera

add_change_app = results.app_add_change  # sprawdzenie co chemy zrobic ( odczytanie rej, czy zmiana adresu )
add_change_fif = results.fif_add_change  # sprawdzenie co chemy zrobic ( odczytanie rej, czy zmiana adresu )
speed_change_app = results.app_speed_change  # sprawdzenie co chemy zrobic ( odczytanie rej, czy zmiana adresu )



units=[]
for i in results.unit[0].split(','):
    units.append(int(i))
speed = results.speed
port=results.port



if add_change_app == False and add_change_fif == False and speed_change_app == False:

    print(
        "\n     Data:\nspeed = {},\nunit = {},\nreg_start= {},\nreg_lenght= {},\nreg_type= {},\nqty= {},".format(
            results.speed, units,
            results.reg_start,
            results.reg_lenght,
            results.data_type,
            results.qty))


    unit = units
    reg_start = results.reg_start
    reg_lenght = results.reg_lenght
    data_type = results.data_type
    qty = results.qty
    rtu = Api(speed=speed, port=port)
    if data_type == 'ui16':
        readholding = rtu.read_holding(unit, reg_start, reg_lenght, data_type, qty)
    elif data_type == 'float':
        readinput = rtu.read_input(unit, reg_start, reg_lenght, data_type, qty)

elif add_change_app == True or add_change_fif == True or speed_change_app == True:

    valNew = int(results.valNew)
    if add_change_app == True:
        rtu = Api(speed=speed, port=port)
        add = rtu.appar_add_change(units[0],units[0], valNew, 'ui16')
    elif add_change_fif == True:
        rtu = Api(speed=speed,port=port)
        add = rtu.fif_add_change(units[0],units[0], valNew, 'ui16')
    elif speed_change_app == True:
        valOld = int(results.valOld)
        rtu = Api(speed=valOld,port=port)
        add = rtu.appar_speed_change(units[0], valOld, valNew, 'ui16')
        rtu=Api(speed=valNew,port=port)
        check=rtu.read_holding(units,0,30,'ui16',5)


if __name__ == '__main__':
    parser.parse_args('-h')

