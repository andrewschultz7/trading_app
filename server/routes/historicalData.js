const { Sequelize, DataTypes } = require("sequelize");
const sequelize = new Sequelize({
    dialect: "sqlite",
    storage: "C:\\Users\\b_mat\\Desktop\\trading_app\\trading_data.db",
  });
const express = require('express');
const router = express.Router();
const app = express();
app.use(express.json()); // Middleware for parsing JSON bodies
app.use(express.urlencoded({ extended: true })); // Middleware for parsing URL-encoded bodies
const { HistoricalData } = require("../tables/historicalDataTable")

router.get("/historical", async (req, res) => {
    try {
        const data = await HistoricalData.findAll();
        return res.json(data);
    } catch (err) {
        console.log(err);
    }
})

module.exports = router
