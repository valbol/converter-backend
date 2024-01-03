import jwt, datetime, os
from flask import Flask, request 
from flask_mysqldb import MySQL
import logging


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s')

server = Flask(__name__)
mysql = MySQL(server)

#config
server.config["MYSQL_HOST"] = os.environ.get("MYSQL_HOST")
server.config["MYSQL_USER"] = os.environ.get("MYSQL_USER")
server.config["MYSQL_PASSWORD"] = os.environ.get("MYSQL_PASSWORD")
server.config["MYSQL_DB"] = os.environ.get("MYSQL_DB")
server.config["MYSQL_PORT"] = int(os.environ.get("MYSQL_PORT"))

@server.route("/login", methods=["POST"])
def login():
  auth = request.authorization
  if not auth:
    return "missing credentials", 401
  
  # Check db for username and pass 
  cur = mysql.connection.cursor()
  res = cur.execute(
    'SELECT email, password FROM user WHERE email=%s', (auth.username,)
  )
  if res > 0:
    user_row = cur.fetchone()
    email = user_row[0]
    password = user_row[1]

    if auth.username != email or auth.password != password:
      return 'invalid credentials', 401
    else:
      return createJWT(auth.username, os.environ.get('JWT_SECRET'), True)
  else: 
      return 'invalid credentials', 401

def createJWT(username, secret, authz):
  return jwt.encode(
    {
      "username": username,
      "exp": datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(days=1),
      "iat": datetime.datetime.utcnow(),
      "admin":authz
    },
    secret,
    algorithm='HS256'
  )
     
@server.route('/validate', methods=['POST'])
def validate():
  encoded_jwt = request.headers['Authorization']
  
  if not encoded_jwt:
    return 'missing credentials', 401
  
  encoded_jwt = encoded_jwt.split(" ")[1]
  logging.info(f"jwt={encoded_jwt}")  
  
  try:
    decoded = jwt.decode(
      encoded_jwt, os.environ.get('JWT_SECRET'), algorithms=["HS256"]
    )
    print(decoded)
  except jwt.ExpiredSignatureError:
    print("Token has expired.")
  except jwt.InvalidTokenError:
    print("Invalid token.")
  except Exception as e:
    logging.exception(f"An error occurred: {str(e)}")
    return "not authorized", 403
  
  return decoded, 200
    
  
if __name__ == "__main__":
  # 0.0.0.0 - we tell our flask server to listen to all available ip's, that is the way so spin off on a docker machine
  # as ips changing, also if we dont configure it will default to localhost, and its not accessible from the outside
  server.run(host="0.0.0.0" ,port=5000)