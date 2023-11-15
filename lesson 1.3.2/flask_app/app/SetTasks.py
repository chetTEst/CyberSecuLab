import random
from .models import db, Questions, Ports
from . import app


random.seed()


def setQuestions():
    dataforbase = [
        {"filename": 'Аутентификация.docx', "hash": '091a5ab424015f4c818f5230a9df74cc006396f82dd68afcb91961944a388b1e',
         "type": False},
        {"filename": 'Защита.docx', "hash": '46f2df680bad4290ae2470659a730d3c56aaa3ecf7687597e81f8e803d06ea93',
         "type": False},
        {"filename": 'Угроза_безопасности.docx',
         "hash": '0a03d7015f9c1bf940e6fed566bc1812c5c8d317dda99cc6d5c546ffe180b1b5', "type": False},
        {"filename": 'Шифрование.docx', "hash": '4a9bc03b9766f9aee039cf77701881ba84dde1b43c9418052d5bc7a04cb53ad0',
         "type": False},
        {"filename": 'Animals.com', "hash": '3c1b6a4ab285737b3049d693da03121a1fd697faba9d7d9822c3ff0eb2ee92b9',
         "type": False},
        {"filename": 'Arctwo.exe', "hash": '8e64a82675a4b94e47e2fb67325e42a0b7ec04f3c130af891e93db29d6a46abf',
         "type": False},
        {"filename": 'Basica.com', "hash": 'c26b99a2b211378552a153d1029c845aae2900d09fc92733d546fca70ddba9a5',
         "type": False},
        {"filename": 'bopinst205.exe', "hash": '50a59e36cbf9661f4f3daddb3d061aab74f5f07ee1277581f39bbeb9e7bf21a3',
         "type": False},
        {"filename": 'Bowling.exe', "hash": '3642a7208a98f4f20485c258719a49ae121a23c2048779706101035b198849ca',
         "type": False},
        {"filename": 'Det.exe', "hash": '9d5719560a4dbe2c01706c2834aa0dc09c073ca459d433ec953aa0dd0d150272',
         "type": False},
        {"filename": 'DOSBox0.74.exe', "hash": 'a9e270217d12867c2609d9423d1b2ed83fcf7cd08aeeee3ab09a4afdf9e9418e',
         "type": False},
        {"filename": 'screenscrew.exe', "hash": 'e03520794f00fb39ef3cfff012f72a5d03c60f89de28dbe69016f6ed151b5338',
         "type": True},
        {"filename": 'popup.exe', "hash": 'f8f7b5f20ca57c61df6dc8ff49f2f5f90276a378ec17397249fdc099a6e1dcd8',
         "type": True},
        {"filename": 'flasher.exe', "hash": '30676ad5dc94c3fec3d77d87439b2bf0a1aaa7f01900b68002a06f11caee9ce6',
         "type": True},
        {"filename": 'crazy_caps.exe', "hash": '6820c71df417e434c5ad26438c901c780fc5a80b28a466821b47d20b8424ef08',
         "type": True},
        {"filename": 'avoid.exe', "hash": '3ac8cc58dcbceaec3dab046aea050357e0e2248d30b0804c738c9a5b037c220d',
         "type": True},
        {"filename": 'vi4a.apk', "hash": 'b0ff5690c31f160808a869a14fa55f9e38c82de81cf98b895badc88c997ee45c',
         "type": True},
        {"filename": 'loveyou.exe', "hash": '1edc8771e2a1a70023fc9ddeb5a6bc950380224b75e8306eb70da8eb80cb5b71',
         "type": True},
        {"filename": 'IconDance.exe', "hash": 'a4b6e53453d1874a6f78f0d7aa14dfafba778062f4b85b42b4c1001e1fc17095',
         "type": True},
        {"filename": 'AntiVirus.bat', "hash": 'de68a7c44cf968dd891996dfdd07ffbdb3d425b45ba90a6a8b7ff4ffa01e837f',
         "type": True},
        {"filename": 'Fork.bat', "hash": 'faf1303a43186f1a010bb88955ed1203d8a6a33cef9a21be00131f407c722ea7',
         "type": True},
        {"filename": 'eicar.com', "hash": '275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f',
         "type": True},
        {"filename": 'WindowsUpdate.exe', "hash": '0fda176b199295f72fafc3bc25cefa27fa44ed7712c3a24ca2409217e430436d',
         "type": True}]

    with app.app_context():
        if Questions.query.count() == 0:
            for data in dataforbase:
                question = Questions(filename=data["filename"], hash=data["hash"], isVirus=data['type'])
                db.session.add(question)
            db.session.commit()

def setPorts():
    dataforbase = [{'number': '21(FTP)', 'about': 'Протокол передачи файлов используется для передачи файлов между FTP-хостом/сервером и FTP-клиентом. При отсутствии надлежащей защиты FTP может быть использован злоумышленниками для загрузки вредоносных или конфиденциальных файлов.', 'isDanger': True},
                   {'number': '22(SSH)', 'about': 'Secure Shell используется для безопасного входа в систему, передачи файлов и выполнения команд.', 'isDanger': False},
                   {'number': '23(Telnet)', 'about': 'Telnet используется для двунаправленного интерактивного текстового взаимодействия. Telnet небезопасен, поскольку передает данные открытым текстом, включая пароли.', 'isDanger': True},
                   {'number': '25(SMTP)', 'about': 'Simple Mail Transfer Protocol используется для маршрутизации электронной почты между почтовыми серверами.', 'isDanger': False},
                   {'number': '53(DNS)', 'about': 'Система доменных имен используется для разрешения доменных имен. Через этот порт запрашивают информацию об IP адресе домена', 'isDanger': False},
                   {'number': '80(HTTP)', 'about': 'Протокол передачи гипертекста используется для передачи гипертекста через Интернет. Позволяет получить интернет страницу и отобразить ее в браузере', 'isDanger': False},
                   {'number': '110(POP3)', 'about': 'Post Office Protocol версии 3 используется локальными почтовыми клиентами для получения электронной почты с удаленного сервера.', 'isDanger': False},
                   {'number': '143(IMAP)', 'about': ' Internet Message Access Protocol используется почтовыми клиентами для получения сообщений с почтового сервера.', 'isDanger': False},
                   {'number': '443(HTTPS)', 'about': 'Hypertext Transfer Protocol Secure используется для безопасного взаимодействия с веб-браузерами.', 'isDanger': False},
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
    with app.app_context():
        if Ports.query.count() == 0:
            for data in dataforbase:
                question = Ports(number=data["number"], about=data["about"], isDanger=data['isDanger'])
                db.session.add(question)
            db.session.commit()


setQuestions()
setPorts()
