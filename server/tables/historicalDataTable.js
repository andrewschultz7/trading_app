const { Sequelize } = require("sequelize");

const sequelize = new Sequelize({
  dialect: "sqlite",
  storage: "C:\\Users\\b_mat\\Desktop\\trading_app\\trading_data.db",
});

const historicalData = sequelize.define("HistoricalData", {
  Datetime: {
    type: DataTypes.DATE,
    allowNull: false,
  },
  Open: {
    type: DataTypes.DECIMAL(10, 2),
    allowNull: false,
  },
  Close: {
    type: DataTypes.DECIMAL(10, 2),
    allowNull: false,
  },
  High: {
    type: DataTypes.DECIMAL(10, 2),
    allowNull: false,
  },
  Low: {
    type: DataTypes.DECIMAL(10, 2),
    allowNull: false,
  },
  Volume: {
    type: DataTypes.INTEGER,
    allowNull: false,
  },
});

historicalData.sync();

module.exports = historicalData
