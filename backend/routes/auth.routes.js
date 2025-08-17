const express = require("express");
const authRouter = express.Router();
const {register, login, profile}= require("../controllers/auth.controller");
const authMiddleware = require("../middlewares/authMiddleware");

// Public Routes
authRouter.post("/register", register);
authRouter.post("/login", login);

// Protected Route 
authRouter.get("/profile", authMiddleware, profile);

module.exports = authRouter;
