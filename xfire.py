#!/usr/bin/env python

class User:
    def __init__(self, name, nick, id):
        self.name = name
        self.nick = nick
        self.id = id

class Packet:
    def __init__(self, id):
        self.attribCount = 0
        self.contents = ""
        self.id = id

    def addStringAttribute(self, key, value):
        self.attribCount += 1
        dataSize = 1 + int(len(value)/256)
        self.contents += chr(len(key))
        self.contents += key
        self.contents += chr(1) #Datasize?
        self.contents += chr(len(value))
        self.contents += chr(0)
        self.contents += value

    def addIntegerAttribute(self, key, value, extraValue=0, extraExtraValue=0, extraExtraExtraValue=0):
        self.attribCount += 1
        self.contents += chr(len(key))
        self.contents += key
        self.contents += chr(2)
        self.contents += chr(value)
        self.contents += chr(extraValue) + chr(extraExtraValue) + chr(extraExtraExtraValue)
    def addBooleanAttribute(self, key, value):
        self.attribCount += 1
        self.contents += chr(len(key))
        self.contents += key
        self.contents += chr(1)
        self.contents += chr(value)
        self.contents += chr(0)



    def get(self):
        out = chr(self.id) + chr(0) + chr(self.attribCount) + self.contents
        out = chr((len(out) + 2) % 256) + chr(int((len(out) + 2) / 256)) + out
        return out


normalCharacters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
def printHex(s):
    out = ""
    start = 0
    for c in s:
        code = ord(c)
        out += hex(code)[2:] + "  "
        if len(hex(code)[2:]) == 1:
            out += " "
        start += 1
        if start % 16 == 0:
            out += ",   "
            for i in range(start-16, start):
                if s[i] in normalCharacters:
                    out += s[i]
                else:
                    out += "."
            out += "\n"
    print out

import socket
TCP_IP = 'IPHERE'
TCP_PORT = 25999
BUFFER_SIZE = 1024  # Normally 1024, but we want fast response
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)
conn, addr = s.accept()
print 'Connection address:', addr
i = 0
while 1:
    data = conn.recv(BUFFER_SIZE)
    if not data: break
    print "received data:"
    #print data
    packed = ""
    for c in str(data):
        packed += str(ord(c)) + ", " + c + "  "
    #print packed
    printHex(data)
    print "Received length: " + str(len(data))
    print "------"
    i += 1
    if i == 1:
        saltPacket = Packet(128)
        saltPacket.addStringAttribute("salt", "5853ab14df6d90744943734beee321f09b5eaf41")
        conn.send(saltPacket.get())
    if i == 2000: #Incorrect Login Packet. The reason integer describes the error.
        incorrectLoginPacket = Packet(129)
        incorrectLoginPacket.addIntegerAttribute("reason", 0)
        conn.send(incorrectLoginPacket.get())
    if i == 3: #Login packet, god knows what these parameters mean but they work
        packet = Packet(130)
        packet.addIntegerAttribute("userid", 4, 7, 2)

        packet.contents += chr(3) + "sid" + chr(3) + "1234123412341234"
        packet.attribCount += 1

        packet.addStringAttribute("nick", "Din mamma")
        packet.addIntegerAttribute("status", 3)
        packet.addBooleanAttribute("dlset", 0)
        packet.addBooleanAttribute("p2pset", 0)
        packet.addBooleanAttribute("clntset", 0)
        packet.addIntegerAttribute("minrect", 1)
        packet.addIntegerAttribute("maxrect", 84, 03)
        packet.addIntegerAttribute("ctry", 83, 02)

        packet.addIntegerAttribute("n1", int("3C",16), int("B2",16), int("58",16), int("D0",16))
        packet.addIntegerAttribute("n2", int("3D",16), int("B2",16), int("58",16), int("D0",16))
        packet.addIntegerAttribute("n3", int("3E",16), int("B2",16), int("58",16), int("D0",16))
        packet.addIntegerAttribute("pip", int("9C",16), int("A5",16), int("80",16), int("5F",16))

        packet.addStringAttribute("salt", "5853ab14df6d90744943734beee321f09b5eaf41")
        packet.addStringAttribute("reason", "Josh Turner")

        print "Sending the login"
        conn.send(packet.get())
        #printHex(packet.get())
    if i == 4: #
        packet = Packet(131)
        numFriends = 1
        friends = []
        friends.append(User("Fullname", "Nick", 5))


        packet.attribCount += 3

        packet.contents += chr(len("friends")) + "friends" + chr(4) + chr(1) + chr(numFriends)
        for i in range(numFriends):
            packet.contents += chr(0) + chr(len(friends[i].name)) + chr(0) + friends[i].name

        packet.contents += chr(len("nick")) + "nick" + chr(4) + chr(1) + chr(numFriends)
        for i in range(numFriends):
            packet.contents += chr(0) + chr(len(friends[i].nick)) + chr(0) + friends[i].nick

        packet.contents += chr(len("userid")) + "userid" + chr(4) + chr(2) + chr(numFriends) + chr(0)
        for i in range(numFriends):
            packet.contents += chr(friends[i].id) + chr(0) + chr(0) + chr(0)
        conn.send(packet.get())
conn.close()
