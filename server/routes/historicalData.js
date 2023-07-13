const { Sequelize, DataTypes } = require("sequelize");
const sequelize = new Sequelize({
    dialect: "sqlite",
    storage: "./trading_data.db",
  });
const express = require('express');
const router = express.Router();
const app = express();
app.use(express.json()); // Middleware for parsing JSON bodies
app.use(express.urlencoded({ extended: true })); // Middleware for parsing URL-encoded bodies
const { HistoricalData } = require("../tables/historicalDataTable")

const NodeCache = require('node-cache');
const cache = new NodeCache();

router.get('/historical', async (req, res) => {
  try {
    // Check if the data is already cached
    const cachedData = cache.get('historicalData');

    if (cachedData) {
      // Return the cached data
      return res.json(cachedData);
    }

    // Fetch the data from the database
    const data = await HistoricalData.findAll();

    // Calculate the one-fourth index to split the data
    const oneFourthIndex = Math.ceil(data.length / 10);

    // Extract the first one-fourth of the data
    const oneFourthData = data.slice(0, oneFourthIndex);

    // Cache the data for future requests
    cache.set('historicalData', oneFourthData);

    return res.json(oneFourthData);
  } catch (err) {
    console.log(err);
    return res.status(500).json({ error: 'Failed to retrieve historical data' });
  }
});

module.exports = router;
