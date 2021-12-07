require('dotenv').config();
const express = require('express');
const app = express();

const nodemailer = require('nodemailer');

app.use(express.urlencoded({
    extended: false
}));

app.use(express.json());

app.post('/sendEmail', async (req, res, next) => {

    const {
        to,
        path,
        fileName
    } = req.body;

    const newDate = new Date(Date.now());

    const from = "Human Detection App <tunincode@gmail.com>";
    const subject = `ATENÇÃO! Possível presença humana detectada às ${newDate.toLocaleTimeString()} de hoje`;
    const text = "O nosso sistema detectou uma possível presença humana. \n\nBaixe o vídeo enviado para verificar.";
    const html = "";

    const smtpConfig = {
        host: 'smtp.gmail.com',
        port: 465,
        secure: true, // use SSL
        auth: {
            user: process.env.SMTP_USER,
            pass: process.env.SMTP_PASS,
        }
    };

    try {
        
        const transporter = nodemailer.createTransport(smtpConfig);

        const info = transporter.sendMail({
            from: from,
            to: to,
            subject: subject,
            text: (text == null ? '' : text),
            html: (html == null ? '' : html),
            attachments: [
                {
                    filename: fileName,
                    path: `${path}/${fileName}`
                }
            ],
        });

        console.log('email enviado');

        res.json({
            message: 'email enviado'
        });

    } catch (error) {
        console.log(error);
    }

});

const PORT = 5000;
app.listen(PORT, () => {
    console.log('API Rodando na porta ' + PORT);
});
