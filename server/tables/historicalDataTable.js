const { Sequelize, DataTypes } = require("sequelize");

const sequelize = new Sequelize({
  dialect: "sqlite",
  storage: "C:\\Users\\b_mat\\Desktop\\trading_app\\trading_data.db",
});

const HistoricalData = sequelize.define("HistoricalData", {
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

sequelize
  .authenticate()
  .then(() => {
    console.log("Connection has been established successfully.");
    HistoricalData.sync()
      .then(() => {
        console.log("Table created successfully.");
        sequelize.query("SELECT * FROM trading_data", { type: Sequelize.QueryTypes.SELECT })
          .then((results) => {
            HistoricalData.bulkCreate(results)
              .then(() => {
                console.log("Data inserted successfully.");
              })
              .catch((error) => {
                console.error("Error inserting data:", error);
              });
          })
          .catch((error) => {
            console.error("Error retrieving data:", error);
          });
      })
      .catch((error) => {
        console.error("Error creating table:", error);
      });
  })
  .catch((error) => {
    console.error("Unable to connect to the database:", error);
  });

  module.exports = { HistoricalData };
