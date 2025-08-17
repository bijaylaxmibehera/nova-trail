const express = require('express')
const dotenv = require('dotenv')
const cors = require('cors')
const bodyParser=require('body-parser')
const connectDB = require('./database/connectDB')
const authRouter= require('./routes/auth.routes')

dotenv.config()
const app = express()

app.use(cors())
app.use(express.json())
app.use(bodyParser.urlencoded({ extended: true }))
app.use(bodyParser.json())

// DB connect
connectDB()

//routes
app.use('/api/auth', authRouter)

const PORT = process.env.PORT || 5000
app.listen(PORT, () => console.log(`Server running on port ${PORT}`))
