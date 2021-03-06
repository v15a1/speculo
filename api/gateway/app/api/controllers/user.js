const userModel = require("../models/user");
const bcrypt = require("bcrypt");
const jwt = require("jsonwebtoken");

module.exports = {
    createUser: function (req, res, next) {

        userModel.findOne({email: req.body.email}, function (err, user) {
            if (err) next(err);

            if (user != null) {
                res.status(409).json({
                    status: "failed",
                    message: "User already exists!"
                });

                return;
            }

            userModel.create(
                {
                    name: req.body.name,
                    email: req.body.email,
                    password: req.body.password,
                    type: 'user'
                },
                function (err, result) {
                    if (err) next(err);
                    else
                        res.json({
                            status: "success",
                            message: "User added successfully!",
                            data: {
                                name: req.body.name,
                                email: req.body.email,
                                password: req.body.password
                            }
                        });
                }
            );
        });
    },

    createAdmin: function (req, res, next) {

        userModel.findOne({email: req.body.email}, function (err, admin) {
            if (err) next(err);

            if (admin != null) {
                res.status(409).json({
                    status: "failed",
                    message: "Admin already exists!"
                });

                return;
            }

            userModel.create(
                {
                    name: req.body.name,
                    email: req.body.email,
                    password: req.body.password,
                    type: 'admin'
                },
                function (err, result) {
                    if (err) next(err);
                    else
                        res.json({
                            status: "success",
                            message: "Admin added successfully!",
                            data: {
                                name: req.body.name,
                                email: req.body.email,
                                password: req.body.password
                            }
                        });
                }
            );
        });
    },


    authenticateUser: function (req, res, next) {
        userModel.findOne({email: req.body.email}, function (err, userInfo) {
            if (err) {
                next(err);
            }else if(!userInfo){

                res.status(401).json({
                    status: "error",
                    message: "Invalid email/password!",
                });
                
            } else {
                if (bcrypt.compareSync(req.body.password, userInfo.password)) {
                    const token = jwt.sign(
                        {id: userInfo._id},
                        req.app.get("secretKey"),
                        {expiresIn: "24h"}
                    );
                    res.json({
                        status: "success",
                        message: "User found!",
                        data: {user: userInfo, token: token}
                    });
                } else {
                    res.status(401).json({
                        status: "error",
                        message: "Invalid email/password!",
                    });
                }
            }
        });
    },

    authenticateAdmin: function (req, res, next) {
        userModel.findOne({email: req.body.email}, function (err, adminInfo) {
            if (err) {
                next(err);
            }else if(!adminInfo){

                res.status(401).json({
                    status: "error",
                    message: "Invalid email/password!",
                });
                
            } else {
                if (bcrypt.compareSync(req.body.password, adminInfo.password)) {
                    const token = jwt.sign(
                        {id: adminInfo._id},
                        req.app.get("secretKey"),
                        {expiresIn: "24h"}
                    );
                    res.json({
                        status: "success",
                        message: "Admin found!",
                        data: {user: adminInfo, token: token}
                    });
                } else {
                    res.status(401).json({
                        status: "error",
                        message: "Invalid email/password!",
                    });
                }
            }
        });
    },


    validateUser: function(req, res, next){
        jwt.verify(req.headers["x-access-token"], req.app.get("secretKey"), function (
            err,
            decoded
        ) {
            if (err) {
                res.json({status: "error", message: err.message, data: null});
            } else {
                // add user id to request
                req.body.userId = decoded.id;
                next();
            }
        });
    }
};
