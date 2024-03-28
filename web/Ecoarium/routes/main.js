const express = require('express');
const router = express.Router();
const db = require('../models');
const { isLoggedIn } = require('./middlewares');

//포인트 불러오기
router.get('/loadpoint', isLoggedIn, async (req,res, next) => {
    try{
        const points = req.user.points
        res.json(points);
    } catch (error) {
        console.error(error);
        return next(error);
    }
});

//포인트 생성 (디버깅용 임시)
router.get('/createpoint', isLoggedIn, async (req,res, next) => {
    try{
        //포인트 + 1
        const points = req.user.points
        await db.User.update({
            points: points + 1,
        }, {
            where: {
              id: req.user.id,
            }
        });
        //획득 기록 생성
        await db.Point_earning.create({
            location: "성결대점",
            type: 1,
            state: 1,
            userId: req.user.id,
        });
        res.redirect('/');
    } catch (error) {
        console.error(error);
        return next(error);
    }
});

//바코드 번호 생성
router.get('/createbarcode', isLoggedIn, async (req,res, next) => {
    try{
        const year = req.user.createdAt.getFullYear() % 100;
        const id = req.user.id;
        const number = parseInt((year*10000 + id%10000) * 10000000000 + Math.random()*10000000000);
        await db.User.update({
            barcode: number,
            }, {
                where: {
                    Id: req.user.id,
                }
        });
        res.json(number);
    } catch (error) {
        console.error(error);
        return next(error);
    }
});


module.exports = router;
