# %%
# pip install fastapi uvicorn ollama openai python-multipart python-dotenv Pillow pymysql

import os
import io
import base64
from typing import Annotated
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import ollama
from openai import OpenAI
from PIL import Image
import database

# .env 로드
load_dotenv()

app = FastAPI()

# DB 초기화 (테이블 생성)
database.initDatabase()

# CORS 설정: 모든 Origin 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def encodeImageToBase64(imageBytes):
    """ 이미지 바이트를 Base64 문자열로 변환합니다. """
    return base64.b64encode(imageBytes).decode("utf-8")

@app.post("/analyze")
async def analyzeImage(
    image: Annotated[UploadFile, File()],
    question: Annotated[str, Form()]
):
    """ 
    업로드된 이미지를 분석하고 질문에 답하는 API입니다. 
    설정된 모델(OLLAMA 또는 GPT)을 사용하며 결과를 DB에 저장합니다.!!
    """
    try:
        # 파일 정보 및 바이트 읽기
        fileName = image.filename
        imageBytes = await image.read()
        
        # 환경 변수에서 모델 선택
        useModel = os.getenv("USE_MODEL", "OLLAMA")
        finalAnswer = ""
        
        # 1. OLLAMA 모드
        if useModel == "OLLAMA":
            # gemma4:e2b 모델 사용
            ollamaResponse = ollama.generate(
                model="gemma4:e2b",
                prompt=question,
                images=[imageBytes]
            )
            finalAnswer = ollamaResponse["response"]
            
        # 2. GPT 모드
        elif useModel == "GPT":
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            base64Image = encodeImageToBase64(imageBytes)
            
            gptResponse = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": question},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64Image}"
                                }
                            }
                        ]
                    }
                ]
            )
            finalAnswer = gptResponse.choices[0].message.content
            
        # 그 외 예외 케이스
        else:
            return {"success": False, "message": "설정된 USE_MODEL이 올바르지 않습니다. (OLLAMA 또는 GPT)"}
            
        # DB에 결과 저장
        dbResult = database.saveAnalysisResult(fileName, question, finalAnswer, useModel)
        
        if dbResult["success"] == True:
            return {
                "success": True,
                "model": useModel,
                "fileName": fileName,
                "question": question,
                "answer": finalAnswer
            }
        else:
            return {"success": False, "message": "DB 저장 실패: " + dbResult["message"]}
            
    except Exception as e:
        # 공통 에러 응답 포맷
        return {"success": False, "message": str(e)}

@app.get("/results")
async def getResults():
    """ 저장된 모든 분석 결과를 조회합니다. """
    try:
        results = database.fetchAllResults()
        return results
    except Exception as e:
        return {"success": False, "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


