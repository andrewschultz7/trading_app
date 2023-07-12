CREATE TABLE `trading_data` (
  `Timestamp` INT,
  `gmtoffset` INT,
  `Datetime` DATETIME2,
  `Open` DECIMAL(10,2),
  `Close` DECIMAL(10,2),
  `High` DECIMAL(10,2),
  `Low` DECIMAL(10,2),
  `Volume` INT,
  `vwap` DECIMAL(10,2)
);


CREATE TABLE `three_barsignal` (
  `Timestart` INT,
  `Timeeend` INT,
  `riskreward` INT,
  `success` TEXT
);