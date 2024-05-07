const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const { exec } = require('child_process');

const app = express();
const port = 3000;

const uploadDir = path.join(__dirname, 'uploads');
if (!fs.existsSync(uploadDir)){
    fs.mkdirSync(uploadDir);
}

const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    cb(null, uploadDir);
  },
  filename: function (req, file, cb) {
    cb(null, file.originalname);
  }
});

const upload = multer({ storage: storage });

app.use(express.static('public'));

app.post('/upload', upload.single('image'), (req, res) => {
  if (!req.file) {
    return res.status(400).send('No files were uploaded.');
  }
  
  // 업로드된 이미지 파일 이름
  const imageName = req.file.originalname;

  // 가상 환경 활성화 명령어
  const activateEnvCommand = 'conda activate ENV00';

  // 파이썬 파일 실행 명령어 (가상 환경 활성화 후 실행)
  const pythonScriptCommand = `python model.py uploads/"${imageName}"`;

  // 가상 환경 활성화 후 파이썬 스크립트 실행
  exec(`${activateEnvCommand} && ${pythonScriptCommand}`, (error, stdout, stderr) => {
    if (error) {
      console.error(`exec error: ${error}`);
      return res.status(500).send('Error executing Python script.');
    }
    console.log(`stdout: ${stdout}`);

    // stdout에서 예측값 추출
    const predictionRegex = /Prediction: \[\[(\d+\.\d+)\]\]/;
    const match = stdout.match(predictionRegex);
    const prediction = match ? parseFloat(match[1]) : null;
    console.log(prediction);

    if (prediction !== null) {
      // 파이썬 실행 결과를 클라이언트에게 반환
      res.send(`${prediction}`);
    } else {
      res.status(500).send('Error extracting prediction from stdout.');
    }
  });
});


app.listen(port, () => {
  console.log(`Server is running at http://localhost:${port}`);
});
