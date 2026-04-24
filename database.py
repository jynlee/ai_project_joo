import pymysql
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

def connectDatabase():
    """ MySQL 데이터베이스에 연결하고 연결 객체를 반환합니다.! """
    try:
        dbConnection = pymysql.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            db=os.getenv("DB_NAME"),
            port=int(os.getenv("DB_PORT")),
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor
        )
        return dbConnection
    except Exception as e:
        return {"success": False, "message": str(e)}

def initDatabase():
    """ 분석 결과를 저장할 테이블이 없으면 생성합니다. """
    try:
        dbConn = connectDatabase()
        if isinstance(dbConn, dict):
            return dbConn
            
        dbCursor = dbConn.cursor()
        createTableQuery = """
        CREATE TABLE IF NOT EXISTS analysis_results (
            id INT AUTO_INCREMENT PRIMARY KEY,
            fileName VARCHAR(255),
            question TEXT,
            answer TEXT,
            modelName VARCHAR(50),
            createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        dbCursor.execute(createTableQuery)
        dbConn.commit()
        dbConn.close()
        return {"success": True, "message": "테이블 초기화 성공"}
    except Exception as e:
        return {"success": False, "message": str(e)}

def saveAnalysisResult(fileName, question, answer, modelName):
    """ 분석 결과(파일명, 질문, 답변, 사용 모델)를 DB에 저장합니다. """
    try:
        dbConn = connectDatabase()
        if isinstance(dbConn, dict):
            return dbConn
            
        dbCursor = dbConn.cursor()
        insertQuery = "INSERT INTO analysis_results (fileName, question, answer, modelName) VALUES (%s, %s, %s, %s)"
        insertValues = (fileName, question, answer, modelName)
        
        dbCursor.execute(insertQuery, insertValues)
        dbConn.commit()
        dbConn.close()
        
        return {"success": True, "message": "데이터 저장 성공"}
    except Exception as e:
        return {"success": False, "message": str(e)}

def fetchAllResults():
    """ 저장된 모든 분석 결과를 조회합니다. """
    try:
        dbConn = connectDatabase()
        if isinstance(dbConn, dict):
            return dbConn
            
        dbCursor = dbConn.cursor()
        selectQuery = "SELECT * FROM analysis_results ORDER BY createdAt DESC"
        dbCursor.execute(selectQuery)
        queryResult = dbCursor.fetchall()
        
        # 리스트 컴프리헨션 사용 금지: for i in range 형식을 사용
        processedData = []
        for i in range(0, len(queryResult)):
            processedData.append(queryResult[i])
            
        dbConn.close()
        return {"success": True, "data": processedData}
    except Exception as e:
        return {"success": False, "message": str(e)}
