# -*- coding: utf-8 -*-
"""
Created on Fri Jul 04 12:10:33 2014

@author: aitor
"""

from socket import *
import thread

# Connection config
HOST, PORT = "localhost", 9999
BUFF = 1024

#*********************
#* Protocol messages *
#*********************
END_CHAR = '\0d'
# Client commands
CMD_REGISTER = "REGISTER" # id
CMD_FIND_GAME = "FIND_GAME" # id
CMD_DO_MOVE =  "DO_MOVE" # id movement(0..8)
CMD_GET_MOVE = "GET_MOVE" # id
# Response msgs
MSG_WAITING_PLAYERS = "WAITING_FOR_PLAYERS"
MSG_RIVAL = "RIVAL" # rival_id turn(0/1)
MSG_NOT_REGISTERED = "NOT_REGISTERED"
MSG_WAIT_FOR_MOVE = "WAIT_FOR_MOVE"
MSG_WAIT_FOR_RIVAL = "WAIT_FOR_RIVAL"
MSG_WAIT_FOR_TURN = "WAIT_FOR_TURN"
MSG_RIVAL_MOVE = "RIVAL_MOVE" # rival_id move
MSG_ACK = "ACK" # rival_id move


class TicTacToeServer:
    
    def __init__(self):
        self.waiting_players = []
        self.player1 = ''
        self.player1_move = ''
        self.player2 = ''
        self.player2_move = ''
        self.current_turn = ''
    
    def handler(self, clientsock,addr):
        data = clientsock.recv(BUFF)
        if data: 
            print repr(addr) + ' recv:' + repr(data)
            
            #*****************************************************************************
            # REGISTER  
            #*****************************************************************************
            if data.startswith(CMD_REGISTER):
                #REGISTER ID
                player_id = data.split(' ')[1]
                self.waiting_players.append(player_id)
                print "REGISTER %s" % (player_id)
                print "Total players: %i" % (len(self.waiting_players))
            
            #*****************************************************************************
            # FIND_GAME
            #*****************************************************************************
            elif data.startswith(CMD_FIND_GAME):
                #FIND_GAME ID
                print data.split(' ')
                player_id = data.split(' ')[1]
                print "FIND_GAME %s" % (player_id)

                if self.player2 == player_id: # When doing it randomly it will not be player2
                    print "Turn already assigned."
                    # Tell player1 that he is the second to move and who his rival is
                    clientsock.send("%s %s %i%s" % (MSG_RIVAL, self.player1, 1, END_CHAR))
                    
                elif self.player1 == player_id: # When doing it randomly it will not be player1
                    print "Turn already assigned."                    
                    # Tell player1 that he is the first to move and who his rival is
                    clientsock.send("%s %s %i%s" % (MSG_RIVAL, self.player2, 0, END_CHAR)) 
                    
                    
                elif player_id not in self.waiting_players:
                    print 'Player has to register first.'
                    clientsock.send(MSG_NOT_REGISTERED + END_CHAR)
                    
                
                elif len(self.waiting_players) > 1: 
                    print "Assigning turn."
                    #TODO do this randomly
                    self.player1 = player_id
                    self.current_turn = self.player1
                    # Find the second player
                    for player in self.waiting_players:
                        if player != player_id:
                            self.player2 = player
                            break
                        
                    # Remove assigned players
                    self.waiting_players.remove(self.player1)
                    self.waiting_players.remove(self.player2)
                    clientsock.send("%s %s %i%s" % (MSG_RIVAL, self.player2, 0, END_CHAR))                                     
                else:
                    print "Wait for players."
                    clientsock.send(MSG_WAITING_PLAYERS + END_CHAR)
           
            #*****************************************************************************
            # DO_MOVE  
            #*****************************************************************************
            elif data.startswith(CMD_DO_MOVE):
                # DO_MOVE id movement
                
                player_id = data.split(' ')[1]
                move = data.split(' ')[2]
                print 'Player:', player_id
                print 'Move:', move
            
                print 'Pre move'
                print '-Turn:', self.current_turn
                print '-Player 1:', self.player1, self.player1_move
                print '-Player 2:', self.player2, self.player2_move
                
                if self.current_turn == player_id:
                    if self.player2 == player_id:
                        if self.player2_move != '':
                            print "Previous move not retrieved"
                            clientsock.send(MSG_WAIT_FOR_RIVAL + END_CHAR)
                        else:
                            print "Storing move for player 2"
                            self.player2_move = move
                            self.current_turn = self.player1
                            clientsock.send(MSG_ACK + END_CHAR)
                            
                            
                    elif self.player1 == player_id:
                        if self.player1_move != '':
                            print "Previous move not retrieved"
                            clientsock.send(MSG_WAIT_FOR_RIVAL + END_CHAR)
                        else:
                            print "Storing move for player 1"
                            self.player1_move = move
                            self.current_turn = self.player2
                            clientsock.send(MSG_ACK + END_CHAR)
                    
                    print 'Post move'
                    print '-Turn:', self.current_turn                    
                    print '-Player 1:', self.player1, self.player1_move
                    print '-Player 2:', self.player2, self.player2_move
                    
                else:
                    print "Not player's turn"
                    clientsock.send(MSG_WAIT_FOR_TURN + END_CHAR)
                    
            #*****************************************************************************
            # GET_MOVE  
            #*****************************************************************************
            elif data.startswith(CMD_GET_MOVE):
                # GET_MOVE id
                player_id = data.split(' ')[1]  
                
                print 'Pre get_move'
                print '-Turn:', self.current_turn
                print '-Player 1:', self.player1, self.player1_move
                print '-Player 2:', self.player2, self.player2_move
                
                if self.player1 != player_id:
                    if self.player1_move == '':
                        print "Waiting for player 1 move"
                        clientsock.send(MSG_WAIT_FOR_MOVE + END_CHAR)
                    else:
                        print "Sending player 1 move to player 2: ", self.player1_move
                        clientsock.send(MSG_RIVAL_MOVE + self.player1 + self.player1_move + END_CHAR)
                        self.player1_move = ''
                        
                elif self.player2 != player_id:
                    if self.player2_move == '':
                        print "Waiting for player 2 move"
                        clientsock.send(MSG_WAIT_FOR_MOVE + END_CHAR)
                    else:
                        print "Sending player 2 move to player 1:", self.player2_move
                        clientsock.send(MSG_RIVAL_MOVE + self.player2 + self.player2_move + END_CHAR)
                        self.player2_move = ''
                
                print 'Post get_move'
                print '-Turn:', self.current_turn
                print '-Player 1:', self.player1, self.player1_move
                print '-Player 2:', self.player2, self.player2_move
                

    
        #clientsock.close()
        print addr, "- closed connection" #log on console
        
    def start(self):
        ADDR = (HOST, PORT)
        serversock = socket(AF_INET, SOCK_STREAM)
        serversock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        serversock.bind(ADDR)
        serversock.listen(5)
        while True:
            print ''
            print '******* Listening on port %i *******' % (PORT)
            clientsock, addr = serversock.accept()
            print 'New connections:', addr
            thread.start_new_thread(self.handler, (clientsock, addr))

if __name__=='__main__':
    server = TicTacToeServer()
    server.start()
    
    
    

#sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#sock.connect((HOST, PORT))
#sock.sendall("REGISTER 1 \n")
#sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#sock.connect((HOST, PORT))
#sock.sendall("REGISTER 2 \n")
#sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#sock.connect((HOST, PORT))
#sock.sendall("FIND_GAME 1 \n")
#sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#sock.connect((HOST, PORT))
#sock.sendall("FIND_GAME 2 \n")
#sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#sock.connect((HOST, PORT))
#sock.sendall("DO_MOVE 1 4 \n")
#sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#sock.connect((HOST, PORT))
#sock.sendall("GET_MOVE 2 \n")
#sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#sock.connect((HOST, PORT))
#sock.sendall("DO_MOVE 2 5 \n")
#sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#sock.connect((HOST, PORT))
#sock.sendall("GET_MOVE 1 \n")
#
#sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#sock.connect((HOST, PORT))
#sock.sendall("DO_MOVE 2 5 \n")