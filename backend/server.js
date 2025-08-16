const express = require('express')
const dotenv = require('dotenv')
const cors = require('cors')
const connectDB = require('./database/connectDB')

dotenv.config()
const app = express()

app.use(cors())
app.use(express.json())

// DB connect
connectDB()

const PORT = process.env.PORT || 5000
app.listen(PORT, () => console.log(`Server running on port ${PORT}`))
