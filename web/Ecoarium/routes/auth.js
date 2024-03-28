const express = require('express');
const passport = require('passport');
const bcrypt = require('bcrypt');
const db = require('../models');
const { isLoggedIn, isNotLoggedIn } = require('./middlewares');
const { User } = require('../models');
require('dotenv').config();
const router = express.Router();

//회원가입 라우터
router.post('/join', isNotLoggedIn, async (req, res, next) => {
    const { user_id, password, password_verification, nickname } = req.body;
    try {
        const exUser = await User.findOne({ where: { user_id } });
        if (exUser) {
            req.flash('joinError', '이미 가입된 이메일입니다.');
            res.locals.flashMessage = '이미 가입된 이메일입니다.';
            return res.redirect('/join');
        }
        if (password != password_verification) {
            req.flash('joinError', '비밀번호가 일치하지 않습니다.');
            res.locals.flashMessage = '비밀번호가 일치하지 않습니다.';
            return res.redirect('/join');
        }
        if (!password) {
            req.flash('joinError', '비밀번호를 입력해 주세요.');
            res.locals.flashMessage = '비밀번호를 입력해 주세요.';
            return res.redirect('/join');
        }
        //비밀번호와 api키 암호화
        const hash = await bcrypt.hash(password, 12);
        await User.create({
            user_id,
            password: hash,
            nickname,
            points: 0
        });
        return res.redirect('/');
    } catch (error) {
        console.error(error);
        return next(error);
    }
});

//로그인 라우터
router.post('/login', isNotLoggedIn, (req, res, next) => {
    passport.authenticate('local', (authError, user, info) => {
        if (authError) {
            console.error(authError);
            return next(authError);
        }
        if (!user) {
            req.flash('loginError', info.message);
            return res.redirect('/');
        }
        return req.login(user, (loginError) => {
            if (loginError) {
                console.error(loginError);
                return next(loginError);
            }
            return res.redirect('/');
        });
    })(req, res, next); 
});

//로그아웃 라우터
router.get('/logout', isLoggedIn, (req, res, next) => {
    req.logout((err) => {
        if (err) {
            console.error(err);
            return next(err);
        }
        req.session.destroy((err) => {
            if (err) {
                console.error(err);
                return next(err);
            }
            res.redirect('/');
        });
    });
});

//비밀번호 변경 라우터
router.post('/change-pw', isLoggedIn, async (req, res, next) => {
    const { present_pw, new_pw, new_pw_verification } = req.body;
    try {
      const hash = await bcrypt.hash(new_pw, 12);
      if (new_pw != new_pw_verification) {
        req.flash('joinError', '새 비밀번호와 비밀번호 확인이 일치하지 않습니다.');
        res.locals.flashMessage = '새 비밀번호와 비밀번호 확인이 일치하지 않습니다.';
        return res.redirect('/changepw');
      }
      const result = await bcrypt.compare(present_pw, req.user.password);
      if (!result) {
        req.flash('joinError', '비밀번호가 일치하지 않습니다.');
        res.locals.flashMessage = '비밀번호가 일치하지 않습니다.';
        return res.redirect('/changepw');
      }
      await db.User.update({
        password: hash
      }, {
        where: {
          id: req.user.id
        },
      });
      return res.redirect('/mypage');
    } catch (error) {
      console.error(error);
      return next(error);
    }
  });
  
  //계정 삭제 라우터
  router.post('/withdrawal', isLoggedIn, async (req, res, next) => {
    const { present_pw } = req.body;
    try {
      const result = await bcrypt.compare(present_pw, req.user.password);
      if (!result) {
        req.flash('joinError', '비밀번호가 일치하지 않습니다.');
        res.locals.flashMessage = '비밀번호가 일치하지 않습니다.';
        return res.redirect('/withdrawal');
      }
      await db.User.update({
        user_id:null,
        password:null,
        GptApiKey:null,
        GptApiIv:null,
      }, {
        where: {
          id: req.user.id
        },
      });
      await db.User.destroy({ 
        where: {
          Id: req.user.id
        },
      });
      await db.Chatlog.destroy({ 
        where: {
          userId: req.user.id
        },
      });
      await db.Reminder.destroy({ 
        where: {
          userId: req.user.id
        },
      });
      res.redirect('/');
    } catch (error) {
      console.error(error);
      next(error);
    }
  });
  
  module.exports = router;
  