const express = require('express');
const router = express.Router();
const db = require('../models');
const { isLoggedIn } = require('./middlewares');

//프로필 불러오기
router.get('/load-profile', isLoggedIn, async (req,res, next) => {
    try{
        const user = req.user;
        res.json(user);
    } catch (error) {
        console.error(error);
        return next(error);
    }
});

//닉네임 수정
router.put('/modify', isLoggedIn, async (req, res, next) => {
    try {
      await db.User.update({
        nickname: req.body.nickname,
      }, {
        where: {
          id:req.user.id,
        }
      });
      res.redirect('/');
    } catch (error) {
      console.error(error);
      next(error);
    }
  });


module.exports = router;