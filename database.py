import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

def connectDatabase():
    """ MySQL 데이터베이스에 연결하고 연결 객체를 반환합니다. """
    try:
        dbConnection = pymysql.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            db=os.getenv("DB_NAME"),
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor
        )
        return dbConnection
    except Exception as e:
        errorResponse = {"success": False, "message": str(e)}
        print(errorResponse)
        return None

def executeQuery(queryString):
    """ SQL 쿼리를 실행합니다. """
    try:
        dbConn = connectDatabase()
        dbCursor = dbConn.cursor()
        dbCursor.execute(queryString)
        queryResult = dbCursor.fetchall()
        
        # 리스트 컴프리헨션 금지 규칙 준수
        processedData = []
        for i in range(0, len(queryResult)):
            processedData.append(queryResult[i])
            
        dbConn.commit()
        dbConn.close()
        return processedData
    except Exception as e:
        return {"success": False, "message": str(e)}
