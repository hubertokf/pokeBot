from yowsup.layers.interface                           import YowInterfaceLayer, ProtocolEntityCallback
from yowsup.layers.protocol_messages.protocolentities  import TextMessageProtocolEntity
from yowsup.layers.protocol_receipts.protocolentities  import OutgoingReceiptProtocolEntity
from yowsup.layers.protocol_acks.protocolentities      import OutgoingAckProtocolEntity

import re
import sqlite3
import time
import random, string

class EchoLayer(YowInterfaceLayer):
    
    def randomword(self, length):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(length))

    @ProtocolEntityCallback("message")
    def onMessage(self, messageProtocolEntity):
        # receipt = OutgoingReceiptProtocolEntity(messageProtocolEntity.getId(), messageProtocolEntity.getFrom(), 'read', messageProtocolEntity.getParticipant())
        # self.toLower(receipt)

        # if messageProtocolEntity.getType() == "text":
        #     if messageProtocolEntity.getBody().startswith("!"):
        #         header = "*=== TARS PokeBot ===*\n\n"

        #         message = header

        #         outgoingMessageProtocolEntity = TextMessageProtocolEntity(
        #             message,
        #             to = messageProtocolEntity.getAuthor())
            
        #         self.toLower(outgoingMessageProtocolEntity)
        conn = sqlite3.connect('database.db')
        # send receipt otherwise we keep receiving the same message over and over
        time.sleep(2)
        receipt = OutgoingReceiptProtocolEntity(messageProtocolEntity.getId(), messageProtocolEntity.getFrom(), 'read', messageProtocolEntity.getParticipant())
        self.toLower(receipt)
        
        if messageProtocolEntity.getType() == "text":
    
            body = ""

            c = conn.cursor()
            userNumber = messageProtocolEntity.getAuthor().split('@')[0]
            c.execute('SELECT * FROM Users WHERE number={0}'.format(userNumber))
            user = c.fetchone()

            if user == None:
                c.execute("INSERT INTO Users ('number') values ('{0}')".format(userNumber))
                conn.commit()

            # print("=============================================================")
            # print(dir(messageProtocolEntity))
            # print("AUTHOR: "+messageProtocolEntity.getAuthor())
            # print("FROM: "+messageProtocolEntity.getFrom())
            # print("TO: "+str(messageProtocolEntity.getTo()).encode('utf-8'))
            # print("PARTICIPANT: "+str(messageProtocolEntity.getParticipant()).encode('utf-8'))
            # print("TYPE: "+messageProtocolEntity.getType())
            # print("Isgroup: "+str(messageProtocolEntity.isGroupMessage()).encode('utf-8'))
            # print("BODY: "+messageProtocolEntity.getBody())
            # print("=============================================================")
            if messageProtocolEntity.getBody().startswith("!"):
                command = messageProtocolEntity.getBody().split('!')[1]
                command = command.split(' ')
                #ações
                if command[0] == "registrar":
                    #!novaraid <local> <hora> <inimigo> <codigo>
                    if len(command) == 4:
                        c.execute("SELECT u.* from Users as u WHERE u.number == '{0}'".format(userNumber))
                        result = c.fetchone()
                        if len(result) != 0:
                            c.execute("UPDATE Users SET 'nickname' = '{0}', 'team' = '{1}','level' = '{2}' WHERE Users.number == '{3}'".format(command[1], command[2], command[3],userNumber))
                            conn.commit()

                            body = "Você foi registrado com sucesso {0}".format(command[1])
                        else:
                            body = "Erro, você não está nos conformes"
                    else:
                        body = "Para executar esta ação utilize esta sintaxe: \n!registrar <nickname> <time> <nível>"
                
                elif command[0] == "nova":
                    #!novaraid <local> <hora> <inimigo> <codigo>
                    if len(command) == 5:
                        c.execute("SELECT r.* from Raids as r WHERE r.code == '{0}'".format(command[4]))
                        result = c.fetchall()
                        if len(result) != 0:
                            body = "Uma raid com este código já existe"
                        else:
                            c.execute("INSERT INTO Raids ('location', 'time', 'enemy', 'code') values ('{0}','{1}','{2}','{3}')".format(command[1], command[2], command[3], command[4]))
                            conn.commit()
                            body = "Raid cadastrada com sucesso"
                    elif len(command) == 4:
                        code = self.randomword(4)
                        c.execute("SELECT r.* from Raids as r WHERE r.code == '{0}'".format(code))
                        result = c.fetchall()
                        if len(result) != 0:
                            code = self.randomword(4)
                        c.execute("INSERT INTO Raids ('location', 'time', 'enemy', 'code') values ('{0}','{1}','{2}','{3}')".format(command[1], command[2], command[3], code))
                        conn.commit()
                        body = "Raid cadastrada com sucesso"
                    else:
                        body = "Para executar esta ação utilize esta sintaxe: \n!novaraid <local> <hora> <inimigo> <codigo>\nSe o código não for fornecido, será gerado um randomico."
                
                elif command[0] == "listar":
                    #!listaraids
                    c.execute("SELECT r.* from Raids as r")
                    result = c.fetchall()
                    if len(result) != 0:
                        for row in result:
                            c.execute("SELECT p.*, u.* from Participants as p JOIN Users as u ON u.number == p.user WHERE p.raid == '{0}'".format(row[3]))
                            result2 = c.fetchall()

                            body = body+"*({4})* Raid codigo *{0}* contra o *{1}* as *{2}* no(a) *{3}* ".format(row[3],row[2], row[1], row[0],len(result2))

                            if len(result2) != 0:
                                for row2 in result2:
                                    body = body+"->{0} ({1}), {2} level {3}\n".format(row2[4], row2[3], row2[6], row2[7])
                                
                            body = body+"\n\n"
                    else:
                        body = "Nenhuma raid cadastrada"
                
                elif command[0] == "remover":
                    if len(command) == 2:
                        c.execute("SELECT r.* from Raids as r WHERE r.code == '{0}'".format(command[1]))
                        result = c.fetchall()
                        if len(result) == 0:
                            body = "Esta raid não existe"
                        else:
                            c.execute("SELECT r.* from Raids as r WHERE r.code == '{0}'".format(command[1]))
                            # c.execute("SELECT r.* from Raids as r WHERE r.code == '{0}' and r.owner == '{1}'".format(command[1],userNumber))
                            result = c.fetchall()
                            if len(result) == 0:
                                body = "Apenas o criador pode remover uma lista de raid"
                            else:
                                c.execute("DELETE FROM Raids WHERE code = '{0}'".format(command[1]))
                                conn.commit()
                                body = "Raid removida com sucesso"
                    else:
                        body = "Para executar esta ação utilize esta sintaxe: \n!removerraid <codigo>"
                
                elif command[0] == "entrar":
                    if len(command) == 2:
                        c.execute("SELECT p.* from Participants as p WHERE p.raid == '{0}' and p.user == '{1}'".format(command[1],userNumber))
                        result = c.fetchall()
                        if len(result) != 0:
                            body = "Você já está nesta lista"
                        else:
                            c.execute("INSERT INTO Participants ('raid', 'user') values ('{0}','{1}')".format(command[1],userNumber))
                            conn.commit()
                            body = "Acesso permitido"
                    else:
                        body = "Para executar esta ação utilize esta sintaxe: \n!entrarraid <codigo>"
                
                elif command[0] == "sair":
                    if len(command) == 2:
                        c.execute("SELECT p.* from Participants as p WHERE p.raid == '{0}' and p.user == '{1}'".format(command[1],userNumber))
                        result = c.fetchall()
                        if len(result) == 0:
                            body = "Você não está nesta lista"
                        else:
                            c.execute("DELETE FROM Participants WHERE  raid = '{0}' AND user = '{1}'".format(command[1],userNumber))
                            conn.commit()
                            body = "Você foi removido da lista da Raid {0}".format(command[1])
                    else:
                        body = "Para executar esta ação utilize esta sintaxe: \n!sairraid <codigo>"
                # Comandos cadastrados no banco
                else:
                    c.execute("SELECT c.label as command, r.text as response from Commands as c left join Responses as r on r.command == c.id where c.label == '{0}'".format(command[0]))
                    dbCommand = c.fetchone()
                    if dbCommand != None:
                        body = dbCommand[1]
                    else:
                        body = "Comando desconhecido"

                header = "*=== TARS PokeBot ===*\n\n"

                message = header+body

                time.sleep(2)
                outgoingMessageProtocolEntity = TextMessageProtocolEntity(
                    message,
                    to = messageProtocolEntity.getAuthor())
                
                self.toLower(outgoingMessageProtocolEntity)
        
        conn.close()

    @ProtocolEntityCallback("receipt")
    def onReceipt(self, entity):
        ack = OutgoingAckProtocolEntity(entity.getId(), "receipt", entity.getType(), entity.getFrom())
        self.toLower(ack)