const { Sequelize } = require("sequelize");
const express = require("express");
const app = express();
// Establish sql database
const sequelize = new Sequelize("root", "root", "root", {
  host: "localhost",
  dialect: "sqlite",
  storage: "C:\\Users\\b_mat\\Desktop\\trading_app\\trading_data.db"
});

// Establish connections to tables

//Test Routes

app.get("/", (req, res) => {
  try {
    res.send("Test World");
  } catch (err) {
    console.log(err);
  }
});

try {
  sequelize.authenticate();
  console.log("Connection to database has been established successfully.");
} catch (error) {
  console.error("Unable to connect to the database:", error);
}


app.listen((port = 8080), () => {
    console.log(`Server running. Listening on port ${port}.`);
  });
