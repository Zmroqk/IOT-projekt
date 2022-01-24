import csv
from getpass import getpass
import os
from uuid import uuid4
import database as db

session: db.alchemyOrm.Session = db.Session()

def print_logs_to_csv():
   print('Printed to logs.csv')
   with open('logs.csv', 'w', newline='') as csvfile:
      writer = csv.writer(csvfile, dialect='excel')
      logs = session.query(db.Log).all()
      writer.writerow(['id', 'card_id', 'timestamp', 'log'])
      for log in logs:
         writer.writerow([log.id, log.card_id, log.timestamp, log.log])

def login():
   email = input('Email: ')
   found_user: db.User = session.query(db.User).filter(db.User.email == email).first()
   if found_user is None:
      print(f'Incorrect email')
   else:
      if found_user.passwordHash is None:
         newPassword = getpass('No password set, please set password: ')
         found_user.passwordHash = newPassword
         session.commit()
      password = getpass('Password: ')
      if found_user.passwordHash == password:
         print('Logged in')
         return found_user
      print('Invalid password')
      return None

def increaseBalance(user: db.User):
   increaseAmount = input('Increase account balance by: ')
   if (float(increaseAmount) > 0):
      user.balance += float(increaseAmount) * 100
      session.commit()
      print(f'Increased account balance by {float(increaseAmount)}. Account balance: {user.balance/100:.2f}')
   else:
      print('Increase amount must be larger than 0')

def showBalance(user: db.User):
   print(f'Your balance: {float(user.balance)/100}')

def registerUser():
   user = db.User()
   user.email = input('Email: ')
   session.add(user)
   session.commit()
   print(f'Registered user: {user.id}')

def registerTerminal():
   terminal = db.Terminal()
   terminal.terminalName = input('Terminal name: ')
   terminal.rentalCount = int(input('Available rentals: '))
   terminal.passwordHash = str(uuid4())
   session.add(terminal)
   session.commit()
   print(f'Registered terminal: {terminal.id} with auto generated password: {terminal.passwordHash}')

def registerRegistrationTerminal():
   terminal = db.RegisterTerminal()
   terminal.terminalName = input('Terminal name: ')
   terminal.passwordHash = str(uuid4())
   session.add(terminal)
   session.commit()
   print(f'Registered terminal: {terminal.id} with auto generated password: {terminal.passwordHash}')


def startApp():
   user: db.User = None
   while(True):
      cmd = input('Podaj komende: ')
      if user is None and cmd == 'login':
         user = login()
      elif user is not None and cmd == 'logout':
         print('Logged out')
         user = None
      elif user is not None and user.isAdmin and cmd == 'print-logs':
         print_logs_to_csv()
      elif user is not None and cmd == 'increase-balance':
         increaseBalance(user)
      elif user is not None and cmd == 'show-balance':
         showBalance(user)
      elif user is not None and user.isAdmin and cmd == 'register-user':
         registerUser()
      elif user is not None and user.isAdmin and cmd == 'register-terminal':
         registerTerminal()
      elif user is not None and user.isAdmin and cmd == 'register-register-terminal':
         registerRegistrationTerminal()
      elif cmd == 'clear':
         os.system('cls' if os.name == 'nt' else 'clear')
      else:
         print('Command not found')