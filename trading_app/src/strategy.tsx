import { useEffect, useState, useRef, useCallback } from "react";
import "./App.css";
import Chart from "react-apexcharts";
import { Link } from "react-router-dom";

const directionEmojis = {
  up: "🚀",
  down: "🔻",
  "": "",
};

const initialAnnotations = [];

const initialChartOptions = {
  chart: {
    type: "line",
    height: 350,
    animations: {
      enabled: true,
      easing: "linear",
      dynamicAnimation: {
        speed: 150,
      },
    },
  },
  stroke: {
    width: [2, 1],
  },
  series: [],
  title: {
    text: "CandleStick Chart",
    align: "left",
  },
  xaxis: {
    type: "datetime",
  },
  yaxis: {
    tooltip: {
      enabled: true,
    },
  },
  annotations: {
    points: initialAnnotations,
  },
  //   plotOptions: {
  //     candlestick: {
  //       colors: {
  //         upward: 'rgb(0,255,0)',
  //         downward: 'rgb(255,0,0)',
  //       },
  //     },
  //   },
  colors: ["#546E7A", "#E91E63", "#FFBB5C", "#78D6C6", "#22A699"],
};

const Strategy = () => {
  const chartRef = useRef(null);
  const [chartData, setChartData] = useState({
    series: [],
    price: -1,
    prevPrice: -1,
    priceTime: new Date(),
    annotations: initialAnnotations,
  });
  const [strategyData, setStrategyData] = useState(null);
  const [curStrategyData, setCurStrategyData] = useState(0);
  const [chartOptions, setChartOptions] = useState(initialChartOptions);

  const fetchData = useCallback(async () => {
    try {
      const strategyUrl = `http://localhost:8000/strategy`;
      const strategyResponse = await fetch(strategyUrl);
      const data = await strategyResponse.json();
      setStrategyData(data);
    } catch (error) {
      console.log(error);
    }
  }, []);

  const fetchCandles = useCallback(async () => {
    try {
      if (strategyData) {
        const curStrat = strategyData[curStrategyData];
        const start = curStrat?.prebuffer;
        const end = curStrat?.postbuffer;
        const retrieveCandlesUrl = `http://localhost:8000/candles/retrieve?start=${start}&end=${end}`;
        const candlesResponse = await fetch(retrieveCandlesUrl);
        const data = await candlesResponse.json();

        const prices = data.map((item) => ({
          x: new Date(item.datetime).getTime(),
          y: [item.open, item.high, item.low, item.close],
        }));

        const ema009Line = data.map((x) => ({
          x: new Date(x.datetime).getTime(),
          y: x.ema009,
        }));

        const ema021Line = data.map((x) => ({
          x: new Date(x.datetime).getTime(),
          y: x.ema021,
        }));

        const ema200Line = data.map((x) => ({
          x: new Date(x.datetime).getTime(),
          y: x.ema200,
        }));

        const vwapLine = data.map((x) => ({
          x: new Date(x.datetime).getTime(),
          y: x.vwap,
        }));

        const newAnnotations = {
          xaxis: [
            {
              x: new Date(curStrat.box.timestart).getTime() - 110000,
              x2: new Date(curStrat.box.timeend).getTime() + 110000,
              fillColor: "#C5C6D0",
              opacity: 0.4,
              label: {
                borderColor: "#C5C6D0",
                style: {
                  fontSize: "10px",
                  color: "#000",
                  background: "#C5C6D0",
                },
                offsetY: -10,
                text: "Box",
              },
            },
          ],
        };

        setChartOptions({ ...chartOptions, annotations: newAnnotations });

        const latestPrice = parseFloat(prices[prices.length - 1].y[3]);

        setChartData((prevChartData) => ({
          ...prevChartData,
          prevPrice:
            prevChartData.price !== latestPrice
              ? latestPrice
              : prevChartData.prevPrice,
          price: latestPrice,
          priceTime: new Date(prices[prices.length - 1].x),
          series: [
            { name: "candlesticks", type: "candlestick", data: prices },
            { name: "ema009", type: "line", data: ema009Line },
            { name: "ema021", type: "line", data: ema021Line },
            { name: "ema200", type: "line", data: ema200Line },
            { name: "vwap", type: "line", data: vwapLine },
          ],
        }));
      }
    } catch (error) {
      console.log(error);
    }
  }, [strategyData, curStrategyData, chartOptions]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  useEffect(() => {
    if (strategyData && curStrategyData >= 0) {
      fetchCandles();
    }
  }, [strategyData, curStrategyData, fetchCandles]);

  //   const handleChartClick = useCallback(
  //     ({ dataPointIndex }) => {
  //       if (chartRef.current) {
  //         const annotationText = `Annotation ${chartData.annotations.length + 1}`;
  //         const chart = chartRef.current.chart;
  //         const series = chart.w.globals.series[0];
  //         const dataItem = series[dataPointIndex];

  //         const offsetY = -30 * chartData.annotations.length;

  //         const annotation = {
  //           x: dataItem.x,
  //           y: dataItem.y[3],
  //           marker: {
  //             size: 4,
  //             fillColor: '#ff0000',
  //             strokeColor: '#fff',
  //             radius: 2,
  //           },
  //           label: {
  //             borderColor: '#ff0000',
  //             style: {
  //               color: '#fff',
  //               background: '#ff0000',
  //             },
  //             text: annotationText,
  //             offsetY,
  //           },
  //         };

  //         chart.addPointAnnotation(annotation);
  //         setChartData((prevChartData) => ({
  //           ...prevChartData,
  //           annotations: [...prevChartData.annotations, annotation],
  //         }));
  //       }
  //     },
  //     [chartData.annotations],
  //   );

  const direction =
    chartData.prevPrice < chartData.price
      ? "up"
      : chartData.prevPrice > chartData.price
      ? "down"
      : "";

  const cycleButton = (c) => {
    const maxIndex = strategyData.length - 1;
    if (c == -1 && curStrategyData <= 0) {
      setCurStrategyData(maxIndex);
    } else if (c == 1 && curStrategyData >= maxIndex) {
      setCurStrategyData(0);
    } else {
      setCurStrategyData((prevCounter) => prevCounter + c);
    }
  };

  return (
    <div>
      <nav>
        <Link to={`/`}>Main</Link>
      </nav>
      <div className="ticker">Sample Data</div>
      <div className={`price ${direction}`}>
        ${chartData.price} {directionEmojis[direction]}
      </div>
      <div className="price-time">
        {chartData.priceTime && chartData.priceTime.toLocaleTimeString()}
      </div>
      <div style={{ textAlign: "right" }}>
        <button onClick={() => cycleButton(-1)}>Previous</button>
        <span style={{ margin: "0 10px" }}>{curStrategyData}</span>
        <button onClick={() => cycleButton(1)}>Next</button>
      </div>
      <Chart
        options={chartOptions}
        series={chartData.series}
        type="candlestick"
        width="100%"
        height={320}
        ref={chartRef}
      />
    </div>
  );
};

export default Strategy;
