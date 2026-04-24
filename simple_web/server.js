/**
 * npm install express multer axios cors form-data
 * node server.js 명령어로 실행 (3000 포트)
 */

const express = require('express');
const multer = require('multer');
const axios = require('axios');
const cors = require('cors');
const path = require('path');
const FormData = require('form-data');

const app = express();
const PORT = 3000;

// 미들웨어 설정
app.use(cors());
app.use(express.json());
app.use(express.static('public')); // public 폴더의 정적 파일 제공

// Multer 설정: 메모리에 파일 임시 저장
const storage = multer.memoryStorage();
const upload = multer({ storage: storage });

/**
 * 프론트엔드로부터 이미지와 질문을 받아 FastAPI 서버로 전달하는 Proxy API
 */
app.post('/proxy/analyze', upload.single('image'), async (req, res) => {
    try {
        const { question } = req.body;
        const file = req.file;

        if (!file) {
            return res.status(400).json({ success: false, message: "이미지 파일이 없습니다." });
        }

        // FastAPI 서버로 보낼 FormData 생성
        const formData = new FormData();
        formData.append('image', file.buffer, {
            filename: file.originalname,
            contentType: file.mimetype,
        });
        formData.append('question', question);

        // FastAPI 서버(8000 포트)로 요청 전달
        const response = await axios.post('http://localhost:8000/analyze', formData, {
            headers: {
                ...formData.getHeaders()
            }
        });

        // FastAPI 서버의 결과를 클라이언트에 반환
        res.json(response.data);

    } catch (error) {
        console.error("Error during proxy request:", error.message);
        res.status(500).json({
            success: false,
            message: "서버 통신 중 에러가 발생했습니다: " + error.message
        });
    }
});

// 서버 시작
app.listen(PORT, () => {
    console.log(`Web server is running at http://localhost:${PORT}`);
});
