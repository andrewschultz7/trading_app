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

      // Calculate the one-fourth index to split the data
      const oneFourthIndex = Math.ceil(data.length / 10);

      // Extract the first one-fourth of the data
      const oneFourthData = data.slice(0, oneFourthIndex);

      return res.json(oneFourthData);
    } catch (err) {
      console.log(err);
      return res.status(500).json({ error: "Failed to retrieve historical data" });
    }
  });



module.exports = router
