const { Sequelize } = require("sequelize");

// Establish dynamic path to local db
const dotenv = require("dotenv");

//Establish connections to routes
const express = require("express");
const app = express();
const cors = require("cors");
app.use(cors());

// Establish sql database
const sequelize = new Sequelize("root", "root", "root", {
  host: "localhost",
  dialect: "sqlite",
  // add path from trading_data.db following the storage key below
  storage: "./trading_data.db",
});
const router = express.Router();

// Establish connections to tables

const { HistoricalData } = require("./tables/historicalDataTable");

// Establish connections to routes

const historicalDataRouter = require("./routes/historicalData");
app.use("/", historicalDataRouter);

// Load env variables

dotenv.config();

//Test Routes

app.get("/", (req, res) => {
  try {
    res.send("Test World");
  } catch (err) {
    console.log(err);
  }
});

// connect to DB
try {
  sequelize.authenticate();
  console.log("Connection to database has been established successfully.");
} catch (error) {
  console.error("Unable to connect to the database:", error);
}

// connect to server
app.listen((port = 8080), () => {
  console.log(`Server running. Listening on port ${port}.`);
});
