const express = require('express');
const router = express.Router();
const db = require('../models');
const { isLoggedIn } = require('./middlewares');

//상품 불러오기
router.get('/load', isLoggedIn, async (req,res, next) => {
    try{
        const item = await db.Store.findAll();
        res.json(item);
    } catch (error) {
        console.error(error);
        return next(error);
    }
});

//상품 교환
router.put('/exchange', isLoggedIn, async (req,res, next) => {
    try{
        const point_earning = await db.Point_earning.findAll({where: {userId: req.user.id}});
        const point_usage = await db.Point_usage.findAll({where: {userId: req.user.id}});
        const point = point_earning.length - point_usage.length;
        const itemId = req.body.itemId;
        const item = await db.Store.findOne({where: {id: itemId}});

        if (item.price <= point){
            //포인트 차감
            const points = req.user.points
            await db.User.update({
                points: points - item.price,
            }, {
                where: {
                    id: req.user.id,
                }
            });
            //사용내역 생성
            const point_usage = await db.Point_usage.create({
                itemId: itemId,
                price: item.price,
                userId: req.user.id,
                img: item.img,
            });
            await point_usage.save();
            //상품함에 상품 생성
            const earned_item = await db.Inventory.create({
                itemId: itemId,
                state: 1,
                userId: req.user.id,
            });
            await earned_item.save();
        };
        res.redirect('/');
    } catch (error) {
        console.error(error);
        next(error);
    }
});

module.exports = router;