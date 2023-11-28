import random
from .models import db, Questions, Ports
from . import app


random.seed()


def setPorts():
    dataforbase = [{'number': '21(FTP)', 'about': 'Протокол передачи файлов используется для передачи файлов между FTP-хостом/сервером и FTP-клиентом. При отсутствии надлежащей защиты FTP может быть использован злоумышленниками для загрузки вредоносных или конфиденциальных файлов.', 'isDanger': True},
                   {'number': '22(SSH)', 'about': 'Secure Shell используется для безопасного входа в систему, передачи файлов и выполнения команд.', 'isDanger': False},
                   {'number': '23(Telnet)', 'about': 'Telnet используется для двунаправленного интерактивного текстового взаимодействия. Telnet небезопасен, поскольку передает данные открытым текстом, включая пароли.', 'isDanger': True},
                   {'number': '25(SMTP)', 'about': 'Simple Mail Transfer Protocol используется для маршрутизации электронной почты между почтовыми серверами.', 'isDanger': False},
                   {'number': '53(DNS)', 'about': 'Система доменных имен используется для разрешения доменных имен. Через этот порт запрашивают информацию об IP адресе домена', 'isDanger': False},
                   {'number': '110(POP3)', 'about': 'Post Office Protocol версии 3 используется локальными почтовыми клиентами для получения электронной почты с удаленного сервера.', 'isDanger': False},
                   {'number': '143(IMAP)', 'about': ' Internet Message Access Protocol используется почтовыми клиентами для получения сообщений с почтового сервера.', 'isDanger': False},
                   {'number': '465(SMTPS)', 'about': 'SMTP-сервер (Secure SMTP) используется для безопасной отправки электронной почты.', 'isDanger': False},
                   {'number': '587(SMTP)', 'about': 'SMTP Mail Submission используется для отправки и ретрансляции электронной почты.', 'isDanger': False},
                   {'number': '990(FTPS)', 'about': 'FTP Secure используется для FTP-соединений по протоколу SSL/TLS. Защищенный протокол передачи файлов', 'isDanger': False},
                   {'number': '993(IMAPS)', 'about': 'IMAP Secure используется для защищенных IMAP-соединений. Сулжит для синхронизации и передачи почтовых сообщений', 'isDanger': False},
                   {'number': '995(POP3S)', 'about': 'POP3 Secure используется для защищенных POP3-соединений. Post Office Protocol версии 3 используется локальными почтовыми клиентами.', 'isDanger': False},
                   {'number': '1433(MSSQL)', 'about': 'База данных управляемая через язык структурированных запросов. Microsoft SQL Server', 'isDanger': False},
                   {'number': '3306(MySQL)', 'about': 'Служба баз данных MySQL. База данных управляемая через язык структурированных запросов.', 'isDanger': False},
                   {'number': '19(Chargen)', 'about': 'Протокол генератора символов, служба пакета Internet Protocol Suite, используемая для тестирования и отладки. На рабочих машинах лучше не использовать, может быть использован злоумышленниками', 'isDanger': True},
                   {'number': '69(TFTP)', 'about': 'Тривиальный протокол передачи файлов, не имеет средств защиты и может быть использован, если его оставить открытым.', 'isDanger': True},
                   {'number': '135(RPC)', 'about': 'Удаленный вызов процедур, используется Windows для выполнения сетевых операций, может быть использован для несанкционированного удаленного доступа.', 'isDanger': True},
                   {'number': '137(NetBIOS)', 'about': 'Используется в старых версиях Windows для совместного доступа к файлам и принтерам, может быть использован, если не защищен должным образом.', 'isDanger': True},
                   {'number': '138(NetBIOS)', 'about': 'Используется в старых версиях Windows для совместного доступа к файлам и принтерам, может быть использован, если не защищен должным образом.', 'isDanger': True},
                   {'number': '139(NetBIOS)', 'about': 'Используется в старых версиях Windows для совместного доступа к файлам и принтерам, может быть использован, если не защищен должным образом.', 'isDanger': True},
                   {'number': '445(SMB)', 'about': 'Server Message Block, используемый для обмена файлами в Windows, может быть использован для несанкционированного доступа или атак с целью получения выкупа.', 'isDanger': True},
                   {'number': '515(LPD)', 'about': 'Line Printer Daemon, используемый для сетевой печати, может быть использован для печати произвольных файлов, если оставить его открытым.', 'isDanger': True},
                   {'number': '8080(HTTP-Proxy):', 'about': 'При отсутствии надлежащей защиты может быть использован для несанкционированного использования прокси-сервера или веб-атак.', 'isDanger': True},
                   {'number': '79(Finger)', 'about': 'Старый протокол, используемый для получения информации о пользователе или системе. Если его оставить открытым, он может раскрыть конфиденциальную информацию.', 'isDanger': True},
                   {'number': '111(RPCbind)', 'about': 'Службы удаленного вызова процедур (RPC) могут быть использованы для получения несанкционированного доступа к системе.', 'isDanger': True},
                   {'number': '8000(iRDMI)', 'about': 'Интерфейс Intel Remote Desktop Management Interface. Если оставить его открытым, он может быть использован для несанкционированного удаленного управления.', 'isDanger': True}
                   ]
    dataforbase_80_443 = [{'number': '80(HTTP)', 'about': 'Протокол передачи гипертекста используется для передачи гипертекста через Интернет. Позволяет получить интернет страницу и отобразить ее в браузере', 'isDanger': False},
                          {'number': '443(HTTPS)', 'about': 'Hypertext Transfer Protocol Secure используется для безопасного взаимодействия с веб-браузерами.', 'isDanger': False}]
    with app.app_context():
        if Ports.query.count() == 0:
            for data in dataforbase_80_443:
                question = Ports(number=data["number"], about=data["about"], isDanger=data['isDanger'], isAnswer=True)
                db.session.add(question)
            db.session.commit()
            for data in dataforbase:
                question = Ports(number=data["number"], about=data["about"], isDanger=data['isDanger'])
                db.session.add(question)
            db.session.commit()

setPorts()
